from typing import Optional
import datetime as dt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, SessionLocal, get_db
from .models import User, Institution, AcademicUnit, AcademicAssignment, AcademicWork, StudentAcademicWork, ClassSession, AttendanceEntry, Record, ParentStudentLink, StudentLocation, SosEvent, Audit
from .schemas import LoginRequest, RecordIn, LocationUpdate, SosIn, AIChatRequest, InstitutionIn, AcademicUnitIn, AcademicAssignmentIn, AcademicActivityIn, AcademicWorkIn, SubmissionIn, GradeIn, ClassSessionIn, AttendanceMarkIn
from .security import verify_password, create_token, current_user, require_roles
from .rbac import ROLE_MENUS, dashboard_for, module_access_for, can
from .seed import seed, DEMO_PASSWORD, DEMO_USERS

Base.metadata.create_all(bind=engine)
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
    if payload.parent_id is not None:
        parent=db.get(AcademicUnit,payload.parent_id)
        if not parent or parent.tenant_id != user.tenant_id:
            raise HTTPException(400,"Invalid parent academic unit")
    row=AcademicUnit(tenant_id=user.tenant_id,campus_id=payload.campus_id,unit_type=unit_type,name=payload.name.strip(),code=payload.code.strip().upper(),parent_id=payload.parent_id,status=payload.status)
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

def _students_for_unit(db:Session,tenant_id:int,unit_id:int):
    ids=db.scalars(select(AcademicAssignment.user_id).where(AcademicAssignment.tenant_id==tenant_id,AcademicAssignment.unit_id==unit_id,AcademicAssignment.status=="Active",AcademicAssignment.assignment_type.in_(["COURSE_REGISTRATION","SECTION_ASSIGNMENT","ENROLLMENT"]))).all()
    return set(ids)

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
    start=_parse_due_at(payload.starts_at); end=_parse_due_at(payload.ends_at)
    if not start or not end or end<=start: raise HTTPException(400,"Session end time must be after start time")
    row=ClassSession(tenant_id=user.tenant_id,unit_id=payload.unit_id,teacher_user_id=user.id,title=payload.title,starts_at=start,ends_at=end,room=payload.room)
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
    sessions=db.scalars(select(ClassSession).where(ClassSession.tenant_id==user.tenant_id,ClassSession.unit_id.in_(_assigned_unit_ids(db,user))).order_by(ClassSession.starts_at.desc())).all()
    rows=[]; attended=0; counted=0
    for session in sessions:
        entry=db.scalar(select(AttendanceEntry).where(AttendanceEntry.session_id==session.id,AttendanceEntry.student_user_id==user.id))
        status=entry.status if entry else "UNMARKED"
        if status!="UNMARKED":
            counted+=1
            if status in {"PRESENT","LATE","EXCUSED"}: attended+=1
        rows.append({"session_id":session.id,"title":session.title,"starts_at":session.starts_at,"room":session.room,"status":status})
    return {"percentage":round(attended*100/counted,1) if counted else None,"attended":attended,"marked_sessions":counted,"sessions":rows}

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
