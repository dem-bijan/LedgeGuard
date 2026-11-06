import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

_url = (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@localhost:5432/{os.environ['POSTGRES_DB']}"
)
_engine = create_engine(_url)


@pytest.fixture
def db_engine():
    """The shared engine itself, for tests that need multiple independent
    DB connections/sessions at once (e.g. simulating real concurrency)."""
    return _engine


@pytest.fixture
def db_session():
    """A real DB session, wiped clean after each test so tests don't leak
    rows into each other (deleted in FK-safe order: children before parents)."""
    session = Session(_engine)
    yield session
    session.rollback()
    session.execute(Base.metadata.tables["ledger_entries"].delete())
    session.execute(Base.metadata.tables["transactions"].delete())
    session.execute(Base.metadata.tables["accounts"].delete())
    session.commit()
    session.close()
