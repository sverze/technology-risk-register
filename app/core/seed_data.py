from sqlalchemy.orm import Session

from app.models.risk import DropdownValue


def seed_dropdown_values(db: Session) -> None:
    """Seed the database with dropdown values."""

    # Check if already seeded
    if db.query(DropdownValue).first():
        return

    dropdown_data = [
        # Risk Categories
        ("risk_category", "Cybersecurity", 1),
        ("risk_category", "Infrastructure", 2),
        ("risk_category", "Application", 3),
        ("risk_category", "Data Management", 4),
        ("risk_category", "Cloud Services", 5),
        ("risk_category", "Vendor/Third Party", 6),
        ("risk_category", "Regulatory/Compliance", 7),
        ("risk_category", "Operational", 8),
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
        # Risk Owner Department
        ("risk_owner_department", "Information Technology", 1),
        ("risk_owner_department", "Cybersecurity", 2),
        ("risk_owner_department", "Operations", 3),
        ("risk_owner_department", "Finance", 4),
        ("risk_owner_department", "Legal/Compliance", 5),
        ("risk_owner_department", "Business Units", 6),
        # Technology Domain
        ("technology_domain", "Infrastructure", 1),
        ("technology_domain", "Applications", 2),
        ("technology_domain", "Data/Databases", 3),
        ("technology_domain", "Network/Communications", 4),
        ("technology_domain", "Security Systems", 5),
        ("technology_domain", "Cloud Services", 6),
        # Business Criticality
        ("business_criticality", "Critical", 1),
        ("business_criticality", "High", 2),
        ("business_criticality", "Medium", 3),
        ("business_criticality", "Low", 4),
        # Update Type
        ("update_type", "Risk Assessment Change", 1),
        ("update_type", "Control Update", 2),
        ("update_type", "Status Change", 3),
        ("update_type", "Incident/Event", 4),
        ("update_type", "Review/Reassessment", 5),
    ]

    for category, value, order in dropdown_data:
        dropdown_value = DropdownValue(
            category=category, value=value, display_order=order
        )
        db.add(dropdown_value)

    db.commit()
