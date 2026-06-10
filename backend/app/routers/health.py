from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service="manufacturing-quality-api",
        environment=settings.environment,
        dependencies={
            "postgres": "configured",
            "redpanda": "configured",
            "elasticsearch": "configured",
            "ai_provider": settings.ai_provider,
        },
    )
