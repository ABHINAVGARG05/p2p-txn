import hashlib
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Transaction

PREFIX = "idem:"

def build_key(user_id: int, operation: str, unique_part: str | None) -> str:
    base = f"{user_id}:{operation}:{unique_part or ''}".encode()
    return hashlib.sha256(base).hexdigest()[:64]


def ensure_idempotent(db: Session, key: str):
    existing = db.query(Transaction).filter(Transaction.idempotency_key == key).first()
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate operation")
