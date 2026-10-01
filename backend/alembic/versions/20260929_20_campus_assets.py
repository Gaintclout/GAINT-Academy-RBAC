"""add campus assets
Revision ID: 20260929_20
Revises: 20260929_19
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_20";down_revision="20260929_19";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("campus_assets",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("campus_id",sa.Integer(),nullable=False),sa.Column("asset_code",sa.String(60),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("category",sa.String(80),nullable=False),sa.Column("serial_number",sa.String(120),nullable=False,server_default=""),sa.Column("location",sa.String(120),nullable=False,server_default=""),sa.Column("assigned_to",sa.String(120),nullable=False,server_default=""),sa.Column("condition",sa.String(30),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("notes",sa.Text(),nullable=False,server_default=""),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_campus_assets_tenant_id","campus_assets",["tenant_id"]);op.create_index("ix_campus_assets_campus_id","campus_assets",["campus_id"]);op.create_index("ix_campus_assets_asset_code","campus_assets",["asset_code"]);op.create_index("ix_campus_assets_category","campus_assets",["category"])
def downgrade(): op.drop_table("campus_assets")
