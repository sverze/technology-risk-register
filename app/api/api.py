from fastapi import APIRouter

from app.api.endpoints import dashboard, dropdown, risks
from app.api import admin

api_router = APIRouter()
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(dropdown.router, prefix="/dropdown", tags=["dropdown"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
