from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


def make_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_settings().database_url
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args

        if ":memory:" in url:
            engine_kwargs["poolclass"] = StaticPool

    return create_engine(url, **engine_kwargs)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
