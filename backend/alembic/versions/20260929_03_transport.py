"""add transport domain tables

Revision ID: 20260929_03
Revises: 20260928_02
"""
from alembic import op
import sqlalchemy as sa

revision = "20260929_03"
down_revision = "20260928_02"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("transport_routes",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False), sa.Column("name",sa.String(120),nullable=False),
        sa.Column("code",sa.String(50),nullable=False), sa.Column("status",sa.String(30),nullable=False))
    op.create_index("ix_transport_routes_tenant_id","transport_routes",["tenant_id"])
    op.create_index("ix_transport_routes_campus_id","transport_routes",["campus_id"])
    op.create_table("transport_vehicles",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False), sa.Column("vehicle_number",sa.String(60),nullable=False),
        sa.Column("label",sa.String(120),nullable=False), sa.Column("status",sa.String(30),nullable=False))
    op.create_index("ix_transport_vehicles_tenant_id","transport_vehicles",["tenant_id"])
    op.create_index("ix_transport_vehicles_campus_id","transport_vehicles",["campus_id"])
    op.create_table("transport_stops",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("route_id",sa.Integer(),sa.ForeignKey("transport_routes.id"),nullable=False),
        sa.Column("name",sa.String(120),nullable=False), sa.Column("stop_order",sa.Integer(),nullable=False))
    op.create_index("ix_transport_stops_tenant_id","transport_stops",["tenant_id"])
    op.create_index("ix_transport_stops_route_id","transport_stops",["route_id"])
    op.create_table("student_transport_allocations",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("tenant_id",sa.Integer(),nullable=False),
        sa.Column("campus_id",sa.Integer(),nullable=False),
        sa.Column("student_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("route_id",sa.Integer(),sa.ForeignKey("transport_routes.id"),nullable=False),
        sa.Column("vehicle_id",sa.Integer(),sa.ForeignKey("transport_vehicles.id"),nullable=True),
        sa.Column("stop_id",sa.Integer(),sa.ForeignKey("transport_stops.id"),nullable=False),
        sa.Column("pickup_time",sa.String(10),nullable=False), sa.Column("drop_time",sa.String(10),nullable=False),
        sa.Column("status",sa.String(30),nullable=False), sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.UniqueConstraint("tenant_id","student_user_id",name="uq_student_transport_allocation"))
    for col in ("tenant_id","campus_id","student_user_id","route_id","vehicle_id","stop_id"):
        op.create_index("ix_student_transport_allocations_"+col,"student_transport_allocations",[col])

def downgrade():
    op.drop_table("student_transport_allocations")
    op.drop_table("transport_stops")
    op.drop_table("transport_vehicles")
    op.drop_table("transport_routes")
