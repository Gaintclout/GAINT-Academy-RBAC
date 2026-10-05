"""Security/RBAC regression coverage for authentication, privilege and tenant boundaries."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed

client = TestClient(app)
PASSWORD = "Password@123"


@pytest.fixture(scope="module", autouse=True)
def security_baseline():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)


def login(email, password=PASSWORD):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.parametrize("path", [
    "/api/v1/auth/me",
    "/api/v1/users",
    "/api/v1/finance/summary",
    "/api/v1/hr/staff",
    "/api/v1/auditor/dashboard",
])
def test_protected_endpoints_reject_missing_credentials(path):
    assert client.get(path).status_code in (401, 403)


@pytest.mark.parametrize("authorization", [
    "Bearer not-a-jwt",
    "Bearer ",
    "Basic Zm9vOmJhcg==",
])
def test_protected_endpoint_rejects_invalid_authorization(authorization):
    response = client.get("/api/v1/auth/me", headers={"Authorization": authorization})
    assert response.status_code in (401, 403)


def test_invalid_password_does_not_authenticate():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@gaintacademy.com",
        "password": "DefinitelyWrong@123",
    })
    assert response.status_code == 401
    assert "access_token" not in response.text


@pytest.mark.parametrize("email", [
    "teacher@gaintacademy.com",
    "student@gaintacademy.com",
    "parent@gaintacademy.com",
    "accounts@gaintacademy.com",
    "hr@gaintacademy.com",
    "campus@gaintacademy.com",
    "auditor@gaintacademy.com",
])
def test_non_admin_roles_cannot_create_users(email):
    headers = login(email)
    response = client.post("/api/v1/users", headers=headers, json={
        "name": "Privilege Escalation Attempt",
        "email": f"blocked.{email}",
        "password": "Blocked@123",
        "role": "Institution Admin",
        "campus_id": 1,
    })
    assert response.status_code == 403


@pytest.mark.parametrize("admin_email,foreign_email", [
    ("admin@gaintacademy.com", "school.student@gaintacademy.com"),
    ("admin@gaintacademy.com", "college.student@gaintacademy.com"),
    ("school.admin@gaintacademy.com", "student@gaintacademy.com"),
    ("college.admin@gaintacademy.com", "student@gaintacademy.com"),
])
def test_admin_user_listing_is_tenant_scoped(admin_email, foreign_email):
    rows = client.get("/api/v1/users", headers=login(admin_email))
    assert rows.status_code == 200, rows.text
    emails = {row["email"] for row in rows.json()}
    assert foreign_email not in emails


def test_admin_cannot_mutate_foreign_tenant_user():
    university_admin = login("admin@gaintacademy.com")
    school_admin = login("school.admin@gaintacademy.com")
    school_rows = client.get("/api/v1/users", headers=school_admin)
    assert school_rows.status_code == 200
    foreign = next(row for row in school_rows.json() if row["role"] == "Student")

    response = client.patch(
        f"/api/v1/users/{foreign['id']}",
        headers=university_admin,
        json={"name": "Cross Tenant Mutation"},
    )
    assert response.status_code == 404
