from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Wallet, Transaction, TransactionType, TransactionStatus
from app.utils.idempotency import build_key, ensure_idempotent

class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_wallet(self, user_id: int) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return wallet

    def top_up(self, user_id: int, amount: Decimal) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        wallet.balance = wallet.balance + amount  # type: ignore
        txn = Transaction(type=TransactionType.add_money, status=TransactionStatus.completed, amount=amount, to_wallet_id=wallet.id)
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def withdraw(self, user_id: int, amount: Decimal) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        if wallet.balance < amount:  # type: ignore
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.balance = wallet.balance - amount  # type: ignore
        txn = Transaction(type=TransactionType.withdraw, status=TransactionStatus.completed, amount=amount, from_wallet_id=wallet.id)
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def transfer(self, from_user_id: int, to_user_id: int, amount: Decimal, idempotency_key: str | None = None) -> Wallet:
        from_wallet = self.db.query(Wallet).filter(Wallet.user_id == from_user_id).with_for_update().first()
        to_wallet = self.db.query(Wallet).filter(Wallet.user_id == to_user_id).with_for_update().first()
        if not from_wallet or not to_wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        if from_wallet.balance < amount:  # type: ignore
            raise HTTPException(status_code=400, detail="Insufficient balance")
        final_key = None
        if idempotency_key:
            final_key = build_key(from_user_id, "transfer", idempotency_key)
            ensure_idempotent(self.db, final_key)
        from_wallet.balance = from_wallet.balance - amount  # type: ignore
        to_wallet.balance = to_wallet.balance + amount  # type: ignore
        txn = Transaction(type=TransactionType.transfer, status=TransactionStatus.completed, amount=amount, from_wallet_id=from_wallet.id, to_wallet_id=to_wallet.id, idempotency_key=final_key)
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(from_wallet)
        return from_wallet
