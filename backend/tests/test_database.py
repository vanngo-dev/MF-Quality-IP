from sqlalchemy.engine import Engine

from app.db import Base, SessionLocal, engine, make_engine, metadata


def test_database_configuration_imports_correctly() -> None:
    assert metadata is Base.metadata
    assert isinstance(engine, Engine)
    assert SessionLocal.kw["autoflush"] is False


def test_make_engine_supports_sqlite_for_tests() -> None:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")

    try:
        assert sqlite_engine.url.get_backend_name() == "sqlite"
    finally:
        sqlite_engine.dispose()
