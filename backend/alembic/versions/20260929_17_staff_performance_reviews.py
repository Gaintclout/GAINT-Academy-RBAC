"""add staff performance reviews
Revision ID: 20260929_17
Revises: 20260929_16
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_17";down_revision="20260929_16";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("staff_performance_reviews",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("staff_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("review_period",sa.String(80),nullable=False),sa.Column("rating",sa.Integer(),nullable=False),sa.Column("strengths",sa.Text(),nullable=False,server_default=""),sa.Column("improvement_areas",sa.Text(),nullable=False,server_default=""),sa.Column("goals",sa.Text(),nullable=False,server_default=""),sa.Column("status",sa.String(30),nullable=False),sa.Column("reviewed_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_staff_performance_reviews_tenant_id","staff_performance_reviews",["tenant_id"]);op.create_index("ix_staff_performance_reviews_staff_user_id","staff_performance_reviews",["staff_user_id"]);op.create_index("ix_staff_performance_reviews_review_period","staff_performance_reviews",["review_period"])
def downgrade(): op.drop_table("staff_performance_reviews")
