from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de la plateforme ScamGuard - detection et explication des fraudes numeriques",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def prepare_database() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Systeme"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
