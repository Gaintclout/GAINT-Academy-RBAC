"""add library catalog and loans

Revision ID: 20260929_04
Revises: 20260929_03
"""
from alembic import op
import sqlalchemy as sa

revision = "20260929_04"
down_revision = "20260929_03"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("library_books",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False),
        sa.Column("accession_no",sa.String(80),nullable=False),
        sa.Column("isbn",sa.String(30),nullable=True),
        sa.Column("title",sa.String(200),nullable=False),
        sa.Column("author",sa.String(160),nullable=False),
        sa.Column("category",sa.String(100),nullable=False),
        sa.Column("status",sa.String(30),nullable=False),
        sa.UniqueConstraint("tenant_id","accession_no",name="uq_library_book_accession"))
    op.create_index("ix_library_books_tenant_id","library_books",["tenant_id"])
    op.create_index("ix_library_books_campus_id","library_books",["campus_id"])
    op.create_table("library_loans",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False),
        sa.Column("book_id",sa.Integer(),sa.ForeignKey("library_books.id"),nullable=False),
        sa.Column("borrower_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("issued_at",sa.DateTime(),nullable=False),
        sa.Column("due_at",sa.DateTime(),nullable=False),
        sa.Column("returned_at",sa.DateTime(),nullable=True),
        sa.Column("fine_amount",sa.Numeric(12,2),nullable=False),
        sa.Column("status",sa.String(30),nullable=False))
    for col in ("tenant_id","campus_id","book_id","borrower_user_id"):
        op.create_index("ix_library_loans_"+col,"library_loans",[col])

def downgrade():
    op.drop_table("library_loans")
    op.drop_table("library_books")
