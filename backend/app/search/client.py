from functools import lru_cache
from typing import Any

from app.config import get_settings


@lru_cache
def get_elasticsearch_client() -> Any:
    try:
        from elasticsearch import Elasticsearch
    except ImportError as exc:
        raise RuntimeError("Install the elasticsearch package to use search features.") from exc

    return Elasticsearch(get_settings().elasticsearch_url)

