import datetime

from pydantic import BaseModel , Field
import uuid 
from decimal import Decimal


class TransferRequest(BaseModel):
    idempotency_key: str
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount: Decimal = Field(gt=Decimal(0))
    description: str | None = None


class TransferResponse(BaseModel):
    id: uuid.UUID
    idempotency_key: str | None = None
    description: str | None = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}