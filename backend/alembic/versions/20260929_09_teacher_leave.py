"""add teacher leave requests

Revision ID: 20260929_09
Revises: 20260929_08
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_09"
down_revision="20260929_08"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("teacher_leave_requests",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("teacher_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("leave_type",sa.String(length=60),nullable=False,server_default="Casual"),
        sa.Column("start_date",sa.DateTime(),nullable=False),
        sa.Column("end_date",sa.DateTime(),nullable=False),
        sa.Column("reason",sa.Text(),nullable=False),
        sa.Column("status",sa.String(length=30),nullable=False,server_default="PENDING"),
        sa.Column("reviewer_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=True),
        sa.Column("reviewer_note",sa.Text(),nullable=False,server_default=""),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_teacher_leave_requests_tenant_id","teacher_leave_requests",["tenant_id"])
    op.create_index("ix_teacher_leave_requests_teacher_user_id","teacher_leave_requests",["teacher_user_id"])
def downgrade():
    op.drop_table("teacher_leave_requests")
