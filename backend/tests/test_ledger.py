"""
Milestone 2 test: the double-entry invariant actually holds.

A balanced set of ledger entries (including a multi-way split, not just a
simple two-account transfer) must succeed and be queryable afterward.
An unbalanced set must be rejected, and must leave zero trace in the
database — not a partial write.
"""

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from app.ledger import create_transaction
from app.models import LedgerEntry, Transaction


def test_balanced_two_way_transfer_succeeds(db_session, make_account):
    alice = make_account("Alice")
    bob = make_account("Bob")
    db_session.commit()

    txn = create_transaction(
        db_session,
        "Alice pays Bob",
        [(alice.id, Decimal("-50.00")), (bob.id, Decimal("50.00"))],
    )

    entries = db_session.scalars(
        select(LedgerEntry).where(LedgerEntry.transaction_id == txn.id)
    ).all()

    assert len(entries) == 2
    assert sum(e.amount for e in entries) == Decimal("0.00")


def test_balanced_three_way_split_succeeds(db_session, make_account):
    """Proves the schema actually generalizes past 2 parties, per the
    fee-split example from the design discussion — not just a coincidence
    that 2-account transfers happen to work."""
    alice = make_account("Alice")
    bob = make_account("Bob")
    bank_fees = make_account("BankFees")
    db_session.commit()

    txn = create_transaction(
        db_session,
        "Alice pays Bob, bank takes a fee",
        [
            (alice.id, Decimal("-52.00")),
            (bob.id, Decimal("50.00")),
            (bank_fees.id, Decimal("2.00")),
        ],
    )

    entries = db_session.scalars(
        select(LedgerEntry).where(LedgerEntry.transaction_id == txn.id)
    ).all()

    assert len(entries) == 3
    assert sum(e.amount for e in entries) == Decimal("0.00")


def test_unbalanced_transaction_is_rejected_with_no_trace(db_session, make_account):
    alice = make_account("Alice")
    bob = make_account("Bob")
    db_session.commit()

    with pytest.raises(ValueError):
        create_transaction(
            db_session,
            "Broken transfer",
            [(alice.id, Decimal("-50.00")), (bob.id, Decimal("40.00"))],
        )

    # Not just "it raised" — confirm nothing partial got written.
    assert db_session.scalars(select(Transaction)).all() == []
    assert db_session.scalars(select(LedgerEntry)).all() == []


def test_db_trigger_blocks_unbalanced_entry_bypassing_create_transaction(db_session, make_account):
    """create_transaction()'s Python check only protects callers who use it.
    This proves the invariant is also enforced by Postgres itself, for any
    code path that writes to ledger_entries directly."""
    alice = make_account("Alice")
    db_session.commit()

    txn = Transaction(description="Direct bypass attempt")
    db_session.add(txn)
    db_session.flush()

    bad_entry = LedgerEntry(transaction_id=txn.id, account_id=alice.id, amount=Decimal("999.00"))
    db_session.add(bad_entry)

    with pytest.raises(DatabaseError):
        db_session.commit()
