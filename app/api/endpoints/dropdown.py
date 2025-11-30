from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.risk import DropdownValue
from app.services.dropdown_service import DropdownService

router = APIRouter()


@router.get("/values", response_model=list[DropdownValue])
def get_dropdown_values(
    category: str | None = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
) -> list[DropdownValue]:
    """Get dropdown values, optionally filtered by category."""
    service = DropdownService(db)
    return service.get_dropdown_values(category=category)


@router.get("/categories", response_model=list[str])
def get_dropdown_categories(db: Session = Depends(get_db)) -> list[str]:
    """Get all available dropdown categories."""
    service = DropdownService(db)
    return service.get_dropdown_categories()


@router.get("/values/by-category", response_model=dict[str, list[DropdownValue]])
def get_dropdown_values_by_category(
    categories: list[str] | None = Query(None, description="Specific categories to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, list[DropdownValue]]:
    """Get dropdown values grouped by category."""
    service = DropdownService(db)
    return service.get_dropdown_values_by_categories(categories=categories)
