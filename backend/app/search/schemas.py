from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: str
    type: str
    title: str
    summary: str | None = None
    score: float | None = None
    source: dict[str, Any] = Field(default_factory=dict)


class GroupedSearchResults(BaseModel):
    defects: list[SearchResult] = Field(default_factory=list)
    alerts: list[SearchResult] = Field(default_factory=list)
    investigations: list[SearchResult] = Field(default_factory=list)
    events: list[SearchResult] = Field(default_factory=list)


class GroupedSearchResponse(BaseModel):
    query: str
    results: GroupedSearchResults


class SearchCollectionResponse(BaseModel):
    query: str
    results: list[SearchResult]

