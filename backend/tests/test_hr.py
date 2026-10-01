import os
os.environ["DATABASE_URL"]="sqlite:///./test_hr.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution
from app.security import hash_password

client=TestClient(app)
PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all([
            Institution(id=1,name="Tenant One",institution_type="SCHOOL",code="T1"),
            Institution(id=2,name="Tenant Two",institution_type="COLLEGE",code="T2"),
        ]); db.flush()
        db.add_all([
            User(email="hr1@test.local",name="HR One",role="HR",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="admin1@test.local",name="Admin One",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="auditor1@test.local",name="Auditor One",role="Auditor",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="teacher1@test.local",name="Teacher One",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="accounts1@test.local",name="Accounts One",role="Accounts",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="student1@test.local",name="Student One",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="hr2@test.local",name="HR Two",role="HR",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
            User(email="teacher2@test.local",name="Teacher Two",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
        ]); db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD}); assert r.status_code==200
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def ids():
    with SessionLocal() as db:
        return {u.email:u.id for u in db.scalars(select(User)).all()}

def test_hr_read_rbac_and_tenant_isolation():
    h=auth("hr1@test.local"); auditor=auth("auditor1@test.local"); student=auth("student1@test.local")
    for path in ("/api/v1/hr/staff","/api/v1/hr/attendance","/api/v1/hr/leave","/api/v1/hr/documents","/api/v1/hr/recruitment","/api/v1/hr/performance","/api/v1/hr/reports"):
        assert client.get(path,headers=h).status_code==200
        assert client.get(path,headers=auditor).status_code==200
        assert client.get(path,headers=student).status_code==403
    staff=client.get("/api/v1/hr/staff",headers=h).json()
    assert any(x["email"]=="teacher1@test.local" for x in staff)
    assert all(x["email"]!="teacher2@test.local" for x in staff)

def test_hr_attendance_validation_update_and_cross_tenant_block():
    i=ids(); h=auth("hr1@test.local")
    payload={"staff_user_id":i["teacher1@test.local"],"attendance_date":"2026-10-01","status":"PRESENT","note":"On time"}
    r=client.post("/api/v1/hr/attendance",headers=h,json=payload); assert r.status_code==200
    payload["status"]="HALF_DAY"; payload["note"]="Approved half day"
    updated=client.post("/api/v1/hr/attendance",headers=h,json=payload); assert updated.status_code==200
    rows=client.get("/api/v1/hr/attendance",headers=h).json()
    assert len(rows)==1 and rows[0]["status"]=="HALF_DAY"
    assert client.post("/api/v1/hr/attendance",headers=h,json={**payload,"status":"INVALID"}).status_code==400
    assert client.post("/api/v1/hr/attendance",headers=h,json={**payload,"staff_user_id":i["teacher2@test.local"]}).status_code==400
    assert client.post("/api/v1/hr/attendance",headers=auth("auditor1@test.local"),json=payload).status_code==403

def test_teacher_leave_review_rules_and_tenant_isolation():
    teacher=auth("teacher1@test.local"); h=auth("hr1@test.local")
    created=client.post("/api/v1/teacher/leave",headers=teacher,json={"leave_type":"Casual","start_date":"2026-10-10","end_date":"2026-10-11","reason":"Personal"}); assert created.status_code==200
    leave_id=created.json()["id"]
    assert client.patch(f"/api/v1/hr/leave/{leave_id}",headers=h,json={"status":"REJECTED","reviewer_note":""}).status_code==400
    ok=client.patch(f"/api/v1/hr/leave/{leave_id}",headers=h,json={"status":"APPROVED","reviewer_note":"Approved"}); assert ok.status_code==200
    assert client.patch(f"/api/v1/hr/leave/{leave_id}",headers=h,json={"status":"REJECTED","reviewer_note":"Changed"}).status_code==409
    other=client.post("/api/v1/teacher/leave",headers=auth("teacher2@test.local"),json={"leave_type":"Sick","start_date":"2026-10-20","end_date":"2026-10-21","reason":"Illness"}).json()
    assert client.patch(f"/api/v1/hr/leave/{other['id']}",headers=h,json={"status":"APPROVED","reviewer_note":""}).status_code==404

def test_hr_documents_validate_staff_tenant_and_status():
    i=ids(); h=auth("hr1@test.local")
    good={"staff_user_id":i["teacher1@test.local"],"document_type":"Qualification","title":"Degree","document_ref":"DOC-1","expiry_date":"","status":"ACTIVE","notes":""}
    assert client.post("/api/v1/hr/documents",headers=h,json=good).status_code==200
    assert client.post("/api/v1/hr/documents",headers=h,json={**good,"staff_user_id":i["teacher2@test.local"],"document_ref":"DOC-X"}).status_code==400
    assert client.post("/api/v1/hr/documents",headers=h,json={**good,"status":"INVALID"}).status_code==400
    assert client.post("/api/v1/hr/documents",headers=auth("auditor1@test.local"),json=good).status_code==403

def test_hr_recruitment_duplicate_stage_and_write_rbac():
    h=auth("hr1@test.local")
    candidate={"name":"Candidate One","email":"candidate@test.local","phone":"","position":"Teacher","stage":"APPLIED","source":"Careers","notes":""}
    created=client.post("/api/v1/hr/recruitment",headers=h,json=candidate); assert created.status_code==200
    assert client.post("/api/v1/hr/recruitment",headers=h,json=candidate).status_code==409
    cid=created.json()["id"]
    assert client.patch(f"/api/v1/hr/recruitment/{cid}",headers=h,json={"stage":"INTERVIEW","notes":"Round one"}).status_code==200
    assert client.patch(f"/api/v1/hr/recruitment/{cid}",headers=h,json={"stage":"INVALID"}).status_code==400
    assert client.post("/api/v1/hr/recruitment",headers=auth("auditor1@test.local"),json={**candidate,"email":"blocked@test.local"}).status_code==403

def test_hr_performance_validation_cross_tenant_and_reports():
    i=ids(); h=auth("hr1@test.local")
    good={"staff_user_id":i["teacher1@test.local"],"review_period":"2026 Annual","rating":4,"strengths":"Teaching","improvement_areas":"Documentation","goals":"Mentoring","status":"COMPLETED"}
    assert client.post("/api/v1/hr/performance",headers=h,json=good).status_code==200
    assert client.post("/api/v1/hr/performance",headers=h,json={**good,"staff_user_id":i["teacher2@test.local"]}).status_code==400
    assert client.post("/api/v1/hr/performance",headers=h,json={**good,"status":"INVALID"}).status_code==400
    assert client.post("/api/v1/hr/performance",headers=auth("auditor1@test.local"),json=good).status_code==403
    report=client.get("/api/v1/hr/reports",headers=h); assert report.status_code==200
    assert report.json()["performance"]["reviews"]==1
    assert report.json()["performance"]["average_rating"]==4.0
