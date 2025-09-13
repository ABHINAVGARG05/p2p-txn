from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Wallet(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    balance = Column(Numeric(18, 2), default=0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="wallet")
    outgoing_transactions = relationship("Transaction", foreign_keys='Transaction.from_wallet_id', back_populates="from_wallet")
    incoming_transactions = relationship("Transaction", foreign_keys='Transaction.to_wallet_id', back_populates="to_wallet")

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_wallet_user'),
    )
