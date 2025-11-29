from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.risk import DropdownValue, Risk, RiskLogEntry


def seed_dropdown_values(db: Session) -> None:
    """Seed the database with dropdown values."""

    # Check if already seeded
    if db.query(DropdownValue).first():
        return

    dropdown_data = [
        # Risk Categories (unchanged)
        ("risk_category", "Cybersecurity", 1),
        ("risk_category", "Infrastructure", 2),
        ("risk_category", "Application", 3),
        ("risk_category", "Data Management", 4),
        ("risk_category", "Cloud Services", 5),
        ("risk_category", "Vendor/Third Party", 6),
        ("risk_category", "Regulatory/Compliance", 7),
        ("risk_category", "Operational", 8),
        # Risk Status (unchanged)
        ("risk_status", "Active", 1),
        ("risk_status", "Monitoring", 2),
        ("risk_status", "Closed", 3),
        ("risk_status", "Accepted", 4),
        # Risk Response Strategy (unchanged)
        ("risk_response_strategy", "Avoid", 1),
        ("risk_response_strategy", "Mitigate", 2),
        ("risk_response_strategy", "Transfer", 3),
        ("risk_response_strategy", "Accept", 4),
        # Business Disruption Impact Rating (NEW)
        ("business_disruption_impact_rating", "Low", 1),
        ("business_disruption_impact_rating", "Moderate", 2),
        ("business_disruption_impact_rating", "Major", 3),
        ("business_disruption_impact_rating", "Catastrophic", 4),
        # Business Disruption Likelihood Rating (NEW)
        ("business_disruption_likelihood_rating", "Remote", 1),
        ("business_disruption_likelihood_rating", "Unlikely", 2),
        ("business_disruption_likelihood_rating", "Possible", 3),
        ("business_disruption_likelihood_rating", "Probable", 4),
        # Controls Coverage (NEW - replaces control_status)
        ("controls_coverage", "Not Applicable", 1),
        ("controls_coverage", "No Controls", 2),
        ("controls_coverage", "Incomplete Coverage", 3),
        ("controls_coverage", "Complete Coverage", 4),
        # Controls Effectiveness (NEW)
        ("controls_effectiveness", "Not Applicable", 1),
        ("controls_effectiveness", "Not Possible to Assess", 2),
        ("controls_effectiveness", "Partially Effective", 3),
        ("controls_effectiveness", "Fully Effective", 4),
        # Risk Owner Department (unchanged)
        ("risk_owner_department", "Information Technology", 1),
        ("risk_owner_department", "Cybersecurity", 2),
        ("risk_owner_department", "Operations", 3),
        ("risk_owner_department", "Finance", 4),
        ("risk_owner_department", "Legal/Compliance", 5),
        ("risk_owner_department", "Business Units", 6),
        # Technology Domain (unchanged)
        ("technology_domain", "Infrastructure", 1),
        ("technology_domain", "Applications", 2),
        ("technology_domain", "Data/Databases", 3),
        ("technology_domain", "Network/Communications", 4),
        ("technology_domain", "Security Systems", 5),
        ("technology_domain", "Cloud Services", 6),
        # Update Type (unchanged)
        ("update_type", "Risk Assessment Change", 1),
        ("update_type", "Control Update", 2),
        ("update_type", "Status Change", 3),
        ("update_type", "Incident/Event", 4),
        ("update_type", "Review/Reassessment", 5),
    ]

    for category, value, order in dropdown_data:
        dropdown_value = DropdownValue(category=category, value=value, display_order=order)
        db.add(dropdown_value)

    db.commit()


