from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models.money_request import MoneyRequestStatus
from app.models.refund import RefundStatus

class MoneyRequestCreate(BaseModel):
    target_user_id: int
    amount: Decimal = Field(gt=0)

class MoneyRequestOut(BaseModel):
    id: int
    requester_wallet_id: int
    target_wallet_id: int
    amount: Decimal
    status: MoneyRequestStatus
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True

class MoneyRequestAction(BaseModel):
    approve: bool

class RefundCreate(BaseModel):
    original_transaction_id: int
    amount: Decimal = Field(gt=0)
    reason: str | None = None

class RefundOut(BaseModel):
    id: int
    original_transaction_id: int
    amount: Decimal
    status: RefundStatus
    reason: str | None
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True
