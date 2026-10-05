import os
os.environ.setdefault("DATABASE_URL","sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution, AcademicUnit
from app.security import hash_password

client=TestClient(app)
PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all([
            Institution(id=1,name="Admin Test School",institution_type="SCHOOL",code="ADMIN-T1"),
            Institution(id=2,name="Other College",institution_type="COLLEGE",code="ADMIN-T2"),
        ]); db.flush()
        db.add_all([
            User(email="admin1@test.local",name="Admin One",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="student1@test.local",name="Pupil One",role="Student",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="teacher1@test.local",name="Teacher One",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="admin2@test.local",name="Admin Two",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=92,campus_id=92,is_active=True),
            User(email="student2@test.local",name="Other Student",role="Student",password_hash=hash_password(PASSWORD),tenant_id=92,campus_id=92,is_active=True),
        ])
        db.add_all([
            AcademicUnit(tenant_id=91,campus_id=91,unit_type="CAMPUS",name="School Campus",code="SC-1",status="Active"),
            AcademicUnit(tenant_id=92,campus_id=92,unit_type="CAMPUS",name="Other Campus",code="OC-1",status="Active"),
        ])
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD})
    assert r.status_code==200
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def test_admin_user_directory_is_tenant_scoped():
    rows=client.get("/api/v1/users",headers=auth("admin1@test.local"))
    assert rows.status_code==200
    emails={x["email"] for x in rows.json()}
    assert {"admin1@test.local","student1@test.local","teacher1@test.local"} <= emails
    assert "admin2@test.local" not in emails and "student2@test.local" not in emails

def test_admin_cannot_mutate_other_tenant_user():
    h=auth("admin1@test.local")
    other=next(x for x in client.get("/api/v1/users",headers=auth("admin2@test.local")).json() if x["email"]=="student2@test.local")
    assert client.patch(f"/api/v1/users/{other['id']}",headers=h,json={"name":"Cross Tenant"}).status_code==404

def test_non_admin_cannot_create_or_update_users():
    h=auth("teacher1@test.local")
    payload={"name":"Blocked","email":"blocked@test.local","password":"Test@123","role":"Student","campus_id":91}
    assert client.post("/api/v1/users",headers=h,json=payload).status_code==403
    student=next(x for x in client.get("/api/v1/users",headers=auth("admin1@test.local")).json() if x["email"]=="student1@test.local")
    assert client.patch(f"/api/v1/users/{student['id']}",headers=h,json={"name":"Blocked"}).status_code==403

def test_admin_self_protection_and_role_validation():
    h=auth("admin1@test.local")
    me=client.get("/api/v1/auth/me",headers=h).json()
    assert client.patch(f"/api/v1/users/{me['id']}",headers=h,json={"is_active":False}).status_code==409
    assert client.patch(f"/api/v1/users/{me['id']}",headers=h,json={"role":"Teacher"}).status_code==409
    assert client.post("/api/v1/users",headers=h,json={"name":"Bad Role","email":"badrole@test.local","password":"Test@123","role":"Super Admin","campus_id":91}).status_code==400

def test_admin_academic_structure_rejects_cross_tenant_parent():
    h=auth("admin1@test.local")
    other=client.get("/api/v1/academic-structure",headers=auth("admin2@test.local")).json()[0]
    payload={"unit_type":"SCHOOL_FACULTY","name":"Blocked Faculty","code":"BLOCK","parent_id":other["id"],"campus_id":91,"status":"Active"}
    assert client.post("/api/v1/academic-structure",headers=h,json=payload).status_code==400

def test_admin_inventory_and_asset_mutations_are_tenant_scoped():
    h=auth("admin1@test.local")
    item={"campus_id":91,"name":"Paper","category":"Office","item_code":"ADM-INV","quantity":10,"minimum_quantity":2,"location":"Store","status":"ACTIVE","notes":""}
    created=client.post("/api/v1/admin/inventory",headers=h,json=item); assert created.status_code==200
    iid=created.json()["id"]
    assert client.patch(f"/api/v1/admin/inventory/{iid}",headers=auth("admin2@test.local"),json={"quantity":1,"status":"ACTIVE","notes":""}).status_code==404
    asset={"campus_id":91,"asset_code":"ADM-ASSET","name":"Projector","category":"IT","serial_number":"S1","location":"Room 1","assigned_to":"","condition":"GOOD","status":"ACTIVE","notes":""}
    made=client.post("/api/v1/admin/assets",headers=h,json=asset); assert made.status_code==200
    aid=made.json()["id"]
    assert client.patch(f"/api/v1/admin/assets/{aid}",headers=auth("admin2@test.local"),json={"location":"","assigned_to":"","condition":"GOOD","status":"ACTIVE","notes":""}).status_code==404

def test_teacher_cannot_use_admin_privileged_surfaces():
    h=auth("teacher1@test.local")
    for path in ("/api/v1/admissions/summary","/api/v1/admin/inventory-assets","/api/v1/admin/visitors","/api/v1/admin/health","/api/v1/admin/hostels"):
        assert client.get(path,headers=h).status_code==403
