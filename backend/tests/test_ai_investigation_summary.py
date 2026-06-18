from fastapi.testclient import TestClient

from app.ai.providers import (
    AlertEvidence,
    DefectEvidence,
    InvestigationEvidenceContext,
    MockInvestigationSummaryProvider,
    SensorEvidence,
    get_investigation_summary_provider,
)


def _ids(client: TestClient) -> tuple[int, int, int]:
    vehicle_id = client.get("/api/v1/vehicles").json()[0]["id"]
    station_id = client.get("/api/v1/stations").json()[0]["id"]
    equipment_id = client.get("/api/v1/equipment").json()[0]["id"]

    return vehicle_id, station_id, equipment_id


def _create_alert(client: TestClient, **overrides: object) -> dict[str, object]:
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
    response = client.post("/api/v1/alerts", json=payload)

    assert response.status_code == 201
    return response.json()


def _create_defect(client: TestClient) -> dict[str, object]:
    vehicle_id, station_id, equipment_id = _ids(client)
    response = client.post(
        "/api/v1/defects",
        json={
            "defect_code": "TORQUE_LOW",
            "vehicle_id": vehicle_id,
            "station_id": station_id,
            "equipment_id": equipment_id,
            "severity": "high",
            "description": "Torque value below acceptable threshold",
            "status": "open",
        },
    )

    assert response.status_code == 201
    return response.json()


def _create_investigation_from_alert(client: TestClient, alert_id: int) -> dict[str, object]:
    response = client.post(
        f"/api/v1/alerts/{alert_id}/investigation",
        json={
            "title": "Investigate repeated torque defects",
            "summary": "Initial investigation opened from quality alert.",
            "root_cause_hypothesis": "Torque tool may be drifting out of calibration.",
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_mock_provider_returns_structured_summary() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Investigate torque defects",
            summary="Initial notes",
            root_cause_hypothesis="Possible calibration drift",
            evidence_json={},
            alert=AlertEvidence(
                alert_code="REPEATED_DEFECT_STATION",
                title="Repeated defects detected",
                description="Multiple defects",
                severity="high",
                evidence_json={"defect_count": 5},
                station_code="ST-TORQUE",
                equipment_code="EQ-TQ-01",
            ),
            defects=[
                DefectEvidence(
                    defect_code="TORQUE_LOW",
                    description="Torque below threshold",
                    severity="high",
                    status="open",
                )
            ],
        )
    )

    assert summary.likely_issue
    assert summary.evidence
    assert summary.recommended_next_checks
    assert summary.limitations
    assert summary.confidence in {"low", "medium"}


def test_mock_provider_uses_alert_evidence() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Investigate alert",
            summary=None,
            root_cause_hypothesis=None,
            evidence_json={},
            alert=AlertEvidence(
                alert_code="REPEATED_DEFECT_STATION",
                title="Repeated defects detected",
                description="Multiple defects",
                severity="high",
                evidence_json={"defect_count": 5, "window_minutes": 30},
                station_code="ST-TORQUE",
                equipment_code=None,
            ),
        )
    )

    assert any("REPEATED_DEFECT_STATION" in item for item in summary.evidence)
    assert any("defect_count" in item for item in summary.evidence)


def test_mock_provider_uses_defect_evidence() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Investigate torque",
            summary=None,
            root_cause_hypothesis=None,
            evidence_json={},
            defects=[
                DefectEvidence(
                    defect_code="TORQUE_OUT_OF_SPEC",
                    description="Torque out of spec",
                    severity="high",
                    status="open",
                )
            ],
        )
    )

    assert "torque" in summary.likely_issue.lower()
    assert any("TORQUE_OUT_OF_SPEC" in item for item in summary.evidence)


