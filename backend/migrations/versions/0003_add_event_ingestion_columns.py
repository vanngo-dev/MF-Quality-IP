"""Add event ingestion columns.

Revision ID: 0003_ingestion
Revises: 0002_workflows
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_ingestion"
down_revision: str | None = "0002_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("production_events", sa.Column("event_id", sa.String(length=36), nullable=True))
    op.add_column(
        "production_events",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(op.f("ix_production_events_event_id"), "production_events", ["event_id"], unique=True)

    op.add_column("sensor_readings", sa.Column("event_id", sa.String(length=36), nullable=True))
    op.add_column("sensor_readings", sa.Column("station_id", sa.Integer(), nullable=True))
    op.add_column(
        "sensor_readings",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(op.f("ix_sensor_readings_event_id"), "sensor_readings", ["event_id"], unique=True)
    op.create_index(op.f("ix_sensor_readings_station_id"), "sensor_readings", ["station_id"], unique=False)
    op.create_foreign_key(
        "fk_sensor_readings_station_id_stations",
        "sensor_readings",
        "stations",
        ["station_id"],
        ["id"],
    )

    op.add_column("defects", sa.Column("event_id", sa.String(length=36), nullable=True))
    op.add_column(
        "defects",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(op.f("ix_defects_event_id"), "defects", ["event_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_defects_event_id"), table_name="defects")
    op.drop_column("defects", "created_at")
    op.drop_column("defects", "event_id")

    op.drop_constraint("fk_sensor_readings_station_id_stations", "sensor_readings", type_="foreignkey")
    op.drop_index(op.f("ix_sensor_readings_station_id"), table_name="sensor_readings")
    op.drop_index(op.f("ix_sensor_readings_event_id"), table_name="sensor_readings")
    op.drop_column("sensor_readings", "created_at")
    op.drop_column("sensor_readings", "station_id")
    op.drop_column("sensor_readings", "event_id")

    op.drop_index(op.f("ix_production_events_event_id"), table_name="production_events")
    op.drop_column("production_events", "created_at")
    op.drop_column("production_events", "event_id")
