from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class WalletBase(BaseModel):
    currency: str = Field(default="USD", min_length=3, max_length=3)

class WalletOut(WalletBase):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WalletTopUp(BaseModel):
    amount: Decimal = Field(gt=0)

class WalletWithdraw(BaseModel):
    amount: Decimal = Field(gt=0)

class WalletTransfer(BaseModel):
    to_user_id: int
    amount: Decimal = Field(gt=0)
    idempotency_key: str | None = None
