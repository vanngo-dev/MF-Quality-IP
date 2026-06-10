from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_session, make_engine
from app.db.seed import seed_database
from app.main import create_app


@pytest.fixture()
def session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        yield factory
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def seeded_client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    with session_factory() as session:
        seed_database(session)

    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client
