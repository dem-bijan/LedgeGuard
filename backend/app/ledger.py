
from decimal import Decimal
import uuid

from app.models import Transaction ,LedgerEntry



def create_transaction(session,description: str | None, entries: list[tuple[uuid.UUID,Decimal]]) -> Transaction:
    if len(entries) < 2:
        raise ValueError("A transaction needs at least two entries to be meaningful")
    total = sum(amount for _, amount in entries)
    if total != Decimal(0):
        raise ValueError("Transaction is not balanced")
    transaction = Transaction(description=description)
    session.add(transaction)
    session.flush()  
    for  account_id, amount in entries:
        obj = LedgerEntry(transaction_id=transaction.id, account_id=account_id, amount=amount)
        session.add(obj)
    session.commit()
    return transaction