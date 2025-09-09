from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import DashboardData
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db)) -> DashboardData:
    service = DashboardService(db)
    return service.get_dashboard_data()
