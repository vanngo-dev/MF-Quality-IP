from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.search.client import get_elasticsearch_client
from app.search.schemas import GroupedSearchResponse, SearchCollectionResponse
from app.search.service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])


def get_search_service() -> SearchService:
    return SearchService(get_elasticsearch_client())


SearchDependency = Annotated[SearchService, Depends(get_search_service)]


@router.get("", response_model=GroupedSearchResponse)
def search_all(
    service: SearchDependency,
    q: str = Query(..., description="Search query text."),
    limit: int = Query(10, ge=1, le=50),
) -> GroupedSearchResponse:
    query = _clean_query(q)
    return GroupedSearchResponse(query=query, results=service.search_all(query, limit))


@router.get("/defects", response_model=SearchCollectionResponse)
def search_defects(
    service: SearchDependency,
    q: str = Query(..., description="Search query text."),
    limit: int = Query(10, ge=1, le=50),
) -> SearchCollectionResponse:
    query = _clean_query(q)
    return SearchCollectionResponse(query=query, results=service.search_defects(query, limit))


@router.get("/alerts", response_model=SearchCollectionResponse)
def search_alerts(
    service: SearchDependency,
    q: str = Query(..., description="Search query text."),
    limit: int = Query(10, ge=1, le=50),
) -> SearchCollectionResponse:
    query = _clean_query(q)
    return SearchCollectionResponse(query=query, results=service.search_alerts(query, limit))


@router.get("/investigations", response_model=SearchCollectionResponse)
def search_investigations(
    service: SearchDependency,
    q: str = Query(..., description="Search query text."),
    limit: int = Query(10, ge=1, le=50),
) -> SearchCollectionResponse:
    query = _clean_query(q)
    return SearchCollectionResponse(query=query, results=service.search_investigations(query, limit))


@router.get("/events", response_model=SearchCollectionResponse)
def search_events(
    service: SearchDependency,
    q: str = Query(..., description="Search query text."),
    limit: int = Query(10, ge=1, le=50),
) -> SearchCollectionResponse:
    query = _clean_query(q)
    return SearchCollectionResponse(query=query, results=service.search_events(query, limit))


def _clean_query(query: str) -> str:
    cleaned = query.strip()

    if not cleaned:
        raise HTTPException(status_code=400, detail="Search query must not be empty.")

    return cleaned

