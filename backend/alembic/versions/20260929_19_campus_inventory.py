"""add campus inventory
Revision ID: 20260929_19
Revises: 20260929_18
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_19";down_revision="20260929_18";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("campus_inventory_items",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("campus_id",sa.Integer(),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("category",sa.String(80),nullable=False),sa.Column("item_code",sa.String(60),nullable=False,server_default=""),sa.Column("quantity",sa.Integer(),nullable=False),sa.Column("minimum_quantity",sa.Integer(),nullable=False),sa.Column("location",sa.String(120),nullable=False,server_default=""),sa.Column("status",sa.String(30),nullable=False),sa.Column("notes",sa.Text(),nullable=False,server_default=""),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_campus_inventory_items_tenant_id","campus_inventory_items",["tenant_id"]);op.create_index("ix_campus_inventory_items_campus_id","campus_inventory_items",["campus_id"]);op.create_index("ix_campus_inventory_items_category","campus_inventory_items",["category"])
def downgrade(): op.drop_table("campus_inventory_items")
