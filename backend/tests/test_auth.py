from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r=client.get("/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_student_login_and_dashboard():
    r=client.post("/api/v1/auth/login",json={
        "email":"student@gaintacademy.com",
        "password":"Password@123"
    })
    assert r.status_code==200
    token=r.json()["access_token"]
    d=client.get("/api/v1/dashboard",headers={"Authorization":f"Bearer {token}"})
    assert d.status_code==200
    assert d.json()["type"]=="student"

def test_parent_cannot_fetch_random_student():
    r=client.post("/api/v1/auth/login",json={
        "email":"parent@gaintacademy.com","password":"Password@123"
    })
    token=r.json()["access_token"]
    d=client.get("/api/v1/parents/children/999999/location",headers={"Authorization":f"Bearer {token}"})
    assert d.status_code==403


def _login(email,password="Password@123"):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":password})
    assert r.status_code==200
    return {"Authorization":f"Bearer {r.json()['access_token']}"}

def test_student_cannot_access_accounts_finance():
    h=_login("student@gaintacademy.com")
    assert client.get("/api/v1/finance/summary",headers=h).status_code==403
    assert client.get("/api/v1/finance/payments",headers=h).status_code==403

def test_teacher_cannot_manage_fee_ledger():
    h=_login("teacher@gaintacademy.com")
    student=client.post("/api/v1/auth/login",json={"email":"student@gaintacademy.com","password":"Password@123"}).json()["user"]
    r=client.post("/api/v1/fee-ledger",headers=h,json={"student_user_id":student["id"],"fee_code":"NOPE","title":"Unauthorized","amount_due":100})
    assert r.status_code==403

def test_parent_cannot_access_institution_finance_report():
    h=_login("parent@gaintacademy.com")
    assert client.get("/api/v1/finance/report",headers=h).status_code==403

def test_auditor_finance_is_read_only():
    h=_login("auditor@gaintacademy.com")
    assert client.get("/api/v1/finance/summary",headers=h).status_code==200
    student=client.post("/api/v1/auth/login",json={"email":"student@gaintacademy.com","password":"Password@123"}).json()["user"]
    r=client.post("/api/v1/fee-ledger",headers=h,json={"student_user_id":student["id"],"fee_code":"AUDIT","title":"Audit attempt","amount_due":100})
    assert r.status_code==403


def test_student_cannot_open_admin_users_module():
    h=_login("student@gaintacademy.com")
    r=client.get("/api/v1/module-access/Users%20%26%20Roles",headers=h)
    assert r.status_code==403

def test_accounts_cannot_open_hr_recruitment_module():
    h=_login("accounts@gaintacademy.com")
    r=client.get("/api/v1/module-access/Recruitment",headers=h)
    assert r.status_code==403

def test_hr_cannot_open_accounts_payments_module():
    h=_login("hr@gaintacademy.com")
    r=client.get("/api/v1/module-access/Payments",headers=h)
    assert r.status_code==403

def test_campus_admin_cannot_open_accounts_refunds_module():
    h=_login("campus@gaintacademy.com")
    r=client.get("/api/v1/module-access/Refunds",headers=h)
    assert r.status_code==403

def test_teacher_cannot_open_audit_trail_module():
    h=_login("teacher@gaintacademy.com")
    r=client.get("/api/v1/module-access/Audit%20Trail",headers=h)
    assert r.status_code==403

def test_parent_cannot_open_staff_module():
    h=_login("parent@gaintacademy.com")
    r=client.get("/api/v1/module-access/Staff",headers=h)
    assert r.status_code==403
