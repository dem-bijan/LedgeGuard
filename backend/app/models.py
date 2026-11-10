from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from decimal import Decimal
import datetime
from sqlalchemy import UUID, ForeignKey, Numeric, func , DateTime





class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[str] 
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"),index=True)
    rib: Mapped[str] = mapped_column(unique=True)
    label: Mapped[str]
    currency: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    flagged : Mapped[bool]  = mapped_column(default=False)
    flagging_reason: Mapped[str| None]
    flagged_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    idempotency_key: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    description: Mapped[str | None] 
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"),index=True)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"),index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


class PendingTransfer(Base):
    __tablename__="pending_transfers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    idempotency_key: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    from_account_id :Mapped[uuid.UUID] =  mapped_column(ForeignKey("accounts.id"),index=True )
    to_account_id :Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"),index=True )
    requester_id  :Mapped[uuid.UUID] =mapped_column(ForeignKey("users.id")) 
    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    requested_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    status :Mapped[str] = mapped_column(server_default="pending")
    description: Mapped[str|None]
    execute_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    executed_transaction_id :Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transactions.id") , index=True , nullable=True)