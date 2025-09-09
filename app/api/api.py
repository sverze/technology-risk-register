from fastapi import APIRouter

from app.api.endpoints import dashboard, risks

api_router = APIRouter()
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
