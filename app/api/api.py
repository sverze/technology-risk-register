from fastapi import APIRouter, Depends

from app.api import admin
from app.api.endpoints import chat, dashboard, dropdown, risks
from app.api.routes import auth
from app.core.security import get_current_user

api_router = APIRouter()

# Auth routes (no authentication required)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Protected routes (authentication required)
api_router.include_router(risks.router, prefix="/risks", tags=["risks"], dependencies=[Depends(get_current_user)])
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)]
)
api_router.include_router(
    dropdown.router, prefix="/dropdown", tags=["dropdown"], dependencies=[Depends(get_current_user)]
)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_user)])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])
