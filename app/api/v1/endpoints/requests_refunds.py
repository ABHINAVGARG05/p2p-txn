from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models import User
from app.schemas import MoneyRequestCreate, MoneyRequestOut, MoneyRequestAction, RefundCreate, RefundOut
from app.services.request_refund_service import RequestRefundService

router = APIRouter(prefix="/actions", tags=["requests-refunds"])

@router.post("/request", response_model=MoneyRequestOut)
def create_request(data: MoneyRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = RequestRefundService(db)
    return service.create_money_request(current_user.id, data.target_user_id, data.amount)

@router.post("/request/{request_id}/action", response_model=MoneyRequestOut)
def act_on_request(request_id: int, action: MoneyRequestAction, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = RequestRefundService(db)
    return service.act_on_request(request_id, current_user.id, action.approve)

@router.post("/refund", response_model=RefundOut)
def create_refund(data: RefundCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = RequestRefundService(db)
    return service.create_refund(data.original_transaction_id, data.amount, data.reason)
