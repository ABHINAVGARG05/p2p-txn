from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Transaction, Wallet, User, Refund, TransactionStatus, RefundStatus

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self):
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_wallet_balance = self.db.query(func.coalesce(func.sum(Wallet.balance), 0)).scalar() or 0
        total_transactions = self.db.query(func.count(Transaction.id)).scalar() or 0
        failed_transactions = self.db.query(func.count(Transaction.id)).filter(Transaction.status == TransactionStatus.failed).scalar() or 0
        pending_refunds = self.db.query(func.count(Refund.id)).filter(Refund.status == RefundStatus.pending).scalar() or 0
        return {
            "total_users": total_users,
            "total_wallet_balance": float(total_wallet_balance),
            "total_transactions": total_transactions,
            "failed_transactions": failed_transactions,
            "pending_refunds": pending_refunds,
        }
