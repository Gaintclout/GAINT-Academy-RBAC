"""add recruitment candidates
Revision ID: 20260929_16
Revises: 20260929_15
"""
from alembic import op
import sqlalchemy as sa
revision="20260929_16";down_revision="20260929_15";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("recruitment_candidates",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.Integer(),nullable=False),sa.Column("name",sa.String(120),nullable=False),sa.Column("email",sa.String(180),nullable=False),sa.Column("phone",sa.String(40),nullable=False,server_default=""),sa.Column("position",sa.String(120),nullable=False),sa.Column("stage",sa.String(40),nullable=False),sa.Column("source",sa.String(80),nullable=False,server_default=""),sa.Column("notes",sa.Text(),nullable=False,server_default=""),sa.Column("recorded_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    for col in ["tenant_id","name","email","position","stage"]: op.create_index("ix_recruitment_candidates_"+col,"recruitment_candidates",[col])
def downgrade(): op.drop_table("recruitment_candidates")
