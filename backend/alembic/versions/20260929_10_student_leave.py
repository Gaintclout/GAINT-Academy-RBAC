"""add student leave requests
Revision ID: 20260929_10
Revises: 20260929_09
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_10"
down_revision="20260929_09"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("student_leave_requests",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False,index=True),
        sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False,index=True),
        sa.Column("requested_by_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False,index=True),
        sa.Column("leave_type",sa.String(60),nullable=False,server_default="Casual"),
        sa.Column("start_date",sa.DateTime(),nullable=False),
        sa.Column("end_date",sa.DateTime(),nullable=False),
        sa.Column("reason",sa.Text(),nullable=False),
        sa.Column("status",sa.String(30),nullable=False,server_default="PENDING"),
        sa.Column("reviewer_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=True),
        sa.Column("reviewer_note",sa.Text(),nullable=False,server_default=""),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))
def downgrade():
    op.drop_table("student_leave_requests")
