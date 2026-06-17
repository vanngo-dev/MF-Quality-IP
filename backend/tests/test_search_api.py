from app.routers.search import get_search_service
from app.search.schemas import GroupedSearchResults, SearchResult


class FakeSearchService:
    def __init__(self, empty: bool = False) -> None:
        self.empty = empty

    def search_all(self, query: str, limit: int = 10) -> GroupedSearchResults:
        if self.empty:
            return GroupedSearchResults()

        return GroupedSearchResults(
            defects=[SearchResult(id="1", type="defect", title="TORQUE_LOW", summary="Torque below threshold")],
            alerts=[SearchResult(id="2", type="alert", title="Repeated torque defects", summary="Defect spike")],
            investigations=[
                SearchResult(id="3", type="investigation", title="Investigate torque defects", summary="Root cause")
            ],
            events=[SearchResult(id="4", type="event", title="station_exit", summary="ST-TORQUE")],
        )

    def search_defects(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [] if self.empty else [SearchResult(id="1", type="defect", title="TORQUE_LOW")]

    def search_alerts(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [] if self.empty else [SearchResult(id="2", type="alert", title="Repeated torque defects")]

    def search_investigations(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [] if self.empty else [SearchResult(id="3", type="investigation", title="Investigate torque defects")]

    def search_events(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [] if self.empty else [SearchResult(id="4", type="event", title="station_exit")]


def test_search_endpoint_rejects_empty_query(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    response = seeded_client.get("/api/v1/search?q=%20%20%20")

    assert response.status_code == 400
    assert response.json()["detail"] == "Search query must not be empty."


def test_search_endpoint_returns_grouped_response_shape(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    response = seeded_client.get("/api/v1/search?q=torque")

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "torque"
    assert set(payload["results"]) == {"defects", "alerts", "investigations", "events"}
    assert payload["results"]["defects"][0]["title"] == "TORQUE_LOW"


def test_search_defects_endpoint_returns_matching_defect(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    response = seeded_client.get("/api/v1/search/defects?q=torque")

    assert response.status_code == 200
    assert response.json()["results"][0]["type"] == "defect"


def test_search_alerts_endpoint_returns_matching_alert(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    response = seeded_client.get("/api/v1/search/alerts?q=defect")

    assert response.status_code == 200
    assert response.json()["results"][0]["title"] == "Repeated torque defects"


def test_search_investigations_endpoint_returns_matching_investigation(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService()

    response = seeded_client.get("/api/v1/search/investigations?q=root")

    assert response.status_code == 200
    assert response.json()["results"][0]["type"] == "investigation"


def test_search_no_results_returns_empty_groups(seeded_client):
    seeded_client.app.dependency_overrides[get_search_service] = lambda: FakeSearchService(empty=True)

    response = seeded_client.get("/api/v1/search?q=nonsense")

    assert response.status_code == 200
    assert response.json()["results"] == {
        "defects": [],
        "alerts": [],
        "investigations": [],
        "events": [],
    }

