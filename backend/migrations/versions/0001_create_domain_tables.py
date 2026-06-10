"""Create manufacturing domain tables.

Revision ID: 0001_domain
Revises:
Create Date: 2026-06-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_domain"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plants_code"), "plants", ["code"], unique=True)

    op.create_table(
        "production_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("product_family", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_production_lines_code"), "production_lines", ["code"], unique=True)
    op.create_index(op.f("ix_production_lines_plant_id"), "production_lines", ["plant_id"], unique=False)

    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("line_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["line_id"], ["production_lines.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("line_id", "code", name="uq_station_line_code"),
    )
    op.create_index(op.f("ix_stations_code"), "stations", ["code"], unique=False)
    op.create_index(op.f("ix_stations_line_id"), "stations", ["line_id"], unique=False)

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("asset_tag", sa.String(length=60), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("equipment_type", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_equipment_asset_tag"), "equipment", ["asset_tag"], unique=True)
    op.create_index(op.f("ix_equipment_station_id"), "equipment", ["station_id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vin", sa.String(length=17), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("model_year", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=40), nullable=False),
        sa.Column("line_id", sa.Integer(), nullable=False),
        sa.Column("current_station_id", sa.Integer(), nullable=True),
        sa.Column("build_status", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["current_station_id"], ["stations.id"]),
        sa.ForeignKeyConstraint(["line_id"], ["production_lines.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicles_current_station_id"), "vehicles", ["current_station_id"], unique=False)
    op.create_index(op.f("ix_vehicles_line_id"), "vehicles", ["line_id"], unique=False)
    op.create_index(op.f("ix_vehicles_vin"), "vehicles", ["vin"], unique=True)

    op.create_table(
        "production_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_production_events_event_type"), "production_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_production_events_occurred_at"), "production_events", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_production_events_station_id"), "production_events", ["station_id"], unique=False)
    op.create_index(op.f("ix_production_events_vehicle_id"), "production_events", ["vehicle_id"], unique=False)

    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("metric_name", sa.String(length=80), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sensor_readings_equipment_id"), "sensor_readings", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_sensor_readings_metric_name"), "sensor_readings", ["metric_name"], unique=False)
    op.create_index(op.f("ix_sensor_readings_recorded_at"), "sensor_readings", ["recorded_at"], unique=False)

    op.create_table(
        "defects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_defects_detected_at"), "defects", ["detected_at"], unique=False)
    op.create_index(op.f("ix_defects_severity"), "defects", ["severity"], unique=False)
    op.create_index(op.f("ix_defects_station_id"), "defects", ["station_id"], unique=False)
    op.create_index(op.f("ix_defects_status"), "defects", ["status"], unique=False)
    op.create_index(op.f("ix_defects_vehicle_id"), "defects", ["vehicle_id"], unique=False)

    op.create_table(
        "quality_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("defect_id", sa.Integer(), nullable=False),
        sa.Column("alert_code", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["defect_id"], ["defects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quality_alerts_alert_code"), "quality_alerts", ["alert_code"], unique=False)
    op.create_index(op.f("ix_quality_alerts_created_at"), "quality_alerts", ["created_at"], unique=False)
    op.create_index(op.f("ix_quality_alerts_defect_id"), "quality_alerts", ["defect_id"], unique=False)
    op.create_index(op.f("ix_quality_alerts_status"), "quality_alerts", ["status"], unique=False)

    op.create_table(
        "investigations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("defect_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["defect_id"], ["defects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_investigations_closed_at"), "investigations", ["closed_at"], unique=False)
    op.create_index(op.f("ix_investigations_defect_id"), "investigations", ["defect_id"], unique=False)
    op.create_index(op.f("ix_investigations_opened_at"), "investigations", ["opened_at"], unique=False)
    op.create_index(op.f("ix_investigations_status"), "investigations", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_investigations_status"), table_name="investigations")
    op.drop_index(op.f("ix_investigations_opened_at"), table_name="investigations")
    op.drop_index(op.f("ix_investigations_defect_id"), table_name="investigations")
    op.drop_index(op.f("ix_investigations_closed_at"), table_name="investigations")
    op.drop_table("investigations")

    op.drop_index(op.f("ix_quality_alerts_status"), table_name="quality_alerts")
    op.drop_index(op.f("ix_quality_alerts_defect_id"), table_name="quality_alerts")
    op.drop_index(op.f("ix_quality_alerts_created_at"), table_name="quality_alerts")
    op.drop_index(op.f("ix_quality_alerts_alert_code"), table_name="quality_alerts")
    op.drop_table("quality_alerts")

    op.drop_index(op.f("ix_defects_vehicle_id"), table_name="defects")
    op.drop_index(op.f("ix_defects_status"), table_name="defects")
    op.drop_index(op.f("ix_defects_station_id"), table_name="defects")
    op.drop_index(op.f("ix_defects_severity"), table_name="defects")
    op.drop_index(op.f("ix_defects_detected_at"), table_name="defects")
    op.drop_table("defects")

    op.drop_index(op.f("ix_sensor_readings_recorded_at"), table_name="sensor_readings")
    op.drop_index(op.f("ix_sensor_readings_metric_name"), table_name="sensor_readings")
    op.drop_index(op.f("ix_sensor_readings_equipment_id"), table_name="sensor_readings")
    op.drop_table("sensor_readings")

    op.drop_index(op.f("ix_production_events_vehicle_id"), table_name="production_events")
    op.drop_index(op.f("ix_production_events_station_id"), table_name="production_events")
    op.drop_index(op.f("ix_production_events_occurred_at"), table_name="production_events")
    op.drop_index(op.f("ix_production_events_event_type"), table_name="production_events")
    op.drop_table("production_events")

    op.drop_index(op.f("ix_vehicles_vin"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_line_id"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_current_station_id"), table_name="vehicles")
    op.drop_table("vehicles")

    op.drop_index(op.f("ix_equipment_station_id"), table_name="equipment")
    op.drop_index(op.f("ix_equipment_asset_tag"), table_name="equipment")
    op.drop_table("equipment")

    op.drop_index(op.f("ix_stations_line_id"), table_name="stations")
    op.drop_index(op.f("ix_stations_code"), table_name="stations")
    op.drop_table("stations")

    op.drop_index(op.f("ix_production_lines_plant_id"), table_name="production_lines")
    op.drop_index(op.f("ix_production_lines_code"), table_name="production_lines")
    op.drop_table("production_lines")

    op.drop_index(op.f("ix_plants_code"), table_name="plants")
    op.drop_table("plants")
