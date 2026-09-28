from typing import Optional
import datetime as dt
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, SessionLocal, get_db
from .models import User, Institution, AcademicUnit, AcademicAssignment, EnrollmentHistory, AcademicWork, StudentAcademicWork, ClassSession, AttendanceEntry, GradeRule, ExamResult, FeeLedger, FeePayment, Record, ParentStudentLink, StudentLocation, SosEvent, Audit
from .schemas import LoginRequest, RecordIn, LocationUpdate, SosIn, AIChatRequest, InstitutionIn, AcademicUnitIn, AcademicAssignmentIn, AcademicActivityIn, AcademicWorkIn, SubmissionIn, GradeIn, ClassSessionIn, AttendanceMarkIn, GradeRuleIn, ExamResultIn, FeeLedgerIn, FeePaymentIn, UserAdminUpdate, UserAdminCreate, ParentStudentLinkIn, StudentEnrollmentIn, StudentEnrollmentUpdate, StudentAdminUpdate
from .security import verify_password, hash_password, create_token, current_user, require_roles
from .rbac import ROLE_MENUS, dashboard_for, module_access_for, can
from .seed import seed, DEMO_PASSWORD, DEMO_USERS

settings.validate_runtime()
if settings.AUTO_CREATE_SCHEMA:
    Base.metadata.create_all(bind=engine)
if settings.SEED_DEMO_DATA:
    with SessionLocal() as db:
        seed(db)

app = FastAPI(
    title="GAINT Academy API",
    version="2.0.0",
    description="GAINT Academy role-based education, campus and safety platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def audit(db: Session, user: User, action: str, resource: str, details: str = ""):
    db.add(Audit(
        tenant_id=user.tenant_id,
        actor=user.email,
        action=action,
        resource=resource,
        details=details,
    ))

@app.get("/")
def root():
    return {
        "service":"GAINT Academy API",
        "version":"2.0.0",
        "status":"running",
        "docs":"/docs",
        "health":"/health",
    }

@app.get("/health")
def health():
    return {"status":"ok","service":"GAINT Academy API"}

@app.get("/api/v1/demo-accounts")
def demo_accounts():
    if not settings.SEED_DEMO_DATA:
        raise HTTPException(404, "Demo accounts are disabled")
    return {
        "password": DEMO_PASSWORD,
        "accounts":[{"email":e,"name":n,"role":r} for e,n,r in DEMO_USERS],
    }

def institution_payload(db: Session, tenant_id: int):
    row = db.get(Institution, tenant_id)
    if not row:
        return {"id": tenant_id, "name": "GAINT Academy", "institution_type": "UNIVERSITY", "code": ""}
    return {"id": row.id, "name": row.name, "institution_type": row.institution_type, "code": row.code}

@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email==email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {
        "access_token":create_token(user),
        "token_type":"bearer",
        "user":{
            "id":user.id,"name":user.name,"email":user.email,"role":user.role,
            "tenant_id":user.tenant_id,"campus_id":user.campus_id,
            "institution": institution_payload(db, user.tenant_id),
        }
    }

@app.get("/api/v1/auth/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "id":user.id,"name":user.name,"email":user.email,"role":user.role,
        "tenant_id":user.tenant_id,"campus_id":user.campus_id,
        "institution": institution_payload(db, user.tenant_id),
    }

@app.get("/api/v1/institution")
def institution_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return institution_payload(db, user.tenant_id)

@app.put("/api/v1/institution")
def update_institution(payload: InstitutionIn, user: User = Depends(require_roles("Institution Admin")), db: Session = Depends(get_db)):
    institution_type = payload.institution_type.strip().upper()
    if institution_type not in {"SCHOOL","COLLEGE","UNIVERSITY","TRAINING_INSTITUTE"}:
        raise HTTPException(400, "Unsupported institution type")
    row = db.get(Institution, user.tenant_id)
    if not row:
        row = Institution(id=user.tenant_id, name=payload.name.strip(), institution_type=institution_type, code=payload.code.strip().upper())
        db.add(row)
    else:
        row.name = payload.name.strip()
        row.institution_type = institution_type
        row.code = payload.code.strip().upper()
    audit(db, user, "UPDATE", "institution", institution_type)
    db.commit(); db.refresh(row)
    return institution_payload(db, user.tenant_id)

@app.get("/api/v1/academic-structure")
def academic_structure(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AcademicUnit).where(AcademicUnit.tenant_id == user.tenant_id).order_by(AcademicUnit.unit_type, AcademicUnit.name)).all()
    return [{"id":r.id,"unit_type":r.unit_type,"name":r.name,"code":r.code,"parent_id":r.parent_id,"campus_id":r.campus_id,"status":r.status} for r in rows]

@app.post("/api/v1/academic-structure")
def create_academic_unit(payload: AcademicUnitIn, user: User = Depends(require_roles("Institution Admin")), db: Session = Depends(get_db)):
    allowed={"CAMPUS","SCHOOL_FACULTY","DEPARTMENT","PROGRAM","ACADEMIC_PERIOD","COURSE","SECTION_BATCH"}
    unit_type=payload.unit_type.strip().upper()
    if unit_type not in allowed:
        raise HTTPException(400,"Unsupported academic unit type")
    hierarchy={
        "CAMPUS":set(),
        "SCHOOL_FACULTY":{"CAMPUS"},
        "DEPARTMENT":{"SCHOOL_FACULTY"},
        "PROGRAM":{"DEPARTMENT"},
        "ACADEMIC_PERIOD":{"PROGRAM"},
        "COURSE":{"ACADEMIC_PERIOD"},
        "SECTION_BATCH":{"COURSE"},
    }
    parent=None
    if payload.parent_id is not None:
        parent=db.get(AcademicUnit,payload.parent_id)
        if not parent or parent.tenant_id != user.tenant_id:
            raise HTTPException(400,"Invalid parent academic unit")
    expected=hierarchy[unit_type]
    if not expected and parent is not None:
        raise HTTPException(400,f"{unit_type} must be a top-level academic unit")
    if expected and parent is None:
        raise HTTPException(400,f"{unit_type} requires a parent academic unit")
    if parent is not None and parent.unit_type not in expected:
        allowed=", ".join(sorted(expected))
        raise HTTPException(400,f"{unit_type} must be created under: {allowed}")
    code=payload.code.strip().upper()
    duplicate=db.scalar(select(AcademicUnit).where(
        AcademicUnit.tenant_id==user.tenant_id,
        AcademicUnit.code==code,
    ))
    if duplicate: raise HTTPException(409,"Academic unit code already exists in this institution")
    row=AcademicUnit(tenant_id=user.tenant_id,campus_id=payload.campus_id,unit_type=unit_type,name=payload.name.strip(),code=code,parent_id=payload.parent_id,status=payload.status)
    db.add(row); audit(db,user,"CREATE","academic_structure",f"{unit_type}:{row.name}"); db.commit(); db.refresh(row)
    return {"id":row.id,"unit_type":row.unit_type,"name":row.name,"code":row.code,"parent_id":row.parent_id,"campus_id":row.campus_id,"status":row.status}

