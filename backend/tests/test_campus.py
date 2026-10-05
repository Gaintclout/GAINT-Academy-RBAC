import os
os.environ["DATABASE_URL"]="sqlite:///./test_campus.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution
from app.security import hash_password

client=TestClient(app); PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all([Institution(id=1,name="Tenant One",institution_type="SCHOOL",code="T1"),Institution(id=2,name="Tenant Two",institution_type="COLLEGE",code="T2")]); db.flush()
        db.add_all([
          User(email="campus1@test.local",name="Campus One",role="Campus Admin",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
          User(email="campus1b@test.local",name="Campus Other",role="Campus Admin",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=2,is_active=True),
          User(email="campus2@test.local",name="Campus Tenant Two",role="Campus Admin",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
          User(email="student1@test.local",name="Student One",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
          User(email="student1b@test.local",name="Student Other Campus",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=2,is_active=True),
          User(email="student2@test.local",name="Student Tenant Two",role="Student",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
          User(email="teacher1@test.local",name="Teacher One",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
        ]); db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD}); assert r.status_code==200
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def test_campus_people_reads_are_campus_and_tenant_scoped():
    h=auth("campus1@test.local")
    students=client.get("/api/v1/campus/students",headers=h); assert students.status_code==200
    assert [x["email"] for x in students.json()]==["student1@test.local"]
    staff=client.get("/api/v1/campus/staff",headers=h); assert staff.status_code==200
    emails={x["email"] for x in staff.json()}
    assert "teacher1@test.local" in emails and "campus1@test.local" in emails
    assert "campus1b@test.local" not in emails and "campus2@test.local" not in emails
    dashboard=client.get("/api/v1/campus/dashboard",headers=h); assert dashboard.status_code==200
    assert dashboard.json()["students"]["total"]==1

def test_non_campus_roles_cannot_use_campus_operations():
    student=auth("student1@test.local"); teacher=auth("teacher1@test.local")
    for path in ("/api/v1/campus/dashboard","/api/v1/campus/students","/api/v1/campus/staff","/api/v1/campus/attendance","/api/v1/campus/transport","/api/v1/campus/visitors","/api/v1/campus/inventory","/api/v1/campus/assets","/api/v1/campus/events","/api/v1/campus/grievances","/api/v1/campus/reports"):
        assert client.get(path,headers=student).status_code==403
        assert client.get(path,headers=teacher).status_code==403

def test_visitor_lifecycle_and_cross_campus_mutation_block():
    h=auth("campus1@test.local")
    created=client.post("/api/v1/campus/visitors",headers=h,json={"name":"Visitor One","phone":"123","purpose":"Meeting","person_to_meet":"Teacher One"}); assert created.status_code==200
    vid=created.json()["id"]
    assert client.patch(f"/api/v1/campus/visitors/{vid}",headers=h,json={"status":"CHECKED_OUT"}).status_code==200
    assert client.patch(f"/api/v1/campus/visitors/{vid}",headers=auth("campus1b@test.local"),json={"status":"CHECKED_OUT"}).status_code==404
    assert client.patch(f"/api/v1/campus/visitors/{vid}",headers=auth("campus2@test.local"),json={"status":"CHECKED_OUT"}).status_code==404

def test_inventory_validation_and_cross_campus_isolation():
    h=auth("campus1@test.local")
    item={"name":"Paper","category":"Office","item_code":"INV-1","quantity":10,"minimum_quantity":2,"location":"Store","status":"ACTIVE","notes":""}
    created=client.post("/api/v1/campus/inventory",headers=h,json=item); assert created.status_code==200
    iid=created.json()["id"]
    assert client.post("/api/v1/campus/inventory",headers=h,json={**item,"item_code":"NEG","quantity":-1}).status_code in (400,422)
    assert client.patch(f"/api/v1/campus/inventory/{iid}",headers=h,json={"quantity":5,"status":"ACTIVE","notes":"Adjusted"}).status_code==200
    assert client.patch(f"/api/v1/campus/inventory/{iid}",headers=auth("campus1b@test.local"),json={"quantity":1,"status":"ACTIVE","notes":""}).status_code==404
    assert client.get("/api/v1/campus/inventory",headers=auth("campus1b@test.local")).json()==[]

def test_asset_duplicate_validation_and_cross_tenant_isolation():
    h=auth("campus1@test.local")
    asset={"asset_code":"ASSET-1","name":"Projector","category":"IT","serial_number":"S1","location":"Room 1","assigned_to":"","condition":"GOOD","status":"ACTIVE","notes":""}
    created=client.post("/api/v1/campus/assets",headers=h,json=asset); assert created.status_code==200
    aid=created.json()["id"]
    assert client.post("/api/v1/campus/assets",headers=h,json=asset).status_code==409
    assert client.patch(f"/api/v1/campus/assets/{aid}",headers=h,json={"location":"Room 2","assigned_to":"","condition":"DAMAGED","status":"ACTIVE","notes":"Repair"}).status_code==200
    assert client.patch(f"/api/v1/campus/assets/{aid}",headers=auth("campus2@test.local"),json={"location":"","assigned_to":"","condition":"GOOD","status":"ACTIVE","notes":""}).status_code==404
    assert client.get("/api/v1/campus/assets",headers=auth("campus2@test.local")).json()==[]

def test_event_date_and_audience_validation_with_campus_isolation():
    h=auth("campus1@test.local")
    event={"title":"Annual Day","event_type":"Cultural","venue":"Hall","starts_at":"2026-10-20T10:00:00","ends_at":"2026-10-20T12:00:00","audience_role":"ALL","registration_required":True,"registration_deadline":"2026-10-19T18:00:00"}
    assert client.post("/api/v1/campus/events",headers=h,json=event).status_code==200
    assert client.post("/api/v1/campus/events",headers=h,json={**event,"title":"Bad Dates","ends_at":"2026-10-20T09:00:00"}).status_code==400
    assert client.post("/api/v1/campus/events",headers=h,json={**event,"title":"Bad Audience","audience_role":"HR"}).status_code==400
    assert client.get("/api/v1/campus/events",headers=auth("campus1b@test.local")).json()==[]
    assert client.get("/api/v1/campus/events",headers=auth("campus2@test.local")).json()==[]

def test_reports_only_aggregate_assigned_campus():
    h=auth("campus1@test.local")
    client.post("/api/v1/campus/visitors",headers=h,json={"name":"Own Visitor","phone":"","purpose":"Meeting","person_to_meet":""})
    client.post("/api/v1/campus/inventory",headers=h,json={"name":"Own Stock","category":"Office","item_code":"OWN","quantity":1,"minimum_quantity":2,"location":"","status":"ACTIVE","notes":""})
    report=client.get("/api/v1/campus/reports",headers=h); assert report.status_code==200
    data=report.json()
    assert data["campus_id"]==1 and data["people"]["students"]==1
    assert data["visitors"]["total"]==1 and data["inventory"]["items"]==1 and data["inventory"]["low_stock"]==1
    other=client.get("/api/v1/campus/reports",headers=auth("campus1b@test.local")).json()
    assert other["campus_id"]==2 and other["people"]["students"]==1 and other["visitors"]["total"]==0 and other["inventory"]["items"]==0
