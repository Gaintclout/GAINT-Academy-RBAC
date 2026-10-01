"""add teacher notes

Revision ID: 20260929_07
Revises: 20260929_06
"""
from alembic import op
import sqlalchemy as sa

revision = "20260929_07"
down_revision = "20260929_06"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "teacher_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("teacher_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("academic_units.id"), nullable=True),
        sa.Column("subject", sa.String(length=180), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("visibility", sa.String(length=30), nullable=False, server_default="PRIVATE"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_teacher_notes_tenant_id","teacher_notes",["tenant_id"])
    op.create_index("ix_teacher_notes_teacher_user_id","teacher_notes",["teacher_user_id"])
    op.create_index("ix_teacher_notes_student_user_id","teacher_notes",["student_user_id"])
    op.create_index("ix_teacher_notes_unit_id","teacher_notes",["unit_id"])

def downgrade():
    op.drop_table("teacher_notes")
