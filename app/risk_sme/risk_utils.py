"""
Utility functions for the Risk SME Agent.
Provides schema introspection and helper functions for SQLAlchemy Risk models.
"""

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.risk import DropdownValue, Risk, RiskLogEntry


def build_sqlalchemy_schema(session: Session) -> str:
    """
    Build a human-readable schema description for the Risk model.
    Returns a formatted string describing tables, columns, types, and relationships.
    """
    lines = []

    # Risk table schema
    lines.append("=" * 80)
    lines.append("TABLE: risks")
    lines.append("=" * 80)
    lines.append("")
    lines.append("COLUMNS:")

    inspector = inspect(Risk)
    for col in inspector.columns:
        col_type = str(col.type)
        nullable = "NULL" if col.nullable else "NOT NULL"
        primary = "PRIMARY KEY" if col.primary_key else ""

        extra_info = f"{nullable} {primary}".strip()
        lines.append(f"  - {col.name}: {col_type} {extra_info}")

    lines.append("")
    lines.append("RELATIONSHIPS:")
    lines.append("  - log_entries: List[RiskLogEntry] (one-to-many)")
    lines.append("    Access via: risk.log_entries")

    lines.append("")
    lines.append("")

    # RiskLogEntry table schema
    lines.append("=" * 80)
    lines.append("TABLE: risk_log_entries")
    lines.append("=" * 80)
    lines.append("")
    lines.append("COLUMNS:")

    inspector = inspect(RiskLogEntry)
    for col in inspector.columns:
        col_type = str(col.type)
        nullable = "NULL" if col.nullable else "NOT NULL"
        primary = "PRIMARY KEY" if col.primary_key else ""
        foreign = "FOREIGN KEY -> risks.risk_id" if col.name == "risk_id" else ""

        extra_info = f"{nullable} {primary} {foreign}".strip()
        lines.append(f"  - {col.name}: {col_type} {extra_info}")

    lines.append("")
    lines.append("RELATIONSHIPS:")
    lines.append("  - risk: Risk (many-to-one)")
    lines.append("    Access via: log_entry.risk")

    return "\n".join(lines)


def get_sample_risks(session: Session, limit: int = 3) -> list[dict[str, Any]]:
    """
    Fetch sample risks to show data patterns.
    Returns a list of dictionaries with key fields.
    """
    risks = session.query(Risk).limit(limit).all()

    samples = []
    for risk in risks:
        samples.append(
            {
                "risk_id": risk.risk_id,
                "risk_title": risk.risk_title,
                "risk_category": risk.risk_category,
                "risk_status": risk.risk_status,
                "technology_domain": risk.technology_domain,
                "risk_owner": risk.risk_owner,
                "business_disruption_net_exposure": risk.business_disruption_net_exposure,
                "log_entry_count": len(risk.log_entries) if risk.log_entries else 0,
            }
        )

    return samples


def get_dropdown_values(session: Session) -> dict[str, list[str]]:
    """
    Extract valid enum values from DropdownValue table.
    Returns a dictionary mapping category names to their valid values.
    """
    dropdown_values = (
        session.query(DropdownValue)
        .filter(DropdownValue.is_active)
        .order_by(DropdownValue.category, DropdownValue.display_order)
        .all()
    )

    categories = {}
    for dv in dropdown_values:
        if dv.category not in categories:
            categories[dv.category] = []
        categories[dv.category].append(dv.value)

    return categories


def build_schema_block(session: Session) -> str:
    """
    Build a complete schema block for the LLM prompt.
    Includes table schemas, sample data, and domain-specific notes.
    """
    schema = build_sqlalchemy_schema(session)
    samples = get_sample_risks(session, limit=3)
    dropdowns = get_dropdown_values(session)

    lines = [schema, ""]

    # Add sample data
    lines.append("=" * 80)
    lines.append("SAMPLE DATA (first 3 risks):")
    lines.append("=" * 80)
    for i, sample in enumerate(samples, 1):
        lines.append(f"\n{i}. {sample['risk_id']}: {sample['risk_title']}")
        lines.append(f"   Category: {sample['risk_category']}, Status: {sample['risk_status']}")
        lines.append(f"   Domain: {sample['technology_domain']}, Owner: {sample['risk_owner']}")
        lines.append(f"   Exposure: {sample['business_disruption_net_exposure']}")
        lines.append(f"   Log Entries: {sample['log_entry_count']}")

    lines.append("\n")

    # Add dropdown values
    lines.append("=" * 80)
    lines.append("VALID VALUES (from dropdown_values table):")
    lines.append("=" * 80)
    for category, values in sorted(dropdowns.items()):
        lines.append(f"\n{category}:")
        for val in values:
            lines.append(f"  - {val}")

    lines.append("\n")

    # Add domain notes
    lines.append("=" * 80)
    lines.append("DOMAIN NOTES:")
    lines.append("=" * 80)
    lines.append(
        """
CALCULATED FIELDS:
- business_disruption_net_exposure is AUTO-CALCULATED from impact × likelihood
  Format: "Category (number)" e.g., "Critical (15)", "High (11)", "Medium (7)", "Low (3)"
  Do NOT try to filter or set this field directly

RELATIONSHIPS:
- To get log entries for a risk: risk.log_entries (returns list)
- To count log entries: len(risk.log_entries)
- To get risk from log entry: log_entry.risk (returns Risk object)

DATE QUERIES:
- Use datetime.date for comparisons with Date columns
- Example: from datetime import date, timedelta
  recent = date.today() - timedelta(days=30)
  risks = session.query(Risk).filter(Risk.last_reviewed >= recent).all()

COMMON QUERY PATTERNS:
- Filter by category: Risk.risk_category == "Technology"
- Filter by status: Risk.risk_status == "Active"
- Filter by owner: Risk.risk_owner.like("%Smith%")
- Filter by exposure: Risk.business_disruption_net_exposure.like("Critical%")
- Multiple conditions: session.query(Risk).filter(and_(condition1, condition2))
- Either/or conditions: session.query(Risk).filter(or_(condition1, condition2))

TEXT SEARCH:
- Exact match: Risk.risk_title == "Database Failure"
- Partial match: Risk.risk_title.like("%database%")  (case-sensitive)
- Case-insensitive: Risk.risk_title.ilike("%database%")  (SQLite specific)

AGGREGATIONS:
- Count: session.query(Risk).filter(...).count()
- Group by: session.query(Risk.technology_domain, func.count()).group_by(Risk.technology_domain)
    """.strip()
    )

    return "\n".join(lines)


def format_risk_for_display(risk: Risk) -> dict[str, Any]:
    """
    Format a Risk object for user-friendly display.
    Returns a dictionary with key information.
    """
    return {
        "id": risk.risk_id,
        "title": risk.risk_title,
        "category": risk.risk_category,
        "status": risk.risk_status,
        "domain": risk.technology_domain,
        "owner": risk.risk_owner,
        "exposure": risk.business_disruption_net_exposure,
        "last_reviewed": str(risk.last_reviewed),
        "next_review": str(risk.next_review_date),
    }
