import os
os.environ["DATABASE_URL"]="sqlite:///./test_parent.db"

"""Focused Parent / Guardian security regression coverage.

The broad parent workflows are covered in test_auth.py. These tests lock down the
most important parent boundary: a parent can only see linked learners and cannot
cross into administrative write surfaces.
"""
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution, ParentStudentLink
from app.security import hash_password

client=TestClient(app)
PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all([Institution(id=1,name="Parent Test School",institution_type="SCHOOL",code="PARENT-T1"),Institution(id=2,name="Other College",institution_type="COLLEGE",code="PARENT-T2")]); db.flush()
        parent=User(email="parent@test.local",name="Parent One",role="Parent / Guardian",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True)
        student=User(email="student@test.local",name="Linked Pupil",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True)
        other=User(email="other@test.local",name="Other Pupil",role="Student",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True)
        db.add_all([parent,student,other]); db.flush(); db.add(ParentStudentLink(tenant_id=1,parent_user_id=parent.id,student_user_id=student.id,relationship="Guardian")); db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def login(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD})
    assert r.status_code==200
    return {"Authorization":f"Bearer {r.json()['access_token']}"}

def test_parent_linked_child_surfaces_and_unlinked_guard():
    h=login("parent@test.local")
    children=client.get("/api/v1/parents/children",headers=h)
    assert children.status_code==200
    for child in children.json():
        for suffix in ("fees","academics","transport","location"):
            assert client.get(f"/api/v1/parents/children/{child['id']}/{suffix}",headers=h).status_code==200
    for suffix in ("fees","academics","transport","location"):
        assert client.get(f"/api/v1/parents/children/999999/{suffix}",headers=h).status_code==403

def test_parent_self_service_is_not_available_to_student():
    parent=login("parent@test.local"); student=login("student@test.local")
    for path in ("/api/v1/parents/dashboard","/api/v1/parents/children","/api/v1/parents/events","/api/v1/parents/grievances","/api/v1/parents/leave","/api/v1/parents/messages","/api/v1/parents/messages/recipients"):
        assert client.get(path,headers=parent).status_code==200
        assert client.get(path,headers=student).status_code==403

def test_parent_cannot_use_admin_finance_hr_or_campus_mutations():
    h=login("parent@test.local")
    assert client.get("/api/v1/finance/report",headers=h).status_code==403
    assert client.post("/api/v1/fee-ledger",headers=h,json={"student_user_id":999999,"fee_code":"PARENT","title":"Blocked","amount_due":100}).status_code==403
    assert client.post("/api/v1/hr/recruitment",headers=h,json={"name":"Blocked","email":"blocked-parent@test.local","position":"Teacher"}).status_code==403
    assert client.post("/api/v1/campus/visitors",headers=h,json={"name":"Blocked","purpose":"Blocked"}).status_code==403

def test_parent_has_no_generic_privileged_action_escape_hatch():
    h=login("parent@test.local")
    for action in ("approve","pay","manage_users"):
        assert client.post(f"/api/v1/module-actions/{action}",headers=h,json={"page":"Parent Dashboard"}).status_code==403
