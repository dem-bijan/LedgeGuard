"""
Milestone 3 test: the actual HTTP-reachable /transfer endpoint, not just
the underlying transfer() function. Covers the response_model wiring and
the two exception handlers mapping business errors to HTTP status codes.
"""

from decimal import Decimal

from fastapi.testclient import TestClient

from app.ledger import create_transaction
from app.main import app
from app.models import Account

client = TestClient(app)


def _funded_account(session, name, amount, key):
    account = Account(name=name, currency="MAD")
    source = Account(name=f"source-{key}", currency="MAD")
    session.add_all([account, source])
    session.flush()
    create_transaction(
        session, "seed", [(source.id, -amount), (account.id, amount)], idempotency_key=key
    )
    session.commit()
    return account


def test_transfer_endpoint_success(db_session):
    alice = _funded_account(db_session, "Alice", Decimal("100.00"), "api-seed-1")
    bob = Account(name="Bob", currency="MAD")
    db_session.add(bob)
    db_session.commit()

    response = client.post(
        "/transfer",
        json={
            "idempotency_key": "api-key-success",
            "from_account_id": str(alice.id),
            "to_account_id": str(bob.id),
            "amount": "40.00",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["idempotency_key"] == "api-key-success"
    assert body["id"] is not None


def test_transfer_endpoint_insufficient_funds_returns_409(db_session):
    alice = _funded_account(db_session, "Alice", Decimal("10.00"), "api-seed-2")
    bob = Account(name="Bob", currency="MAD")
    db_session.add(bob)
    db_session.commit()

    response = client.post(
        "/transfer",
        json={
            "idempotency_key": "api-key-insufficient",
            "from_account_id": str(alice.id),
            "to_account_id": str(bob.id),
            "amount": "500.00",
        },
    )

    assert response.status_code == 409


def test_transfer_endpoint_rejects_non_positive_amount(db_session):
    alice = Account(name="Alice", currency="MAD")
    bob = Account(name="Bob", currency="MAD")
    db_session.add_all([alice, bob])
    db_session.commit()

    response = client.post(
        "/transfer",
        json={
            "idempotency_key": "api-key-invalid",
            "from_account_id": str(alice.id),
            "to_account_id": str(bob.id),
            "amount": "0",
        },
    )

    assert response.status_code == 422
