from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "manufacturing-quality-api",
        "environment": "local",
        "dependencies": {
            "postgres": "configured",
            "redpanda": "configured",
            "elasticsearch": "configured",
            "ai_provider": "mock",
        },
    }


def test_root_points_to_operational_endpoints() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["health"] == "/health"
    assert response.json()["docs"] == "/docs"
