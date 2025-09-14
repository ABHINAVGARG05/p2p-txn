from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import Transaction, Wallet

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int, page: int = 1, size: int = 20):
        size = min(size, 100)
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        stmt = select(Transaction).where((Transaction.from_wallet_id == wallet.id) | (Transaction.to_wallet_id == wallet.id)).order_by(Transaction.id.desc()).offset((page-1)*size).limit(size)
        items = self.db.execute(stmt).scalars().all()
        total = self.db.query(func.count(Transaction.id)).filter((Transaction.from_wallet_id == wallet.id) | (Transaction.to_wallet_id == wallet.id)).scalar() or 0
        return items, total
