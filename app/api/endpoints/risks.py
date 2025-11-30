from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.risk import (
    PaginatedRiskResponse,
    PaginationMetadata,
    Risk,
    RiskCreate,
    RiskLogEntryCreate,
    RiskLogEntryResponse,
    RiskLogEntryUpdate,
    RiskUpdate,
    RiskUpdateResponse,  # Legacy compatibility
)
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/", response_model=PaginatedRiskResponse)
def get_risks(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    db: Session = Depends(get_db),
) -> PaginatedRiskResponse:
    """Get risks with optional filtering, searching, and sorting.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        category: Filter by risk category
        status: Filter by risk status
        search: Search in risk title and description (case-insensitive)
        sort_by: Field to sort by (e.g., 'risk_title', 'current_risk_rating')
        sort_order: Sort order ('asc' or 'desc')

    Returns:
        Paginated response with risks and pagination metadata
    """
    if limit > 500:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 500")
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    service = RiskService(db)

    # Get risks and total count
    risks = service.get_risks(
        skip=skip,
        limit=limit,
        category=category,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total = service.get_risks_count(
        category=category,
        status=status,
        search=search,
    )

    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    has_prev = page > 1
    has_next = page < pages

    pagination = PaginationMetadata(
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
        has_prev=has_prev,
        has_next=has_next,
    )

    return PaginatedRiskResponse(
        items=risks,  # type: ignore[arg-type]
        pagination=pagination,
    )


@router.get("/{risk_id}", response_model=Risk)
def get_risk(risk_id: str, db: Session = Depends(get_db)) -> Risk:
    service = RiskService(db)
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk  # type: ignore[return-value,no-any-return]


@router.post("/", response_model=Risk)
def create_risk(risk_data: RiskCreate, db: Session = Depends(get_db)) -> Risk:
    service = RiskService(db)
    return service.create_risk(risk_data)  # type: ignore[return-value,no-any-return]


@router.put("/{risk_id}", response_model=Risk)
def update_risk(risk_id: str, risk_data: RiskUpdate, db: Session = Depends(get_db)) -> Risk:
    service = RiskService(db)
    risk = service.update_risk(risk_id, risk_data)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk  # type: ignore[return-value,no-any-return]


@router.delete("/{risk_id}")
def delete_risk(risk_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    service = RiskService(db)
    if not service.delete_risk(risk_id):
        raise HTTPException(status_code=404, detail="Risk not found")
    return {"message": "Risk deleted successfully"}


@router.get("/{risk_id}/updates", response_model=list[RiskUpdateResponse])
def get_risk_updates(risk_id: str, db: Session = Depends(get_db)) -> list[RiskUpdateResponse]:
    """Get all update logs for a specific risk."""
    service = RiskService(db)
    # First check if risk exists
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    return service.get_risk_updates(risk_id)  # type: ignore[return-value]


@router.get("/updates/recent", response_model=list[RiskUpdateResponse])
def get_recent_risk_updates(limit: int = 50, db: Session = Depends(get_db)) -> list[RiskUpdateResponse]:
    """Get recent risk updates across all risks."""
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    service = RiskService(db)
    return service.get_recent_risk_updates(limit=limit)  # type: ignore[return-value]


# New RiskLogEntry endpoints
@router.post("/{risk_id}/log-entries", response_model=RiskLogEntryResponse)
def create_risk_log_entry(
    risk_id: str, log_entry_data: RiskLogEntryCreate, db: Session = Depends(get_db)
) -> RiskLogEntryResponse:
    """Create a new log entry for a risk."""
    service = RiskService(db)

    # Ensure risk exists
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    # Set the risk_id in the log entry data
    log_entry_data.risk_id = risk_id

    return service.create_risk_log_entry(log_entry_data)  # type: ignore[return-value,no-any-return]


@router.get("/{risk_id}/log-entries", response_model=list[RiskLogEntryResponse])
def get_risk_log_entries(risk_id: str, db: Session = Depends(get_db)) -> list[RiskLogEntryResponse]:
    """Get all log entries for a specific risk, ordered by most recent first."""
    service = RiskService(db)

    # First check if risk exists
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    return service.get_risk_log_entries(risk_id)  # type: ignore[return-value]


@router.get("/log-entries/{log_entry_id}", response_model=RiskLogEntryResponse)
def get_risk_log_entry(log_entry_id: str, db: Session = Depends(get_db)) -> RiskLogEntryResponse:
    """Get a specific log entry by ID."""
    service = RiskService(db)
    log_entry = service.get_risk_log_entry(log_entry_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry  # type: ignore[return-value,no-any-return]


@router.put("/log-entries/{log_entry_id}", response_model=RiskLogEntryResponse)
def update_risk_log_entry(
    log_entry_id: str, log_entry_data: RiskLogEntryUpdate, db: Session = Depends(get_db)
) -> RiskLogEntryResponse:
    """Update an existing log entry."""
    service = RiskService(db)
    log_entry = service.update_risk_log_entry(log_entry_id, log_entry_data)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry  # type: ignore[return-value,no-any-return]


@router.post("/log-entries/{log_entry_id}/approve", response_model=RiskLogEntryResponse)
def approve_risk_log_entry(log_entry_id: str, reviewed_by: str, db: Session = Depends(get_db)) -> RiskLogEntryResponse:
    """Approve a log entry and update the parent risk's current rating."""
    service = RiskService(db)
    log_entry = service.approve_risk_log_entry(log_entry_id, reviewed_by)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry  # type: ignore[return-value,no-any-return]


@router.post("/log-entries/{log_entry_id}/reject", response_model=RiskLogEntryResponse)
def reject_risk_log_entry(log_entry_id: str, reviewed_by: str, db: Session = Depends(get_db)) -> RiskLogEntryResponse:
    """Reject a log entry."""
    service = RiskService(db)
    log_entry = service.reject_risk_log_entry(log_entry_id, reviewed_by)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry  # type: ignore[return-value,no-any-return]


@router.delete("/log-entries/{log_entry_id}")
def delete_risk_log_entry(log_entry_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a log entry."""
    service = RiskService(db)
    if not service.delete_risk_log_entry(log_entry_id):
        raise HTTPException(status_code=404, detail="Log entry not found")
    return {"message": "Log entry deleted successfully"}
