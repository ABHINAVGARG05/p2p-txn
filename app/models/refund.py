from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Enum as SAEnum, String
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class RefundStatus(str, enum.Enum):
    pending = "PENDING"
    processed = "PROCESSED"
    failed = "FAILED"

class Refund(Base):
    id = Column(Integer, primary_key=True, index=True)
    original_transaction_id = Column(Integer, ForeignKey("transaction.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    status = Column(SAEnum(RefundStatus), default=RefundStatus.pending, nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    original_transaction = relationship("Transaction")
