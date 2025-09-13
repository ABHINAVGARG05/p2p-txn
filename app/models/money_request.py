from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class MoneyRequestStatus(str, enum.Enum):
    pending = "PENDING"
    approved = "APPROVED"
    rejected = "REJECTED"

class MoneyRequest(Base):
    id = Column(Integer, primary_key=True, index=True)
    requester_wallet_id = Column(Integer, ForeignKey("wallet.id", ondelete="CASCADE"), nullable=False, index=True)
    target_wallet_id = Column(Integer, ForeignKey("wallet.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    status = Column(SAEnum(MoneyRequestStatus), default=MoneyRequestStatus.pending, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    requester_wallet = relationship("Wallet", foreign_keys=[requester_wallet_id], backref="requests_sent")
    target_wallet = relationship("Wallet", foreign_keys=[target_wallet_id], backref="requests_received")
