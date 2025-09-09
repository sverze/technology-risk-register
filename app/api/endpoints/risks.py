from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.risk import Risk, RiskCreate, RiskUpdate
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/", response_model=list[Risk])
def get_risks(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[Risk]:
    service = RiskService(db)
    return service.get_risks(skip=skip, limit=limit, category=category, status=status)


@router.get("/{risk_id}", response_model=Risk)
def get_risk(risk_id: str, db: Session = Depends(get_db)) -> Risk:
    service = RiskService(db)
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.post("/", response_model=Risk)
def create_risk(risk_data: RiskCreate, db: Session = Depends(get_db)) -> Risk:
    service = RiskService(db)
    return service.create_risk(risk_data)


@router.put("/{risk_id}", response_model=Risk)
def update_risk(
    risk_id: str, risk_data: RiskUpdate, db: Session = Depends(get_db)
) -> Risk:
    service = RiskService(db)
    risk = service.update_risk(risk_id, risk_data)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.delete("/{risk_id}")
def delete_risk(risk_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    service = RiskService(db)
    if not service.delete_risk(risk_id):
        raise HTTPException(status_code=404, detail="Risk not found")
    return {"message": "Risk deleted successfully"}
