from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RecordIn(BaseModel):
    module: str
    name: str
    code: str = ""
    category: str = "General"
    status: str = "Active"
    notes: str = ""

class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float = Field(default=0, ge=0)
    source: str = "MOBILE"
    tracking_context: str = "TRANSPORT"
    status: str = "ACTIVE"

class SosIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    message: str = ""

class AIChatRequest(BaseModel):
    message: str


class InstitutionIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    institution_type: str
    code: str = Field(min_length=2, max_length=50)


class AcademicUnitIn(BaseModel):
    unit_type: str
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=1, max_length=60)
    parent_id: Optional[int] = None
    campus_id: int = 1
    status: str = "Active"


class AcademicAssignmentIn(BaseModel):
    user_id: int
    unit_id: int
    assignment_type: str
    status: str = "Active"


class AcademicActivityIn(BaseModel):
    module: str
    unit_id: int
    name: str = Field(min_length=2, max_length=180)
    code: str = ""
    category: str = "General"
    status: str = "Active"
    notes: str = ""


class AcademicWorkIn(BaseModel):
    unit_id: int
    work_type: str
    title: str = Field(min_length=2, max_length=180)
    description: str = ""
    max_marks: float = Field(default=0, ge=0)
    due_at: Optional[str] = None

class SubmissionIn(BaseModel):
    submission_text: str = Field(min_length=1)

class GradeIn(BaseModel):
    marks: float = Field(ge=0)
    grade: str = ""
    feedback: str = ""


class ClassSessionIn(BaseModel):
    unit_id: int
    title: str = Field(min_length=2, max_length=180)
    starts_at: str
    ends_at: str
    room: str = ""

class AttendanceMarkIn(BaseModel):
    student_user_id: int
    status: str
    note: str = ""


class GradeRuleIn(BaseModel):
    name: str
    min_percentage: float = Field(ge=0, le=100)
    max_percentage: float = Field(ge=0, le=100)
    grade: str
    grade_point: Optional[float] = None
    result_status: str = "PASS"

class ExamResultIn(BaseModel):
    student_user_id: int
    marks: float = Field(ge=0)
    remarks: str = ""


class FeeLedgerIn(BaseModel):
    student_user_id: int
    fee_code: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=2, max_length=180)
    amount_due: float = Field(gt=0)
    due_at: Optional[str] = None

class FeeConcessionIn(BaseModel):
    ledger_id: int = Field(ge=1)
    amount: float = Field(gt=0)
    reason: str = Field(min_length=2, max_length=1000)

class FeeRefundIn(BaseModel):
    payment_id: int = Field(ge=1)
    amount: float = Field(gt=0)
    reason: str = Field(min_length=2, max_length=1000)
    reference: str = Field(default="", max_length=100)

class FinanceReconciliationIn(BaseModel):
    reconciliation_date: str
    bank_amount: float = Field(ge=0)
    reference: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=1000)

class FeePaymentIn(BaseModel):
    amount: float = Field(gt=0)
    reference: str = Field(default="", max_length=100)


class UserAdminUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    role: Optional[str] = None
    campus_id: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None


class UserAdminCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=8, max_length=128)
    role: str
    campus_id: int = Field(default=1, ge=1)


class ParentStudentLinkIn(BaseModel):
    parent_user_id: int
    student_user_id: int
    relationship: str = Field(default="Guardian", min_length=2, max_length=40)


class StudentEnrollmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=8, max_length=128)
    campus_id: int = Field(default=1, ge=1)
    program_unit_id: int
    section_unit_id: Optional[int] = None
    course_unit_ids: list[int] = Field(default_factory=list)
    parent_user_id: Optional[int] = None
    relationship: str = Field(default="Guardian", min_length=2, max_length=40)


class StudentEnrollmentUpdate(BaseModel):
    section_unit_id: Optional[int] = None
    status: Optional[str] = None


class StudentAdminUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(default=None, min_length=5, max_length=180)
    campus_id: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None


class StudentAcademicManagementIn(BaseModel):
    section_unit_id: Optional[int] = None
    course_unit_ids: Optional[list[int]] = None

class StudentGuardianManagementIn(BaseModel):
    parent_user_id: int
    relationship: str = Field(default="Guardian", min_length=2, max_length=40)


class GrievanceIn(BaseModel):
    category: str = "General"
    subject: str
    details: str
    priority: str = "Normal"


class ParentStudentLeaveIn(BaseModel):
    student_user_id: int
    leave_type: str = Field(default="Casual", min_length=2, max_length=60)
    start_date: str
    end_date: str
    reason: str = Field(min_length=2)

class TeacherNoteIn(BaseModel):
    student_user_id: int
    unit_id: Optional[int] = None
    subject: str = Field(min_length=2, max_length=180)
    note: str = Field(min_length=1)
    visibility: str = "PRIVATE"


class TeacherMessageIn(BaseModel):
    recipient_user_id: int
    student_user_id: Optional[int] = None
    subject: str = Field(min_length=2, max_length=180)
    body: str = Field(min_length=1)


class TeacherLeaveIn(BaseModel):
    leave_type: str = Field(default="Casual", min_length=2, max_length=60)
    start_date: str
    end_date: str
    reason: str = Field(min_length=2)
