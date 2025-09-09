from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RiskBase(BaseModel):
    risk_title: str = Field(..., max_length=100)
    risk_category: str = Field(..., max_length=50)
    risk_description: str = Field(..., max_length=400)

    inherent_probability: int = Field(..., ge=1, le=5)
    inherent_impact: int = Field(..., ge=1, le=5)
    current_probability: int = Field(..., ge=1, le=5)
    current_impact: int = Field(..., ge=1, le=5)

    risk_status: str = Field(..., max_length=20)
    risk_response_strategy: str = Field(..., max_length=20)
    planned_mitigations: str | None = Field(None, max_length=200)

    preventative_controls_status: str = Field(..., max_length=20)
    preventative_controls_description: str | None = Field(None, max_length=150)
    detective_controls_status: str = Field(..., max_length=20)
    detective_controls_description: str | None = Field(None, max_length=150)
    corrective_controls_status: str = Field(..., max_length=20)
    corrective_controls_description: str | None = Field(None, max_length=150)
    control_gaps: str | None = Field(None, max_length=150)

    risk_owner: str = Field(..., max_length=50)
    risk_owner_department: str = Field(..., max_length=50)
    systems_affected: str | None = Field(None, max_length=150)
    technology_domain: str = Field(..., max_length=50)

    ibs_impact: bool
    number_of_ibs_affected: int | None = Field(None, ge=0)
    business_criticality: str = Field(..., max_length=20)
    financial_impact_low: Decimal | None = Field(None, ge=0)
    financial_impact_high: Decimal | None = Field(None, ge=0)
    rto_hours: int | None = Field(None, ge=0)
    rpo_hours: int | None = Field(None, ge=0)
    sla_impact: str | None = Field(None, max_length=100)
    slo_impact: str | None = Field(None, max_length=100)

    date_identified: date
    last_reviewed: date
    next_review_date: date


class RiskCreate(RiskBase):
    pass


class RiskUpdate(RiskBase):
    pass


class Risk(RiskBase):
    risk_id: str
    inherent_risk_rating: int
    current_risk_rating: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskUpdateBase(BaseModel):
    update_date: date
    updated_by: str = Field(..., max_length=50)
    update_type: str = Field(..., max_length=50)
    update_summary: str = Field(..., max_length=300)
    previous_risk_rating: str | None = Field(None, max_length=20)
    new_risk_rating: str | None = Field(None, max_length=20)


class RiskUpdateCreate(RiskUpdateBase):
    risk_id: str = Field(..., max_length=12)


class RiskUpdateResponse(RiskUpdateBase):
    update_id: str
    risk_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    per_page: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")


class PaginatedRiskResponse(BaseModel):
    """Paginated response for risk lists."""
    items: list[Risk] = Field(..., description="List of risks")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class DropdownValueBase(BaseModel):
    category: str = Field(..., max_length=50)
    value: str = Field(..., max_length=100)
    display_order: int = 0
    is_active: bool = True


class DropdownValue(DropdownValueBase):
    id: int

    class Config:
        from_attributes = True
