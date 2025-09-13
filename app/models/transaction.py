from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime, Enum as SAEnum, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class TransactionType(str, enum.Enum):
    add_money = "ADD_MONEY"
    withdraw = "WITHDRAW"
    transfer = "TRANSFER"
    request_payment = "REQUEST_PAYMENT"
    refund = "REFUND"
    reversal = "REVERSAL"

class TransactionStatus(str, enum.Enum):
    pending = "PENDING"
    completed = "COMPLETED"
    failed = "FAILED"

class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SAEnum(TransactionType), nullable=False, index=True)
    status = Column(SAEnum(TransactionStatus), nullable=False, index=True, default=TransactionStatus.pending)
    amount = Column(Numeric(18, 2), nullable=False)
    from_wallet_id = Column(Integer, ForeignKey("wallet.id", ondelete="SET NULL"), nullable=True, index=True)
    to_wallet_id = Column(Integer, ForeignKey("wallet.id", ondelete="SET NULL"), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    idempotency_key = Column(String(64), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    from_wallet = relationship("Wallet", foreign_keys=[from_wallet_id], back_populates="outgoing_transactions")
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id], back_populates="incoming_transactions")

    __table_args__ = (
        Index('ix_transaction_type_status', 'type', 'status'),
        UniqueConstraint('idempotency_key', name='uq_transaction_idempotency'),
    )
