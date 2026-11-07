"""
Milestone 3/4 test: the actual HTTP-reachable /transfer endpoint, not just
the underlying transfer() function. Covers the response_model wiring, the
exception handlers mapping business errors to HTTP status codes, and that
the endpoint is actually locked down behind auth + ownership now.
"""

from decimal import Decimal

from fastapi.testclient import TestClient

from app.ledger import create_transaction
from app.main import app

client = TestClient(app)


def _fund(session, make_account, account, amount, key):
    source = make_account(f"source-{key}")
    create_transaction(
        session, "seed", [(source.id, -amount), (account.id, amount)], idempotency_key=key
    )
    session.commit()


def test_transfer_endpoint_success(db_session, make_account, auth_cookies):
    alice = make_account("Alice")
    bob = make_account("Bob")
    _fund(db_session, make_account, alice, Decimal("100.00"), "api-seed-1")

    response = client.post(
        "/transfer",
        cookies=auth_cookies(alice),
        json={
            "idempotency_key": "api-key-success",
            "from_rib": alice.rib,
            "to_rib": bob.rib,
            "amount": "40.00",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["idempotency_key"] == "api-key-success"
    assert body["id"] is not None


def test_transfer_endpoint_insufficient_funds_returns_409(db_session, make_account, auth_cookies):
    alice = make_account("Alice")
    bob = make_account("Bob")
    _fund(db_session, make_account, alice, Decimal("10.00"), "api-seed-2")

    response = client.post(
        "/transfer",
        cookies=auth_cookies(alice),
        json={
            "idempotency_key": "api-key-insufficient",
            "from_rib": alice.rib,
            "to_rib": bob.rib,
            "amount": "500.00",
        },
    )

    assert response.status_code == 409


def test_transfer_endpoint_rejects_non_positive_amount(db_session, make_account, auth_cookies):
    alice = make_account("Alice")
    bob = make_account("Bob")
    db_session.commit()

    response = client.post(
        "/transfer",
        cookies=auth_cookies(alice),
        json={
            "idempotency_key": "api-key-invalid",
            "from_rib": alice.rib,
            "to_rib": bob.rib,
            "amount": "0",
        },
    )

    assert response.status_code == 422


def test_transfer_endpoint_requires_auth(db_session, make_account):
    alice = make_account("Alice")
    bob = make_account("Bob")
    db_session.commit()

    response = client.post(
        "/transfer",
        json={
            "idempotency_key": "api-key-no-auth",
            "from_rib": alice.rib,
            "to_rib": bob.rib,
            "amount": "10.00",
        },
    )

    assert response.status_code == 401


def test_transfer_endpoint_rejects_non_owner(db_session, make_account, auth_cookies):
    alice = make_account("Alice")
    bob = make_account("Bob")
    mallory = make_account("Mallory")
    _fund(db_session, make_account, alice, Decimal("100.00"), "api-seed-owner")

    # Mallory is logged in, but tries to move money out of Alice's account
    response = client.post(
        "/transfer",
        cookies=auth_cookies(mallory),
        json={
            "idempotency_key": "api-key-not-owner",
            "from_rib": alice.rib,
            "to_rib": bob.rib,
            "amount": "10.00",
        },
    )

    assert response.status_code == 403
