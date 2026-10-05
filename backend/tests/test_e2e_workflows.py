"""Cross-module E2E regression across the core GAINT Academy role hand-offs.

The detailed create/update rules live in the domain suites. These scenarios protect
the integrated hand-offs users depend on after those domain operations complete.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed

client=TestClient(app)
PASSWORD="Password@123"

@pytest.fixture(scope="module",autouse=True)
def baseline():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD})
    assert r.status_code==200,r.text
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def get(email,path):
    r=client.get(path,headers=auth(email))
    assert r.status_code==200,(email,path,r.status_code,r.text)
    return r.json()

@pytest.mark.parametrize("prefix",["","school.","college."])
def test_admin_student_parent_academic_handoff(prefix):
    admin=f"{prefix}admin@gaintacademy.com"
    student=f"{prefix}student@gaintacademy.com"
    parent=f"{prefix}parent@gaintacademy.com"
    users=get(admin,"/api/v1/users")
    assert student in {u["email"] for u in users}
    profile=get(student,"/api/v1/student/profile")
    children=get(parent,"/api/v1/parents/children")
    assert any(c.get("email")==student for c in children)
    assert profile.get("email",student)==student

@pytest.mark.parametrize("prefix",["","school.","college."])
def test_teacher_student_learning_visibility(prefix):
    teacher=f"{prefix}teacher@gaintacademy.com"
    student=f"{prefix}student@gaintacademy.com"
    roster=get(teacher,"/api/v1/teacher-roster")
    profile=get(student,"/api/v1/student/profile")
    assert isinstance(roster,list)
    assert profile

@pytest.mark.parametrize("prefix",["","school.","college."])
def test_accounts_auditor_finance_handoff(prefix):
    accounts=f"{prefix}accounts@gaintacademy.com"
    auditor=f"{prefix}auditor@gaintacademy.com"
    finance=get(accounts,"/api/v1/finance/summary")
    audit_finance=get(auditor,"/api/v1/finance/summary")
    assert isinstance(finance,dict)
    assert isinstance(audit_finance,dict)
    blocked=client.post("/api/v1/users",headers=auth(auditor),json={
        "name":"E2E Blocked","email":f"{prefix}e2e.blocked@test.local",
        "password":"Blocked@123","role":"Student","campus_id":1})
    assert blocked.status_code==403

@pytest.mark.parametrize("prefix",["","school.","college."])
def test_hr_campus_operations_handoff(prefix):
    hr=f"{prefix}hr@gaintacademy.com"
    campus=f"{prefix}campus@gaintacademy.com"
    staff=get(hr,"/api/v1/hr/staff")
    students=get(campus,"/api/v1/campus/students")
    assert isinstance(staff,list)
    assert isinstance(students,list)

@pytest.mark.parametrize("prefix",["","school.","college."])
def test_student_library_and_events_handoff(prefix):
    student=f"{prefix}student@gaintacademy.com"
    library=get(student,"/api/v1/library/me")
    events=get(student,"/api/v1/student/events")
    assert isinstance(library,(dict,list))
    assert isinstance(events,list)
