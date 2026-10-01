"""add enrollment history

Revision ID: 20260928_02
Revises: 20260928_01
"""
from alembic import op
import sqlalchemy as sa

revision="20260928_02"
down_revision="20260928_01"
branch_labels=None
depends_on=None

def upgrade():
    if "enrollment_history" in set(sa.inspect(op.get_bind()).get_table_names()):
        return
    op.create_table(
        "enrollment_history",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("event_type",sa.String(40),nullable=False),
        sa.Column("from_unit_id",sa.Integer(),sa.ForeignKey("academic_units.id"),nullable=True),
        sa.Column("to_unit_id",sa.Integer(),sa.ForeignKey("academic_units.id"),nullable=True),
        sa.Column("details",sa.Text(),nullable=False,server_default=""),
        sa.Column("actor_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("created_at",sa.DateTime(),nullable=False),
    )
    op.create_index("ix_enrollment_history_tenant_id","enrollment_history",["tenant_id"])
    op.create_index("ix_enrollment_history_student_user_id","enrollment_history",["student_user_id"])
    op.create_index("ix_enrollment_history_event_type","enrollment_history",["event_type"])
    op.create_index("ix_enrollment_history_actor_user_id","enrollment_history",["actor_user_id"])

def downgrade():
    op.drop_table("enrollment_history")
