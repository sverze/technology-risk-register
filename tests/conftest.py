import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.main import app
from app.models.risk import Base, DropdownValue, Risk

# Test database URL - use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
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
        inherent_probability=3,
        inherent_impact=4,
        current_probability=3,
        current_impact=4,
        risk_status="Open",
        risk_response_strategy="Mitigate",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Adequate",
        risk_owner_department="IT",
        technology_domain="Security",
        ibs_impact=False,
        business_criticality="Medium",
        date_identified=date.today(),
        last_reviewed=date.today(),
        next_review_date=date.today(),
    )
    risk1.calculate_risk_ratings()

    risk2 = Risk(
        risk_id="TR-2024-INF-001",
        risk_title="Infrastructure Risk",
        risk_description="Test infrastructure risk",
        risk_category="Infrastructure",
        risk_owner="Test User 2",
        inherent_probability=2,
        inherent_impact=3,
        current_probability=2,
        current_impact=3,
        risk_status="Open",
        risk_response_strategy="Mitigate",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Adequate",
        risk_owner_department="Operations",
        technology_domain="Infrastructure",
        ibs_impact=True,
        business_criticality="High",
        date_identified=date.today(),
        last_reviewed=date.today(),
        next_review_date=date.today(),
    )
    risk2.calculate_risk_ratings()

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
        inherent_probability=5,
        inherent_impact=5,
        current_probability=4,
        current_impact=4,
        risk_status="Active",
        risk_response_strategy="Mitigate",
        preventative_controls_status="Adequate",
        detective_controls_status="Inadequate",
        corrective_controls_status="Adequate",
        control_gaps="Missing monitoring tools",
        risk_owner_department="IT",
        technology_domain="Security",
        ibs_impact=True,
        number_of_ibs_affected=5,
        business_criticality="Critical",
        financial_impact_low=Decimal("500000.00"),
        financial_impact_high=Decimal("2000000.00"),
        date_identified=date.today() - timedelta(days=30),
        last_reviewed=date.today() - timedelta(days=10),
        next_review_date=date.today() + timedelta(days=20),
    )
    risk1.calculate_risk_ratings()
    risks.append(risk1)

    # High risk
    risk2 = Risk(
        risk_id="TR-2024-INF-001",
        risk_title="Infrastructure Failure",
        risk_description="Critical infrastructure failure risk",
        risk_category="Infrastructure",
        risk_owner="Infrastructure Team",
        inherent_probability=4,
        inherent_impact=3,
        current_probability=3,
        current_impact=4,
        risk_status="Active",
        risk_response_strategy="Accept",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Adequate",
        risk_owner_department="Operations",
        technology_domain="Infrastructure",
        ibs_impact=True,
        number_of_ibs_affected=3,
        business_criticality="High",
        financial_impact_low=Decimal("100000.00"),
        financial_impact_high=Decimal("800000.00"),
        date_identified=date.today() - timedelta(days=60),
        last_reviewed=date.today() - timedelta(days=15),
        next_review_date=date.today() + timedelta(days=15),
    )
    risk2.calculate_risk_ratings()
    risks.append(risk2)

    # Medium risk
    risk3 = Risk(
        risk_id="TR-2024-APP-001",
        risk_title="Application Performance",
        risk_description="Application performance degradation",
        risk_category="Application",
        risk_owner="Development Team",
        inherent_probability=3,
        inherent_impact=2,
        current_probability=2,
        current_impact=3,
        risk_status="Monitoring",
        risk_response_strategy="Transfer",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Inadequate",
        risk_owner_department="Engineering",
        technology_domain="Applications",
        ibs_impact=False,
        business_criticality="Medium",
        financial_impact_low=Decimal("10000.00"),
        financial_impact_high=Decimal("50000.00"),
        date_identified=date.today() - timedelta(days=45),
        last_reviewed=date.today(),
        next_review_date=date.today() + timedelta(days=30),
    )
    risk3.calculate_risk_ratings()
    risks.append(risk3)

    # Low risk
    risk4 = Risk(
        risk_id="TR-2024-OPS-001",
        risk_title="Operational Process Gap",
        risk_description="Minor operational process improvement needed",
        risk_category="Operational",
        risk_owner="Operations Team",
        inherent_probability=2,
        inherent_impact=2,
        current_probability=1,
        current_impact=2,
        risk_status="Active",
        risk_response_strategy="Avoid",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Adequate",
        risk_owner_department="Operations",
        technology_domain="Business Process",
        ibs_impact=False,
        business_criticality="Low",
        financial_impact_low=Decimal("1000.00"),
        financial_impact_high=Decimal("5000.00"),
        date_identified=date.today() - timedelta(days=90),
        last_reviewed=date.today() - timedelta(days=60),
        next_review_date=date.today() - timedelta(days=5),  # Overdue
    )
    risk4.calculate_risk_ratings()
    risks.append(risk4)

    # Closed risk (should not appear in dashboard)
    risk5 = Risk(
        risk_id="TR-2024-CLD-001",
        risk_title="Closed Cloud Risk",
        risk_description="This risk has been closed",
        risk_category="Cloud Services",
        risk_owner="Cloud Team",
        inherent_probability=3,
        inherent_impact=3,
        current_probability=1,
        current_impact=1,
        risk_status="Closed",
        risk_response_strategy="Mitigate",
        preventative_controls_status="Adequate",
        detective_controls_status="Adequate",
        corrective_controls_status="Adequate",
        risk_owner_department="IT",
        technology_domain="Cloud",
        ibs_impact=False,
        business_criticality="Low",
        financial_impact_low=Decimal("5000.00"),
        financial_impact_high=Decimal("25000.00"),
        date_identified=date.today() - timedelta(days=120),
        last_reviewed=date.today() - timedelta(days=30),
        next_review_date=date.today() + timedelta(days=90),
    )
    risk5.calculate_risk_ratings()
    risks.append(risk5)

    # Add all risks to session
    for risk in risks:
        db_session.add(risk)

    # Add some risk updates for activity tracking
    from app.models.risk import RiskLogEntry

    update1 = RiskLogEntry(
        update_id="UPD-TR-2024-CYB-001-01",
        risk_id="TR-2024-CYB-001",
        update_date=date.today() - timedelta(days=15),
        updated_by="Security Team",
        update_type="Risk Assessment Change",
        update_summary="Risk rating increased due to new threat intelligence",
        previous_risk_rating="12 (High)",
        new_risk_rating="16 (Critical)",
    )
    db_session.add(update1)

    update2 = RiskLogEntry(
        update_id="UPD-TR-2024-INF-001-01",
        risk_id="TR-2024-INF-001",
        update_date=date.today() - timedelta(days=20),
        updated_by="Infrastructure Team",
        update_type="Risk Assessment Change",
        update_summary="Risk rating updated after control implementation",
        previous_risk_rating="15 (Critical)",
        new_risk_rating="12 (High)",
    )
    db_session.add(update2)

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
        dropdown_value = DropdownValue(
            category=category, value=value, display_order=order, is_active=True
        )
        dropdown_values.append(dropdown_value)
        db_session.add(dropdown_value)

    db_session.commit()
    return dropdown_values


@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
