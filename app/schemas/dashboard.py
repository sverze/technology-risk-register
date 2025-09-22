from decimal import Decimal

from pydantic import BaseModel


class RiskSeverityDistribution(BaseModel):
    critical: int  # 16-25
    high: int  # 12-15
    medium: int  # 6-11
    low: int  # 1-5


class TechnologyDomainRisk(BaseModel):
    domain: str
    risk_count: int
    average_risk_rating: float


class ControlPosture(BaseModel):
    preventative_adequate_percentage: float
    detective_adequate_percentage: float
    corrective_adequate_percentage: float
    risks_with_control_gaps: int


class TopRisk(BaseModel):
    risk_id: str
    risk_title: str
    business_disruption_net_exposure: str
    financial_impact_high: Decimal | None
    ibs_affected: str | None
    risk_owner: str


class RiskResponseBreakdown(BaseModel):
    mitigate: int
    accept: int
    transfer: int
    avoid: int


class RiskManagementActivity(BaseModel):
    risks_reviewed_this_month: int
    overdue_reviews: int
    recent_risk_rating_changes: int


class BusinessServiceExposure(BaseModel):
    risks_affecting_ibs: int
    total_ibs_affected: int
    percentage_risks_with_ibs_impact: float
    critical_risks_affecting_ibs: int


class DashboardData(BaseModel):
    # Overall Risk Exposure
    total_active_risks: int
    critical_high_risk_count: int
    risk_trend_change: float  # Month-over-month percentage change

    # Risk Distribution
    risk_severity_distribution: RiskSeverityDistribution

    # Technology Domains
    technology_domain_risks: list[TechnologyDomainRisk]

    # Control Posture
    control_posture: ControlPosture

    # Top Priority Risks
    top_priority_risks: list[TopRisk]

    # Risk Response Strategy
    risk_response_breakdown: RiskResponseBreakdown

    # Financial Impact
    total_financial_exposure: Decimal
    average_financial_impact: Decimal
    high_financial_impact_risks: int  # >$1M

    # Risk Management Activity
    risk_management_activity: RiskManagementActivity

    # Business Service Exposure
    business_service_exposure: BusinessServiceExposure
