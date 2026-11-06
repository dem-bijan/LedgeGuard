from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from decimal import Decimal
import datetime
from sqlalchemy import UUID, ForeignKey, Numeric, func , DateTime
class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    name: Mapped[str]
    currency: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


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