def seed_sample_risks(db: Session) -> None:
    """Seed the database with realistic technology risks for Ki Insurance."""

    # Check if already seeded
    if db.query(Risk).first():
        return

    sample_risks = [
        # TR-2025-001: Enterprise Data Loss Event
        {
            "risk_id": "TR-2025-001",
            "risk_title": "Enterprise Data Loss Event",
            "risk_category": "Data Management",
            "risk_description": "Local (aka native) backups with or without defined RPO/RTO targets can fail due to critical risk events such as misconfiguration (UniSuper-style account deletion), backup system failures (OVH fire), and ransomware attacks (Kaseya-style encryption). No enterprise-wide 3-2-1 backup strategy exists with applications relying solely on cloud-provider native backup solutions. In most cases, undefined RTO/RPO targets and untested recovery procedures create potential for permanent data loss and business closure.",
            "risk_status": "Active",
            "risk_owner": "Tom Yandell",
            "risk_owner_department": "Information Technology",
            "technology_domain": "Data/Databases",
            "risk_response_strategy": "Mitigate",
            "systems_affected": "All systems with permanent data storage or configuration repositories",
            "ibs_affected": "ALL",
            "business_disruption_impact_rating": "Catastrophic",
            "business_disruption_impact_description": "IBS will be severely disrupted without a recoverable backup and process to restore. The outages could be weeks/months and reputational damage impaired and likely in some cases, completely fail. A full simulated series of non-functional tests in a fully loaded near identical non-production environment is required for each of the IBS applications to determine the full outcome native backup failure event.",
            "business_disruption_likelihood_rating": "Possible",
            "business_disruption_likelihood_description": "Control gaps across all pillars but specifically with the most critical safeguards such as preventative backup testing and integrity monitoring, the detective SOC and TOC and finally the corrective 3-2-1 backups. The Sentinel project maturation of BCP is essential and this scenario must be considered critical in their planning.",
            "preventative_controls_coverage": "Incomplete Coverage",
            "preventative_controls_effectiveness": "Partially Effective",
            "preventative_controls_description": "Configuration Drift Detection - CSPM tool, Wiz, in place, Azure Config in place. Overall infra state drift tool missing. Backup Testing and Integrity Monitoring - no regular testing in place, and no integrity tool(s) are being used. Endpoint Detection and Response - DarkTrace and Microsoft Defender are being reviewed although not clear whether server EP are covered.",
            "detective_controls_coverage": "Incomplete Coverage",
            "detective_controls_effectiveness": "Not Possible to Assess",
            "detective_controls_description": "Security and Technology Operation Centres - SOC service integration with Ontinue progressing for October 2025; build-it-run-it TOC model under development.",
            "corrective_controls_coverage": "Incomplete Coverage",
            "corrective_controls_effectiveness": "Not Possible to Assess",
            "corrective_controls_description": "Business Continuity Site Activation - BCP plan in development through project Sentinel. 3-2-1 Backup Strategy - No strategy in place, dependent on native backup. Crisis Communication and Stakeholder Management - BCP plan in development through project Sentinel. Emergency Vendor and Service Provider Activation - BCP plan in development through project Sentinel.",
            "financial_impact_low": Decimal("19000000.00"),
            "financial_impact_high": Decimal("250000000.00"),
            "financial_impact_notes": "Low: 1 week outage / 100% of GWP. High: 3 months outage / 100% of GWP",
            "planned_mitigations": "TBC",
            "date_identified": date(2025, 8, 28),
            "last_reviewed": date(2025, 9, 8),
            "next_review_date": date(2025, 10, 8),
        },
        # TR-2025-002: GKE Platform Multi-Tenant Failure
        {
            "risk_id": "TR-2025-002",
            "risk_title": "GKE Platform Multi-Tenant Failure",
            "risk_category": "Infrastructure",
            "risk_description": "Multi-tenant GKE platform hosting all front-office systems suffers from infrastructure challenges including resource management guardrails such as memory exhaustion incidents from misconfigured applications, single load balancer dependency for customer whitelisting, and inability to test non-functional failure scenarios due to lack of environment(s). Platform failure would simultaneously affect all containerised workloads preventing quote generation, data analytics, and customer services.",
            "risk_status": "Active",
            "risk_owner": "Tom Yandell",
            "risk_owner_department": "Information Technology",
            "technology_domain": "Infrastructure",
            "risk_response_strategy": "Mitigate",
            "systems_affected": "Algo, DSS, KiWeb, all GKE-hosted front-office applications",
            "ibs_affected": "ALL front-office IBS",
            "business_disruption_impact_rating": "Moderate",
            "business_disruption_impact_description": "IBS will be impaired and could in some cases completely fail. All front-office applications (Algo, DSS, KiWeb) simultaneously affected during platform failures. Quote generation and customer service response times severely impacted. A full simulated series of non-functional tests in a fully loaded near identical non-production environment is required for each of the IBS applications to determine the full outcome of a GKE disruption event.",
            "business_disruption_likelihood_rating": "Possible",
            "business_disruption_likelihood_description": "Control gaps in preventative measures and incomplete implementation of corrective and detective controls. While cluster capacity is adequate, workload-level configurations for resource management and zone distribution are not enforced, and testing capabilities remain limited.",
            "preventative_controls_coverage": "No Controls",
            "preventative_controls_effectiveness": "Not Possible to Assess",
            "preventative_controls_description": "Chaos Engineering - No capability implemented; single production environment prevents failure testing. Disconnected Testing - Not possible as capability not implemented in any environment. Resource management - Improvements underway but preventative testing remains difficult without adequate test environment.",
            "detective_controls_coverage": "Incomplete Coverage",
            "detective_controls_effectiveness": "Partially Effective",
            "detective_controls_description": "Observability - Grafana and Prometheus federated to Google Managed Prometheus providing external visibility. However, missing alerts for cross-platform dependencies and some monitoring gaps remain. Google Cloud Monitoring provides cluster health monitoring but would struggle with significant lights-out service incidents.",
            "corrective_controls_coverage": "Incomplete Coverage",
            "corrective_controls_effectiveness": "Partially Effective",
            "corrective_controls_description": "Multi-Zone Rescheduling - Multi-zone GKE implemented with adequate resource capacity for zone failures. However, workloads lack anti-affinity configurations. Reduced Blast Radius - Spitting out critical application, not implemented. Adequate Resources - Partially implemented with doubled capacity but workload resource requests/limits not properly configured. 3rd Line Support - Run-books and rehearsals possible and partially implemented.",
            "financial_impact_low": Decimal("1500000.00"),
            "financial_impact_high": Decimal("4000000.00"),
            "financial_impact_notes": "Low: 3 hours outage / 100% of GWP. High: 1 day outage / 100% of GWP",
            "planned_mitigations": "Migration to 10.x network, dedicated node pools for critical workloads, comprehensive testing environment, chaos engineering implementation",
            "date_identified": date(2025, 8, 28),
            "last_reviewed": date(2025, 9, 8),
            "next_review_date": date(2025, 10, 8),
        },
        # TR-2025-003: Identity Provider Cascade Failure
        {
            "risk_id": "TR-2025-003",
            "risk_title": "Identity Provider Cascade Failure",
            "risk_category": "Cybersecurity",
            "risk_description": "Ki operates dual-tenant identity architecture with both Azure and GCP foundations depending entirely on Brit-managed Entra ID without an off-site data back-up or secondary authentication systems. Identity provider failure would immediately disable access to M365, cloud foundations, and federated SaaS applications, with cascade effects lasting 90 minutes to 14 hours based on historical Microsoft Entra incidents (2021, 2024, 2025).",
            "risk_status": "Active",
            "risk_owner": "Sean Duff",
            "risk_owner_department": "Infrastructure",
            "technology_domain": "Security Systems",
            "risk_response_strategy": "Mitigate",
            "systems_affected": "M365 suite, Azure/GCP portals, all federated SaaS applications, Infrastructure-as-Code via GitHub",
            "ibs_affected": "TBC",
            "business_disruption_impact_rating": "Major",
            "business_disruption_impact_description": "Ki business and technology operational staff will be shut out of most tools and services. Front office access is token based thus customers should not be immediately impacted. Although back office applications are mostly SaaS or Azure hosted and will be impacted. Complete authentication failure with existing tokens expiring causing cascading service failures.",
            "business_disruption_likelihood_rating": "Probable",
            "business_disruption_likelihood_description": "Control gaps in preventative measures and incomplete implementation of corrective and detective controls, with most critical safeguards like secondary IdP, break glass procedures, and synthetic testing either not implemented or not fully deployed. Likely to occur more frequently than every 5 years based on past incidents.",
            "preventative_controls_coverage": "No Controls",
            "preventative_controls_effectiveness": "Not Possible to Assess",
            "preventative_controls_description": "Change Management - Not possible as customers cannot control Microsoft deployment processes. Vendor Management - Not implemented; no monthly business reviews with Microsoft. Canary Deployments - Not possible with Entra in current architecture.",
            "detective_controls_coverage": "Incomplete Coverage",
            "detective_controls_effectiveness": "Not Possible to Assess",
            "detective_controls_description": "Synthetic Testing - Not implemented; no periodic authentication testing across IBS or Azure Service Health API integration for proactive incident detection.",
            "corrective_controls_coverage": "Incomplete Coverage",
            "corrective_controls_effectiveness": "Not Possible to Assess",
            "corrective_controls_description": "Secondary IdP - Okta configured as identity broker only, not standalone IdP. DR and Backup - Not implemented; Rubrik planned but not deployed. Break Glass - Partially implemented with 1Password for platform teams, documented Azure/M365 run book exists. 3rd Line Support - Partially implemented with MS Graph API access and GitHub maintaining Azure resource access.",
            "financial_impact_low": Decimal("500000.00"),
            "financial_impact_high": Decimal("2000000.00"),
            "financial_impact_notes": "Low: 4 hours outage / 25% of GWP. High: 2 days outage / 25% of GWP",
            "planned_mitigations": "Convert Okta from broker/bridge to secondary IdP, implement comprehensive break-glass procedures, deploy synthetic authentication monitoring.",
            "date_identified": date(2025, 8, 28),
            "last_reviewed": date(2025, 9, 8),
            "next_review_date": date(2025, 10, 8),
        },
    ]

    # Create Risk objects and add to database
    created_risks = []
    for risk_data in sample_risks:
        risk = Risk(**risk_data)
        risk.calculate_net_exposure()
        db.add(risk)
        created_risks.append(risk)

    # Commit risks first
    db.commit()

    # Add sample risk updates for some risks
    sample_updates = [
        # Update for critical cyber risk
        {
            "log_entry_id": "LOG-CYB-001-01",
            "risk_id": "TR-2025-CYB-001",
            "entry_date": date.today() - timedelta(days=30),
            "created_by": "Sarah Chen",
            "entry_type": "Risk Assessment Change",
            "entry_summary": "Risk rating increased due to new threat intelligence indicating targeting of our sector",
            "previous_risk_rating": 12,
            "new_risk_rating": 15,
        },
        {
            "log_entry_id": "LOG-CYB-001-02",
            "risk_id": "TR-2025-CYB-001",
            "entry_date": date.today() - timedelta(days=14),
            "created_by": "Sarah Chen",
            "entry_type": "Control Update",
            "entry_summary": "Implemented additional endpoint detection capabilities, slightly reducing exposure",
            "previous_risk_rating": 15,
            "new_risk_rating": 15,
        },
        # Update for infrastructure risk
        {
            "log_entry_id": "LOG-INF-002-01",
            "risk_id": "TR-2025-INF-002",
            "entry_date": date.today() - timedelta(days=21),
            "created_by": "Michael Rodriguez",
            "entry_type": "Status Change",
            "entry_summary": "UPS replacement project approved and scheduled for Q2 2025",
            "previous_risk_rating": 12,
            "new_risk_rating": 8,
        },
        # Update for application risk
        {
            "log_entry_id": "LOG-APP-003-01",
            "risk_id": "TR-2025-APP-003",
            "entry_date": date.today() - timedelta(days=35),
            "created_by": "Jennifer Park",
            "entry_type": "Review/Reassessment",
            "entry_summary": "Quarterly review completed. Migration timeline confirmed, risk level maintained",
            "previous_risk_rating": 16,
            "new_risk_rating": 16,
        },
        # Update for operational risk
        {
            "log_entry_id": "LOG-OPS-008-01",
            "risk_id": "TR-2025-OPS-008",
            "entry_date": date.today() - timedelta(days=10),
            "created_by": "Thomas Garcia",
            "entry_type": "Control Update",
            "entry_summary": "Knowledge transfer sessions initiated with junior staff. Documentation project 40% complete",
            "previous_risk_rating": 12,
            "new_risk_rating": 9,
        },
    ]

    # Create RiskLogEntry objects and add to database
    for update_data in sample_updates:
        # Check if log entry already exists
        existing_entry = db.query(RiskLogEntry).filter(RiskLogEntry.log_entry_id == update_data["log_entry_id"]).first()

        if existing_entry:
            print(f"Skipping existing log entry: {update_data['log_entry_id']}")
            continue

        try:
            update = RiskLogEntry(**update_data)
            db.add(update)
            print(f"Added log entry: {update_data['log_entry_id']}")
        except Exception as e:
            print(f"Error creating log entry {update_data['log_entry_id']}: {e}")
            continue

    try:
        db.commit()
        print("Successfully committed risk log entries")
    except Exception as e:
        print(f"Error committing risk log entries: {e}")
        db.rollback()
