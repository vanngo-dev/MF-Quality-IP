from typing import Any

from app.search.indexer import ALERT_INDEX, DEFECT_INDEX, EVENT_INDEX, INVESTIGATION_INDEX
from app.search.schemas import GroupedSearchResults, SearchResult

SEARCH_FIELDS = [
    "vin^5",
    "station_code^4",
    "equipment_code^4",
    "defect_code^4",
    "alert_code^4",
    "title^3",
    "description^3",
    "summary^3",
    "root_cause_hypothesis^3",
    "event_type^2",
    "status",
    "severity",
    "payload_json.*",
    "evidence_json.*",
]


class SearchService:
    def __init__(self, client: Any) -> None:
        self.client = client

    def search_all(self, query: str, limit: int = 10) -> GroupedSearchResults:
        return GroupedSearchResults(
            defects=self.search_defects(query, limit),
            alerts=self.search_alerts(query, limit),
            investigations=self.search_investigations(query, limit),
            events=self.search_events(query, limit),
        )

    def search_defects(self, query: str, limit: int = 10) -> list[SearchResult]:
        return self._search_index(DEFECT_INDEX, query, limit)

    def search_alerts(self, query: str, limit: int = 10) -> list[SearchResult]:
        return self._search_index(ALERT_INDEX, query, limit)

    def search_investigations(self, query: str, limit: int = 10) -> list[SearchResult]:
        return self._search_index(INVESTIGATION_INDEX, query, limit)

    def search_events(self, query: str, limit: int = 10) -> list[SearchResult]:
        return self._search_index(EVENT_INDEX, query, limit)

    def _search_index(self, index_name: str, query: str, limit: int) -> list[SearchResult]:
        try:
            response = self.client.search(
                index=index_name,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": SEARCH_FIELDS,
                        "lenient": True,
                    },
                },
                size=limit,
            )
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                return []
            raise

        hits = response.get("hits", {}).get("hits", [])
        return [self._result_from_hit(hit) for hit in hits]

    def _result_from_hit(self, hit: dict[str, Any]) -> SearchResult:
        source = hit.get("_source", {})
        document_type = source.get("type") or _type_from_index(hit.get("_index", ""))
        title = _result_title(source, document_type)

        return SearchResult(
            id=str(source.get("id", hit.get("_id", ""))),
            type=str(document_type),
            title=title,
            summary=_result_summary(source, document_type),
            score=hit.get("_score"),
            source=source,
        )


def _type_from_index(index_name: str) -> str:
    if index_name == DEFECT_INDEX:
        return "defect"
    if index_name == ALERT_INDEX:
        return "alert"
    if index_name == INVESTIGATION_INDEX:
        return "investigation"
    if index_name == EVENT_INDEX:
        return "event"

    return "unknown"


def _result_title(source: dict[str, Any], document_type: str) -> str:
    if document_type == "defect":
        return str(source.get("defect_code") or "Defect")
    if document_type == "alert":
        return str(source.get("title") or source.get("alert_code") or "Alert")
    if document_type == "investigation":
        return str(source.get("title") or "Investigation")
    if document_type == "event":
        return str(source.get("event_type") or source.get("event_id") or "Event")

    return str(source.get("title") or source.get("id") or "Search result")


def _result_summary(source: dict[str, Any], document_type: str) -> str | None:
    if document_type in {"defect", "alert"}:
        return _string_or_none(source.get("description"))
    if document_type == "investigation":
        return _string_or_none(source.get("summary") or source.get("root_cause_hypothesis"))
    if document_type == "event":
        return _string_or_none(source.get("station_code") or source.get("event_id"))

    return _string_or_none(source.get("summary"))


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None

