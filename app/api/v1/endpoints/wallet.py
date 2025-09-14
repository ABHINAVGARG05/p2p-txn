from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models import User
from app.schemas import WalletOut, WalletTopUp, WalletWithdraw, WalletTransfer
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/me", response_model=WalletOut)
def get_my_wallet(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    service = WalletService(db)
    return service.get_user_wallet(current_user.id)

@router.post("/top-up", response_model=WalletOut)
def top_up(data: WalletTopUp, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    service = WalletService(db)
    return service.top_up(current_user.id, data.amount)

@router.post("/withdraw", response_model=WalletOut)
def withdraw(data: WalletWithdraw, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    service = WalletService(db)
    return service.withdraw(current_user.id, data.amount)

@router.post("/transfer", response_model=WalletOut)
def transfer(data: WalletTransfer, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    service = WalletService(db)
    return service.transfer(current_user.id, data.to_user_id, data.amount, data.idempotency_key)
