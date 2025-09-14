from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models import User
from app.schemas import TransactionList
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/me", response_model=TransactionList)
def list_my_transactions(page: int = 1, size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = TransactionService(db)
    items, total = service.list_for_user(current_user.id, page, size)
    return TransactionList(items=items, total=total, page=page, size=size if size < 100 else 100)
