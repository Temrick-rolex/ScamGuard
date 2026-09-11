from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base

PAGE_ACCUEIL = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ScamGuard API</title>
<style>
  body { font-family: system-ui, sans-serif; background: #F6F8F9; color: #1A1A1A;
         display: flex; min-height: 100vh; align-items: center; justify-content: center;
         margin: 0; }
  .carte { background: #FFFFFF; border: 1px solid #E3E8EA; border-radius: 12px;
           padding: 40px 48px; max-width: 520px; text-align: center; }
  h1 { color: #0B7285; margin: 0 0 6px; font-size: 26px; }
  p { color: #6B7679; line-height: 1.5; }
  a { display: inline-block; margin: 14px 6px 0; padding: 10px 18px; border-radius: 10px;
      background: #0B7285; color: #FFFFFF; text-decoration: none; font-weight: 600; }
  a.secondaire { background: #FFFFFF; color: #0B7285; border: 1px solid #0B7285; }
</style>
</head>
<body>
<div class="carte">
  <h1>ScamGuard API</h1>
  <p>Backend de detection des fraudes numeriques.<br>Le service est operationnel.</p>
  <a href="/docs">Documentation interactive</a>
  <a class="secondaire" href="/health">Etat du service</a>
</div>
</body>
</html>"""


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


@app.get("/", include_in_schema=False)
def accueil() -> HTMLResponse:
    """Page d'accueil minimaliste : confirme que l API est en ligne et
    redirige vers la documentation interactive."""
    return HTMLResponse(PAGE_ACCUEIL)


@app.get("/health", tags=["Systeme"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
