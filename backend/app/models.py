import datetime as dt
from sqlalchemy import String, Text, DateTime, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)

class Institution(Base):
    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    institution_type: Mapped[str] = mapped_column(String(30), default="UNIVERSITY", index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(80), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    tenant_id: Mapped[int] = mapped_column(default=1, index=True)
    campus_id: Mapped[int] = mapped_column(default=1, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class ParentStudentLink(Base):
    __tablename__ = "parent_student_links"
    __table_args__ = (UniqueConstraint("parent_user_id","student_user_id", name="uq_parent_student"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    relationship: Mapped[str] = mapped_column(String(40), default="Guardian")
    tenant_id: Mapped[int] = mapped_column(index=True)

class Record(Base):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    campus_id: Mapped[int] = mapped_column(default=1, index=True)
    module: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    code: Mapped[str] = mapped_column(String(80), default="")
    category: Mapped[str] = mapped_column(String(80), default="General")
    status: Mapped[str] = mapped_column(String(30), default="Active")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class StudentLocation(Base):
    __tablename__ = "student_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    campus_id: Mapped[int] = mapped_column(default=1, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[float] = mapped_column(Float, default=0)
    source: Mapped[str] = mapped_column(String(30), default="MOBILE")
    tracking_context: Mapped[str] = mapped_column(String(40), default="TRANSPORT")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    recorded_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)

class SosEvent(Base):
    __tablename__ = "sos_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class Audit(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    actor: Mapped[str] = mapped_column(String(180))
    action: Mapped[str] = mapped_column(String(120))
    resource: Mapped[str] = mapped_column(String(180))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class AcademicUnit(Base):
    __tablename__ = "academic_units"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    campus_id: Mapped[int] = mapped_column(default=1, index=True)
    unit_type: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(180))
    code: Mapped[str] = mapped_column(String(60))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("academic_units.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Active")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class AcademicAssignment(Base):
    __tablename__ = "academic_assignments"
    __table_args__ = (UniqueConstraint("tenant_id","user_id","unit_id","assignment_type", name="uq_academic_assignment"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("academic_units.id"), index=True)
    assignment_type: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(30), default="Active")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class AcademicWork(Base):
    __tablename__ = "academic_work"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("academic_units.id"), index=True)
    teacher_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    work_type: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    max_marks: Mapped[float] = mapped_column(Float, default=0)
    due_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PUBLISHED")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class StudentAcademicWork(Base):
    __tablename__ = "student_academic_work"
    __table_args__ = (UniqueConstraint("work_id","student_user_id", name="uq_student_academic_work"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("academic_work.id"), index=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    submission_text: Mapped[str] = mapped_column(Text, default="")
    submitted_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    grade: Mapped[str] = mapped_column(String(20), default="")
    feedback: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="PENDING")


class ClassSession(Base):
    __tablename__ = "class_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("academic_units.id"), index=True)
    teacher_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    starts_at: Mapped[dt.datetime] = mapped_column(DateTime, index=True)
    ends_at: Mapped[dt.datetime] = mapped_column(DateTime)
    room: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

class AttendanceEntry(Base):
    __tablename__ = "attendance_entries"
    __table_args__ = (UniqueConstraint("session_id","student_user_id", name="uq_session_student_attendance"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("class_sessions.id"), index=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT")
    note: Mapped[str] = mapped_column(Text, default="")
    marked_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    marked_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)
