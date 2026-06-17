from app.search.indexer import ALERT_INDEX, DEFECT_INDEX
from app.search.service import SearchService


def test_search_service_returns_matching_defect_result():
    client = FakeSearchClient(
        {
            DEFECT_INDEX: [
                {
                    "_index": DEFECT_INDEX,
                    "_id": "1",
                    "_score": 3.5,
                    "_source": {
                        "id": 1,
                        "type": "defect",
                        "defect_code": "TORQUE_LOW",
                        "description": "Torque value below threshold",
                    },
                }
            ]
        }
    )

    results = SearchService(client).search_defects("torque")

    assert results[0].id == "1"
    assert results[0].type == "defect"
    assert results[0].title == "TORQUE_LOW"
    assert results[0].summary == "Torque value below threshold"
    assert client.calls[0]["query"]["multi_match"]["query"] == "torque"


def test_search_service_returns_grouped_results():
    client = FakeSearchClient(
        {
            DEFECT_INDEX: [
                {
                    "_index": DEFECT_INDEX,
                    "_id": "1",
                    "_source": {"id": 1, "type": "defect", "defect_code": "TORQUE_LOW"},
                }
            ],
            ALERT_INDEX: [
                {
                    "_index": ALERT_INDEX,
                    "_id": "2",
                    "_source": {"id": 2, "type": "alert", "title": "Repeated torque defects"},
                }
            ],
        }
    )

    grouped = SearchService(client).search_all("torque")

    assert grouped.defects[0].title == "TORQUE_LOW"
    assert grouped.alerts[0].title == "Repeated torque defects"
    assert grouped.investigations == []
    assert grouped.events == []


def test_search_service_returns_empty_list_when_index_is_missing():
    client = MissingIndexSearchClient()

    results = SearchService(client).search_defects("torque")

    assert results == []


class FakeSearchClient:
    def __init__(self, hits_by_index: dict[str, list[dict[str, object]]]) -> None:
        self.hits_by_index = hits_by_index
        self.calls: list[dict[str, object]] = []

    def search(self, index: str, query: dict[str, object], size: int) -> dict[str, object]:
        self.calls.append({"index": index, "query": query, "size": size})
        return {"hits": {"hits": self.hits_by_index.get(index, [])}}


class MissingIndexSearchClient:
    def search(self, index: str, query: dict[str, object], size: int) -> dict[str, object]:
        raise MissingIndexError()


class MissingIndexError(Exception):
    status_code = 404

