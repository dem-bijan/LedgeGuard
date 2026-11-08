
from decimal import Decimal
import uuid
from sqlalchemy import func, select
from app.models import User
from sqlalchemy.exc import NoResultFound
from app.models import Account, Transaction ,LedgerEntry


def create_transaction(session,description: str | None, entries: list[tuple[uuid.UUID,Decimal]] ,idempotency_key: str|None = None) -> Transaction:
    if len(entries) < 2:
        raise ValueError("A transaction needs at least two entries to be meaningful")
    total = sum(amount for _, amount in entries)
    if total != Decimal(0):
        raise ValueError("Transaction is not balanced")
    transaction = Transaction(description=description, idempotency_key=idempotency_key)
    session.add(transaction)
    session.flush()  
    for  account_id, amount in entries:
        obj = LedgerEntry(transaction_id=transaction.id, account_id=account_id, amount=amount)
        session.add(obj)
    session.commit()
    return transaction



def account_getter(session,user:User):
    stmt = session.query(Account).filter_by(owner_id = user.id).all()
    return stmt



def get_account_for_update(session, account_id: uuid.UUID):
    stmt = select(Account).where(Account.id == account_id).with_for_update()
    return session.execute(stmt).scalar_one()

def get_account_by_rib(session, rib:str)-> Account :
    stmt = select(Account).where(Account.rib == rib)
    try: 
        return session.execute(stmt).scalar_one()
    except NoResultFound:
        raise AccountNotFoundException(f"No account found for this RIB: {rib}")

def get_balance(session , account_id: uuid.UUID) -> Decimal:
    stmt = select(func.sum(LedgerEntry.amount)).where(LedgerEntry.account_id == account_id)
    result = session.execute(stmt).scalar()
    if result is None:
        return Decimal(0)
    else:
        return Decimal(result) 


def transfer(session, idempotency_key: str , from_rib: str , to_rib: str, requester_id:uuid.UUID , amount: Decimal , description: str | None = None) -> Transaction:
    if from_rib == to_rib:
        raise ValueError("Cannot transfer to the same account")
    stmt = select(Transaction).where(Transaction.idempotency_key == idempotency_key)
    existing_transaction = session.execute(stmt).scalar_one_or_none()
    if existing_transaction:
        return existing_transaction
    from_account = get_account_by_rib(session, from_rib)
    if from_account.owner_id != requester_id:
        raise NotAccountOwnerException("You are not the owner of the from account")
    f_a = get_account_for_update(session, from_account.id)
    to_account = get_account_by_rib(session, to_rib)
    balance = get_balance(session, from_account.id)
    if balance < amount:
        raise InsufficientFundsException("Insufficient funds")
    transaction = create_transaction(session, description, [(from_account.id, -amount), (to_account.id, amount)], idempotency_key)
    return transaction


class InsufficientFundsException(Exception):
    pass

class NotAccountOwnerException(Exception):
    pass

class AccountNotFoundException(Exception):
    pass