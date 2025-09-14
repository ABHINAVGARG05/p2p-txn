from decimal import Decimal
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Transaction, TransactionStatus, Wallet

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

@shared_task(name="tasks.settle_transaction", bind=True, max_retries=5, default_retry_delay=10)
def settle_transaction(self, transaction_id: int):
    db: Session = SessionLocal()
    try:
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).with_for_update().first()
        if not txn:
            return
        if txn.status != TransactionStatus.pending:
            return
        # Simplified settlement: just mark completed
        txn.status = TransactionStatus.completed
        db.commit()
    except Exception as exc:  # pragma: no cover
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            if txn:
                txn.status = TransactionStatus.failed
                db.commit()
    finally:
        db.close()

@shared_task(name="tasks.retry_failed")
def retry_failed():
    db: Session = SessionLocal()
    try:
        failed = db.query(Transaction).filter(Transaction.status == TransactionStatus.failed).all()
        for txn in failed:
            txn.status = TransactionStatus.pending
            db.commit()
            settle_transaction.delay(txn.id)
    finally:
        db.close()
