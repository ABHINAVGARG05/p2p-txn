from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, SessionLocal
from app.db import base  # noqa: F401
from app.models import User, Wallet, UserRole
from app.core.security import get_password_hash

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, openapi_url=f"{settings.API_V1_PREFIX}/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RateLimitExceeded)
    def rate_limit_handler(request, exc):  # type: ignore
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.on_event("startup")
    def startup():
       
        from sqlalchemy import inspect
        insp = inspect(engine)
        if not insp.has_table("user"):
            base.Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            su = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
            if not su:
                su = User(email=settings.FIRST_SUPERUSER_EMAIL, hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD), role=UserRole.admin)
                db.add(su)
                db.flush()
                wallet = Wallet(user_id=su.id, balance=0)
                db.add(wallet)
                db.commit()
        finally:
            db.close()

    return app

app = create_app()
