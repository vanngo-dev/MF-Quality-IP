"""Update quality workflow tables.

Revision ID: 0002_workflows
Revises: 0001_domain
Create Date: 2026-06-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_workflows"
down_revision: str | None = "0001_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("defects", sa.Column("defect_code", sa.String(length=80), nullable=False))
    op.add_column("defects", sa.Column("equipment_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_defects_defect_code"), "defects", ["defect_code"], unique=False)
    op.create_index(op.f("ix_defects_equipment_id"), "defects", ["equipment_id"], unique=False)
    op.create_foreign_key("fk_defects_equipment_id_equipment", "defects", "equipment", ["equipment_id"], ["id"])

    op.drop_index(op.f("ix_quality_alerts_defect_id"), table_name="quality_alerts")
    op.drop_constraint("quality_alerts_defect_id_fkey", "quality_alerts", type_="foreignkey")
    op.drop_column("quality_alerts", "defect_id")
    op.drop_column("quality_alerts", "message")
    op.add_column("quality_alerts", sa.Column("station_id", sa.Integer(), nullable=False))
    op.add_column("quality_alerts", sa.Column("equipment_id", sa.Integer(), nullable=True))
    op.add_column("quality_alerts", sa.Column("severity", sa.String(length=40), nullable=False))
    op.add_column("quality_alerts", sa.Column("title", sa.String(length=160), nullable=False))
    op.add_column("quality_alerts", sa.Column("description", sa.Text(), nullable=False))
    op.add_column("quality_alerts", sa.Column("evidence_json", sa.JSON(), nullable=False))
    op.create_index(op.f("ix_quality_alerts_equipment_id"), "quality_alerts", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_quality_alerts_severity"), "quality_alerts", ["severity"], unique=False)
    op.create_index(op.f("ix_quality_alerts_station_id"), "quality_alerts", ["station_id"], unique=False)
    op.create_foreign_key("fk_quality_alerts_station_id_stations", "quality_alerts", "stations", ["station_id"], ["id"])
    op.create_foreign_key(
        "fk_quality_alerts_equipment_id_equipment",
        "quality_alerts",
        "equipment",
        ["equipment_id"],
        ["id"],
    )

    op.drop_index(op.f("ix_investigations_defect_id"), table_name="investigations")
    op.drop_constraint("investigations_defect_id_fkey", "investigations", type_="foreignkey")
    op.drop_column("investigations", "defect_id")
    op.add_column("investigations", sa.Column("alert_id", sa.Integer(), nullable=False))
    op.add_column("investigations", sa.Column("root_cause_hypothesis", sa.Text(), nullable=True))
    op.add_column("investigations", sa.Column("evidence_json", sa.JSON(), nullable=False))
    op.add_column("investigations", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index(op.f("ix_investigations_alert_id"), "investigations", ["alert_id"], unique=False)
    op.create_foreign_key(
        "fk_investigations_alert_id_quality_alerts",
        "investigations",
        "quality_alerts",
        ["alert_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_investigations_alert_id_quality_alerts", "investigations", type_="foreignkey")
    op.drop_index(op.f("ix_investigations_alert_id"), table_name="investigations")
    op.drop_column("investigations", "updated_at")
    op.drop_column("investigations", "evidence_json")
    op.drop_column("investigations", "root_cause_hypothesis")
    op.drop_column("investigations", "alert_id")
    op.add_column("investigations", sa.Column("defect_id", sa.Integer(), nullable=False))
    op.create_foreign_key("investigations_defect_id_fkey", "investigations", "defects", ["defect_id"], ["id"])
    op.create_index(op.f("ix_investigations_defect_id"), "investigations", ["defect_id"], unique=False)

    op.drop_constraint("fk_quality_alerts_equipment_id_equipment", "quality_alerts", type_="foreignkey")
    op.drop_constraint("fk_quality_alerts_station_id_stations", "quality_alerts", type_="foreignkey")
    op.drop_index(op.f("ix_quality_alerts_station_id"), table_name="quality_alerts")
    op.drop_index(op.f("ix_quality_alerts_severity"), table_name="quality_alerts")
    op.drop_index(op.f("ix_quality_alerts_equipment_id"), table_name="quality_alerts")
    op.drop_column("quality_alerts", "evidence_json")
    op.drop_column("quality_alerts", "description")
    op.drop_column("quality_alerts", "title")
    op.drop_column("quality_alerts", "severity")
    op.drop_column("quality_alerts", "equipment_id")
    op.drop_column("quality_alerts", "station_id")
    op.add_column("quality_alerts", sa.Column("message", sa.Text(), nullable=False))
    op.add_column("quality_alerts", sa.Column("defect_id", sa.Integer(), nullable=False))
    op.create_foreign_key("quality_alerts_defect_id_fkey", "quality_alerts", "defects", ["defect_id"], ["id"])
    op.create_index(op.f("ix_quality_alerts_defect_id"), "quality_alerts", ["defect_id"], unique=False)

    op.drop_constraint("fk_defects_equipment_id_equipment", "defects", type_="foreignkey")
    op.drop_index(op.f("ix_defects_equipment_id"), table_name="defects")
    op.drop_index(op.f("ix_defects_defect_code"), table_name="defects")
    op.drop_column("defects", "equipment_id")
    op.drop_column("defects", "defect_code")
