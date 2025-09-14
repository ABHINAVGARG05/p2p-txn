from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_admin_user
from app.models import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats/summary")
def summary_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    service = AnalyticsService(db)
    return service.summary()
