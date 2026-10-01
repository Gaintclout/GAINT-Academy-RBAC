import os
os.environ["DATABASE_URL"]="sqlite:///./test_finance.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
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
        db.add_all([
            Institution(id=1,name="Tenant One",institution_type="SCHOOL",code="T1"),
            Institution(id=2,name="Tenant Two",institution_type="COLLEGE",code="T2"),
        ]); db.flush()
        users=[
            User(email="accounts1@test.local",name="Accounts 1",role="Accounts",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="student1@test.local",name="Student 1",role="Student",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="parent1@test.local",name="Parent 1",role="Parent / Guardian",password_hash=hash_password(PASSWORD),tenant_id=1,campus_id=1,is_active=True),
            User(email="student2@test.local",name="Student 2",role="Student",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
            User(email="parent2@test.local",name="Parent 2",role="Parent / Guardian",password_hash=hash_password(PASSWORD),tenant_id=2,campus_id=1,is_active=True),
        ]; db.add_all(users); db.flush()
        db.add(ParentStudentLink(parent_user_id=users[2].id,student_user_id=users[1].id,relationship="Parent",tenant_id=1)); db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def auth(email):
    r=client.post("/api/v1/auth/login",json={"email":email,"password":PASSWORD}); assert r.status_code==200
    return {"Authorization":"Bearer "+r.json()["access_token"]}

def create_fee(headers,student_id,code="TUITION",amount=100.10):
    return client.post("/api/v1/fee-ledger",headers=headers,json={"student_user_id":student_id,"fee_code":code,"title":"Tuition Fee","amount_due":amount})

def ids():
    with SessionLocal() as db:
        return {u.email:u.id for u in db.scalars(select(User)).all()}

def test_tenant_isolation_and_parent_link_authorization():
    i=ids(); accounts=auth("accounts1@test.local")
    ok=create_fee(accounts,i["student1@test.local"]); assert ok.status_code==200
    cross=create_fee(accounts,i["student2@test.local"],"CROSS"); assert cross.status_code==400
    parent=auth("parent1@test.local")
    assert client.get(f"/api/v1/parents/children/{i['student1@test.local']}/fees",headers=parent).status_code==200
    assert client.get(f"/api/v1/parents/children/{i['student2@test.local']}/fees",headers=parent).status_code==403

def test_overpayment_duplicate_reference_and_decimal_balance():
    i=ids(); h=auth("accounts1@test.local"); fee=create_fee(h,i["student1@test.local"],amount=100.10).json()
    r=client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":0.10,"reference":"BANK-001"}); assert r.status_code==200
    assert r.json()["ledger"]["balance"]==100.0
    duplicate=client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":1,"reference":"BANK-001"}); assert duplicate.status_code==409
    over=client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":100.01,"reference":"BANK-002"}); assert over.status_code==400

def test_cancelled_fee_rejects_payment_and_paid_fee_rejects_cancel():
    i=ids(); h=auth("accounts1@test.local")
    fee=create_fee(h,i["student1@test.local"],"CANCEL",50).json()
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/cancel",headers=h).status_code==200
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":10,"reference":"C1"}).status_code==409
    paid=create_fee(h,i["student1@test.local"],"PAID",50).json()
    assert client.post(f"/api/v1/fee-ledger/{paid['id']}/payments",headers=h,json={"amount":10,"reference":"P1"}).status_code==200
    assert client.post(f"/api/v1/fee-ledger/{paid['id']}/cancel",headers=h).status_code==409

def test_receipts_visible_to_owner_and_linked_parent_only():
    i=ids(); h=auth("accounts1@test.local"); fee=create_fee(h,i["student1@test.local"],"RECEIPT",25).json()
    client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":25,"reference":"R1"})
    assert client.get(f"/api/v1/fee-ledger/{fee['id']}/receipts",headers=auth("student1@test.local")).status_code==200
    assert client.get(f"/api/v1/fee-ledger/{fee['id']}/receipts",headers=auth("parent1@test.local")).status_code==200
    assert client.get(f"/api/v1/fee-ledger/{fee['id']}/receipts",headers=auth("parent2@test.local")).status_code==404


def test_accounts_concession_refund_and_reconciliation_validation():
    i=ids(); h=auth("accounts1@test.local"); student=auth("student1@test.local")
    fee=create_fee(h,i["student1@test.local"],"ADVANCED",100).json()
    assert client.get("/api/v1/finance/concessions",headers=student).status_code==403
    assert client.post("/api/v1/finance/concessions",headers=student,json={"ledger_id":fee["id"],"amount":10,"reason":"Scholarship"}).status_code==403
    assert client.post("/api/v1/finance/concessions",headers=h,json={"ledger_id":fee["id"],"amount":101,"reason":"Too much"}).status_code==400
    concession=client.post("/api/v1/finance/concessions",headers=h,json={"ledger_id":fee["id"],"amount":10,"reason":"Scholarship"})
    assert concession.status_code==200
    payment=client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":50,"reference":"PAY-ADV"}); assert payment.status_code==200
    payment_id=client.get("/api/v1/finance/payments",headers=h).json()[0]["id"]
    assert client.get("/api/v1/finance/refunds",headers=student).status_code==403
    assert client.post("/api/v1/finance/refunds",headers=h,json={"payment_id":payment_id,"amount":51,"reason":"Too much","reference":"REF-X"}).status_code==400
    refund=client.post("/api/v1/finance/refunds",headers=h,json={"payment_id":payment_id,"amount":20,"reason":"Approved reversal","reference":"REF-1"}); assert refund.status_code==200
    assert client.post("/api/v1/finance/refunds",headers=h,json={"payment_id":payment_id,"amount":1,"reason":"Duplicate reference","reference":"REF-1"}).status_code==409
    assert client.get("/api/v1/finance/reconciliations",headers=student).status_code==403
    recon=client.post("/api/v1/finance/reconciliations",headers=h,json={"reconciliation_date":payment.json()["ledger"].get("due_at") or "2026-09-29","bank_amount":0,"reference":"BANK-DAY","notes":"Daily close"})
    assert recon.status_code==200
    assert recon.json()["status"] in {"MATCHED","VARIANCE"}
    assert client.post("/api/v1/finance/reconciliations",headers=h,json={"reconciliation_date":"2026-09-29","bank_amount":0,"reference":"BANK-DAY","notes":""}).status_code==409


def test_parent_receipts_require_active_linked_student():
    i=ids(); h=auth("accounts1@test.local")
    fee=create_fee(h,i["student1@test.local"],"PARENT-ACTIVE",25).json()
    client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":25,"reference":"PARENT-ACTIVE-R1"})
    parent=auth("parent1@test.local")
    assert client.get(f"/api/v1/fee-ledger/{fee['id']}/receipts",headers=parent).status_code==200
    with SessionLocal() as db:
        student=db.get(User,i["student1@test.local"])
        student.is_active=False
        db.commit()
    assert client.get(f"/api/v1/fee-ledger/{fee['id']}/receipts",headers=parent).status_code==403


def test_parent_children_hide_inactive_linked_student():
    i=ids(); parent=auth("parent1@test.local")
    assert any(x["id"]==i["student1@test.local"] for x in client.get("/api/v1/parents/children",headers=parent).json())
    with SessionLocal() as db:
        student=db.get(User,i["student1@test.local"])
        student.is_active=False
        db.commit()
    rows=client.get("/api/v1/parents/children",headers=parent)
    assert rows.status_code==200
    assert all(x["id"]!=i["student1@test.local"] for x in rows.json())
    assert client.get(f"/api/v1/parents/children/{i['student1@test.local']}/fees",headers=parent).status_code==404
    assert client.get(f"/api/v1/parents/children/{i['student1@test.local']}/location",headers=parent).status_code==404


def test_accounts_reject_zero_negative_and_paid_balance_transactions():
    i=ids(); h=auth("accounts1@test.local")
    fee=create_fee(h,i["student1@test.local"],"VALIDATE",50).json()
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":0,"reference":"ZERO-PAY"}).status_code in (400,422)
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":-1,"reference":"NEG-PAY"}).status_code in (400,422)
    assert client.post("/api/v1/finance/concessions",headers=h,json={"ledger_id":fee["id"],"amount":0,"reason":"Invalid"}).status_code in (400,422)
    paid=client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":50,"reference":"FULL-PAY"})
    assert paid.status_code==200
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":1,"reference":"EXTRA-PAY"}).status_code==409
    payment_id=client.get("/api/v1/finance/payments",headers=h).json()[0]["id"]
    assert client.post("/api/v1/finance/refunds",headers=h,json={"payment_id":payment_id,"amount":0,"reason":"Invalid","reference":"ZERO-REF"}).status_code in (400,422)


def test_accounts_report_rejects_reversed_date_range():
    h=auth("accounts1@test.local")
    response=client.get("/api/v1/finance/report?start_date=2026-10-10&end_date=2026-10-01",headers=h)
    assert response.status_code==400


def test_accounts_read_and_write_rbac_boundaries():
    accounts=auth("accounts1@test.local"); student=auth("student1@test.local")
    for path in ("/api/v1/finance/students","/api/v1/finance/summary","/api/v1/finance/payments","/api/v1/finance/concessions","/api/v1/finance/refunds","/api/v1/finance/reconciliations","/api/v1/finance/report"):
        assert client.get(path,headers=accounts).status_code==200
        assert client.get(path,headers=student).status_code==403
    i=ids()
    assert create_fee(student,i["student1@test.local"],"BLOCKED",10).status_code==403


def test_accounts_cross_tenant_finance_mutations_are_blocked():
    i=ids(); h=auth("accounts1@test.local")
    cross=create_fee(h,i["student2@test.local"],"CROSS-TENANT",100)
    assert cross.status_code==400
    with SessionLocal() as db:
        from app.models import FeeLedger,FeePayment
        other=FeeLedger(tenant_id=2,student_user_id=i["student2@test.local"],fee_code="OTHER",title="Other Tenant Fee",amount_due=100,amount_paid=0,status="DUE")
        db.add(other); db.commit(); db.refresh(other)
        other_id=other.id
    assert client.post("/api/v1/finance/concessions",headers=h,json={"ledger_id":other_id,"amount":10,"reason":"Blocked"}).status_code==404
    assert client.post(f"/api/v1/fee-ledger/{other_id}/payments",headers=h,json={"amount":10,"reference":"CROSS-PAY"}).status_code==404


def test_accounts_finance_reads_do_not_leak_other_tenant_data():
    i=ids(); h=auth("accounts1@test.local")
    own=create_fee(h,i["student1@test.local"],"OWN-LEDGER",80).json()
    client.post(f"/api/v1/fee-ledger/{own['id']}/payments",headers=h,json={"amount":20,"reference":"OWN-PAY"})
    with SessionLocal() as db:
        from app.models import FeeLedger,FeePayment
        other=FeeLedger(tenant_id=2,student_user_id=i["student2@test.local"],fee_code="SECRET",title="Other Tenant Fee",amount_due=999,amount_paid=999,status="PAID")
        db.add(other); db.flush()
        db.add(FeePayment(tenant_id=2,ledger_id=other.id,student_user_id=i["student2@test.local"],amount=999,reference="SECRET-PAY",receipt_no="SECRET-RECEIPT",recorded_by=i["student2@test.local"]))
        db.commit()
    ledger=client.get("/api/v1/fee-ledger",headers=h); assert ledger.status_code==200
    assert all(x["fee_code"]!="SECRET" for x in ledger.json())
    payments=client.get("/api/v1/finance/payments",headers=h); assert payments.status_code==200
    assert all(x["reference"]!="SECRET-PAY" for x in payments.json())
    report=client.get("/api/v1/finance/report",headers=h); assert report.status_code==200
    assert all(x["reference"]!="SECRET-PAY" for x in report.json()["payments"])
    summary=client.get("/api/v1/finance/summary",headers=h); assert summary.status_code==200
    assert summary.json()["collected"]==20.0


def test_accounts_cannot_mutate_cancelled_or_foreign_finance_records():
    i=ids(); h=auth("accounts1@test.local")
    fee=create_fee(h,i["student1@test.local"],"LOCKED",75).json()
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/cancel",headers=h).status_code==200
    assert client.post("/api/v1/finance/concessions",headers=h,json={"ledger_id":fee["id"],"amount":5,"reason":"Blocked"}).status_code==409
    assert client.post(f"/api/v1/fee-ledger/{fee['id']}/payments",headers=h,json={"amount":5,"reference":"LOCKED-PAY"}).status_code==409
    with SessionLocal() as db:
        from app.models import FeeLedger,FeePayment
        other=FeeLedger(tenant_id=2,student_user_id=i["student2@test.local"],fee_code="FOREIGN",title="Foreign Fee",amount_due=50,amount_paid=50,status="PAID")
        db.add(other); db.flush()
        payment=FeePayment(tenant_id=2,ledger_id=other.id,student_user_id=i["student2@test.local"],amount=50,reference="FOREIGN-PAY",receipt_no="FOREIGN-R",recorded_by=i["student2@test.local"])
        db.add(payment); db.commit(); db.refresh(payment)
        payment_id=payment.id
    assert client.post("/api/v1/finance/refunds",headers=h,json={"payment_id":payment_id,"amount":5,"reason":"Blocked","reference":"FOREIGN-REF"}).status_code==404
