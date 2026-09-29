"""add fee concessions
Revision ID: 20260929_11
Revises: 20260929_10
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_11"
down_revision="20260929_10"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("fee_concessions",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False,index=True),
        sa.Column("ledger_id",sa.Integer(),sa.ForeignKey("fee_ledgers.id"),nullable=False,index=True),
        sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False,index=True),
        sa.Column("amount",sa.Numeric(12,2),nullable=False),
        sa.Column("reason",sa.Text(),nullable=False),
        sa.Column("status",sa.String(30),nullable=False,server_default="APPROVED"),
        sa.Column("approved_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("created_at",sa.DateTime(),nullable=False))
def downgrade():
    op.drop_table("fee_concessions")
