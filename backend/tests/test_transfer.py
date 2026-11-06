"""
Milestone 3 tests: the transfer API itself.

The concurrency test is the important one here — it's the actual reason
get_account_for_update() locks the row at all. A sequential test (call
transfer() twice, one after another) would never exercise the lock, since
there's no contention unless two transfers are genuinely in flight at once.
"""

import threading
from decimal import Decimal

import pytest

from app.ledger import (
    InsufficientFundsException,
    create_transaction,
    transfer,
)
from app.models import Account


def _account(session, name):
    account = Account(name=name, currency="MAD")
    session.add(account)
    session.flush()
    return account


def _fund(session, account, amount, key):
    """Give an account a starting balance via a seed transaction from a
    throwaway funding source account."""
    source = _account(session, f"funding-source-{key}")
    create_transaction(
        session, "seed funds", [(source.id, -amount), (account.id, amount)], idempotency_key=key
    )


def test_transfer_moves_money_and_is_idempotent_on_replay(db_session):
    alice = _account(db_session, "Alice")
    bob = _account(db_session, "Bob")
    _fund(db_session, alice, Decimal("100.00"), "seed-1")
    db_session.commit()

    txn1 = transfer(db_session, "transfer-key", alice.id, bob.id, Decimal("30.00"))
    txn2 = transfer(db_session, "transfer-key", alice.id, bob.id, Decimal("30.00"))

    assert txn1.id == txn2.id  # replay, not a second transfer
    from app.ledger import get_balance
    assert get_balance(db_session, alice.id) == Decimal("70.00")
    assert get_balance(db_session, bob.id) == Decimal("30.00")


def test_transfer_rejects_insufficient_funds(db_session):
    alice = _account(db_session, "Alice")
    bob = _account(db_session, "Bob")
    _fund(db_session, alice, Decimal("10.00"), "seed-2")
    db_session.commit()

    with pytest.raises(InsufficientFundsException):
        transfer(db_session, "transfer-key-2", alice.id, bob.id, Decimal("50.00"))


def test_concurrent_transfers_cannot_overdraw_account(db_session, db_engine):
    """Alice has exactly 100.00. Two threads each try to transfer 80.00 out
    at the same instant. At most one can succeed -- if the lock didn't
    work, both could read balance=100 before either writes, and both would
    succeed, leaving Alice at -60.00: money created from nothing."""
    from sqlalchemy.orm import Session

    alice = _account(db_session, "Alice")
    bob = _account(db_session, "Bob")
    carol = _account(db_session, "Carol")
    _fund(db_session, alice, Decimal("100.00"), "seed-3")
    db_session.commit()

    barrier = threading.Barrier(2)
    results = {}

    def attempt(name, to_account_id, key):
        session = Session(db_engine)
        try:
            barrier.wait()  # force both threads to hit the DB at the same moment
            txn = transfer(session, key, alice.id, to_account_id, Decimal("80.00"))
            results[name] = ("success", txn.id)
        except InsufficientFundsException:
            results[name] = ("rejected", None)
        finally:
            session.close()

    t1 = threading.Thread(target=attempt, args=("t1", bob.id, "race-key-1"))
    t2 = threading.Thread(target=attempt, args=("t2", carol.id, "race-key-2"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    outcomes = [results["t1"][0], results["t2"][0]]
    assert outcomes.count("success") == 1
    assert outcomes.count("rejected") == 1

    from app.ledger import get_balance
    assert get_balance(db_session, alice.id) == Decimal("20.00")
