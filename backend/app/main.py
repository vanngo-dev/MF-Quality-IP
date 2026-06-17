from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import alerts, defects, domain, health, investigations, search


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="Manufacturing quality investigation and intelligence API.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(domain.router)
    app.include_router(defects.router)
    app.include_router(alerts.router)
    app.include_router(investigations.router)
    app.include_router(search.router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "manufacturing-quality-api",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
