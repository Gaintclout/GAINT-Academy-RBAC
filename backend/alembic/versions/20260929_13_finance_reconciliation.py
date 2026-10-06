"""add finance reconciliations
Revision ID: 20260929_13
Revises: 20260929_12
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_13"
down_revision="20260929_12"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("finance_reconciliations",
      sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False,index=True),
      sa.Column("reconciliation_date",sa.DateTime(),nullable=False,index=True),sa.Column("expected_amount",sa.Numeric(12,2),nullable=False),
      sa.Column("bank_amount",sa.Numeric(12,2),nullable=False),sa.Column("difference",sa.Numeric(12,2),nullable=False),
      sa.Column("reference",sa.String(100),nullable=False,server_default=""),sa.Column("notes",sa.Text(),nullable=False,server_default=""),
      sa.Column("status",sa.String(30),nullable=False),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
      sa.Column("created_at",sa.DateTime(),nullable=False))
def downgrade(): op.drop_table("finance_reconciliations")
