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
