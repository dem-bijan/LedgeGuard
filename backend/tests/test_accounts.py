"""Milestone 4 test: GET /accounts — a user sees only their own accounts, with real balances."""

from decimal import Decimal

from fastapi.testclient import TestClient

from app.ledger import create_transaction
from app.main import app

client = TestClient(app)


def test_get_accounts_returns_only_own_accounts_with_balances(db_session, make_account, auth_cookies):
    alice = make_account("Alice Checking")
    source = make_account("Source")
    create_transaction(
        db_session, "seed", [(source.id, Decimal("-100.00")), (alice.id, Decimal("100.00"))],
        idempotency_key="accounts-test-seed",
    )
    db_session.commit()

    response = client.get("/accounts", cookies=auth_cookies(alice))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["rib"] == alice.rib
    assert body[0]["balance"] == "100.00"


def test_get_accounts_requires_auth(db_session):
    response = client.get("/accounts")
    assert response.status_code == 401
