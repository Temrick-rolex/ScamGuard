from fastapi import APIRouter

from app.api.v1 import admin_reports, admin_users, analyses, auth, me, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(analyses.router)
api_router.include_router(reports.router)
api_router.include_router(admin_users.router)
api_router.include_router(admin_reports.router)
