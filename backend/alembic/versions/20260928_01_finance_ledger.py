"""create student fee ledger and fixed precision payments

Revision ID: 20260928_01
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260928_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind=op.get_bind()
    inspector=sa.inspect(bind)
    tables=set(inspector.get_table_names())
    if "fee_ledgers" not in tables:
        op.create_table(
            "fee_ledgers",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("tenant_id",sa.Integer(),nullable=False,index=True),
            sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False,index=True),
            sa.Column("fee_code",sa.String(60),nullable=False,index=True),
            sa.Column("title",sa.String(180),nullable=False),
            sa.Column("amount_due",sa.Numeric(12,2),nullable=False),
            sa.Column("amount_paid",sa.Numeric(12,2),nullable=False,server_default="0"),
            sa.Column("due_at",sa.DateTime(),nullable=True),
            sa.Column("status",sa.String(30),nullable=False,server_default="DUE"),
            sa.Column("created_at",sa.DateTime(),nullable=False),
            sa.UniqueConstraint("tenant_id","student_user_id","fee_code",name="uq_student_fee_code"),
        )
    else:
        cols={x["name"]:x for x in inspector.get_columns("fee_ledgers")}
        with op.batch_alter_table("fee_ledgers") as batch:
            if "amount_due" in cols: batch.alter_column("amount_due",type_=sa.Numeric(12,2),existing_nullable=False)
            if "amount_paid" in cols: batch.alter_column("amount_paid",type_=sa.Numeric(12,2),existing_nullable=False)
    inspector=sa.inspect(bind); tables=set(inspector.get_table_names())
    if "fee_payments" not in tables:
        op.create_table(
            "fee_payments",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("tenant_id",sa.Integer(),nullable=False,index=True),
            sa.Column("ledger_id",sa.Integer(),sa.ForeignKey("fee_ledgers.id"),nullable=False,index=True),
            sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False,index=True),
            sa.Column("amount",sa.Numeric(12,2),nullable=False),
            sa.Column("reference",sa.String(100),nullable=False,server_default=""),
            sa.Column("receipt_no",sa.String(80),nullable=False,unique=True,index=True),
            sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
            sa.Column("paid_at",sa.DateTime(),nullable=False),
        )
    else:
        cols={x["name"]:x for x in sa.inspect(bind).get_columns("fee_payments")}
        if "amount" in cols:
            with op.batch_alter_table("fee_payments") as batch:
                batch.alter_column("amount",type_=sa.Numeric(12,2),existing_nullable=False)

def downgrade():
    bind=op.get_bind(); tables=set(sa.inspect(bind).get_table_names())
    if "fee_payments" in tables: op.drop_table("fee_payments")
    if "fee_ledgers" in tables: op.drop_table("fee_ledgers")
