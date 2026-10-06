"""add teacher communication

Revision ID: 20260929_08
Revises: 20260929_07
"""
from alembic import op
import sqlalchemy as sa

revision="20260929_08"
down_revision="20260929_07"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("communication_messages",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("sender_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("recipient_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=True),
        sa.Column("subject",sa.String(length=180),nullable=False),
        sa.Column("body",sa.Text(),nullable=False),
        sa.Column("status",sa.String(length=30),nullable=False,server_default="SENT"),
        sa.Column("created_at",sa.DateTime(),nullable=False))
    for name in ("tenant_id","sender_user_id","recipient_user_id","student_user_id"):
        op.create_index("ix_communication_messages_"+name,"communication_messages",[name])

def downgrade():
    op.drop_table("communication_messages")
