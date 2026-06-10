from fastapi.testclient import TestClient


def _ids(client: TestClient) -> tuple[int, int, int]:
    vehicle_id = client.get("/api/v1/vehicles").json()[0]["id"]
    station_id = client.get("/api/v1/stations").json()[0]["id"]
    equipment_id = client.get("/api/v1/equipment").json()[0]["id"]

    return vehicle_id, station_id, equipment_id


def _defect_payload(client: TestClient, **overrides: object) -> dict[str, object]:
    vehicle_id, station_id, equipment_id = _ids(client)
    payload: dict[str, object] = {
        "defect_code": "TORQUE_LOW",
        "vehicle_id": vehicle_id,
        "station_id": station_id,
        "equipment_id": equipment_id,
        "severity": "high",
        "description": "Torque value below acceptable threshold",
        "status": "open",
    }
    payload.update(overrides)

    return payload


def _alert_payload(client: TestClient, **overrides: object) -> dict[str, object]:
    _, station_id, equipment_id = _ids(client)
    payload: dict[str, object] = {
        "alert_code": "REPEATED_DEFECT_STATION",
        "station_id": station_id,
        "equipment_id": equipment_id,
        "severity": "high",
        "title": "Repeated defects detected",
        "description": "Multiple torque defects detected at the same station",
        "evidence_json": {"defect_count": 5, "window_minutes": 30},
        "status": "open",
    }
    payload.update(overrides)

    return payload


def _create_alert(client: TestClient) -> dict[str, object]:
    response = client.post("/api/v1/alerts", json=_alert_payload(client))

    assert response.status_code == 201
    return response.json()


def _investigation_payload(client: TestClient, **overrides: object) -> dict[str, object]:
    alert = _create_alert(client)
    payload: dict[str, object] = {
        "alert_id": alert["id"],
        "title": "Investigate repeated torque defects",
        "summary": "Initial investigation created from quality alert",
        "root_cause_hypothesis": "Torque tool may be drifting out of calibration",
        "evidence_json": {"source": "manual_test"},
        "status": "draft",
    }
    payload.update(overrides)

    return payload


def test_create_defect_success(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client))

    assert response.status_code == 201
    body = response.json()
    assert body["defect_code"] == "TORQUE_LOW"
    assert body["severity"] == "high"
    assert body["status"] == "open"


def test_create_defect_with_invalid_vehicle_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client, vehicle_id=99999))

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_create_defect_with_invalid_station_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client, station_id=99999))

    assert response.status_code == 404
    assert response.json()["detail"] == "Station not found"


def test_create_defect_with_invalid_severity_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client, severity="urgent"))

    assert response.status_code == 422


def test_list_defects_returns_created_defects(seeded_client: TestClient) -> None:
    seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client))

    response = seeded_client.get("/api/v1/defects")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_defect_by_id_returns_expected_defect(seeded_client: TestClient) -> None:
    created = seeded_client.post("/api/v1/defects", json=_defect_payload(seeded_client)).json()

    response = seeded_client.get(f"/api/v1/defects/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_create_alert_success(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/alerts", json=_alert_payload(seeded_client))

    assert response.status_code == 201
    body = response.json()
    assert body["alert_code"] == "REPEATED_DEFECT_STATION"
    assert body["severity"] == "high"
    assert body["evidence_json"]["defect_count"] == 5


def test_create_alert_with_invalid_station_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/alerts", json=_alert_payload(seeded_client, station_id=99999))

    assert response.status_code == 404
    assert response.json()["detail"] == "Station not found"


def test_create_alert_with_invalid_severity_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/alerts", json=_alert_payload(seeded_client, severity="low"))

    assert response.status_code == 422


def test_list_alerts_returns_created_alerts(seeded_client: TestClient) -> None:
    _create_alert(seeded_client)

    response = seeded_client.get("/api/v1/alerts")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_alert_by_id_returns_expected_alert(seeded_client: TestClient) -> None:
    created = _create_alert(seeded_client)

    response = seeded_client.get(f"/api/v1/alerts/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_alert_status_success(seeded_client: TestClient) -> None:
    created = _create_alert(seeded_client)

    response = seeded_client.patch(f"/api/v1/alerts/{created['id']}/status", json={"status": "acknowledged"})

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_update_alert_with_invalid_status_fails(seeded_client: TestClient) -> None:
    created = _create_alert(seeded_client)

    response = seeded_client.patch(f"/api/v1/alerts/{created['id']}/status", json={"status": "closed"})

    assert response.status_code == 422


def test_create_investigation_success(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/investigations", json=_investigation_payload(seeded_client))

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Investigate repeated torque defects"
    assert body["status"] == "draft"


def test_create_investigation_with_invalid_alert_fails(seeded_client: TestClient) -> None:
    response = seeded_client.post(
        "/api/v1/investigations",
        json=_investigation_payload(seeded_client, alert_id=99999),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


def test_list_investigations_returns_created_investigations(seeded_client: TestClient) -> None:
    seeded_client.post("/api/v1/investigations", json=_investigation_payload(seeded_client))

    response = seeded_client.get("/api/v1/investigations")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_investigation_by_id_returns_expected_investigation(seeded_client: TestClient) -> None:
    created = seeded_client.post("/api/v1/investigations", json=_investigation_payload(seeded_client)).json()

    response = seeded_client.get(f"/api/v1/investigations/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_investigation_success(seeded_client: TestClient) -> None:
    created = seeded_client.post("/api/v1/investigations", json=_investigation_payload(seeded_client)).json()

    response = seeded_client.patch(
        f"/api/v1/investigations/{created['id']}",
        json={"status": "active", "summary": "Engineering review is underway"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert response.json()["summary"] == "Engineering review is underway"


def test_update_investigation_with_invalid_status_fails(seeded_client: TestClient) -> None:
    created = seeded_client.post("/api/v1/investigations", json=_investigation_payload(seeded_client)).json()

    response = seeded_client.patch(f"/api/v1/investigations/{created['id']}", json={"status": "closed"})

    assert response.status_code == 422
