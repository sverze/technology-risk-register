import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.risk import Base, DropdownValue, Risk

# Test database URL - use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use a single connection pool for in-memory database
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a database session for tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_risks(db_session):
    """Create sample risks for testing."""
    from datetime import date

    risk1 = Risk(
        risk_id="TR-2024-CYB-001",
        risk_title="Cybersecurity Risk",
        risk_description="Test cybersecurity risk",
        risk_category="Cybersecurity",
        risk_owner="Test User",
        risk_status="Open",
        risk_response_strategy="Mitigate",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="IT",
        technology_domain="Security",
        ibs_affected="IBS-1, IBS-2",
        business_disruption_impact_rating="Major",
        business_disruption_impact_description="Significant impact to operations",
        business_disruption_likelihood_rating="Possible",
        business_disruption_likelihood_description="May occur in normal circumstances",
        date_identified=date.today(),
        last_reviewed=date.today(),
        next_review_date=date.today(),
    )
    risk1.calculate_net_exposure()

    risk2 = Risk(
        risk_id="TR-2024-INF-001",
        risk_title="Infrastructure Risk",
        risk_description="Test infrastructure risk",
        risk_category="Infrastructure",
        risk_owner="Test User 2",
        risk_status="Open",
        risk_response_strategy="Mitigate",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="Operations",
        technology_domain="Infrastructure",
        ibs_affected="IBS-3",
        business_disruption_impact_rating="Moderate",
        business_disruption_impact_description="Moderate impact to operations",
        business_disruption_likelihood_rating="Unlikely",
        business_disruption_likelihood_description="Unlikely to occur",
        date_identified=date.today(),
        last_reviewed=date.today(),
        next_review_date=date.today(),
    )
    risk2.calculate_net_exposure()

    db_session.add(risk1)
    db_session.add(risk2)
    db_session.commit()
    return [risk1, risk2]


