"""College-mode UAT: verify all eight roles remain in the College tenant and key role workspaces work."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed

client=TestClient(app)
PASSWORD="Password@123"
COLLEGE={
 "Institution Admin":"college.admin@gaintacademy.com",
 "Teacher":"college.teacher@gaintacademy.com",
 "Student":"college.student@gaintacademy.com",
 "Parent / Guardian":"college.parent@gaintacademy.com",
 "Accounts":"college.accounts@gaintacademy.com",
 "HR":"college.hr@gaintacademy.com",
 "Campus Admin":"college.campus@gaintacademy.com",
 "Auditor":"college.auditor@gaintacademy.com",
}

@pytest.fixture(scope="module",autouse=True)
def baseline():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db: seed(db)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD})
    assert r.status_code==200,r.text
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def test_college_role_identity_and_tenant_context():
    for role,email in COLLEGE.items():
        r=client.get("/api/v1/auth/me",headers=auth(email))
        assert r.status_code==200,(role,r.text)
        body=r.json()
        assert body["role"]==role
        assert body["tenant_id"]==3
        assert body["institution"]["institution_type"]=="COLLEGE"

def test_college_primary_role_workspaces():
    checks={
      "Institution Admin":["/api/v1/dashboard","/api/v1/admissions/summary","/api/v1/academic-structure"],
      "Teacher":["/api/v1/dashboard","/api/v1/teacher-roster","/api/v1/teacher/events"],
      "Student":["/api/v1/dashboard","/api/v1/student/profile","/api/v1/student/events","/api/v1/library/me"],
      "Parent / Guardian":["/api/v1/dashboard","/api/v1/parents/dashboard","/api/v1/parents/children"],
      "Accounts":["/api/v1/dashboard","/api/v1/finance/summary","/api/v1/finance/payments"],
      "HR":["/api/v1/dashboard","/api/v1/hr/staff","/api/v1/hr/reports"],
      "Campus Admin":["/api/v1/dashboard","/api/v1/campus/dashboard","/api/v1/campus/students"],
      "Auditor":["/api/v1/dashboard","/api/v1/auditor/dashboard","/api/v1/auditor/evidence"],
    }
    for role,paths in checks.items():
        h=auth(COLLEGE[role])
        for path in paths:
            r=client.get(path,headers=h)
            assert r.status_code==200,(role,path,r.status_code,r.text)

def test_college_parent_is_linked_only_to_college_student():
    r=client.get("/api/v1/parents/children",headers=auth(COLLEGE["Parent / Guardian"]))
    assert r.status_code==200,r.text
    rows=r.json()
    assert rows
    assert all(x.get("email","").startswith("college.") for x in rows)

def test_college_admin_user_directory_does_not_leak_other_institutions():
    r=client.get("/api/v1/users",headers=auth(COLLEGE["Institution Admin"]))
    assert r.status_code==200
    emails={x["email"] for x in r.json()}
    assert COLLEGE["Student"] in emails
    assert "student@gaintacademy.com" not in emails
    assert "school.student@gaintacademy.com" not in emails

def test_college_non_admin_privilege_boundaries():
    for role in ("Teacher","Student","Parent / Guardian"):
        h=auth(COLLEGE[role])
        assert client.get("/api/v1/users",headers=h).status_code==403
        assert client.get("/api/v1/hr/staff",headers=h).status_code==403
