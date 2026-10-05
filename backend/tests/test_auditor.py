import os
os.environ["DATABASE_URL"]="sqlite:///./test_auditor.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution, Audit
from app.security import hash_password

client=TestClient(app); PASSWORD="Test@123"

@pytest.fixture(autouse=True)
def auditor_fixture():
    with SessionLocal() as db:
        if not db.get(Institution,90): db.add(Institution(id=90,name="Audit Tenant One",institution_type="SCHOOL",code="AUD90"))
        if not db.get(Institution,91): db.add(Institution(id=91,name="Audit Tenant Two",institution_type="COLLEGE",code="AUD91"))
        db.commit()
        rows=[("auditor90@test.local","Auditor One","Auditor",90),("auditor91@test.local","Auditor Two","Auditor",91),("student90@test.local","Student One","Student",90),("student91@test.local","Student Two Secret","Student",91),("hr90@test.local","HR One","HR",90)]
        for email,name,role,tenant in rows:
            if not db.query(User).filter(User.email==email).first(): db.add(User(email=email,name=name,role=role,password_hash=hash_password(PASSWORD),tenant_id=tenant,campus_id=None,is_active=True))
        db.flush()
        if not db.query(Audit).filter(Audit.tenant_id==90,Audit.details=="VISIBLE-T1").first(): db.add(Audit(tenant_id=90,actor="tenant-one",action="CREATE",resource="visible",details="VISIBLE-T1"))
        if not db.query(Audit).filter(Audit.tenant_id==91,Audit.details=="SECRET-T2").first(): db.add(Audit(tenant_id=91,actor="tenant-two",action="CREATE",resource="secret",details="SECRET-T2"))
        db.commit()
    yield

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD});assert r.status_code==200
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def test_auditor_endpoints_are_auditor_only():
    auditor=auth("auditor90@test.local"); student=auth("student90@test.local"); hr=auth("hr90@test.local")
    for path in ("/api/v1/auditor/dashboard","/api/v1/auditor/compliance","/api/v1/auditor/exceptions","/api/v1/auditor/evidence","/api/v1/auditor/export-reports"):
        assert client.get(path,headers=auditor).status_code==200
        assert client.get(path,headers=student).status_code==403
        assert client.get(path,headers=hr).status_code==403

def test_dashboard_and_audit_trail_are_tenant_scoped():
    h=auth("auditor90@test.local")
    dashboard=client.get("/api/v1/auditor/dashboard",headers=h);assert dashboard.status_code==200
    raw=str(dashboard.json())
    assert "VISIBLE-T1" in raw and "SECRET-T2" not in raw and "Student Two Secret" not in raw
    trail=client.get("/api/v1/audit",headers=h);assert trail.status_code==200
    raw=str(trail.json());assert "VISIBLE-T1" in raw and "SECRET-T2" not in raw

def test_all_auditor_workspaces_do_not_leak_other_tenant():
    h=auth("auditor90@test.local")
    for path in ("/api/v1/auditor/compliance","/api/v1/auditor/exceptions","/api/v1/auditor/evidence","/api/v1/auditor/export-reports"):
        r=client.get(path,headers=h);assert r.status_code==200
        raw=str(r.json())
        assert "SECRET-T2" not in raw and "Student Two Secret" not in raw and "tenant-two" not in raw

def test_auditor_cannot_use_known_mutation_endpoints():
    h=auth("auditor90@test.local")
    assert client.post("/api/v1/campus/visitors",headers=h,json={"name":"X","phone":"","purpose":"X","person_to_meet":""}).status_code==403
    assert client.post("/api/v1/campus/inventory",headers=h,json={"name":"X","category":"General","item_code":"X","quantity":1,"minimum_quantity":0,"location":"","status":"ACTIVE","notes":""}).status_code==403
    assert client.post("/api/v1/campus/assets",headers=h,json={"asset_code":"X","name":"X","category":"General","serial_number":"","location":"","assigned_to":"","condition":"GOOD","status":"ACTIVE","notes":""}).status_code==403
    assert client.post("/api/v1/campus/events",headers=h,json={"title":"X","event_type":"General","venue":"","starts_at":"2026-10-20T10:00:00","ends_at":"2026-10-20T11:00:00","audience_role":"ALL","registration_required":False,"registration_deadline":None}).status_code==403

def test_auditor_has_no_module_action_mutation_escape_hatch():
    h=auth("auditor90@test.local")
    for action in ("approve","pay","message","create_grievance","request_leave","manage_users"):
        r=client.post(f"/api/v1/module-actions/{action}",headers=h,json={"page":"Auditor Dashboard"})
        assert r.status_code==403
