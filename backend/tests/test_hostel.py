import os
os.environ["DATABASE_URL"]="sqlite:///./test_hostel.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base,engine,SessionLocal
from app.models import Institution,User,ParentStudentLink
from app.security import hash_password

client=TestClient(app); PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add(Institution(id=1,name="Hostel School",institution_type="SCHOOL",code="HST")); db.flush()
        db.add_all([
            User(id=1,email="admin@hst.local",name="Admin",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(id=2,email="student@hst.local",name="Student",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(id=3,email="parent@hst.local",name="Parent",role="Parent / Guardian",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(id=4,email="teacher@hst.local",name="Teacher",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
        ]); db.flush()
        db.add(ParentStudentLink(parent_user_id=3,student_user_id=2,relationship="Mother",tenant_id=1)); db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD}); assert r.status_code==200,r.text
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def create_allocation(admin):
    h=client.post("/api/v1/admin/hostels",headers=admin,json={"campus_id":1,"name":"A Block","code":"A","hostel_type":"GENERAL","warden_name":"Warden","warden_phone":"9999999999"}); assert h.status_code==200,h.text
    hostel=h.json()
    r=client.post("/api/v1/admin/hostel-rooms",headers=admin,json={"hostel_id":hostel["id"],"room_number":"101","floor":"1","capacity":1,"room_type":"STANDARD"}); assert r.status_code==200,r.text
    room=r.json()
    a=client.post("/api/v1/admin/hostel-allocations",headers=admin,json={"hostel_id":hostel["id"],"room_id":room["id"],"student_user_id":2,"bed_number":"B1","notes":"Initial"}); assert a.status_code==200,a.text
    return hostel,room,a.json()

def test_admin_hostel_allocation_and_capacity_guard():
    admin=auth("admin@hst.local"); hostel,room,_=create_allocation(admin)
    second=client.post("/api/v1/admin/hostel-allocations",headers=admin,json={"hostel_id":hostel["id"],"room_id":room["id"],"student_user_id":4,"bed_number":"B2","notes":""})
    assert second.status_code in (400,404,409)

def test_student_sees_only_own_accommodation():
    admin=auth("admin@hst.local"); create_allocation(admin)
    r=client.get("/api/v1/accommodation/me",headers=auth("student@hst.local")); assert r.status_code==200,r.text
    assert r.json()["current"]["hostel_name"]=="A Block"; assert r.json()["current"]["room_number"]=="101"; assert r.json()["current"]["bed_number"]=="B1"

def test_parent_sees_linked_child_accommodation():
    admin=auth("admin@hst.local"); create_allocation(admin)
    r=client.get("/api/v1/accommodation/children",headers=auth("parent@hst.local")); assert r.status_code==200,r.text
    child=r.json()["children"][0]; assert child["student_user_id"]==2; assert child["current"]["hostel_name"]=="A Block"

def test_accommodation_role_boundaries():
    assert client.get("/api/v1/accommodation/me",headers=auth("teacher@hst.local")).status_code==403
    assert client.get("/api/v1/accommodation/children",headers=auth("student@hst.local")).status_code==403
    assert client.get("/api/v1/admin/hostels",headers=auth("student@hst.local")).status_code==403

def test_checkout_moves_student_to_history():
    admin=auth("admin@hst.local"); _,_,allocation=create_allocation(admin)
    r=client.patch(f"/api/v1/admin/hostel-allocations/{allocation['id']}/checkout",headers=admin,json={"notes":"Completed"}); assert r.status_code==200,r.text
    me=client.get("/api/v1/accommodation/me",headers=auth("student@hst.local")); assert me.status_code==200
    assert me.json()["current"] is None; assert me.json()["history"][0]["status"]!="ACTIVE"
