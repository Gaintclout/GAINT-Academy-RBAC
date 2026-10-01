"""add grievances

Revision ID: 20260929_06
Revises: 20260929_05
"""
from alembic import op
import sqlalchemy as sa

revision="20260929_06"
down_revision="20260929_05"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("grievances",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False),
        sa.Column("created_by_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("ticket_no",sa.String(40),nullable=False),
        sa.Column("category",sa.String(80),nullable=False),
        sa.Column("subject",sa.String(180),nullable=False),
        sa.Column("details",sa.Text(),nullable=False),
        sa.Column("priority",sa.String(20),nullable=False),
        sa.Column("status",sa.String(30),nullable=False),
        sa.Column("latest_update",sa.Text(),nullable=False),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False),
        sa.UniqueConstraint("tenant_id","ticket_no",name="uq_grievance_ticket"))
    op.create_index("ix_grievances_tenant_id","grievances",["tenant_id"])
    op.create_index("ix_grievances_campus_id","grievances",["campus_id"])
    op.create_index("ix_grievances_created_by_user_id","grievances",["created_by_user_id"])

def downgrade():
    op.drop_table("grievances")
