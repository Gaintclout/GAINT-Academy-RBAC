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