def test_mock_provider_uses_sensor_evidence() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Investigate torque sensor",
            summary=None,
            root_cause_hypothesis=None,
            evidence_json={},
            sensor_readings=[SensorEvidence(metric_name="torque_nm", value=48.2, unit="Nm")],
        )
    )

    assert any("torque_nm" in item for item in summary.evidence)
    assert any("calibration" in item.lower() for item in summary.recommended_next_checks)


def test_missing_evidence_returns_limitations_and_low_confidence() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Thin investigation",
            summary=None,
            root_cause_hypothesis=None,
            evidence_json={},
        )
    )

    assert summary.confidence == "low"
    assert summary.limitations
    assert any("No linked alert" in item for item in summary.limitations)
    assert "Insufficient evidence" in summary.likely_issue


def test_summary_does_not_invent_root_cause_with_minimal_evidence() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Minimal investigation",
            summary=None,
            root_cause_hypothesis=None,
            evidence_json={},
        )
    )

    assert summary.confidence == "low"
    assert "calibration drift" not in summary.likely_issue.lower()
    assert "confirmed root cause" not in summary.likely_issue.lower()


def test_summary_confidence_is_medium_when_multiple_evidence_sources_agree() -> None:
    summary = MockInvestigationSummaryProvider().generate(
        InvestigationEvidenceContext(
            title="Torque investigation",
            summary="Initial notes",
            root_cause_hypothesis="Possible process drift",
            evidence_json={},
            alert=AlertEvidence(
                alert_code="REPEATED_DEFECT_STATION",
                title="Repeated defects detected",
                description="Repeated torque defects",
                severity="high",
                evidence_json={"defect_count": 5},
                station_code="ST-TORQUE",
                equipment_code="EQ-TQ-01",
            ),
            defects=[
                DefectEvidence(
                    defect_code="TORQUE_LOW",
                    description="Torque below threshold",
                    severity="high",
                    status="open",
                )
            ],
            sensor_readings=[SensorEvidence(metric_name="torque_nm", value=48.2, unit="Nm")],
        )
    )

    assert summary.confidence == "medium"


def test_default_provider_is_mock_and_requires_no_external_network() -> None:
    assert isinstance(get_investigation_summary_provider(), MockInvestigationSummaryProvider)


def test_generate_ai_summary_endpoint_succeeds(seeded_client: TestClient) -> None:
    _create_defect(seeded_client)
    alert = _create_alert(seeded_client)
    investigation = _create_investigation_from_alert(seeded_client, int(alert["id"]))

    response = seeded_client.post(f"/api/v1/investigations/{investigation['id']}/ai-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["investigation_id"] == investigation["id"]
    assert body["ai_summary"]["likely_issue"]
    assert body["ai_summary"]["limitations"]


def test_generate_ai_summary_missing_investigation_returns_404(seeded_client: TestClient) -> None:
    response = seeded_client.post("/api/v1/investigations/99999/ai-summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Investigation not found"


def test_ai_summary_is_saved_to_investigation(seeded_client: TestClient) -> None:
    alert = _create_alert(seeded_client)
    investigation = _create_investigation_from_alert(seeded_client, int(alert["id"]))

    response = seeded_client.post(f"/api/v1/investigations/{investigation['id']}/ai-summary")
    detail_response = seeded_client.get(f"/api/v1/investigations/{investigation['id']}")

    assert response.status_code == 200
    assert detail_response.status_code == 200
    assert detail_response.json()["ai_summary"]["likely_issue"] == response.json()["ai_summary"]["likely_issue"]


def test_investigation_updated_at_changes_after_summary_generation(seeded_client: TestClient) -> None:
    alert = _create_alert(seeded_client)
    investigation = _create_investigation_from_alert(seeded_client, int(alert["id"]))

    response = seeded_client.post(f"/api/v1/investigations/{investigation['id']}/ai-summary")
    detail_response = seeded_client.get(f"/api/v1/investigations/{investigation['id']}")

    assert response.status_code == 200
    assert detail_response.json()["updated_at"] != investigation["updated_at"]
