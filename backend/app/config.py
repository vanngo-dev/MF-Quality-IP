from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Manufacturing Quality Intelligence Platform"
    environment: str = "local"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg2://quality:quality@localhost:5432/quality"
    kafka_bootstrap_servers: str = "localhost:19092"
    elasticsearch_url: str = "http://localhost:9200"
    ai_provider: str = "mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
