"""Cross-role UAT smoke coverage for the eight GAINT Academy roles.

This suite verifies that every seeded role can authenticate, reaches its intended
workspace, and is rejected from a representative privileged surface belonging to
another role. Detailed domain behavior remains covered by the dedicated role tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed

client=TestClient(app)
PASSWORD="Password@123"

@pytest.fixture(scope="module", autouse=True)
def ensure_uat_baseline():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)

ROLE_ACCOUNTS={
    "Institution Admin":"admin@gaintacademy.com",
    "Teacher":"teacher@gaintacademy.com",
    "Student":"student@gaintacademy.com",
    "Parent / Guardian":"parent@gaintacademy.com",
    "Accounts":"accounts@gaintacademy.com",
    "HR":"hr@gaintacademy.com",
    "Campus Admin":"campus@gaintacademy.com",
    "Auditor":"auditor@gaintacademy.com",
}

def login(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD})
    assert r.status_code==200, r.text
    body=r.json()
    assert body.get("access_token")
    return {"Authorization":f"Bearer {body['access_token']}"},body["user"]

def test_all_eight_roles_authenticate_and_preserve_identity():
    for role,email in ROLE_ACCOUNTS.items():
        headers,user=login(email)
        assert user["role"]==role
        me=client.get("/api/v1/auth/me",headers=headers)
        assert me.status_code==200, (role,me.text)
        assert me.json()["email"]==email
        assert me.json()["role"]==role

def test_role_dashboards_and_primary_workspaces():
    checks={
        "Institution Admin":["/api/v1/dashboard","/api/v1/admissions/summary","/api/v1/users"],
        "Teacher":["/api/v1/dashboard","/api/v1/teacher-roster","/api/v1/teacher/events"],
        "Student":["/api/v1/dashboard","/api/v1/student/profile","/api/v1/student/events"],
        "Parent / Guardian":["/api/v1/dashboard","/api/v1/parents/dashboard","/api/v1/parents/children"],
        "Accounts":["/api/v1/dashboard","/api/v1/finance/summary","/api/v1/finance/payments"],
        "HR":["/api/v1/dashboard","/api/v1/hr/staff","/api/v1/hr/reports"],
        "Campus Admin":["/api/v1/dashboard","/api/v1/campus/dashboard","/api/v1/campus/students"],
        "Auditor":["/api/v1/dashboard","/api/v1/auditor/dashboard","/api/v1/auditor/evidence"],
    }
    for role,paths in checks.items():
        headers,_=login(ROLE_ACCOUNTS[role])
        for path in paths:
            r=client.get(path,headers=headers)
            assert r.status_code==200, (role,path,r.status_code,r.text)

def test_cross_role_privilege_boundaries():
    checks={
        "Teacher":["/api/v1/users","/api/v1/finance/summary","/api/v1/hr/staff","/api/v1/campus/dashboard"],
        "Student":["/api/v1/users","/api/v1/finance/summary","/api/v1/hr/staff","/api/v1/auditor/dashboard"],
        "Parent / Guardian":["/api/v1/users","/api/v1/finance/report","/api/v1/hr/staff","/api/v1/campus/dashboard"],
        "Accounts":["/api/v1/users","/api/v1/hr/staff","/api/v1/campus/dashboard"],
        "HR":["/api/v1/users","/api/v1/finance/payments","/api/v1/campus/dashboard"],
        "Campus Admin":["/api/v1/finance/summary","/api/v1/hr/staff"],
    }
    for role,paths in checks.items():
        headers,_=login(ROLE_ACCOUNTS[role])
        for path in paths:
            r=client.get(path,headers=headers)
            assert r.status_code==403, (role,path,r.status_code,r.text)

def test_auditor_read_access_does_not_grant_admin_mutation():
    headers,_=login(ROLE_ACCOUNTS["Auditor"])
    assert client.get("/api/v1/finance/summary",headers=headers).status_code==200
    assert client.get("/api/v1/hr/staff",headers=headers).status_code==200
    r=client.post("/api/v1/users",headers=headers,json={
        "name":"Blocked Auditor Mutation","email":"blocked.auditor@test.local",
        "password":"Blocked@123","role":"Student","campus_id":1
    })
    assert r.status_code==403

def test_school_college_university_admins_are_tenant_distinct():
    accounts=[
        ("admin@gaintacademy.com","UNIVERSITY"),
        ("school.admin@gaintacademy.com","SCHOOL"),
        ("college.admin@gaintacademy.com","COLLEGE"),
    ]
    seen=set()
    for email,expected_type in accounts:
        headers,user=login(email)
        seen.add(user["tenant_id"])
        me=client.get("/api/v1/auth/me",headers=headers)
        assert me.status_code==200
        assert me.json()["institution"]["institution_type"]==expected_type
    assert len(seen)==3
