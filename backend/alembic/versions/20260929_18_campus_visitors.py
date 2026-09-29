"""add campus visitors
Revision ID: 20260929_18
Revises: 20260929_17
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_18";down_revision="20260929_17";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("campus_visitors",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("campus_id",sa.Integer(),nullable=False),sa.Column("name",sa.String(120),nullable=False),sa.Column("phone",sa.String(40),nullable=False,server_default=""),sa.Column("purpose",sa.String(250),nullable=False),sa.Column("person_to_meet",sa.String(120),nullable=False,server_default=""),sa.Column("status",sa.String(30),nullable=False),sa.Column("checked_in_at",sa.DateTime(),nullable=False),sa.Column("checked_out_at",sa.DateTime(),nullable=True),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_index("ix_campus_visitors_tenant_id","campus_visitors",["tenant_id"]);op.create_index("ix_campus_visitors_campus_id","campus_visitors",["campus_id"]);op.create_index("ix_campus_visitors_status","campus_visitors",["status"])
def downgrade(): op.drop_table("campus_visitors")
