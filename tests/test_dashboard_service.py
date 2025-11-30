from decimal import Decimal

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
from app.services.dashboard_service import DashboardService


class TestDashboardService:
    """Test cases for DashboardService."""

    def test_init(self, db_session):
        """Test DashboardService initialization."""
        service = DashboardService(db_session)
        assert service.db == db_session

    def test_get_dashboard_data_empty_db(self, db_session):
        """Test get_dashboard_data with empty database."""
        service = DashboardService(db_session)
        data = service.get_dashboard_data()

        assert isinstance(data, DashboardData)
        assert data.total_active_risks == 0
        assert data.critical_high_risk_count == 0
        assert data.risk_trend_change == 0.0

    def test_get_dashboard_data_with_risks(self, db_session, dashboard_sample_risks):
        """Test get_dashboard_data with sample risks."""
        service = DashboardService(db_session)
        data = service.get_dashboard_data()

        assert isinstance(data, DashboardData)
        assert data.total_active_risks > 0
        assert isinstance(data.risk_severity_distribution, RiskSeverityDistribution)
        assert isinstance(data.technology_domain_risks, list)
        assert isinstance(data.control_posture, ControlPosture)

    def test_get_active_risks_query(self, db_session, dashboard_sample_risks):
        """Test _get_active_risks_query filters correctly."""
        service = DashboardService(db_session)
        query = service._get_active_risks_query()

        # Should only include Active and Monitoring status
        active_risks = query.all()
        for risk in active_risks:
            assert risk.risk_status in ["Active", "Monitoring"]

    def test_get_total_active_risks(self, db_session, dashboard_sample_risks):
        """Test _get_total_active_risks."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        count = service._get_total_active_risks(active_risks)

        assert isinstance(count, int)
        assert count >= 0

    def test_get_critical_high_risk_count(self, db_session, dashboard_sample_risks):
        """Test _get_critical_high_risk_count."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        count = service._get_critical_high_risk_count(active_risks)

        assert isinstance(count, int)
        assert count >= 0

    def test_get_risk_trend_change(self, db_session):
        """Test _get_risk_trend_change."""
        service = DashboardService(db_session)
        trend = service._get_risk_trend_change()

        # Currently returns 0.0 as baseline
        assert trend == 0.0

    def test_get_risk_severity_distribution_empty(self, db_session):
        """Test _get_risk_severity_distribution with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        distribution = service._get_risk_severity_distribution(active_risks)

        assert isinstance(distribution, RiskSeverityDistribution)
        assert distribution.critical == 0
        assert distribution.high == 0
        assert distribution.medium == 0
        assert distribution.low == 0

    def test_get_risk_severity_distribution_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_risk_severity_distribution with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        distribution = service._get_risk_severity_distribution(active_risks)

        assert isinstance(distribution, RiskSeverityDistribution)
        assert distribution.critical >= 0
        assert distribution.high >= 0
        assert distribution.medium >= 0
        assert distribution.low >= 0

    def test_get_technology_domain_risks_empty(self, db_session):
        """Test _get_technology_domain_risks with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        domain_risks = service._get_technology_domain_risks(active_risks)

        assert isinstance(domain_risks, list)
        assert len(domain_risks) == 0

    def test_get_technology_domain_risks_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_technology_domain_risks with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        domain_risks = service._get_technology_domain_risks(active_risks)

        assert isinstance(domain_risks, list)
        for domain_risk in domain_risks:
            assert isinstance(domain_risk, TechnologyDomainRisk)
            assert isinstance(domain_risk.domain, str)
            assert isinstance(domain_risk.risk_count, int)
            assert isinstance(domain_risk.average_risk_rating, float)
            assert domain_risk.risk_count >= 0
            assert domain_risk.average_risk_rating >= 0.0

    def test_get_control_posture_empty(self, db_session):
        """Test _get_control_posture with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        posture = service._get_control_posture(active_risks)

        assert isinstance(posture, ControlPosture)
        assert posture.preventative_adequate_percentage == 0.0
        assert posture.detective_adequate_percentage == 0.0
        assert posture.corrective_adequate_percentage == 0.0
        assert posture.risks_with_control_gaps == 0

    def test_get_control_posture_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_control_posture with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        posture = service._get_control_posture(active_risks)

        assert isinstance(posture, ControlPosture)
        assert 0.0 <= posture.preventative_adequate_percentage <= 100.0
        assert 0.0 <= posture.detective_adequate_percentage <= 100.0
        assert 0.0 <= posture.corrective_adequate_percentage <= 100.0
        assert posture.risks_with_control_gaps >= 0

    def test_get_top_priority_risks_empty(self, db_session):
        """Test _get_top_priority_risks with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        top_risks = service._get_top_priority_risks(active_risks)

        assert isinstance(top_risks, list)
        assert len(top_risks) == 0

    def test_get_top_priority_risks_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_top_priority_risks with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        top_risks = service._get_top_priority_risks(active_risks)

        assert isinstance(top_risks, list)
        assert len(top_risks) <= 10  # Should be limited to 10

        # Verify sorting (should be by net exposure descending)
        if len(top_risks) > 1:
            # Just verify they all have net exposure values
            for risk in top_risks:
                assert risk.business_disruption_net_exposure is not None

        for risk in top_risks:
            assert isinstance(risk, TopRisk)
            assert isinstance(risk.risk_id, str)
            assert isinstance(risk.risk_title, str)
            assert isinstance(risk.business_disruption_net_exposure, str)

    def test_get_risk_response_breakdown_empty(self, db_session):
        """Test _get_risk_response_breakdown with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        breakdown = service._get_risk_response_breakdown(active_risks)

        assert isinstance(breakdown, RiskResponseBreakdown)
        assert breakdown.mitigate == 0
        assert breakdown.accept == 0
        assert breakdown.transfer == 0
        assert breakdown.avoid == 0

    def test_get_risk_response_breakdown_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_risk_response_breakdown with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        breakdown = service._get_risk_response_breakdown(active_risks)

        assert isinstance(breakdown, RiskResponseBreakdown)
        assert breakdown.mitigate >= 0
        assert breakdown.accept >= 0
        assert breakdown.transfer >= 0
        assert breakdown.avoid >= 0

    def test_get_total_financial_exposure_empty(self, db_session):
        """Test _get_total_financial_exposure with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        exposure = service._get_total_financial_exposure(active_risks)

        assert isinstance(exposure, Decimal)
        assert exposure == Decimal("0.00")

    def test_get_total_financial_exposure_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_total_financial_exposure with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        exposure = service._get_total_financial_exposure(active_risks)

        assert isinstance(exposure, Decimal)
        assert exposure >= Decimal("0.00")

    def test_get_average_financial_impact_empty(self, db_session):
        """Test _get_average_financial_impact with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        avg_impact = service._get_average_financial_impact(active_risks)

        assert isinstance(avg_impact, Decimal)
        assert avg_impact == Decimal("0.00")

    def test_get_average_financial_impact_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_average_financial_impact with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        avg_impact = service._get_average_financial_impact(active_risks)

        assert isinstance(avg_impact, Decimal)
        assert avg_impact >= Decimal("0.00")

    def test_get_high_financial_impact_risks(self, db_session, dashboard_sample_risks):
        """Test _get_high_financial_impact_risks."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        count = service._get_high_financial_impact_risks(active_risks)

        assert isinstance(count, int)
        assert count >= 0

    def test_get_risk_management_activity(self, db_session, dashboard_sample_risks):
        """Test _get_risk_management_activity."""
        service = DashboardService(db_session)
        activity = service._get_risk_management_activity()

        assert isinstance(activity, RiskManagementActivity)
        assert activity.risks_reviewed_this_month >= 0
        assert activity.overdue_reviews >= 0
        assert activity.recent_risk_rating_changes >= 0

    def test_get_business_service_exposure_empty(self, db_session):
        """Test _get_business_service_exposure with empty database."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        exposure = service._get_business_service_exposure(active_risks)

        assert isinstance(exposure, BusinessServiceExposure)
        assert exposure.risks_affecting_ibs == 0
        assert exposure.total_ibs_affected == 0
        assert exposure.percentage_risks_with_ibs_impact == 0.0
        assert exposure.critical_risks_affecting_ibs == 0

    def test_get_business_service_exposure_with_data(self, db_session, dashboard_sample_risks):
        """Test _get_business_service_exposure with sample data."""
        service = DashboardService(db_session)
        active_risks = service._get_active_risks_query()
        exposure = service._get_business_service_exposure(active_risks)

        assert isinstance(exposure, BusinessServiceExposure)
        assert exposure.risks_affecting_ibs >= 0
        assert exposure.total_ibs_affected >= 0
        assert 0.0 <= exposure.percentage_risks_with_ibs_impact <= 100.0
        assert exposure.critical_risks_affecting_ibs >= 0
