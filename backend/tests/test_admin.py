import os
os.environ.setdefault("DATABASE_URL","sqlite:///./test.db")

import pytest\nfrom sqlalchemy import select, delete
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Institution, AcademicUnit
from app.security import hash_password

client=TestClient(app)
PASSWORD="Test@123"

@pytest.fixture(scope="module", autouse=True)
def admin_security_fixtures():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for row in [
            Institution(id=91,name="Admin Test School",institution_type="SCHOOL",code="ADMIN-T91"),
            Institution(id=92,name="Other College",institution_type="COLLEGE",code="ADMIN-T92"),
        ]:
            if db.get(Institution,row.id) is None: db.add(row)
        db.flush()
        existing={u.email for u in db.scalars(select(User).where(User.email.in_(["admin1@test.local","student1@test.local","teacher1@test.local","admin2@test.local","student2@test.local"]))).all()}
        users=[
            User(email="admin1@test.local",name="Admin One",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="student1@test.local",name="Pupil One",role="Student",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="teacher1@test.local",name="Teacher One",role="Teacher",password_hash=hash_password(PASSWORD),tenant_id=91,campus_id=91,is_active=True),
            User(email="admin2@test.local",name="Admin Two",role="Institution Admin",password_hash=hash_password(PASSWORD),tenant_id=92,campus_id=92,is_active=True),
            User(email="student2@test.local",name="Other Student",role="Student",password_hash=hash_password(PASSWORD),tenant_id=92,campus_id=92,is_active=True),
        ]
        db.add_all([u for u in users if u.email not in existing])
        for tenant,campus,name,code in [(91,91,"School Campus","SC-91"),(92,92,"Other Campus","OC-92")]:
            found=db.scalar(select(AcademicUnit).where(AcademicUnit.tenant_id==tenant,AcademicUnit.code==code))
            if found is None: db.add(AcademicUnit(tenant_id=tenant,campus_id=campus,unit_type="CAMPUS",name=name,code=code,status="Active"))
        db.commit()
    yield

