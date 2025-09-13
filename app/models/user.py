from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions_sent = relationship("Transaction", foreign_keys='Transaction.from_wallet_id', back_populates="from_wallet")
    transactions_received = relationship("Transaction", foreign_keys='Transaction.to_wallet_id', back_populates="to_wallet")
    requests_made = relationship("MoneyRequest", foreign_keys='MoneyRequest.requester_wallet_id', back_populates="requester_wallet")
    requests_received = relationship("MoneyRequest", foreign_keys='MoneyRequest.target_wallet_id', back_populates="target_wallet")
