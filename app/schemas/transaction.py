from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, Any
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    amount: Decimal
    type: TransactionType

class TransactionOut(TransactionBase):
    id: int
    status: TransactionStatus
    from_wallet_id: int | None = None
    to_wallet_id: int | None = None
    reference: str | None = None
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionList(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    size: int
