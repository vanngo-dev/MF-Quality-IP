from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Equipment, Plant, ProductionLine, Station, Vehicle


def _count(session: Session, model: type[object]) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def seed_database(session: Session) -> dict[str, int]:
    existing_plant = session.scalar(select(Plant).where(Plant.code == "PLT-DET"))

    if existing_plant is None:
        plant = Plant(
            code="PLT-DET",
            name="Detroit Quality Assembly",
            location="Detroit, MI",
        )

        line_a = ProductionLine(
            plant=plant,
            code="LINE-A",
            name="Final Assembly Line A",
            product_family="EV Sedan",
        )
        line_b = ProductionLine(
            plant=plant,
            code="LINE-B",
            name="Final Assembly Line B",
            product_family="EV SUV",
        )

        stations = [
            Station(line=line_a, code="A-BODY", name="Body Fit", sequence_order=10),
            Station(line=line_a, code="A-PAINT", name="Paint Inspection", sequence_order=20),
            Station(line=line_a, code="A-FINAL", name="Final Quality Gate", sequence_order=30),
            Station(line=line_b, code="B-BODY", name="Body Fit", sequence_order=10),
            Station(line=line_b, code="B-PAINT", name="Paint Inspection", sequence_order=20),
            Station(line=line_b, code="B-FINAL", name="Final Quality Gate", sequence_order=30),
        ]

        equipment = [
            Equipment(station=stations[0], asset_tag="EQ-A-ROBOT-01", name="Body Weld Robot A1", equipment_type="robot"),
            Equipment(station=stations[0], asset_tag="EQ-A-TORQUE-02", name="Door Torque Tool A2", equipment_type="torque_tool"),
            Equipment(station=stations[1], asset_tag="EQ-A-VISION-03", name="Paint Vision Camera A3", equipment_type="vision_system"),
            Equipment(station=stations[2], asset_tag="EQ-A-SCAN-04", name="Final Scan Station A4", equipment_type="scanner"),
            Equipment(station=stations[3], asset_tag="EQ-B-ROBOT-01", name="Body Weld Robot B1", equipment_type="robot"),
            Equipment(station=stations[3], asset_tag="EQ-B-TORQUE-02", name="Door Torque Tool B2", equipment_type="torque_tool"),
            Equipment(station=stations[4], asset_tag="EQ-B-VISION-03", name="Paint Vision Camera B3", equipment_type="vision_system"),
            Equipment(station=stations[5], asset_tag="EQ-B-ENDTEST-04", name="End-of-Line Tester B4", equipment_type="test_stand"),
        ]

        vehicles = [
            Vehicle(
                vin=f"MQPLANT{index:010d}",
                model="Aster EV" if index <= 5 else "Summit EV",
                model_year=2026,
                color=["White", "Silver", "Blue", "Black", "Red"][index % 5],
                line=line_a if index <= 5 else line_b,
                current_station=stations[(index - 1) % len(stations)],
                build_status="in_progress" if index < 10 else "quality_hold",
            )
            for index in range(1, 11)
        ]

        session.add_all([plant, line_a, line_b, *stations, *equipment, *vehicles])
        session.commit()

    return {
        "plants": _count(session, Plant),
        "lines": _count(session, ProductionLine),
        "stations": _count(session, Station),
        "equipment": _count(session, Equipment),
        "vehicles": _count(session, Vehicle),
    }


def main() -> None:
    with SessionLocal() as session:
        summary = seed_database(session)

    print("Seed data ready:")
    for name, count in summary.items():
        print(f"- {name}: {count}")


if __name__ == "__main__":
    main()
