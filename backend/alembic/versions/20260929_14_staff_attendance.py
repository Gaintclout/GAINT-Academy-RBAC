"""add staff attendance
Revision ID: 20260929_14
Revises: 20260929_13
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_14"
down_revision="20260929_13"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("staff_attendance",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("staff_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("attendance_date",sa.DateTime(),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("note",sa.Text(),nullable=False,server_default=""),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False),sa.UniqueConstraint("tenant_id","staff_user_id","attendance_date",name="uq_staff_attendance_day"))
    op.create_index("ix_staff_attendance_tenant_id","staff_attendance",["tenant_id"]);op.create_index("ix_staff_attendance_staff_user_id","staff_attendance",["staff_user_id"]);op.create_index("ix_staff_attendance_attendance_date","staff_attendance",["attendance_date"])
def downgrade(): op.drop_table("staff_attendance")
