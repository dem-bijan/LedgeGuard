import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.models import Account, Base, User
from app.rib import generate_rib

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
    session.execute(Base.metadata.tables["users"].delete())
    session.commit()
    session.close()


@pytest.fixture
def make_account(db_session):
    """Factory fixture: call make_account("Alice") as many times as needed
    within a test. Creates a throwaway owning User + a real RIB for each
    account, since Account now requires both."""

    def _make(label: str, currency: str = "MAD") -> Account:
        owner = User(
            full_name=label,
            email=f"{uuid.uuid4().hex}@test.local",
            hashed_password="unused-in-these-tests",
            role="customer",
        )
        db_session.add(owner)
        db_session.flush()

        account = Account(label=label, currency=currency, owner_id=owner.id, rib=generate_rib())
        db_session.add(account)
        db_session.flush()
        return account

    return _make


@pytest.fixture
def auth_cookies():
    """Factory: auth_cookies(account) -> a real auth cookie dict for that
    account's owner, without needing to go through /login (which has its
    own dedicated tests already). The token now lives in an httpOnly
    cookie, not the Authorization header."""

    def _cookies(account: Account) -> dict:
        token = create_access_token({"sub": str(account.owner_id), "role": "customer"})
        return {"access_token": token}

    return _cookies
