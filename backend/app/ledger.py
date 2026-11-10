
from decimal import Decimal
import uuid
from sqlalchemy import func, select
from app.models import User
from sqlalchemy.exc import NoResultFound
from app.models import Account, Transaction ,LedgerEntry ,PendingTransfer
import datetime

                                                                                    
#class PendingTransfer(Base):
#    __tablename__="pending_transfers"        
#    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
#    idempotency_key: Mapped[str | None] = mapped_column(unique=True, nullable=True)
#    from_account_id :Mapped[uuid.UUID] =  mapped_column(ForeignKey("accounts.id"),index=True )
#    to_account_id :Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"),index=True )
#    requester_id  :Mapped[uuid.UUID] =mapped_column(ForeignKey("users.id")) #Cant we detect this using get account by rib ?
#    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
#    requested_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
#    status :Mapped[str] = mapped_column(server_default="pending")
#    execute_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
#    executed_transaction_id :Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transactions.id") , index=True , nullable=True)



# class Transaction(Base):
#     __tablename__ = "transactions"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
#     idempotency_key: Mapped[str | None] = mapped_column(unique=True, nullable=True)
#     description: Mapped[str | None] 
#     created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


COOLING_OFF_PERIOD = datetime.timedelta(minutes=2) # Number of minutes set for a transaction to a new rib to take place


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

def create_pending_transfer(session , fa_id:uuid.UUID , ta_id: uuid.UUID , requester_id:uuid.UUID , amount:Decimal , description:str|None , idempotency_key:str|None=None):
    execute_at = datetime.datetime.now(datetime.timezone.utc) + COOLING_OFF_PERIOD
    pending_transfer = PendingTransfer(from_account_id=  fa_id , to_account_id = ta_id , requester_id  = requester_id, amount = amount , description =description , execute_at=execute_at,idempotency_key =idempotency_key)
    session.add(pending_transfer)
    session.commit()
    return pending_transfer

def sweeper(session, user_id :uuid.UUID):
    pending_transfers = select(PendingTransfer).where(PendingTransfer.requester_id == user_id , PendingTransfer.status =="pending" , PendingTransfer.execute_at <= datetime.datetime.now(datetime.timezone.utc)).with_for_update()
    result = session.execute(pending_transfers).scalars()
    for transfer in result:
        balance = get_balance(session,transfer.from_account_id)
        if transfer.amount > balance :
            transfer.status = "failed"
        else:
            transfer.status = "executed"
            executed_transaction = create_transaction(session,transfer.description , [(transfer.from_account_id, -transfer.amount), (transfer.to_account_id,transfer.amount)] , transfer.idempotency_key)
            transfer.executed_transaction_id = executed_transaction.id
    session.commit()

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

def has_prior_transfers(session , from_account_id , to_account_id) -> bool:
    touched_accounts_ids = select(LedgerEntry.transaction_id).where(LedgerEntry.account_id == from_account_id)
    res = session.execute(
        select(LedgerEntry.transaction_id)
               .where(LedgerEntry.account_id == to_account_id ,
                       LedgerEntry.transaction_id.in_(touched_accounts_ids))).first()        
    return res is not None

def transfer(session, idempotency_key: str , from_rib: str , to_rib: str, requester_id:uuid.UUID , amount: Decimal , description: str | None = None) -> Transaction | PendingTransfer:
    if from_rib == to_rib:
        raise ValueError("Cannot transfer to the same account")
    stmt = select(Transaction).where(Transaction.idempotency_key == idempotency_key)                        
    existing_transaction = session.execute(stmt).scalar_one_or_none()
    if existing_transaction:
        return existing_transaction
    from_account = get_account_by_rib(session, from_rib)
    if from_account.owner_id != requester_id:
                raise NotAccountOwnerException("You are not the owner of the from account") # can this be really a case ?sounds odd (avoidable by the front end)
    to_account = get_account_by_rib(session, to_rib)
    f_a = get_account_for_update(session, from_account.id)
    balance = get_balance(session, from_account.id)
    if balance < amount:
                raise InsufficientFundsException("Insufficient funds")
    if has_prior_transfers(session ,from_account.id, to_account.id):    
        return create_transaction(session, description, [(from_account.id, -amount), (to_account.id, amount)], idempotency_key)
    else:
        return create_pending_transfer(session, from_account.id ,to_account.id,from_account.owner_id,amount ,description =description ,idempotency_key =idempotency_key)

def cancel_pending_transfer(session, pending_transfer_id , current_user_id  ):
    pending_transfer = select(PendingTransfer).where(PendingTransfer.id == pending_transfer_id).with_for_update()
    result =session.execute(pending_transfer).scalar_one()
    if result.requester_id != current_user_id:
         raise NotAccountOwnerException("Cannot cancel a not owned transaction")
    if result.status == "pending" or result.status == "cancelled":
        result.status = "cancelled"
        session.commit()
    else:
        raise PendingTransferNotCancellableException("This transaction was already made !")
    return result 


def get_pending_transfers_for_user(session , user_id):
    statement = select(PendingTransfer).where(PendingTransfer.requester_id == user_id , PendingTransfer.status=="pending")
    return session.execute(statement).scalars().all()


class InsufficientFundsException(Exception):
    pass

class NotAccountOwnerException(Exception):
    pass

class AccountNotFoundException(Exception):
    pass
class PendingTransferNotCancellableException(Exception):
    pass