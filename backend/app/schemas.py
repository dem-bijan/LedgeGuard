import datetime

from pydantic import BaseModel , Field
import uuid 
from decimal import Decimal


class TransferRequest(BaseModel):
    idempotency_key: str
    
    from_rib: str
    to_rib: str
    amount: Decimal = Field(gt=Decimal(0))
    description: str | None = None


class TransferResponse(BaseModel):
    id: uuid.UUID
    idempotency_key: str | None = None
    description: str | None = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class AccountResponse(BaseModel):
    id: uuid.UUID
    rib: str
    label: str
    currency: str
    balance: Decimal


class RegisterRequest(BaseModel):
    full_name: str
    email: str 
    password: str = Field(min_length=8)
    role : str ="customer"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str


class RegisterResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    role: str

    model_config = {"from_attributes": True}