@pytest.fixture
def dashboard_sample_risks(db_session):
    """Create comprehensive sample risks for dashboard testing."""
    from datetime import date, timedelta
    from decimal import Decimal

    risks = []

    # Critical risk
    risk1 = Risk(
        risk_id="TR-2024-CYB-001",
        risk_title="Critical Security Breach",
        risk_description="High-impact security vulnerability",
        risk_category="Cybersecurity",
        risk_owner="Security Team",
        risk_status="Active",
        risk_response_strategy="Mitigate",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        preventative_controls_description="Firewalls and access controls in place",
        detective_controls_coverage="Partial",
        detective_controls_effectiveness="Ineffective",
        detective_controls_description="Missing monitoring tools",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="IT",
        technology_domain="Security",
        ibs_affected="IBS-001, IBS-002, IBS-003, IBS-004, IBS-005",
        business_disruption_impact_rating="Catastrophic",
        business_disruption_impact_description="Critical systems would be completely unavailable, affecting all business operations",
        business_disruption_likelihood_rating="Probable",
        business_disruption_likelihood_description="Based on current threat intelligence, this is likely to occur",
        financial_impact_low=Decimal("500000.00"),
        financial_impact_high=Decimal("2000000.00"),
        date_identified=date.today() - timedelta(days=30),
        last_reviewed=date.today() - timedelta(days=10),
        next_review_date=date.today() + timedelta(days=20),
    )
    risk1.calculate_net_exposure()
    risks.append(risk1)

    # High risk
    risk2 = Risk(
        risk_id="TR-2024-INF-001",
        risk_title="Infrastructure Failure",
        risk_description="Critical infrastructure failure risk",
        risk_category="Infrastructure",
        risk_owner="Infrastructure Team",
        risk_status="Active",
        risk_response_strategy="Accept",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="Operations",
        technology_domain="Infrastructure",
        ibs_affected="IBS-006, IBS-007, IBS-008",
        business_disruption_impact_rating="Major",
        business_disruption_impact_description="Significant disruption to infrastructure operations",
        business_disruption_likelihood_rating="Possible",
        business_disruption_likelihood_description="Could occur in normal circumstances",
        financial_impact_low=Decimal("100000.00"),
        financial_impact_high=Decimal("800000.00"),
        date_identified=date.today() - timedelta(days=60),
        last_reviewed=date.today() - timedelta(days=15),
        next_review_date=date.today() + timedelta(days=15),
    )
    risk2.calculate_net_exposure()
    risks.append(risk2)

    # Medium risk
    risk3 = Risk(
        risk_id="TR-2024-APP-001",
        risk_title="Application Performance",
        risk_description="Application performance degradation",
        risk_category="Application",
        risk_owner="Development Team",
        risk_status="Monitoring",
        risk_response_strategy="Transfer",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Partial",
        corrective_controls_effectiveness="Ineffective",
        risk_owner_department="Engineering",
        technology_domain="Applications",
        ibs_affected=None,
        business_disruption_impact_rating="Moderate",
        business_disruption_impact_description="Some degradation in application performance",
        business_disruption_likelihood_rating="Possible",
        business_disruption_likelihood_description="May occur during peak usage",
        financial_impact_low=Decimal("10000.00"),
        financial_impact_high=Decimal("50000.00"),
        date_identified=date.today() - timedelta(days=45),
        last_reviewed=date.today(),
        next_review_date=date.today() + timedelta(days=30),
    )
    risk3.calculate_net_exposure()
    risks.append(risk3)

    # Low risk
    risk4 = Risk(
        risk_id="TR-2024-OPS-001",
        risk_title="Operational Process Gap",
        risk_description="Minor operational process improvement needed",
        risk_category="Operational",
        risk_owner="Operations Team",
        risk_status="Active",
        risk_response_strategy="Avoid",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="Operations",
        technology_domain="Business Process",
        ibs_affected=None,
        business_disruption_impact_rating="Low",
        business_disruption_impact_description="Minor impact to operations",
        business_disruption_likelihood_rating="Unlikely",
        business_disruption_likelihood_description="Unlikely to occur",
        financial_impact_low=Decimal("1000.00"),
        financial_impact_high=Decimal("5000.00"),
        date_identified=date.today() - timedelta(days=90),
        last_reviewed=date.today() - timedelta(days=60),
        next_review_date=date.today() - timedelta(days=5),  # Overdue
    )
    risk4.calculate_net_exposure()
    risks.append(risk4)

    # Closed risk (should not appear in dashboard)
    risk5 = Risk(
        risk_id="TR-2024-CLD-001",
        risk_title="Closed Cloud Risk",
        risk_description="This risk has been closed",
        risk_category="Cloud Services",
        risk_owner="Cloud Team",
        risk_status="Closed",
        risk_response_strategy="Mitigate",
        preventative_controls_coverage="Adequate",
        preventative_controls_effectiveness="Effective",
        detective_controls_coverage="Adequate",
        detective_controls_effectiveness="Effective",
        corrective_controls_coverage="Adequate",
        corrective_controls_effectiveness="Effective",
        risk_owner_department="IT",
        technology_domain="Cloud",
        ibs_affected=None,
        business_disruption_impact_rating="Low",
        business_disruption_impact_description="Minimal impact",
        business_disruption_likelihood_rating="Remote",
        business_disruption_likelihood_description="Very unlikely",
        financial_impact_low=Decimal("5000.00"),
        financial_impact_high=Decimal("25000.00"),
        date_identified=date.today() - timedelta(days=120),
        last_reviewed=date.today() - timedelta(days=30),
        next_review_date=date.today() + timedelta(days=90),
    )
    risk5.calculate_net_exposure()
    risks.append(risk5)

    # Add all risks to session
    for risk in risks:
        db_session.add(risk)

    # Add some risk log entries for activity tracking
    from app.models.risk import RiskLogEntry

    entry1 = RiskLogEntry(
        log_entry_id="LOG-TR-2024-CYB-001-01",
        risk_id="TR-2024-CYB-001",
        entry_date=date.today() - timedelta(days=15),
        created_by="Security Team",
        entry_type="Risk Assessment Change",
        entry_summary="Risk exposure increased due to new threat intelligence",
        previous_net_exposure="High (11)",
        new_net_exposure="Critical (16)",
    )
    db_session.add(entry1)

    entry2 = RiskLogEntry(
        log_entry_id="LOG-TR-2024-INF-001-01",
        risk_id="TR-2024-INF-001",
        entry_date=date.today() - timedelta(days=20),
        created_by="Infrastructure Team",
        entry_type="Risk Assessment Change",
        entry_summary="Risk exposure updated after control implementation",
        previous_net_exposure="Critical (13)",
        new_net_exposure="High (11)",
    )
    db_session.add(entry2)

    db_session.commit()
    return risks


@pytest.fixture
def sample_dropdown_values(db_session):
    """Create sample dropdown values for testing."""
    dropdown_data = [
        # Risk Categories
        ("risk_category", "Cybersecurity", 1),
        ("risk_category", "Infrastructure", 2),
        ("risk_category", "Application", 3),
        ("risk_category", "Data Management", 4),
        # Risk Status
        ("risk_status", "Active", 1),
        ("risk_status", "Monitoring", 2),
        ("risk_status", "Closed", 3),
        ("risk_status", "Accepted", 4),
        # Risk Response Strategy
        ("risk_response_strategy", "Avoid", 1),
        ("risk_response_strategy", "Mitigate", 2),
        ("risk_response_strategy", "Transfer", 3),
        ("risk_response_strategy", "Accept", 4),
        # Control Status
        ("control_status", "Adequate", 1),
        ("control_status", "Partial", 2),
        ("control_status", "Missing", 3),
        ("control_status", "Not Required", 4),
        # Business Criticality
        ("business_criticality", "Critical", 1),
        ("business_criticality", "High", 2),
        ("business_criticality", "Medium", 3),
        ("business_criticality", "Low", 4),
    ]

    dropdown_values = []
    for category, value, order in dropdown_data:
        dropdown_value = DropdownValue(category=category, value=value, display_order=order, is_active=True)
        dropdown_values.append(dropdown_value)
        db_session.add(dropdown_value)

    db_session.commit()
    return dropdown_values


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with authentication that shares the test database."""
    from app.core.config import settings

    # Use the db_session fixture's database setup (tables already created)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        # Login to get auth token
        login_response = test_client.post(
            "/api/v1/auth/login",
            auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            # Add Authorization header to all requests
            test_client.headers.update({"Authorization": f"Bearer {token}"})

        yield test_client

    app.dependency_overrides.clear()
