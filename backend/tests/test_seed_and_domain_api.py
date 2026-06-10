from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.seed import seed_database
from app.models import Equipment, Plant, ProductionLine, Station, Vehicle


def test_seed_data_can_be_created(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        summary = seed_database(session)

        assert summary == {
            "plants": 1,
            "lines": 2,
            "stations": 6,
            "equipment": 8,
            "vehicles": 10,
        }
        assert session.scalar(select(func.count()).select_from(Vehicle)) == 10


def test_read_endpoints_return_seeded_data(seeded_client) -> None:
    plants = seeded_client.get("/api/v1/plants")
    lines = seeded_client.get("/api/v1/lines")
    stations = seeded_client.get("/api/v1/stations")
    equipment = seeded_client.get("/api/v1/equipment")
    vehicles = seeded_client.get("/api/v1/vehicles")

    assert plants.status_code == 200
    assert lines.status_code == 200
    assert stations.status_code == 200
    assert equipment.status_code == 200
    assert vehicles.status_code == 200

    assert len(plants.json()) == 1
    assert len(lines.json()) == 2
    assert len(stations.json()) == 6
    assert len(equipment.json()) == 8
    assert len(vehicles.json()) == 10

    assert plants.json()[0]["code"] == "PLT-DET"
    assert vehicles.json()[0]["vin"] == "MQPLANT0000000001"


def test_vehicle_detail_endpoint_returns_vehicle_by_vin(seeded_client) -> None:
    response = seeded_client.get("/api/v1/vehicles/MQPLANT0000000001")

    assert response.status_code == 200
    assert response.json()["vin"] == "MQPLANT0000000001"
    assert response.json()["build_status"] == "in_progress"


def test_vehicle_detail_endpoint_returns_404_for_unknown_vin(seeded_client) -> None:
    response = seeded_client.get("/api/v1/vehicles/UNKNOWNVIN000000")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_seeded_tables_contain_expected_domain_counts(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        seed_database(session)

        assert session.scalar(select(func.count()).select_from(Plant)) == 1
        assert session.scalar(select(func.count()).select_from(ProductionLine)) == 2
        assert session.scalar(select(func.count()).select_from(Station)) == 6
        assert session.scalar(select(func.count()).select_from(Equipment)) == 8
        assert session.scalar(select(func.count()).select_from(Vehicle)) == 10
