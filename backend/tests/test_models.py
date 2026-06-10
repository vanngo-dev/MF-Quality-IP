from app.models import (
    Defect,
    Equipment,
    Investigation,
    Plant,
    ProductionEvent,
    ProductionLine,
    QualityAlert,
    SensorReading,
    Station,
    Vehicle,
)


def test_orm_models_import_correctly() -> None:
    assert Plant.__tablename__ == "plants"
    assert ProductionLine.__tablename__ == "production_lines"
    assert Station.__tablename__ == "stations"
    assert Equipment.__tablename__ == "equipment"
    assert Vehicle.__tablename__ == "vehicles"
    assert ProductionEvent.__tablename__ == "production_events"
    assert SensorReading.__tablename__ == "sensor_readings"
    assert Defect.__tablename__ == "defects"
    assert QualityAlert.__tablename__ == "quality_alerts"
    assert Investigation.__tablename__ == "investigations"
