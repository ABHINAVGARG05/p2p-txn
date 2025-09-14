from fastapi import APIRouter
from .endpoints import auth, wallet, transactions, requests_refunds, admin

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(wallet.router)
api_router.include_router(transactions.router)
api_router.include_router(requests_refunds.router)
api_router.include_router(admin.router)
