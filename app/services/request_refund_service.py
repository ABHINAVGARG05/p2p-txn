from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Wallet, MoneyRequest, MoneyRequestStatus, Refund, RefundStatus, Transaction, TransactionType, TransactionStatus

class RequestRefundService:
    def __init__(self, db: Session):
        self.db = db

    def create_money_request(self, requester_user_id: int, target_user_id: int, amount):
        requester_wallet = self.db.query(Wallet).filter(Wallet.user_id == requester_user_id).first()
        target_wallet = self.db.query(Wallet).filter(Wallet.user_id == target_user_id).first()
        if not target_wallet:
            raise HTTPException(status_code=404, detail="Target wallet not found")
        req = MoneyRequest(requester_wallet_id=requester_wallet.id, target_wallet_id=target_wallet.id, amount=amount)
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def act_on_request(self, request_id: int, acting_user_id: int, approve: bool):
        req = self.db.query(MoneyRequest).filter(MoneyRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        target_wallet = self.db.query(Wallet).filter(Wallet.id == req.target_wallet_id).first()
        if target_wallet.user_id != acting_user_id:  # type: ignore
            raise HTTPException(status_code=403, detail="Not authorized")
        if req.status != MoneyRequestStatus.pending:
            raise HTTPException(status_code=400, detail="Request already processed")
        if approve:
            requester_wallet = self.db.query(Wallet).filter(Wallet.id == req.requester_wallet_id).with_for_update().first()
            target_wallet = self.db.query(Wallet).filter(Wallet.id == req.target_wallet_id).with_for_update().first()
            if target_wallet.balance < req.amount:  # type: ignore
                raise HTTPException(status_code=400, detail="Insufficient balance")
            target_wallet.balance = target_wallet.balance - req.amount  # type: ignore
            requester_wallet.balance = requester_wallet.balance + req.amount  # type: ignore
            txn = Transaction(type=TransactionType.transfer, status=TransactionStatus.completed, amount=req.amount, from_wallet_id=target_wallet.id, to_wallet_id=requester_wallet.id, reference=f"REQ:{req.id}")
            self.db.add(txn)
            req.status = MoneyRequestStatus.approved
            req.resolved_at = datetime.now(timezone.utc)
        else:
            req.status = MoneyRequestStatus.rejected
            req.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(req)
        return req

    def create_refund(self, original_transaction_id: int, amount, reason: str | None = None):
        txn = self.db.query(Transaction).filter(Transaction.id == original_transaction_id).first()
        if not txn:
            raise HTTPException(status_code=404, detail="Original transaction not found")
        if amount > txn.amount:  # type: ignore
            raise HTTPException(status_code=400, detail="Refund amount exceeds original")
        refund = Refund(original_transaction_id=txn.id, amount=amount, status=RefundStatus.pending, reason=reason)
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)
        return refund
