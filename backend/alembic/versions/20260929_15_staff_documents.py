"""add staff documents
Revision ID: 20260929_15
Revises: 20260929_14
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_15";down_revision="20260929_14";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("staff_documents",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("staff_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("document_type",sa.String(80),nullable=False),sa.Column("title",sa.String(180),nullable=False),sa.Column("document_ref",sa.String(500),nullable=False,server_default=""),sa.Column("expiry_date",sa.DateTime(),nullable=True),sa.Column("status",sa.String(30),nullable=False),sa.Column("notes",sa.Text(),nullable=False,server_default=""),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_staff_documents_tenant_id","staff_documents",["tenant_id"]);op.create_index("ix_staff_documents_staff_user_id","staff_documents",["staff_user_id"]);op.create_index("ix_staff_documents_document_type","staff_documents",["document_type"])
def downgrade(): op.drop_table("staff_documents")
