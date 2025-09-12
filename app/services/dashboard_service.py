from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.risk import Risk, RiskLogEntry
from app.schemas.dashboard import (
    BusinessServiceExposure,
    ControlPosture,
    DashboardData,
    RiskManagementActivity,
    RiskResponseBreakdown,
    RiskSeverityDistribution,
    TechnologyDomainRisk,
    TopRisk,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_data(self) -> DashboardData:
        """Get all dashboard data."""
        active_risks = self._get_active_risks_query()

        return DashboardData(
            # Overall Risk Exposure
            total_active_risks=self._get_total_active_risks(active_risks),
            critical_high_risk_count=self._get_critical_high_risk_count(active_risks),
            risk_trend_change=self._get_risk_trend_change(),
            # Risk Distribution
            risk_severity_distribution=self._get_risk_severity_distribution(
                active_risks
            ),
            # Technology Domains
            technology_domain_risks=self._get_technology_domain_risks(active_risks),
            # Control Posture
            control_posture=self._get_control_posture(active_risks),
            # Top Priority Risks
            top_priority_risks=self._get_top_priority_risks(active_risks),
            # Risk Response Strategy
            risk_response_breakdown=self._get_risk_response_breakdown(active_risks),
            # Financial Impact
            total_financial_exposure=self._get_total_financial_exposure(active_risks),
            average_financial_impact=self._get_average_financial_impact(active_risks),
            high_financial_impact_risks=self._get_high_financial_impact_risks(
                active_risks
            ),
            # Risk Management Activity
            risk_management_activity=self._get_risk_management_activity(),
            # Business Service Exposure
            business_service_exposure=self._get_business_service_exposure(active_risks),
        )

    def _get_active_risks_query(self):
        """Get query for active risks."""
        return self.db.query(Risk).filter(
            or_(Risk.risk_status == "Active", Risk.risk_status == "Monitoring")
        )

    def _get_total_active_risks(self, active_risks) -> int:
        """Get total count of active risks."""
        return active_risks.count()

    def _get_critical_high_risk_count(self, active_risks) -> int:
        """Get count of critical/high risks (rating >= 12)."""
        return active_risks.filter(Risk.current_risk_rating >= 12).count()

    def _get_risk_trend_change(self) -> float:
        """Calculate month-over-month risk trend change."""
        # Get current month count
        date.today().replace(day=1)
        self._get_active_risks_query().count()

        # Get previous month count (simplified - would need historical tracking)
        # For now, return 0 as baseline
        return 0.0

    def _get_risk_severity_distribution(self, active_risks) -> RiskSeverityDistribution:
        """Get risk distribution by severity levels."""
        critical = active_risks.filter(
            and_(Risk.current_risk_rating >= 16, Risk.current_risk_rating <= 25)
        ).count()

        high = active_risks.filter(
            and_(Risk.current_risk_rating >= 12, Risk.current_risk_rating <= 15)
        ).count()

        medium = active_risks.filter(
            and_(Risk.current_risk_rating >= 6, Risk.current_risk_rating <= 11)
        ).count()

        low = active_risks.filter(
            and_(Risk.current_risk_rating >= 1, Risk.current_risk_rating <= 5)
        ).count()

        return RiskSeverityDistribution(
            critical=critical, high=high, medium=medium, low=low
        )

    def _get_technology_domain_risks(self, active_risks) -> list[TechnologyDomainRisk]:
        """Get risk count and average rating by technology domain."""
        results = (
            active_risks.with_entities(
                Risk.technology_domain,
                func.count(Risk.risk_id).label("risk_count"),
                func.avg(Risk.current_risk_rating).label("avg_rating"),
            )
            .group_by(Risk.technology_domain)
            .all()
        )

        return [
            TechnologyDomainRisk(
                domain=result.technology_domain,
                risk_count=result.risk_count,
                average_risk_rating=(
                    float(result.avg_rating) if result.avg_rating else 0.0
                ),
            )
            for result in results
        ]

    def _get_control_posture(self, active_risks) -> ControlPosture:
        """Get control posture statistics."""
        total_risks = active_risks.count()
        if total_risks == 0:
            return ControlPosture(
                preventative_adequate_percentage=0.0,
                detective_adequate_percentage=0.0,
                corrective_adequate_percentage=0.0,
                risks_with_control_gaps=0,
            )

        preventative_adequate = active_risks.filter(
            Risk.preventative_controls_status == "Adequate"
        ).count()

        detective_adequate = active_risks.filter(
            Risk.detective_controls_status == "Adequate"
        ).count()

        corrective_adequate = active_risks.filter(
            Risk.corrective_controls_status == "Adequate"
        ).count()

        control_gaps = active_risks.filter(
            and_(Risk.control_gaps is not None, Risk.control_gaps != "")
        ).count()

        return ControlPosture(
            preventative_adequate_percentage=(preventative_adequate / total_risks)
            * 100,
            detective_adequate_percentage=(detective_adequate / total_risks) * 100,
            corrective_adequate_percentage=(corrective_adequate / total_risks) * 100,
            risks_with_control_gaps=control_gaps,
        )

    def _get_top_priority_risks(self, active_risks) -> list[TopRisk]:
        """Get top 10 highest priority risks with intelligent sorting."""
        risks = (
            active_risks.order_by(
                Risk.current_risk_rating.desc(),
                Risk.financial_impact_high.desc().nulls_last(),
                Risk.ibs_impact.desc(),
            )
            .limit(10)
            .all()
        )

        return [
            TopRisk(
                risk_id=risk.risk_id,
                risk_title=risk.risk_title,
                current_risk_rating=risk.current_risk_rating,
                financial_impact_high=risk.financial_impact_high,
                ibs_impact=risk.ibs_impact,
                risk_owner=risk.risk_owner,
            )
            for risk in risks
        ]

    def _get_risk_response_breakdown(self, active_risks) -> RiskResponseBreakdown:
        """Get risk response strategy breakdown."""
        mitigate = active_risks.filter(
            Risk.risk_response_strategy == "Mitigate"
        ).count()
        accept = active_risks.filter(Risk.risk_response_strategy == "Accept").count()
        transfer = active_risks.filter(
            Risk.risk_response_strategy == "Transfer"
        ).count()
        avoid = active_risks.filter(Risk.risk_response_strategy == "Avoid").count()

        return RiskResponseBreakdown(
            mitigate=mitigate, accept=accept, transfer=transfer, avoid=avoid
        )

    def _get_total_financial_exposure(self, active_risks) -> Decimal:
        """Get total financial exposure (sum of high estimates)."""
        result = active_risks.with_entities(
            func.sum(Risk.financial_impact_high)
        ).scalar()

        return result if result else Decimal("0.00")

    def _get_average_financial_impact(self, active_risks) -> Decimal:
        """Get average financial impact per risk."""
        result = active_risks.with_entities(
            func.avg(Risk.financial_impact_high)
        ).scalar()

        return Decimal(str(result)) if result else Decimal("0.00")

    def _get_high_financial_impact_risks(self, active_risks) -> int:
        """Get count of risks with financial impact > $1M."""
        return active_risks.filter(Risk.financial_impact_high > 1000000).count()

    def _get_risk_management_activity(self) -> RiskManagementActivity:
        """Get risk management activity metrics."""
        current_month_start = date.today().replace(day=1)

        # Risks reviewed this month
        reviewed_this_month = (
            self.db.query(Risk)
            .filter(Risk.last_reviewed >= current_month_start)
            .count()
        )

        # Overdue reviews
        overdue_reviews = (
            self.db.query(Risk).filter(Risk.next_review_date < date.today()).count()
        )

        # Recent rating changes (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_changes = (
            self.db.query(RiskLogEntry)
            .filter(
                and_(
                    RiskLogEntry.entry_date >= thirty_days_ago,
                    RiskLogEntry.entry_type == "Risk Assessment Update",
                )
            )
            .count()
        )

        return RiskManagementActivity(
            risks_reviewed_this_month=reviewed_this_month,
            overdue_reviews=overdue_reviews,
            recent_risk_rating_changes=recent_changes,
        )

    def _get_business_service_exposure(self, active_risks) -> BusinessServiceExposure:
        """Get business service exposure metrics."""
        total_active = active_risks.count()

        # Risks affecting IBS
        ibs_risks = active_risks.filter(Risk.ibs_impact)
        ibs_risk_count = ibs_risks.count()

        # Total IBS affected
        total_ibs_affected = (
            ibs_risks.with_entities(func.sum(Risk.number_of_ibs_affected)).scalar() or 0
        )

        # Percentage with IBS impact
        percentage_with_ibs = (
            (ibs_risk_count / total_active * 100) if total_active > 0 else 0.0
        )

        # Critical risks affecting IBS
        critical_ibs_risks = ibs_risks.filter(Risk.current_risk_rating >= 16).count()

        return BusinessServiceExposure(
            risks_affecting_ibs=ibs_risk_count,
            total_ibs_affected=total_ibs_affected,
            percentage_risks_with_ibs_impact=percentage_with_ibs,
            critical_risks_affecting_ibs=critical_ibs_risks,
        )
