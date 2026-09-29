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


def test_non_admin_cannot_modify_users():
    student=_login("student@gaintacademy.com")
    me=client.get("/api/v1/auth/me",headers=student).json()
    r=client.patch(f"/api/v1/users/{me['id']}",headers=student,json={"name":"Changed"})
    assert r.status_code==403

def test_admin_cannot_remove_own_admin_role_or_deactivate_self():
    admin=_login("admin@gaintacademy.com")
    me=client.get("/api/v1/auth/me",headers=admin).json()
    assert client.patch(f"/api/v1/users/{me['id']}",headers=admin,json={"role":"Teacher"}).status_code==409
    assert client.patch(f"/api/v1/users/{me['id']}",headers=admin,json={"is_active":False}).status_code==409

def test_admin_rejects_unsupported_role():
    admin=_login("admin@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    target=next(x for x in users if x["role"]=="Student")
    r=client.patch(f"/api/v1/users/{target['id']}",headers=admin,json={"role":"Super Admin"})
    assert r.status_code==400


def test_admin_can_create_tenant_locked_user():
    admin=_login("admin@gaintacademy.com")
    r=client.post("/api/v1/users",headers=admin,json={"name":"New Teacher","email":"new.teacher@test.local","password":"Teacher@123","role":"Teacher","campus_id":1})
    assert r.status_code==200
    assert r.json()["role"]=="Teacher"

def test_user_creation_rejects_duplicate_email_and_weak_password():
    admin=_login("admin@gaintacademy.com")
    duplicate=client.post("/api/v1/users",headers=admin,json={"name":"Duplicate","email":"student@gaintacademy.com","password":"Strong@123","role":"Student","campus_id":1})
    assert duplicate.status_code==409
    weak=client.post("/api/v1/users",headers=admin,json={"name":"Weak User","email":"weak@test.local","password":"password","role":"Student","campus_id":1})
    assert weak.status_code==400

def test_non_admin_cannot_create_user():
    teacher=_login("teacher@gaintacademy.com")
    r=client.post("/api/v1/users",headers=teacher,json={"name":"Blocked User","email":"blocked@test.local","password":"Blocked@123","role":"Student","campus_id":1})
    assert r.status_code==403


def test_admin_parent_student_link_management():
    admin=_login("admin@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    parent=next(x for x in users if x["role"]=="Parent / Guardian")
    student=next(x for x in users if x["role"]=="Student")
    existing=client.get("/api/v1/admin/parent-student-links",headers=admin)
    assert existing.status_code==200
    if not any(x["parent_user_id"]==parent["id"] and x["student_user_id"]==student["id"] for x in existing.json()):
        made=client.post("/api/v1/admin/parent-student-links",headers=admin,json={"parent_user_id":parent["id"],"student_user_id":student["id"],"relationship":"Guardian"})
        assert made.status_code==200

def test_non_admin_cannot_manage_parent_student_links():
    teacher=_login("teacher@gaintacademy.com")
    assert client.get("/api/v1/admin/parent-student-links",headers=teacher).status_code==403


def test_admissions_lifecycle_and_history():
    admin=_login("admin@gaintacademy.com")
    units=client.get("/api/v1/academic-structure",headers=admin).json()
    def ensure_unit(unit_type,name,code,parent_id=None):
        existing=next((x for x in units if x["unit_type"]==unit_type),None)
        if existing: return existing
        made=client.post("/api/v1/academic-structure",headers=admin,json={"unit_type":unit_type,"name":name,"code":code,"parent_id":parent_id,"campus_id":1,"status":"Active"})
        assert made.status_code==200, made.text
        row=made.json(); units.append(row); return row
    campus=ensure_unit("CAMPUS","CI Campus","CI-CAMP")
    faculty=ensure_unit("SCHOOL_FACULTY","CI Faculty","CI-FAC",campus["id"])
    department=ensure_unit("DEPARTMENT","CI Department","CI-DEPT",faculty["id"])
    program=ensure_unit("PROGRAM","CI Test Program","CI-PROG",department["id"])
    period=ensure_unit("ACADEMIC_PERIOD","CI Academic Period","CI-PER",program["id"])
    course=ensure_unit("COURSE","CI Test Course","CI-COURSE",period["id"])
    sections=[x for x in units if x["unit_type"]=="SECTION_BATCH"]
    if not sections:
        sections=[ensure_unit("SECTION_BATCH","CI Test Section","CI-SEC",course["id"])]
    email="admission.lifecycle@test.local"
    users=client.get("/api/v1/users",headers=admin).json()
    existing=next((x for x in users if x["email"]==email),None)
    if existing:
        student_id=existing["id"]
    else:
        r=client.post("/api/v1/admissions/enroll-student",headers=admin,json={
            "name":"Admission Lifecycle","email":email,"password":"Student@123",
            "campus_id":1,"program_unit_id":program["id"],"section_unit_id":sections[0]["id"],
            "course_unit_ids":[],"parent_user_id":None,"relationship":"Guardian"
        })
        assert r.status_code==200, r.text
        student_id=r.json()["id"]
    profile=client.get(f"/api/v1/admissions/students/{student_id}/profile",headers=admin)
    assert profile.status_code==200
    assert profile.json()["status"]=="Active"
    if len(sections)>1:
        moved=client.patch(f"/api/v1/admissions/students/{student_id}",headers=admin,json={"section_unit_id":sections[1]["id"]})
        assert moved.status_code==200
    withdrawn=client.patch(f"/api/v1/admissions/students/{student_id}",headers=admin,json={"status":"Withdrawn"})
    assert withdrawn.status_code==200
    reactivated=client.patch(f"/api/v1/admissions/students/{student_id}",headers=admin,json={"status":"Active"})
    assert reactivated.status_code==200
    history=client.get(f"/api/v1/admissions/students/{student_id}/history",headers=admin)
    assert history.status_code==200
    events={x["event_type"] for x in history.json()}
    assert "ENROLLED" in events
    assert "WITHDRAWN" in events
    assert "REACTIVATED" in events

def test_admissions_endpoints_reject_non_admin_roles():
    teacher=_login("teacher@gaintacademy.com")
    assert client.get("/api/v1/admissions/students",headers=teacher).status_code==403
    assert client.get("/api/v1/admissions/summary",headers=teacher).status_code==403
    assert client.post("/api/v1/admissions/enroll-student",headers=teacher,json={
        "name":"Blocked Student","email":"blocked.admission@test.local","password":"Student@123",
        "campus_id":1,"program_unit_id":1,"course_unit_ids":[]
    }).status_code==403

def test_admissions_guardian_link_is_reflected_in_student_list():
    admin=_login("admin@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    parent=next(x for x in users if x["role"]=="Parent / Guardian")
    student=next(x for x in users if x["role"]=="Student")
    links=client.get("/api/v1/admin/parent-student-links",headers=admin).json()
    if not any(x["parent_user_id"]==parent["id"] and x["student_user_id"]==student["id"] for x in links):
        r=client.post("/api/v1/admin/parent-student-links",headers=admin,json={
            "parent_user_id":parent["id"],"student_user_id":student["id"],"relationship":"Guardian"
        })
        assert r.status_code==200
    rows=client.get("/api/v1/admissions/students",headers=admin)
    assert rows.status_code==200
    target=next(x for x in rows.json() if x["id"]==student["id"])
    assert target["has_guardian"] is True


def test_student_management_actions_and_rbac():
    admin=_login("admin@gaintacademy.com")
    teacher=_login("teacher@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    student=next(x for x in users if x["role"]=="Student")
    parent=next(x for x in users if x["role"]=="Parent / Guardian")
    assert client.patch(f"/api/v1/admin/students/{student['id']}",headers=teacher,json={"name":"Blocked"}).status_code==403
    assert client.put(f"/api/v1/admin/students/{student['id']}/guardian",headers=teacher,json={"parent_user_id":parent["id"],"relationship":"Guardian"}).status_code==403
    changed=client.patch(f"/api/v1/admin/students/{student['id']}",headers=admin,json={"name":student["name"]})
    assert changed.status_code==200, changed.text
    linked=client.put(f"/api/v1/admin/students/{student['id']}/guardian",headers=admin,json={"parent_user_id":parent["id"],"relationship":"Guardian"})
    assert linked.status_code==200, linked.text
    profile=client.get(f"/api/v1/admissions/students/{student['id']}/profile",headers=admin)
    assert profile.status_code==200
    assert any(g["id"]==parent["id"] for g in profile.json()["guardians"])
    removed=client.delete(f"/api/v1/admin/students/{student['id']}/guardian",headers=admin)
    assert removed.status_code==200
    profile=client.get(f"/api/v1/admissions/students/{student['id']}/profile",headers=admin).json()
    assert profile["guardians"]==[]

def test_student_academic_management_validates_unit_type():
    admin=_login("admin@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    student=next(x for x in users if x["role"]=="Student")
    units=client.get("/api/v1/academic-structure",headers=admin).json()
    non_section=next((x for x in units if x["unit_type"]!="SECTION_BATCH"),None)
    if non_section:
        r=client.put(f"/api/v1/admin/students/{student['id']}/academics",headers=admin,json={"section_unit_id":non_section["id"]})
        assert r.status_code==400


def test_teacher_assignment_management_rbac_and_validation():
    admin=_login("admin@gaintacademy.com")
    student_headers=_login("student@gaintacademy.com")
    users=client.get("/api/v1/users",headers=admin).json()
    teacher=next(x for x in users if x["role"]=="Teacher")
    units=client.get("/api/v1/academic-structure",headers=admin).json()
    course=next((x for x in units if x["unit_type"]=="COURSE"),None)
    section=next((x for x in units if x["unit_type"]=="SECTION_BATCH"),None)
    program=next((x for x in units if x["unit_type"]=="PROGRAM"),None)
    if course:
        blocked=client.post("/api/v1/academic-assignments",headers=student_headers,json={"user_id":teacher["id"],"unit_id":course["id"],"assignment_type":"FACULTY_ASSIGNMENT","status":"Active"})
        assert blocked.status_code==403
        made=client.post("/api/v1/academic-assignments",headers=admin,json={"user_id":teacher["id"],"unit_id":course["id"],"assignment_type":"FACULTY_ASSIGNMENT","status":"Active"})
        assert made.status_code in (200,409), made.text
    if section:
        made=client.post("/api/v1/academic-assignments",headers=admin,json={"user_id":teacher["id"],"unit_id":section["id"],"assignment_type":"FACULTY_ASSIGNMENT","status":"Active"})
        assert made.status_code in (200,409), made.text
    if program:
        advisor=client.post("/api/v1/academic-assignments",headers=admin,json={"user_id":teacher["id"],"unit_id":program["id"],"assignment_type":"ADVISOR_ASSIGNMENT","status":"Active"})
        assert advisor.status_code in (200,409), advisor.text
    student=next(x for x in users if x["role"]=="Student")
    if course:
        invalid=client.post("/api/v1/academic-assignments",headers=admin,json={"user_id":student["id"],"unit_id":course["id"],"assignment_type":"FACULTY_ASSIGNMENT","status":"Active"})
        assert invalid.status_code==400


def test_student_profile_is_self_scoped_and_student_only():
    student_headers=_login("student@gaintacademy.com")
    teacher_headers=_login("teacher@gaintacademy.com")
    profile=client.get("/api/v1/student/profile",headers=student_headers)
    assert profile.status_code==200, profile.text
    data=profile.json()
    assert data["email"]=="student@gaintacademy.com"
    assert data["status"] in ("Active","Withdrawn")
    assert isinstance(data["academics"],list)
    assert isinstance(data["guardians"],list)
    assert client.get("/api/v1/student/profile",headers=teacher_headers).status_code==403
