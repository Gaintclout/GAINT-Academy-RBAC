from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, SessionLocal, get_db
from .models import User, Institution, AcademicUnit, Record, ParentStudentLink, StudentLocation, SosEvent, Audit
from .schemas import LoginRequest, RecordIn, LocationUpdate, SosIn, AIChatRequest, InstitutionIn, AcademicUnitIn
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