@app.delete("/api/v1/academic-structure/{unit_id}")
def delete_academic_unit(unit_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    row=db.get(AcademicUnit,unit_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Academic unit not found")
    child=db.scalar(select(AcademicUnit).where(AcademicUnit.tenant_id==user.tenant_id,AcademicUnit.parent_id==unit_id))
    if child: raise HTTPException(409,"Remove child units before deleting this item")
    audit(db,user,"DELETE","academic_structure",f"{row.unit_type}:{row.name}"); db.delete(row); db.commit()
    return {"ok":True}

@app.patch("/api/v1/admin/students/{student_id}")
def admin_update_student(student_id:int,payload:StudentAdminUpdate,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    student=db.get(User,student_id)
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student": raise HTTPException(404,"Student not found")
    data=payload.model_dump(exclude_unset=True)
    if "email" in data:
        email=data["email"].strip().lower()
        duplicate=db.scalar(select(User).where(User.email==email,User.id!=student.id))
        if duplicate: raise HTTPException(409,"Email address is already registered")
        student.email=email
    if "name" in data: student.name=data["name"].strip()
    if "campus_id" in data: student.campus_id=data["campus_id"]
    if "is_active" in data and student.is_active!=data["is_active"]:
        previous="ACTIVE" if student.is_active else "WITHDRAWN"
        student.is_active=data["is_active"]
        status="ACTIVE" if student.is_active else "WITHDRAWN"
        db.add(EnrollmentHistory(tenant_id=user.tenant_id,student_user_id=student.id,event_type="REACTIVATED" if student.is_active else "WITHDRAWN",details=f"from={previous};to={status};source=students",actor_user_id=user.id))
    audit(db,user,"UPDATE","student",f"student={student.id};fields={','.join(data.keys())}")
    db.commit()
    return {"id":student.id,"name":student.name,"email":student.email,"campus_id":student.campus_id,"status":"Active" if student.is_active else "Withdrawn"}

@app.get("/api/v1/admissions/summary")
def admission_summary(user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    students=db.scalars(select(User).where(User.tenant_id==user.tenant_id,User.role=="Student")).all()
    active=sum(1 for x in students if x.is_active); withdrawn=len(students)-active
    without_section=0; without_guardian=0
    for student in students:
        section=db.scalar(select(AcademicAssignment.id).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==student.id,AcademicAssignment.assignment_type=="SECTION_ASSIGNMENT",AcademicAssignment.status=="Active"))
        if not section: without_section+=1
        guardian=db.scalar(select(ParentStudentLink.id).where(ParentStudentLink.tenant_id==user.tenant_id,ParentStudentLink.student_user_id==student.id))
        if not guardian: without_guardian+=1
    return {"total":len(students),"active":active,"withdrawn":withdrawn,"without_section":without_section,"without_guardian":without_guardian}

@app.get("/api/v1/admissions/students")
def admission_students(user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    students=db.scalars(select(User).where(User.tenant_id==user.tenant_id,User.role=="Student").order_by(User.name)).all()
    result=[]
    for student in students:
        assignments=db.scalars(select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==student.id,AcademicAssignment.status=="Active")).all()
        details=[]
        for a in assignments:
            unit=db.get(AcademicUnit,a.unit_id)
            if unit: details.append({"id":a.id,"assignment_type":a.assignment_type,"unit_id":unit.id,"unit_name":unit.name,"unit_type":unit.unit_type})
        guardian_link=db.scalar(select(ParentStudentLink.id).where(ParentStudentLink.tenant_id==user.tenant_id,ParentStudentLink.student_user_id==student.id))
        result.append({"id":student.id,"name":student.name,"email":student.email,"campus_id":student.campus_id,"status":"Active" if student.is_active else "Withdrawn","assignments":details,"has_guardian":bool(guardian_link)})
    return result

@app.get("/api/v1/admissions/students/{student_id}/profile")
def admission_student_profile(student_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    student=db.get(User,student_id)
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student": raise HTTPException(404,"Student not found")
    assignments=db.scalars(select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==student.id,AcademicAssignment.status=="Active")).all()
    academics=[]
    for row in assignments:
        unit=db.get(AcademicUnit,row.unit_id)
        if unit: academics.append({"assignment_type":row.assignment_type,"unit_id":unit.id,"unit_name":unit.name,"unit_type":unit.unit_type})
    links=db.scalars(select(ParentStudentLink).where(ParentStudentLink.tenant_id==user.tenant_id,ParentStudentLink.student_user_id==student.id)).all()
    guardians=[]
    for link in links:
        parent=db.get(User,link.parent_user_id)
        if parent and parent.tenant_id==user.tenant_id:
            guardians.append({"id":parent.id,"name":parent.name,"email":parent.email,"relationship":link.relationship,"is_active":parent.is_active})
    history_count=db.scalar(select(func.count(EnrollmentHistory.id)).where(EnrollmentHistory.tenant_id==user.tenant_id,EnrollmentHistory.student_user_id==student.id)) or 0
    return {"id":student.id,"name":student.name,"email":student.email,"campus_id":student.campus_id,"status":"Active" if student.is_active else "Withdrawn","academics":academics,"guardians":guardians,"history_count":history_count}

@app.get("/api/v1/admissions/students/{student_id}/history")
def admission_history(student_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    student=db.get(User,student_id)
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student": raise HTTPException(404,"Student not found")
    rows=db.scalars(select(EnrollmentHistory).where(EnrollmentHistory.tenant_id==user.tenant_id,EnrollmentHistory.student_user_id==student.id).order_by(EnrollmentHistory.created_at.desc())).all()
    result=[]
    for row in rows:
        before=db.get(AcademicUnit,row.from_unit_id) if row.from_unit_id else None; after=db.get(AcademicUnit,row.to_unit_id) if row.to_unit_id else None; actor=db.get(User,row.actor_user_id)
        result.append({"id":row.id,"event_type":row.event_type,"from_unit":before.name if before else None,"to_unit":after.name if after else None,"details":row.details,"actor":actor.name if actor else "Unknown","created_at":row.created_at})
    return result

@app.patch("/api/v1/admissions/students/{student_id}")
def update_admission(student_id:int,payload:StudentEnrollmentUpdate,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    student=db.get(User,student_id)
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student": raise HTTPException(404,"Student not found")
    data=payload.model_dump(exclude_unset=True)
    if "section_unit_id" in data and data["section_unit_id"] is not None:
        section=db.get(AcademicUnit,data["section_unit_id"])
        if not section or section.tenant_id!=user.tenant_id or section.unit_type!="SECTION_BATCH": raise HTTPException(400,"Invalid section or batch")
        old=db.scalars(select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==student.id,AcademicAssignment.assignment_type=="SECTION_ASSIGNMENT")).all()
        previous_unit_id=old[0].unit_id if old else None
        for row in old: db.delete(row)
        db.add(AcademicAssignment(tenant_id=user.tenant_id,user_id=student.id,unit_id=section.id,assignment_type="SECTION_ASSIGNMENT",status="Active"))
        db.add(EnrollmentHistory(tenant_id=user.tenant_id,student_user_id=student.id,event_type="SECTION_TRANSFER",from_unit_id=previous_unit_id,to_unit_id=section.id,details="",actor_user_id=user.id))
        audit(db,user,"UPDATE","student_enrollment",f"student={student.id};section={section.id}")
    if "status" in data:
        status=(data["status"] or "").strip().upper()
        if status not in {"ACTIVE","WITHDRAWN"}: raise HTTPException(400,"Status must be Active or Withdrawn")
        previous="ACTIVE" if student.is_active else "WITHDRAWN"
        student.is_active=status=="ACTIVE"
        if previous!=status:
            db.add(EnrollmentHistory(tenant_id=user.tenant_id,student_user_id=student.id,event_type="REACTIVATED" if status=="ACTIVE" else "WITHDRAWN",details=f"from={previous};to={status}",actor_user_id=user.id))
        audit(db,user,"UPDATE","student_enrollment",f"student={student.id};status={status}")
    db.commit()
    return {"ok":True,"student_id":student.id,"status":"Active" if student.is_active else "Withdrawn"}

@app.post("/api/v1/admissions/enroll-student")
def enroll_student(payload:StudentEnrollmentIn,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    email=payload.email.strip().lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email address is already registered")
    password=payload.password
    if not (any(x.isalpha() for x in password) and any(x.isdigit() for x in password) and any(not x.isalnum() for x in password)):
        raise HTTPException(400,"Password must contain a letter, number and special character")
    program=db.get(AcademicUnit,payload.program_unit_id)
    if not program or program.tenant_id!=user.tenant_id or program.unit_type not in {"PROGRAM","ACADEMIC_PERIOD"}: raise HTTPException(400,"Invalid program or academic period")
    section=None
    if payload.section_unit_id is not None:
        section=db.get(AcademicUnit,payload.section_unit_id)
        if not section or section.tenant_id!=user.tenant_id or section.unit_type!="SECTION_BATCH": raise HTTPException(400,"Invalid section or batch")
    courses=[]
    for unit_id in dict.fromkeys(payload.course_unit_ids):
        unit=db.get(AcademicUnit,unit_id)
        if not unit or unit.tenant_id!=user.tenant_id or unit.unit_type!="COURSE": raise HTTPException(400,"Invalid course")
        courses.append(unit)
    parent=None
    if payload.parent_user_id is not None:
        parent=db.get(User,payload.parent_user_id)
        if not parent or parent.tenant_id!=user.tenant_id or parent.role!="Parent / Guardian" or not parent.is_active: raise HTTPException(400,"Invalid parent or guardian")
    student=User(email=email,name=payload.name.strip(),role="Student",password_hash=hash_password(password),tenant_id=user.tenant_id,campus_id=payload.campus_id,is_active=True)
    db.add(student); db.flush()
    assignments=[AcademicAssignment(tenant_id=user.tenant_id,user_id=student.id,unit_id=program.id,assignment_type="ENROLLMENT",status="Active")]
    if section: assignments.append(AcademicAssignment(tenant_id=user.tenant_id,user_id=student.id,unit_id=section.id,assignment_type="SECTION_ASSIGNMENT",status="Active"))
    assignments.extend(AcademicAssignment(tenant_id=user.tenant_id,user_id=student.id,unit_id=x.id,assignment_type="COURSE_REGISTRATION",status="Active") for x in courses)
    db.add_all(assignments)
    if parent: db.add(ParentStudentLink(parent_user_id=parent.id,student_user_id=student.id,relationship=payload.relationship.strip(),tenant_id=user.tenant_id))
    db.add(EnrollmentHistory(tenant_id=user.tenant_id,student_user_id=student.id,event_type="ENROLLED",to_unit_id=program.id,details=f"section={section.id if section else ''};courses={len(courses)};parent={parent.id if parent else ''}",actor_user_id=user.id))
    audit(db,user,"CREATE","student_enrollment",f"student={student.id};program={program.id};section={section.id if section else ''};courses={len(courses)};parent={parent.id if parent else ''}")
    db.commit(); db.refresh(student)
    return {"id":student.id,"name":student.name,"email":student.email,"program":program.name,"section":section.name if section else None,"courses":[x.name for x in courses],"parent_linked":bool(parent)}

@app.get("/api/v1/academic-assignments")
def academic_assignments(user:User=Depends(current_user),db:Session=Depends(get_db)):
    st=select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id)
    if user.role in {"Student","Teacher"}: st=st.where(AcademicAssignment.user_id==user.id)
    elif user.role not in {"Institution Admin","Campus Admin","Auditor"}: raise HTTPException(403,"Academic assignments are not available for your role")
    rows=db.scalars(st.order_by(AcademicAssignment.id.desc())).all()
    result=[]
    for r in rows:
        assigned=db.get(User,r.user_id); unit=db.get(AcademicUnit,r.unit_id)
        if assigned and unit:
            result.append({"id":r.id,"user_id":r.user_id,"user_name":assigned.name,"user_role":assigned.role,"unit_id":r.unit_id,"unit_name":unit.name,"unit_type":unit.unit_type,"assignment_type":r.assignment_type,"status":r.status})
    return result

@app.post("/api/v1/academic-assignments")
def create_academic_assignment(payload:AcademicAssignmentIn,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    assigned=db.get(User,payload.user_id); unit=db.get(AcademicUnit,payload.unit_id)
    if not assigned or assigned.tenant_id!=user.tenant_id: raise HTTPException(400,"Invalid user")
    if assigned.role not in {"Student","Teacher"}: raise HTTPException(400,"Only Student or Teacher users can receive academic assignments")
    if not unit or unit.tenant_id!=user.tenant_id: raise HTTPException(400,"Invalid academic unit")
    assignment_type=payload.assignment_type.strip().upper()
    allowed={"ENROLLMENT","COURSE_REGISTRATION","SECTION_ASSIGNMENT","FACULTY_ASSIGNMENT","ADVISOR_ASSIGNMENT"}
    if assignment_type not in allowed: raise HTTPException(400,"Unsupported assignment type")

    student_rules={
        "ENROLLMENT":{"PROGRAM","ACADEMIC_PERIOD"},
        "COURSE_REGISTRATION":{"COURSE"},
        "SECTION_ASSIGNMENT":{"SECTION_BATCH"},
    }
    teacher_rules={
        "FACULTY_ASSIGNMENT":{"COURSE","SECTION_BATCH"},
        "ADVISOR_ASSIGNMENT":{"PROGRAM","SECTION_BATCH"},
    }
    role_rules=student_rules if assigned.role=="Student" else teacher_rules
    if assignment_type not in role_rules:
        raise HTTPException(400,f"{assignment_type} is not valid for role {assigned.role}")
    if unit.unit_type not in role_rules[assignment_type]:
        expected=", ".join(sorted(role_rules[assignment_type]))
        raise HTTPException(400,f"{assignment_type} requires academic unit type: {expected}")

    existing=db.scalar(select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==assigned.id,AcademicAssignment.unit_id==unit.id,AcademicAssignment.assignment_type==assignment_type))
    if existing: raise HTTPException(409,"This academic assignment already exists")
    row=AcademicAssignment(tenant_id=user.tenant_id,user_id=assigned.id,unit_id=unit.id,assignment_type=assignment_type,status=payload.status)
    db.add(row); audit(db,user,"CREATE","academic_assignment",f"{assigned.email}:{assignment_type}:{unit.code}"); db.commit(); db.refresh(row)
    return {"id":row.id,"user_name":assigned.name,"unit_name":unit.name,"assignment_type":row.assignment_type,"status":row.status}

@app.delete("/api/v1/academic-assignments/{assignment_id}")
def delete_academic_assignment(assignment_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    row=db.get(AcademicAssignment,assignment_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Academic assignment not found")
    audit(db,user,"DELETE","academic_assignment",str(row.id)); db.delete(row); db.commit()
    return {"ok":True}

@app.get("/api/v1/navigation")
def navigation(user: User = Depends(current_user)):
    return {"role":user.role,"items":ROLE_MENUS.get(user.role,["Dashboard"])}

@app.get("/api/v1/module-access/{page:path}")
def module_access(page: str, user: User = Depends(current_user)):
    result = module_access_for(user.role, page)
    if not result["can_view"]:
        raise HTTPException(403, "This module is not available for your role")
    return result

@app.get("/api/v1/dashboard")
def dashboard(user: User = Depends(current_user)):
    return dashboard_for(user.role)

@app.get("/api/v1/users")
def users(
    user: User = Depends(require_roles("Institution Admin","Campus Admin","Auditor")),
    db: Session = Depends(get_db),
):
    rows = db.scalars(select(User).where(User.tenant_id==user.tenant_id).order_by(User.id)).all()
    return [
        {"id":x.id,"name":x.name,"email":x.email,"role":x.role,"campus_id":x.campus_id,"is_active":x.is_active}
        for x in rows
    ]

@app.post("/api/v1/users")
def create_user(
    payload:UserAdminCreate,
    user:User=Depends(require_roles("Institution Admin")),
    db:Session=Depends(get_db),
):
    allowed_roles={"Institution Admin","Teacher","Student","Parent / Guardian","Accounts","HR","Campus Admin","Auditor"}
    role=payload.role.strip()
    if role not in allowed_roles: raise HTTPException(400,"Unsupported role")
    email=payload.email.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(400,"Invalid email address")
    if db.scalar(select(User).where(User.email==email)):
        raise HTTPException(409,"Email address is already registered")
    password=payload.password
    if not (any(x.isalpha() for x in password) and any(x.isdigit() for x in password) and any(not x.isalnum() for x in password)):
        raise HTTPException(400,"Password must contain a letter, number and special character")
    target=User(email=email,name=payload.name.strip(),role=role,password_hash=hash_password(password),tenant_id=user.tenant_id,campus_id=payload.campus_id,is_active=True)
    db.add(target); db.flush()
    audit(db,user,"CREATE","user",f"user_id={target.id};role={role};campus={target.campus_id}")
    db.commit(); db.refresh(target)
    return {"id":target.id,"name":target.name,"email":target.email,"role":target.role,"campus_id":target.campus_id,"is_active":target.is_active}

@app.patch("/api/v1/users/{target_user_id}")
def update_user(
    target_user_id:int,
    payload:UserAdminUpdate,
    user:User=Depends(require_roles("Institution Admin")),
    db:Session=Depends(get_db),
):
    target=db.get(User,target_user_id)
    if not target or target.tenant_id!=user.tenant_id:
        raise HTTPException(404,"User not found")
    allowed_roles={"Institution Admin","Teacher","Student","Parent / Guardian","Accounts","HR","Campus Admin","Auditor"}
    data=payload.model_dump(exclude_unset=True)
    if "role" in data:
        role=(data["role"] or "").strip()
        if role not in allowed_roles: raise HTTPException(400,"Unsupported role")
        if target.id==user.id and role!="Institution Admin":
            raise HTTPException(409,"You cannot remove your own Institution Admin role")
        target.role=role
    if "is_active" in data:
        if target.id==user.id and data["is_active"] is False:
            raise HTTPException(409,"You cannot deactivate your own account")
        target.is_active=data["is_active"]
    if "name" in data: target.name=data["name"].strip()
    if "campus_id" in data: target.campus_id=data["campus_id"]
    audit(db,user,"UPDATE","user",f"user_id={target.id};fields={','.join(sorted(data.keys()))}")
    db.commit(); db.refresh(target)
    return {"id":target.id,"name":target.name,"email":target.email,"role":target.role,"campus_id":target.campus_id,"is_active":target.is_active}

def _assigned_unit_ids(db:Session,user:User):
    return set(db.scalars(select(AcademicAssignment.unit_id).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==user.id,AcademicAssignment.status=="Active")).all())

def _record_unit_id(record:Record):
    if not record.code.startswith("UNIT:"): return None
    try: return int(record.code.split("|",1)[0].split(":",1)[1])
    except (ValueError,IndexError): return None

@app.get("/api/v1/my-academics")
def my_academics(user:User=Depends(require_roles("Student","Teacher")),db:Session=Depends(get_db)):
    assignments=db.scalars(select(AcademicAssignment).where(AcademicAssignment.tenant_id==user.tenant_id,AcademicAssignment.user_id==user.id,AcademicAssignment.status=="Active").order_by(AcademicAssignment.id)).all()
    result=[]
    for a in assignments:
        unit=db.get(AcademicUnit,a.unit_id)
        if unit: result.append({"assignment_id":a.id,"assignment_type":a.assignment_type,"unit_id":unit.id,"unit_type":unit.unit_type,"name":unit.name,"code":unit.code,"status":a.status})
    return result

@app.get("/api/v1/teacher-roster")
def teacher_roster(user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    assignments=db.scalars(select(AcademicAssignment).where(
        AcademicAssignment.tenant_id==user.tenant_id,
        AcademicAssignment.user_id==user.id,
        AcademicAssignment.status=="Active",
        AcademicAssignment.assignment_type.in_(["FACULTY_ASSIGNMENT","ADVISOR_ASSIGNMENT"]),
    ).order_by(AcademicAssignment.id)).all()
    classes=[]; student_map={}
    for assignment in assignments:
        unit=db.get(AcademicUnit,assignment.unit_id)
        if not unit or unit.unit_type not in {"COURSE","SECTION_BATCH"}: continue
        student_ids=sorted(_students_for_unit(db,user.tenant_id,unit.id))
        classes.append({"assignment_id":assignment.id,"assignment_type":assignment.assignment_type,"unit_id":unit.id,"unit_type":unit.unit_type,"name":unit.name,"code":unit.code,"student_count":len(student_ids)})
        for sid in student_ids:
            student=db.get(User,sid)
            if not student or student.role!="Student" or not student.is_active: continue
            item=student_map.setdefault(sid,{"student_user_id":sid,"student_name":student.name,"classes":[]})
            item["classes"].append({"unit_id":unit.id,"name":unit.name,"code":unit.code,"unit_type":unit.unit_type})
    students=sorted(student_map.values(),key=lambda x:x["student_name"].lower())
    return {"classes":classes,"students":students}

@app.get("/api/v1/academic-activities")
def academic_activities(module:str,user:User=Depends(require_roles("Student","Teacher")),db:Session=Depends(get_db)):
    if not can(user.role,module,"view"): raise HTTPException(403,"This academic module is not available for your role")
    unit_ids=_assigned_unit_ids(db,user)
    if not unit_ids: return []
    rows=db.scalars(select(Record).where(Record.tenant_id==user.tenant_id,Record.module==module).order_by(Record.id.desc())).all()
    result=[]
    for r in rows:
        unit_id=_record_unit_id(r)
        if unit_id in unit_ids:
            result.append({"id":r.id,"module":r.module,"name":r.name,"code":r.code.split("|",1)[1] if "|" in r.code else "","category":r.category,"status":r.status,"notes":r.notes,"unit_id":unit_id})
    return result

@app.post("/api/v1/academic-activities")
def create_academic_activity(payload:AcademicActivityIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    if not can(user.role,payload.module,"create"): raise HTTPException(403,"You cannot create this academic activity")
    if payload.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(403,"This course or section is not assigned to you")
    unit=db.get(AcademicUnit,payload.unit_id)
    if not unit or unit.tenant_id!=user.tenant_id: raise HTTPException(400,"Invalid academic unit")
    r=Record(tenant_id=user.tenant_id,campus_id=user.campus_id,module=payload.module,name=payload.name,code=f"UNIT:{unit.id}|{payload.code}",category=payload.category,status=payload.status,notes=payload.notes)
    db.add(r); audit(db,user,"CREATE",payload.module,f"{unit.code}:{payload.name}"); db.commit(); db.refresh(r)
    return {"id":r.id,"module":r.module,"name":r.name,"unit_id":unit.id,"unit_name":unit.name,"status":r.status}

def _parse_due_at(value):
    if not value: return None
    try: return dt.datetime.fromisoformat(value.replace("Z","+00:00")).replace(tzinfo=None)
    except ValueError: raise HTTPException(400,"Invalid due date")

def _descendant_unit_ids(db:Session,tenant_id:int,unit_id:int):
    """Return a unit and all of its descendants inside the same institution."""
    result={unit_id}; frontier=[unit_id]
    while frontier:
        children=set(db.scalars(select(AcademicUnit.id).where(
            AcademicUnit.tenant_id==tenant_id,
            AcademicUnit.parent_id.in_(frontier),
        )).all())
        children-=result
        if not children: break
        result.update(children); frontier=list(children)
    return result

def _students_for_unit(db:Session,tenant_id:int,unit_id:int):
    # A course-level activity also applies to students enrolled in child
    # sections/batches. Section-level activities remain scoped to that section.
    scoped_units=_descendant_unit_ids(db,tenant_id,unit_id)
    ids=db.scalars(select(AcademicAssignment.user_id).where(
        AcademicAssignment.tenant_id==tenant_id,
        AcademicAssignment.unit_id.in_(scoped_units),
        AcademicAssignment.status=="Active",
        AcademicAssignment.assignment_type.in_(["COURSE_REGISTRATION","SECTION_ASSIGNMENT","ENROLLMENT"]),
    )).all()
    if not ids: return set()
    students=db.scalars(select(User.id).where(
        User.tenant_id==tenant_id,
        User.id.in_(set(ids)),
        User.role=="Student",
        User.is_active==True,
    )).all()
    return set(students)

@app.get("/api/v1/academic-work")
def list_academic_work(work_type:Optional[str]=None,user:User=Depends(require_roles("Student","Teacher")),db:Session=Depends(get_db)):
    unit_ids=_assigned_unit_ids(db,user)
    if not unit_ids: return []
    st=select(AcademicWork).where(AcademicWork.tenant_id==user.tenant_id,AcademicWork.unit_id.in_(unit_ids))
    if work_type: st=st.where(AcademicWork.work_type==work_type.upper())
    rows=db.scalars(st.order_by(AcademicWork.id.desc())).all()
    result=[]
    for w in rows:
        item={"id":w.id,"unit_id":w.unit_id,"work_type":w.work_type,"title":w.title,"description":w.description,"max_marks":w.max_marks,"due_at":w.due_at,"status":w.status}
        if user.role=="Student":
            sub=db.scalar(select(StudentAcademicWork).where(StudentAcademicWork.work_id==w.id,StudentAcademicWork.student_user_id==user.id))
            item["submission"]=None if not sub else {"status":sub.status,"submitted_at":sub.submitted_at,"marks":sub.marks,"grade":sub.grade,"feedback":sub.feedback}
        result.append(item)
    return result

@app.post("/api/v1/academic-work")
def create_work(payload:AcademicWorkIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    kind=payload.work_type.strip().upper()
    if kind not in {"HOMEWORK","ASSIGNMENT","EXAM"}: raise HTTPException(400,"Unsupported academic work type")
    if payload.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(403,"This course or section is not assigned to you")
    unit=db.get(AcademicUnit,payload.unit_id)
    if not unit or unit.tenant_id!=user.tenant_id: raise HTTPException(400,"Invalid academic unit")
    if unit.unit_type not in {"COURSE","SECTION_BATCH"}: raise HTTPException(400,"Academic work can only be created for a Course or Section / Batch")
    w=AcademicWork(tenant_id=user.tenant_id,unit_id=payload.unit_id,teacher_user_id=user.id,work_type=kind,title=payload.title,description=payload.description,max_marks=payload.max_marks,due_at=_parse_due_at(payload.due_at))
    db.add(w); audit(db,user,"CREATE",kind,payload.title); db.commit(); db.refresh(w)
    return {"id":w.id,"title":w.title,"work_type":w.work_type,"status":w.status}

@app.post("/api/v1/academic-work/{work_id}/submit")
def submit_work(work_id:int,payload:SubmissionIn,user:User=Depends(require_roles("Student")),db:Session=Depends(get_db)):
    w=db.get(AcademicWork,work_id)
    if not w or w.tenant_id!=user.tenant_id or w.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Academic work not found")
    sub=db.scalar(select(StudentAcademicWork).where(StudentAcademicWork.work_id==work_id,StudentAcademicWork.student_user_id==user.id))
    if not sub:
        sub=StudentAcademicWork(tenant_id=user.tenant_id,work_id=work_id,student_user_id=user.id)
        db.add(sub)
    sub.submission_text=payload.submission_text; sub.submitted_at=dt.datetime.utcnow(); sub.status="SUBMITTED"
    audit(db,user,"SUBMIT",w.work_type,w.title); db.commit(); db.refresh(sub)
    return {"id":sub.id,"status":sub.status,"submitted_at":sub.submitted_at}

@app.get("/api/v1/academic-work/{work_id}/submissions")
def work_submissions(work_id:int,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    w=db.get(AcademicWork,work_id)
    if not w or w.tenant_id!=user.tenant_id or w.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Academic work not found")
    students=_students_for_unit(db,user.tenant_id,w.unit_id)
    result=[]
    for sid in students:
        student=db.get(User,sid); sub=db.scalar(select(StudentAcademicWork).where(StudentAcademicWork.work_id==work_id,StudentAcademicWork.student_user_id==sid))
        result.append({"student_id":sid,"student_name":student.name if student else "Student","submission_id":sub.id if sub else None,"status":sub.status if sub else "PENDING","marks":sub.marks if sub else None,"grade":sub.grade if sub else "","feedback":sub.feedback if sub else ""})
    return result

@app.put("/api/v1/academic-work/{work_id}/students/{student_id}/grade")
def grade_work(work_id:int,student_id:int,payload:GradeIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    w=db.get(AcademicWork,work_id)
    if not w or w.tenant_id!=user.tenant_id or w.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Academic work not found")
    if student_id not in _students_for_unit(db,user.tenant_id,w.unit_id): raise HTTPException(400,"Student is not enrolled in this course or section")
    if w.max_marks and payload.marks>w.max_marks: raise HTTPException(400,"Marks cannot exceed maximum marks")
    sub=db.scalar(select(StudentAcademicWork).where(StudentAcademicWork.work_id==work_id,StudentAcademicWork.student_user_id==student_id))
    if not sub:
        sub=StudentAcademicWork(tenant_id=user.tenant_id,work_id=work_id,student_user_id=student_id)
        db.add(sub)
    sub.marks=payload.marks; sub.grade=payload.grade.strip(); sub.feedback=payload.feedback; sub.status="GRADED"
    audit(db,user,"GRADE",w.work_type,f"{w.title}:student={student_id}"); db.commit()
    return {"ok":True,"marks":sub.marks,"grade":sub.grade,"status":sub.status}

@app.get("/api/v1/class-sessions")
def class_sessions(user:User=Depends(require_roles("Student","Teacher")),db:Session=Depends(get_db)):
    unit_ids=_assigned_unit_ids(db,user)
    if not unit_ids: return []
    st=select(ClassSession).where(ClassSession.tenant_id==user.tenant_id,ClassSession.unit_id.in_(unit_ids))
    if user.role=="Teacher": st=st.where(ClassSession.teacher_user_id==user.id)
    rows=db.scalars(st.order_by(ClassSession.starts_at.desc())).all()
    return [{"id":x.id,"unit_id":x.unit_id,"title":x.title,"starts_at":x.starts_at,"ends_at":x.ends_at,"room":x.room,"status":x.status} for x in rows]

@app.post("/api/v1/class-sessions")
def create_class_session(payload:ClassSessionIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    if payload.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(403,"This course or section is not assigned to you")
    unit=db.get(AcademicUnit,payload.unit_id)
    if not unit or unit.tenant_id!=user.tenant_id: raise HTTPException(400,"Invalid academic unit")
    if unit.unit_type not in {"COURSE","SECTION_BATCH"}: raise HTTPException(400,"Class sessions can only be scheduled for a Course or Section / Batch")
    start=_parse_due_at(payload.starts_at); end=_parse_due_at(payload.ends_at)
    if not start or not end or end<=start: raise HTTPException(400,"Session end time must be after start time")
    overlap=select(ClassSession).where(
        ClassSession.tenant_id==user.tenant_id,
        ClassSession.starts_at < end,
        ClassSession.ends_at > start,
    )
    teacher_conflict=db.scalar(overlap.where(ClassSession.teacher_user_id==user.id))
    if teacher_conflict:
        raise HTTPException(409,f"Teacher already has an overlapping class session: {teacher_conflict.title}")
    unit_conflict=db.scalar(overlap.where(ClassSession.unit_id==payload.unit_id))
    if unit_conflict:
        raise HTTPException(409,f"This course or section already has an overlapping class session: {unit_conflict.title}")
    room=(payload.room or "").strip()
    if room:
        room_conflict=db.scalar(overlap.where(ClassSession.room==room))
        if room_conflict:
            raise HTTPException(409,f"Room is already booked for an overlapping class session: {room_conflict.title}")
    row=ClassSession(tenant_id=user.tenant_id,unit_id=payload.unit_id,teacher_user_id=user.id,title=payload.title,starts_at=start,ends_at=end,room=room)
    db.add(row); audit(db,user,"CREATE","class_session",payload.title); db.commit(); db.refresh(row)
    return {"id":row.id,"title":row.title,"status":row.status}

@app.get("/api/v1/class-sessions/{session_id}/attendance")
def session_attendance(session_id:int,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    session=db.get(ClassSession,session_id)
    if not session or session.tenant_id!=user.tenant_id or session.teacher_user_id!=user.id: raise HTTPException(404,"Class session not found")
    students=_students_for_unit(db,user.tenant_id,session.unit_id)
    result=[]
    for sid in students:
        student=db.get(User,sid)
        entry=db.scalar(select(AttendanceEntry).where(AttendanceEntry.session_id==session_id,AttendanceEntry.student_user_id==sid))
        result.append({"student_user_id":sid,"student_name":student.name if student else "Student","status":entry.status if entry else "UNMARKED","note":entry.note if entry else ""})
    return result

@app.put("/api/v1/class-sessions/{session_id}/attendance")
def mark_attendance(session_id:int,payload:AttendanceMarkIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    session=db.get(ClassSession,session_id)
    if not session or session.tenant_id!=user.tenant_id or session.teacher_user_id!=user.id: raise HTTPException(404,"Class session not found")
    if payload.student_user_id not in _students_for_unit(db,user.tenant_id,session.unit_id): raise HTTPException(400,"Student is not enrolled in this class")
    status=payload.status.strip().upper()
    if status not in {"PRESENT","ABSENT","LATE","EXCUSED"}: raise HTTPException(400,"Invalid attendance status")
    entry=db.scalar(select(AttendanceEntry).where(AttendanceEntry.session_id==session_id,AttendanceEntry.student_user_id==payload.student_user_id))
    if not entry:
        entry=AttendanceEntry(tenant_id=user.tenant_id,session_id=session_id,student_user_id=payload.student_user_id,marked_by=user.id)
        db.add(entry)
    entry.status=status; entry.note=payload.note; entry.marked_by=user.id; entry.marked_at=dt.datetime.utcnow()
    audit(db,user,"ATTENDANCE",f"session:{session_id}",f"student={payload.student_user_id}:{status}"); db.commit()
    return {"ok":True,"status":status}

@app.get("/api/v1/my-attendance")
def my_attendance(user:User=Depends(require_roles("Student")),db:Session=Depends(get_db)):
    assigned=_assigned_unit_ids(db,user)
    # Include sessions created at a parent course when the student is assigned
    # to one of that course's child sections/batches.
    visible_units=set(assigned)
    for unit_id in list(assigned):
        unit=db.get(AcademicUnit,unit_id)
        seen=set()
        while unit and unit.parent_id and unit.parent_id not in seen:
            seen.add(unit.parent_id)
            parent=db.get(AcademicUnit,unit.parent_id)
            if not parent or parent.tenant_id!=user.tenant_id: break
            if parent.unit_type=="COURSE": visible_units.add(parent.id)
            unit=parent
    if not visible_units:
        return {"percentage":None,"attended":0,"absent":0,"late":0,"excused":0,"marked_sessions":0,"counted_sessions":0,"sessions":[]}
    sessions=db.scalars(select(ClassSession).where(ClassSession.tenant_id==user.tenant_id,ClassSession.unit_id.in_(visible_units)).order_by(ClassSession.starts_at.desc())).all()
    rows=[]; attended=0; absent=0; late=0; excused=0; marked=0; counted=0
    for session in sessions:
        if user.id not in _students_for_unit(db,user.tenant_id,session.unit_id): continue
        entry=db.scalar(select(AttendanceEntry).where(AttendanceEntry.session_id==session.id,AttendanceEntry.student_user_id==user.id))
        status=entry.status if entry else "UNMARKED"
        if status!="UNMARKED":
            marked+=1
            if status=="EXCUSED":
                excused+=1
            else:
                counted+=1
                if status=="PRESENT": attended+=1
                elif status=="LATE": attended+=1; late+=1
                elif status=="ABSENT": absent+=1
        rows.append({"session_id":session.id,"title":session.title,"starts_at":session.starts_at,"room":session.room,"status":status})
    return {"percentage":round(attended*100/counted,1) if counted else None,"attended":attended,"absent":absent,"late":late,"excused":excused,"marked_sessions":marked,"counted_sessions":counted,"sessions":rows}

@app.get("/api/v1/grade-rules")
def grade_rules(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(GradeRule).where(GradeRule.tenant_id==user.tenant_id).order_by(GradeRule.min_percentage.desc())).all()
    return [{"id":r.id,"name":r.name,"min_percentage":r.min_percentage,"max_percentage":r.max_percentage,"grade":r.grade,"grade_point":r.grade_point,"result_status":r.result_status} for r in rows]

@app.post("/api/v1/grade-rules")
def create_grade_rule(payload:GradeRuleIn,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    if payload.max_percentage<payload.min_percentage: raise HTTPException(400,"Maximum percentage must be greater than or equal to minimum percentage")
    if payload.grade_point is not None and payload.grade_point<0: raise HTTPException(400,"Grade point cannot be negative")
    result_status=payload.result_status.strip().upper()
    if result_status not in {"PASS","FAIL"}: raise HTTPException(400,"Result status must be PASS or FAIL")
    if not payload.name.strip() or not payload.grade.strip(): raise HTTPException(400,"Grade rule name and grade are required")
    overlap=db.scalar(select(GradeRule).where(GradeRule.tenant_id==user.tenant_id,GradeRule.min_percentage<=payload.max_percentage,GradeRule.max_percentage>=payload.min_percentage))
    if overlap: raise HTTPException(409,"Grade percentage range overlaps an existing rule")
    data=payload.model_dump(); data["name"]=payload.name.strip(); data["grade"]=payload.grade.strip().upper(); data["result_status"]=result_status
    r=GradeRule(tenant_id=user.tenant_id,**data)
    db.add(r); audit(db,user,"CREATE","grade_rule",f"{r.grade}:{r.min_percentage}-{r.max_percentage}"); db.commit(); db.refresh(r)
    return {"id":r.id,"grade":r.grade}

@app.delete("/api/v1/grade-rules/{rule_id}")
def delete_grade_rule(rule_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    r=db.get(GradeRule,rule_id)
    if not r or r.tenant_id!=user.tenant_id: raise HTTPException(404,"Grade rule not found")
    db.delete(r); audit(db,user,"DELETE","grade_rule",r.grade); db.commit(); return {"ok":True}

def _grading_scheme_gaps(db:Session,tenant_id:int):
    rules=db.scalars(select(GradeRule).where(GradeRule.tenant_id==tenant_id).order_by(GradeRule.min_percentage,GradeRule.max_percentage)).all()
    if not rules: return [(0.0,100.0)]
    gaps=[]; cursor=0.0
    for rule in rules:
        if rule.min_percentage>cursor: gaps.append((cursor,rule.min_percentage))
        cursor=max(cursor,rule.max_percentage)
    if cursor<100.0: gaps.append((cursor,100.0))
    return gaps

def _grade_for(db:Session,tenant_id:int,percentage:float):
    return db.scalar(select(GradeRule).where(GradeRule.tenant_id==tenant_id,GradeRule.min_percentage<=percentage,GradeRule.max_percentage>=percentage).order_by(GradeRule.min_percentage.desc()))

@app.get("/api/v1/exams/{work_id}/results")
def exam_results_register(work_id:int,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    exam=db.get(AcademicWork,work_id)
    if not exam or exam.tenant_id!=user.tenant_id or exam.work_type!="EXAM" or exam.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Exam not found")
    student_ids=sorted(_students_for_unit(db,user.tenant_id,exam.unit_id))
    saved={r.student_user_id:r for r in db.scalars(select(ExamResult).where(ExamResult.tenant_id==user.tenant_id,ExamResult.work_id==work_id)).all()}
    rows=[]
    for sid in student_ids:
        student=db.get(User,sid); r=saved.get(sid)
        rows.append({"student_id":sid,"student_name":student.name if student else "Student","marks":r.marks if r else None,"percentage":r.percentage if r else None,"grade":r.grade if r else "","grade_point":r.grade_point if r else None,"result_status":r.result_status if r else "","remarks":r.remarks if r else "","published":bool(r.published) if r else False})
    return {"exam":{"id":exam.id,"title":exam.title,"max_marks":exam.max_marks,"unit_id":exam.unit_id},"students":rows,"complete":bool(student_ids) and all(sid in saved for sid in student_ids),"published":bool(saved) and all(r.published for r in saved.values())}

@app.put("/api/v1/exams/{work_id}/results")
def save_exam_result(work_id:int,payload:ExamResultIn,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    exam=db.get(AcademicWork,work_id)
    if not exam or exam.tenant_id!=user.tenant_id or exam.work_type!="EXAM" or exam.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Exam not found")
    if payload.student_user_id not in _students_for_unit(db,user.tenant_id,exam.unit_id): raise HTTPException(400,"Student is not enrolled in this exam course")
    if exam.max_marks<=0: raise HTTPException(400,"Exam maximum marks must be greater than zero")
    if payload.marks>exam.max_marks: raise HTTPException(400,"Marks cannot exceed maximum marks")
    percentage=round(payload.marks*100/exam.max_marks,2); rule=_grade_for(db,user.tenant_id,percentage)
    if not rule: raise HTTPException(409,"No grading rule covers this percentage")
    row=db.scalar(select(ExamResult).where(ExamResult.work_id==work_id,ExamResult.student_user_id==payload.student_user_id))
    if row and row.published: raise HTTPException(409,"Published results are locked and cannot be edited")
    if not row:
        row=ExamResult(tenant_id=user.tenant_id,work_id=work_id,student_user_id=payload.student_user_id,marks=payload.marks,percentage=percentage,grade=rule.grade,grade_point=rule.grade_point,result_status=rule.result_status,remarks=payload.remarks)
        db.add(row)
    else:
        row.marks=payload.marks; row.percentage=percentage; row.grade=rule.grade; row.grade_point=rule.grade_point; row.result_status=rule.result_status; row.remarks=payload.remarks
    audit(db,user,"GRADE","exam_result",f"exam={work_id}:student={payload.student_user_id}:{rule.grade}"); db.commit()
    return {"ok":True,"percentage":percentage,"grade":rule.grade,"grade_point":rule.grade_point,"result_status":rule.result_status}

@app.post("/api/v1/exams/{work_id}/publish")
def publish_exam_results(work_id:int,user:User=Depends(require_roles("Teacher")),db:Session=Depends(get_db)):
    exam=db.get(AcademicWork,work_id)
    if not exam or exam.tenant_id!=user.tenant_id or exam.work_type!="EXAM" or exam.unit_id not in _assigned_unit_ids(db,user): raise HTTPException(404,"Exam not found")
    gaps=_grading_scheme_gaps(db,user.tenant_id)
    if gaps:
        formatted=", ".join(f"{a:g}-{b:g}%" for a,b in gaps)
        raise HTTPException(409,f"Grading scheme is incomplete. Configure coverage for: {formatted}")
    student_ids=_students_for_unit(db,user.tenant_id,exam.unit_id)
    if not student_ids: raise HTTPException(409,"No enrolled students for this exam")
    rows=db.scalars(select(ExamResult).where(ExamResult.tenant_id==user.tenant_id,ExamResult.work_id==work_id)).all()
    entered={r.student_user_id for r in rows}
    missing=student_ids-entered
    if missing: raise HTTPException(409,f"Enter results for all enrolled students before publishing. Missing: {len(missing)}")
    for r in rows: r.published=True
    audit(db,user,"PUBLISH","exam_results",f"exam={work_id}:count={len(rows)}"); db.commit(); return {"ok":True,"published":len(rows)}

@app.get("/api/v1/my-results")
def my_results(user:User=Depends(require_roles("Student")),db:Session=Depends(get_db)):
    rows=db.scalars(select(ExamResult).where(ExamResult.tenant_id==user.tenant_id,ExamResult.student_user_id==user.id,ExamResult.published==True).order_by(ExamResult.id.desc())).all()
    result=[]; points=[]
    for r in rows:
        exam=db.get(AcademicWork,r.work_id); unit=db.get(AcademicUnit,exam.unit_id) if exam else None
        if exam and unit:
            result.append({"exam_id":exam.id,"exam":exam.title,"course":unit.name,"marks":r.marks,"max_marks":exam.max_marks,"percentage":r.percentage,"grade":r.grade,"grade_point":r.grade_point,"result_status":r.result_status,"remarks":r.remarks})
            if r.grade_point is not None: points.append(r.grade_point)
    average=round(sum(points)/len(points),2) if points else None
    return {"results":result,"average_grade_point":average,"gpa":average}

@app.get("/api/v1/records")
def records(
    module: Optional[str]=None,
    q: Optional[str]=None,
    user: User=Depends(current_user),
    db: Session=Depends(get_db),
):
    st = select(Record).where(Record.tenant_id==user.tenant_id)
    if user.role=="Campus Admin":
        st = st.where(Record.campus_id==user.campus_id)
    if module:
        if not can(user.role, module, "view"):
            raise HTTPException(403, "This module is not available for your role")
        st=st.where(Record.module==module)
    elif user.role not in {"Institution Admin", "Campus Admin", "Auditor"}:
        raise HTTPException(400, "module is required for this role")
    if q:
        st=st.where(Record.name.ilike(f"%{q}%"))
    rows=db.scalars(st.order_by(Record.id.desc())).all()
    return [
        {"id":r.id,"module":r.module,"name":r.name,"code":r.code,"category":r.category,
         "status":r.status,"notes":r.notes,"created_at":r.created_at}
        for r in rows
    ]

@app.post("/api/v1/records")
def create_record(
    payload: RecordIn,
    user: User=Depends(current_user),
    db: Session=Depends(get_db),
):
    if not can(user.role, payload.module, "create"):
        raise HTTPException(403, "You do not have permission to create records in this module")
    r=Record(
        tenant_id=user.tenant_id,campus_id=user.campus_id,
        **payload.model_dump()
    )
    db.add(r)
    audit(db,user,"CREATE",payload.module,payload.name)
    db.commit(); db.refresh(r)
    return {"id":r.id,**payload.model_dump()}

@app.put("/api/v1/records/{rid}")
def update_record(
    rid:int,payload:RecordIn,
    user:User=Depends(current_user),
    db:Session=Depends(get_db),
):
    if not can(user.role, payload.module, "update"):
        raise HTTPException(403, "You do not have permission to update records in this module")
    r=db.get(Record,rid)
    if not r or r.tenant_id!=user.tenant_id:
        raise HTTPException(404,"Record not found")
    if user.role=="Campus Admin" and r.campus_id!=user.campus_id:
        raise HTTPException(403,"Outside campus scope")
    for k,v in payload.model_dump().items():
        setattr(r,k,v)
    audit(db,user,"UPDATE",f"{payload.module}:{rid}",payload.name)
    db.commit()
    return {"ok":True}

@app.delete("/api/v1/records/{rid}")
def delete_record(
    rid:int,
    user:User=Depends(current_user),
    db:Session=Depends(get_db),
):
    r=db.get(Record,rid)
    if not r or r.tenant_id!=user.tenant_id:
        raise HTTPException(404,"Record not found")
    if not can(user.role, r.module, "delete"):
        raise HTTPException(403, "You do not have permission to delete records in this module")
    if user.role=="Campus Admin" and r.campus_id!=user.campus_id:
        raise HTTPException(403,"Outside campus scope")
    audit(db,user,"DELETE",f"{r.module}:{r.id}",r.name)
    db.delete(r); db.commit()
    return {"ok":True}

@app.get("/api/v1/admin/parent-student-links")
def admin_parent_student_links(user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    links=db.scalars(select(ParentStudentLink).where(ParentStudentLink.tenant_id==user.tenant_id).order_by(ParentStudentLink.id)).all()
    result=[]
    for link in links:
        parent=db.get(User,link.parent_user_id); student=db.get(User,link.student_user_id)
        if parent and student:
            result.append({"id":link.id,"parent_user_id":parent.id,"parent_name":parent.name,"parent_email":parent.email,"student_user_id":student.id,"student_name":student.name,"student_email":student.email,"relationship":link.relationship})
    return result

@app.post("/api/v1/admin/parent-student-links")
def create_parent_student_link(payload:ParentStudentLinkIn,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    parent=db.get(User,payload.parent_user_id); student=db.get(User,payload.student_user_id)
    if not parent or parent.tenant_id!=user.tenant_id or parent.role!="Parent / Guardian" or not parent.is_active:
        raise HTTPException(400,"Invalid parent or guardian")
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student" or not student.is_active:
        raise HTTPException(400,"Invalid student")
    existing=db.scalar(select(ParentStudentLink).where(ParentStudentLink.parent_user_id==parent.id,ParentStudentLink.student_user_id==student.id))
    if existing: raise HTTPException(409,"This parent and student are already linked")
    row=ParentStudentLink(parent_user_id=parent.id,student_user_id=student.id,relationship=payload.relationship.strip(),tenant_id=user.tenant_id)
    db.add(row); db.flush(); audit(db,user,"CREATE","parent_student_link",f"parent={parent.id};student={student.id};relationship={row.relationship}"); db.commit(); db.refresh(row)
    return {"id":row.id,"parent_user_id":parent.id,"student_user_id":student.id,"relationship":row.relationship}

@app.delete("/api/v1/admin/parent-student-links/{link_id}")
def delete_parent_student_link(link_id:int,user:User=Depends(require_roles("Institution Admin")),db:Session=Depends(get_db)):
    row=db.get(ParentStudentLink,link_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Parent-student link not found")
    details=f"parent={row.parent_user_id};student={row.student_user_id};relationship={row.relationship}"
    db.delete(row); audit(db,user,"DELETE","parent_student_link",details); db.commit()
    return {"ok":True}

@app.get("/api/v1/parents/children")
def parent_children(
    user:User=Depends(require_roles("Parent / Guardian")),
    db:Session=Depends(get_db),
):
    links=db.scalars(select(ParentStudentLink).where(
        ParentStudentLink.parent_user_id==user.id,
        ParentStudentLink.tenant_id==user.tenant_id,
    )).all()
    result=[]
    for link in links:
        student=db.get(User,link.student_user_id)
        if student:
            result.append({
                "id":student.id,"name":student.name,"email":student.email,
                "relationship":link.relationship,
            })
    return result

def _fee_payload(row:FeeLedger):
    balance=max(0,row.amount_due-row.amount_paid)
    status="CANCELLED" if row.status=="CANCELLED" else ("PAID" if balance<=0 else ("PARTIAL" if row.amount_paid>0 else "DUE"))
    return {"id":row.id,"student_user_id":row.student_user_id,"fee_code":row.fee_code,"title":row.title,"amount_due":float(row.amount_due),"amount_paid":float(row.amount_paid),"balance":float(balance),"due_at":row.due_at,"status":status}

@app.get("/api/v1/finance/students")
def finance_students(user:User=Depends(require_roles("Accounts","Institution Admin")),db:Session=Depends(get_db)):
    rows=db.scalars(select(User).where(User.tenant_id==user.tenant_id,User.role=="Student",User.is_active==True).order_by(User.name)).all()
    return [{"id":x.id,"name":x.name,"email":x.email} for x in rows]

@app.get("/api/v1/finance/payments")
def finance_payments(user:User=Depends(require_roles("Accounts","Institution Admin","Auditor")),db:Session=Depends(get_db)):
    rows=db.scalars(select(FeePayment).where(FeePayment.tenant_id==user.tenant_id).order_by(FeePayment.paid_at.desc())).all()
    result=[]
    for x in rows:
        ledger=db.get(FeeLedger,x.ledger_id); student=db.get(User,x.student_user_id)
        result.append({"id":x.id,"ledger_id":x.ledger_id,"fee_code":ledger.fee_code if ledger else "","fee_title":ledger.title if ledger else "","student_user_id":x.student_user_id,"student_name":student.name if student else f"Student {x.student_user_id}","amount":float(x.amount),"reference":x.reference,"receipt_no":x.receipt_no,"paid_at":x.paid_at})
    return result

@app.get("/api/v1/fee-ledger")
def fee_ledger(user:User=Depends(current_user),db:Session=Depends(get_db)):
    st=select(FeeLedger).where(FeeLedger.tenant_id==user.tenant_id)
    if user.role=="Student": st=st.where(FeeLedger.student_user_id==user.id)
    elif user.role not in {"Accounts","Institution Admin","Auditor"}: raise HTTPException(403,"Fee ledger is not available for your role")
    return [_fee_payload(x) for x in db.scalars(st.order_by(FeeLedger.id.desc())).all()]

@app.post("/api/v1/fee-ledger")
def create_fee_ledger(payload:FeeLedgerIn,user:User=Depends(require_roles("Accounts","Institution Admin")),db:Session=Depends(get_db)):
    student=db.get(User,payload.student_user_id)
    if not student or student.tenant_id!=user.tenant_id or student.role!="Student" or not student.is_active: raise HTTPException(400,"Invalid student")
    code=payload.fee_code.strip().upper()
    if db.scalar(select(FeeLedger).where(FeeLedger.tenant_id==user.tenant_id,FeeLedger.student_user_id==student.id,FeeLedger.fee_code==code)): raise HTTPException(409,"This fee is already assigned to the student")
    due=_parse_due_at(payload.due_at)
    row=FeeLedger(tenant_id=user.tenant_id,student_user_id=student.id,fee_code=code,title=payload.title.strip(),amount_due=payload.amount_due,amount_paid=0,due_at=due,status="DUE")
    db.add(row); db.flush(); audit(db,user,"CREATE","fee_ledger",f"student={student.id};fee={code};amount={payload.amount_due}"); db.commit(); db.refresh(row)
    return _fee_payload(row)

@app.post("/api/v1/fee-ledger/{ledger_id}/cancel")
def cancel_fee_ledger(ledger_id:int,user:User=Depends(require_roles("Accounts","Institution Admin")),db:Session=Depends(get_db)):
    row=db.get(FeeLedger,ledger_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Fee ledger entry not found")
    if row.amount_paid>0: raise HTTPException(409,"A fee with recorded payments cannot be cancelled")
    if row.status=="CANCELLED": return _fee_payload(row)
    row.status="CANCELLED"; audit(db,user,"CANCEL","fee_ledger",f"ledger={row.id};student={row.student_user_id}"); db.commit()
    return _fee_payload(row)

@app.get("/api/v1/finance/report")
def finance_report(start_date:str|None=None,end_date:str|None=None,user:User=Depends(require_roles("Accounts","Institution Admin","Auditor")),db:Session=Depends(get_db)):
    st=select(FeePayment).where(FeePayment.tenant_id==user.tenant_id)
    try:
        if start_date: st=st.where(FeePayment.paid_at>=dt.datetime.fromisoformat(start_date))
        if end_date:
            end=dt.datetime.fromisoformat(end_date)
            if len(end_date)<=10: end=end+dt.timedelta(days=1)
            st=st.where(FeePayment.paid_at<end)
    except ValueError: raise HTTPException(400,"Invalid report date")
    rows=db.scalars(st.order_by(FeePayment.paid_at.desc())).all()
    items=[]; total=0
    for x in rows:
        ledger=db.get(FeeLedger,x.ledger_id); student=db.get(User,x.student_user_id); total+=x.amount
        items.append({"receipt_no":x.receipt_no,"student_id":x.student_user_id,"student_name":student.name if student else f"Student {x.student_user_id}","student_email":student.email if student else "","fee_code":ledger.fee_code if ledger else "","fee_title":ledger.title if ledger else "","amount":x.amount,"reference":x.reference,"paid_at":x.paid_at})
    return {"start_date":start_date,"end_date":end_date,"payment_count":len(items),"total_collected":float(total),"payments":items}

@app.get("/api/v1/finance/summary")
def finance_summary(user:User=Depends(require_roles("Accounts","Institution Admin","Auditor")),db:Session=Depends(get_db)):
    rows=db.scalars(select(FeeLedger).where(FeeLedger.tenant_id==user.tenant_id)).all()
    active=[x for x in rows if x.status!="CANCELLED"]
    assigned=sum((x.amount_due for x in active),0); collected=sum((x.amount_paid for x in active),0); outstanding=max(0,assigned-collected)
    return {"assigned":float(assigned),"collected":float(collected),"outstanding":float(outstanding),"ledger_count":len(active),"paid_count":sum(1 for x in active if x.amount_paid>=x.amount_due),"partial_count":sum(1 for x in active if 0<x.amount_paid<x.amount_due),"due_count":sum(1 for x in active if x.amount_paid<=0)}

@app.post("/api/v1/fee-ledger/{ledger_id}/payments")
def record_fee_payment(ledger_id:int,payload:FeePaymentIn,user:User=Depends(require_roles("Accounts","Institution Admin")),db:Session=Depends(get_db)):
    row=db.get(FeeLedger,ledger_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Fee ledger entry not found")
    if row.status=="CANCELLED": raise HTTPException(409,"Cancelled fees cannot receive payments")
    balance=max(0,row.amount_due-row.amount_paid)
    reference=payload.reference.strip()
    if reference and db.scalar(select(FeePayment).where(FeePayment.tenant_id==user.tenant_id,FeePayment.reference==reference)): raise HTTPException(409,"This payment reference has already been recorded")
    payment_amount=Decimal(str(payload.amount)).quantize(Decimal("0.01"))
    if payment_amount>balance: raise HTTPException(400,"Payment cannot exceed outstanding balance")
    receipt=f"GAINT-{user.tenant_id}-{dt.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}-{ledger_id}"
    payment=FeePayment(tenant_id=user.tenant_id,ledger_id=row.id,student_user_id=row.student_user_id,amount=payment_amount,reference=reference,receipt_no=receipt,recorded_by=user.id)
    row.amount_paid+=payment_amount; row.status="PAID" if row.amount_paid>=row.amount_due else "PARTIAL"
    db.add(payment); audit(db,user,"PAYMENT","fee_ledger",f"student={row.student_user_id};receipt={receipt};amount={payment_amount}"); db.commit()
    return {"ok":True,"receipt_no":receipt,"ledger":_fee_payload(row)}

@app.get("/api/v1/fee-ledger/{ledger_id}/receipts")
def fee_receipts(ledger_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.get(FeeLedger,ledger_id)
    if not row or row.tenant_id!=user.tenant_id: raise HTTPException(404,"Fee ledger entry not found")
    allowed=user.role in {"Accounts","Institution Admin","Auditor"} or (user.role=="Student" and row.student_user_id==user.id)
    if user.role=="Parent / Guardian":
        allowed=db.scalar(select(ParentStudentLink.id).where(ParentStudentLink.parent_user_id==user.id,ParentStudentLink.student_user_id==row.student_user_id,ParentStudentLink.tenant_id==user.tenant_id)) is not None
    if not allowed: raise HTTPException(403,"You cannot view these receipts")
    rows=db.scalars(select(FeePayment).where(FeePayment.ledger_id==ledger_id,FeePayment.tenant_id==user.tenant_id).order_by(FeePayment.paid_at.desc())).all()
    return [{"id":x.id,"amount":x.amount,"reference":x.reference,"receipt_no":x.receipt_no,"paid_at":x.paid_at} for x in rows]

@app.get("/api/v1/parents/children/{student_id}/fees")
def parent_child_fees(student_id:int,user:User=Depends(require_roles("Parent / Guardian")),db:Session=Depends(get_db)):
    student=_linked_child(db,user,student_id)
    rows=db.scalars(select(FeeLedger).where(FeeLedger.tenant_id==user.tenant_id,FeeLedger.student_user_id==student.id).order_by(FeeLedger.id.desc())).all()
    return {"student":{"id":student.id,"name":student.name,"email":student.email},"records":[_fee_payload(x) for x in rows],"payment_ready":False,"message":"Fee ledger is live. Online gateway payment remains disabled until a production payment provider is configured."}

def _linked_child(db:Session,parent:User,student_id:int):
    link=db.scalar(select(ParentStudentLink).where(
        ParentStudentLink.parent_user_id==parent.id,
        ParentStudentLink.student_user_id==student_id,
        ParentStudentLink.tenant_id==parent.tenant_id,
    ))
    if not link: raise HTTPException(403,"This student is not linked to your account")
    student=db.get(User,student_id)
    if not student or student.tenant_id!=parent.tenant_id or student.role!="Student" or not student.is_active:
        raise HTTPException(404,"Linked student not found")
    return student

@app.get("/api/v1/parents/children/{student_id}/academics")
def parent_child_academics(student_id:int,user:User=Depends(require_roles("Parent / Guardian")),db:Session=Depends(get_db)):
    student=_linked_child(db,user,student_id)
    unit_ids=_assigned_unit_ids(db,student)
    visible_units=set(unit_ids)
    for uid in list(unit_ids):
        unit=db.get(AcademicUnit,uid)
        while unit and unit.parent_id:
            unit=db.get(AcademicUnit,unit.parent_id)
            if not unit or unit.tenant_id!=user.tenant_id: break
            if unit.unit_type=="COURSE": visible_units.add(unit.id)
    works=db.scalars(select(AcademicWork).where(
        AcademicWork.tenant_id==user.tenant_id,
        AcademicWork.unit_id.in_(visible_units) if visible_units else False,
    ).order_by(AcademicWork.id.desc())).all() if visible_units else []
    homework=[]
    for work in works:
        if student.id not in _students_for_unit(db,user.tenant_id,work.unit_id): continue
        if work.work_type not in {"HOMEWORK","ASSIGNMENT"}: continue
        submission=db.scalar(select(StudentAcademicWork).where(StudentAcademicWork.work_id==work.id,StudentAcademicWork.student_user_id==student.id))
        homework.append({"id":work.id,"work_type":work.work_type,"title":work.title,"due_at":work.due_at,"status":submission.status if submission else "NOT_SUBMITTED","score":submission.score if submission else None})

    sessions=db.scalars(select(ClassSession).where(
        ClassSession.tenant_id==user.tenant_id,
        ClassSession.unit_id.in_(visible_units) if visible_units else False,
    ).order_by(ClassSession.starts_at.desc())).all() if visible_units else []
    attendance=[]; attended=0; counted=0; excused=0
    for session in sessions:
        if student.id not in _students_for_unit(db,user.tenant_id,session.unit_id): continue
        entry=db.scalar(select(AttendanceEntry).where(AttendanceEntry.session_id==session.id,AttendanceEntry.student_user_id==student.id))
        status=entry.status if entry else "UNMARKED"
        if status=="EXCUSED": excused+=1
        elif status!="UNMARKED":
            counted+=1
            if status in {"PRESENT","LATE"}: attended+=1
        attendance.append({"session_id":session.id,"title":session.title,"starts_at":session.starts_at,"room":session.room,"status":status})

    results=db.scalars(select(ExamResult).where(
        ExamResult.tenant_id==user.tenant_id,
        ExamResult.student_user_id==student.id,
        ExamResult.published==True,
    ).order_by(ExamResult.id.desc())).all()
    result_rows=[]
    for result in results:
        exam=db.get(AcademicWork,result.work_id)
        if exam: result_rows.append({"exam_id":exam.id,"title":exam.title,"marks":result.marks,"percentage":result.percentage,"grade":result.grade,"grade_point":result.grade_point,"result_status":result.result_status})

    audit(db,user,"ACADEMIC_VIEW",f"student:{student.id}","parent_link_verified"); db.commit()
    return {"student":{"id":student.id,"name":student.name,"email":student.email},"attendance":{"percentage":round(attended*100/counted,1) if counted else None,"attended":attended,"counted_sessions":counted,"excused":excused,"sessions":attendance},"homework":homework,"results":result_rows}

def _latest_location(db:Session, student_id:int, tenant_id:int):
    return db.scalar(
        select(StudentLocation)
        .where(
            StudentLocation.student_user_id==student_id,
            StudentLocation.tenant_id==tenant_id,
        )
        .order_by(desc(StudentLocation.recorded_at),desc(StudentLocation.id))
        .limit(1)
    )

@app.post("/api/v1/location/update")
def update_location(
    payload:LocationUpdate,
    user:User=Depends(require_roles("Student")),
    db:Session=Depends(get_db),
):
    allowed_contexts={"TRANSPORT","SCHOOL_HOURS","FIELD_TRIP","SOS"}
    if payload.tracking_context not in allowed_contexts:
        raise HTTPException(400,"Tracking context is not allowed")
    row=StudentLocation(
        student_user_id=user.id,
        tenant_id=user.tenant_id,
        campus_id=user.campus_id,
        **payload.model_dump(),
    )
    db.add(row)
    audit(db,user,"LOCATION_UPDATE","student_location",payload.tracking_context)
    db.commit(); db.refresh(row)
    return {
        "id":row.id,"recorded_at":row.recorded_at,"status":row.status,
        "tracking_context":row.tracking_context
    }

@app.get("/api/v1/location/me")
def my_location(
    user:User=Depends(require_roles("Student")),
    db:Session=Depends(get_db),
):
    row=_latest_location(db,user.id,user.tenant_id)
    if not row:
        return {"available":False}
    return {
        "available":True,"student_id":user.id,"name":user.name,
        "latitude":row.latitude,"longitude":row.longitude,"accuracy":row.accuracy,
        "source":row.source,"tracking_context":row.tracking_context,"status":row.status,
        "recorded_at":row.recorded_at,
    }

@app.get("/api/v1/parents/children/{student_id}/location")
def parent_child_location(
    student_id:int,
    user:User=Depends(require_roles("Parent / Guardian")),
    db:Session=Depends(get_db),
):
    link=db.scalar(select(ParentStudentLink).where(
        ParentStudentLink.parent_user_id==user.id,
        ParentStudentLink.student_user_id==student_id,
        ParentStudentLink.tenant_id==user.tenant_id,
    ))
    if not link:
        raise HTTPException(403,"This student is not linked to your account")
    student=db.get(User,student_id)
    row=_latest_location(db,student_id,user.tenant_id)
    audit(db,user,"LOCATION_VIEW",f"student:{student_id}","parent_link_verified")
    db.commit()
    if not row:
        return {"available":False,"student_id":student_id,"name":student.name if student else "Student"}
    return {
        "available":True,"student_id":student_id,"name":student.name if student else "Student",
        "latitude":row.latitude,"longitude":row.longitude,"accuracy":row.accuracy,
        "source":row.source,"tracking_context":row.tracking_context,"status":row.status,
        "recorded_at":row.recorded_at,
        "bus":{"route":"Route A1","vehicle":"GAINT BUS 12","eta_minutes":12}
    }

@app.get("/api/v1/admin/live-locations")
def live_locations(
    user:User=Depends(require_roles("Institution Admin","Campus Admin")),
    db:Session=Depends(get_db),
):
    students=db.scalars(select(User).where(
        User.tenant_id==user.tenant_id,
        User.role=="Student",
    )).all()
    result=[]
    for student in students:
        if user.role=="Campus Admin" and student.campus_id!=user.campus_id:
            continue
        row=_latest_location(db,student.id,user.tenant_id)
        if row:
            result.append({
                "student_id":student.id,"name":student.name,
                "latitude":row.latitude,"longitude":row.longitude,
                "status":row.status,"tracking_context":row.tracking_context,
                "recorded_at":row.recorded_at,
            })
    audit(db,user,"LOCATION_MONITOR_VIEW","live_locations",f"count={len(result)}")
    db.commit()
    return result

@app.post("/api/v1/sos")
def create_sos(
    payload:SosIn,
    user:User=Depends(require_roles("Student")),
    db:Session=Depends(get_db),
):
    event=SosEvent(
        student_user_id=user.id,tenant_id=user.tenant_id,
        latitude=payload.latitude,longitude=payload.longitude,
        message=payload.message,status="OPEN",
    )
    db.add(event)
    db.add(StudentLocation(
        student_user_id=user.id,tenant_id=user.tenant_id,campus_id=user.campus_id,
        latitude=payload.latitude,longitude=payload.longitude,accuracy=0,
        source="SOS",tracking_context="SOS",status="EMERGENCY",
    ))
    audit(db,user,"SOS_CREATE","sos",payload.message)
    db.commit(); db.refresh(event)
    return {"id":event.id,"status":event.status}

@app.get("/api/v1/audit")
def audits(
    user:User=Depends(require_roles("Institution Admin","Campus Admin","Auditor")),
    db:Session=Depends(get_db),
):
    rows=db.scalars(
        select(Audit)
        .where(Audit.tenant_id==user.tenant_id)
        .order_by(Audit.id.desc()).limit(200)
    ).all()
    return [
        {"id":a.id,"actor":a.actor,"action":a.action,"resource":a.resource,
         "details":a.details,"created_at":a.created_at}
        for a in rows
    ]

@app.post("/api/v1/module-actions/{action}")
def module_action(
    action: str,
    payload: dict,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    page = str(payload.get("page", "")).strip()
    if not page:
        raise HTTPException(400, "page is required")
    allowed_actions = {
        "approve",
        "pay",
        "message",
        "create_grievance",
        "request_leave",
        "export",
        "manage_users",
    }
    if action not in allowed_actions:
        raise HTTPException(400, "Unsupported module action")
    if not can(user.role, page, action):
        raise HTTPException(403, "You do not have permission for this action")
    details = str(payload.get("details", "")).strip()
    audit(db, user, action.upper(), page, details)
    db.commit()
    return {
        "ok": True,
        "page": page,
        "action": action,
        "message": f"{action.replace('_', ' ').title()} action accepted.",
    }

@app.post("/api/v1/ai/chat")
def ai_chat(payload:AIChatRequest,user:User=Depends(current_user)):
    return {
        "answer":"AI provider adapter is ready. Connect the approved production model/provider and filter retrieved institutional context by role and tenant.",
        "question":payload.message,
        "requires_provider":True,
        "role":user.role,
        "tenant_id":user.tenant_id,
    }
