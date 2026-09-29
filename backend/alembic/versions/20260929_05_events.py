"""add academy events

Revision ID: 20260929_05
Revises: 20260929_04
"""
from alembic import op
import sqlalchemy as sa

revision="20260929_05"
down_revision="20260929_04"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("academy_events",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=True),
        sa.Column("title",sa.String(180),nullable=False),
        sa.Column("event_type",sa.String(60),nullable=False),
        sa.Column("venue",sa.String(180),nullable=False),
        sa.Column("starts_at",sa.DateTime(),nullable=False),
        sa.Column("ends_at",sa.DateTime(),nullable=False),
        sa.Column("organizer_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=True),
        sa.Column("audience_role",sa.String(60),nullable=False),
        sa.Column("registration_required",sa.Boolean(),nullable=False),
        sa.Column("registration_deadline",sa.DateTime(),nullable=True),
        sa.Column("status",sa.String(30),nullable=False))
    op.create_index("ix_academy_events_tenant_id","academy_events",["tenant_id"])
    op.create_index("ix_academy_events_campus_id","academy_events",["campus_id"])
    op.create_index("ix_academy_events_starts_at","academy_events",["starts_at"])
    op.create_table("event_registrations",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("event_id",sa.Integer(),sa.ForeignKey("academy_events.id"),nullable=False),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("status",sa.String(30),nullable=False),
        sa.Column("registered_at",sa.DateTime(),nullable=False),
        sa.UniqueConstraint("tenant_id","event_id","user_id",name="uq_event_registration_user"))
    op.create_index("ix_event_registrations_tenant_id","event_registrations",["tenant_id"])
    op.create_index("ix_event_registrations_event_id","event_registrations",["event_id"])
    op.create_index("ix_event_registrations_user_id","event_registrations",["user_id"])

def downgrade():
    op.drop_table("event_registrations")
    op.drop_table("academy_events")
