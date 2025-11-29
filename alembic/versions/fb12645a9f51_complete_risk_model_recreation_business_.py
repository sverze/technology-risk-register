"""Complete Risk Model Recreation - Business Disruption Model

Revision ID: fb12645a9f51
Revises: 70cfbd2a804e
Create Date: 2025-09-21 12:24:27.433242

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fb12645a9f51"
down_revision: str | Sequence[str] | None = "70cfbd2a804e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - Complete recreation for Business Disruption model."""
    # Drop existing tables to start fresh
    op.drop_table("risk_log_entries")
    op.drop_table("risks")
    op.drop_table("dropdown_values")

    # Create dropdown_values table
    op.create_table(
        "dropdown_values",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dropdown_values_category"), "dropdown_values", ["category"], unique=False)

    # Create risks table with new Business Disruption model
    op.create_table(
        "risks",
        # Core Risk Identification Fields
        sa.Column("risk_id", sa.String(length=12), nullable=False),
        sa.Column("risk_title", sa.String(length=100), nullable=False),
        sa.Column("risk_category", sa.String(length=50), nullable=False),
        sa.Column("risk_description", sa.String(length=500), nullable=False),  # Increased from 400
        # Risk Management Fields
        sa.Column("risk_status", sa.String(length=20), nullable=False),
        sa.Column("risk_response_strategy", sa.String(length=20), nullable=False),
        sa.Column("planned_mitigations", sa.String(length=200), nullable=True),
        # Control Management Fields - Updated naming and increased description length
        sa.Column("preventative_controls_coverage", sa.String(length=30), nullable=False),
        sa.Column("preventative_controls_effectiveness", sa.String(length=30), nullable=False),
        sa.Column("preventative_controls_description", sa.String(length=500), nullable=True),  # Increased from 150
        sa.Column("detective_controls_coverage", sa.String(length=30), nullable=False),
        sa.Column("detective_controls_effectiveness", sa.String(length=30), nullable=False),
        sa.Column("detective_controls_description", sa.String(length=500), nullable=True),  # Increased from 150
        sa.Column("corrective_controls_coverage", sa.String(length=30), nullable=False),
        sa.Column("corrective_controls_effectiveness", sa.String(length=30), nullable=False),
        sa.Column("corrective_controls_description", sa.String(length=500), nullable=True),  # Increased from 150
        # Ownership & Systems Fields
        sa.Column("risk_owner", sa.String(length=50), nullable=False),
        sa.Column("risk_owner_department", sa.String(length=50), nullable=False),
        sa.Column("systems_affected", sa.String(length=150), nullable=True),
        sa.Column("technology_domain", sa.String(length=50), nullable=False),
        # Business Disruption Assessment Fields - New model
        sa.Column("ibs_affected", sa.String(length=200), nullable=True),  # Replaced boolean ibs_impact
        sa.Column("business_disruption_impact_rating", sa.String(length=20), nullable=False),
        sa.Column("business_disruption_impact_description", sa.String(length=400), nullable=False),
        sa.Column("business_disruption_likelihood_rating", sa.String(length=20), nullable=False),
        sa.Column("business_disruption_likelihood_description", sa.String(length=400), nullable=False),
        sa.Column("business_disruption_net_exposure", sa.String(length=30), nullable=False),  # Auto-calculated
        # Financial Impact Fields
        sa.Column("financial_impact_low", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("financial_impact_high", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("financial_impact_notes", sa.String(length=200), nullable=True),  # New field
        # Review & Timeline Fields
        sa.Column("date_identified", sa.Date(), nullable=False),
        sa.Column("last_reviewed", sa.Date(), nullable=False),
        sa.Column("next_review_date", sa.Date(), nullable=False),
        # Audit Fields
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("risk_id"),
    )
    op.create_index(op.f("ix_risks_risk_id"), "risks", ["risk_id"], unique=False)

    # Create risk_log_entries table with new Business Disruption rating system
    op.create_table(
        "risk_log_entries",
        # Primary identification
        sa.Column("log_entry_id", sa.String(length=15), nullable=False),
        sa.Column("risk_id", sa.String(length=12), nullable=False),
        # Entry metadata
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("entry_summary", sa.String(length=500), nullable=False),
        # Business Disruption rating changes
        sa.Column("previous_net_exposure", sa.String(length=30), nullable=True),
        sa.Column("new_net_exposure", sa.String(length=30), nullable=True),
        sa.Column("previous_impact_rating", sa.String(length=20), nullable=True),
        sa.Column("new_impact_rating", sa.String(length=20), nullable=True),
        sa.Column("previous_likelihood_rating", sa.String(length=20), nullable=True),
        sa.Column("new_likelihood_rating", sa.String(length=20), nullable=True),
        # Actions and context
        sa.Column("mitigation_actions_taken", sa.String(length=300), nullable=True),
        sa.Column("risk_owner_at_time", sa.String(length=50), nullable=True),
        sa.Column("supporting_evidence", sa.String(length=200), nullable=True),
        # Workflow and approval
        sa.Column("entry_status", sa.String(length=20), nullable=True),
        sa.Column("created_by", sa.String(length=50), nullable=False),
        sa.Column("reviewed_by", sa.String(length=50), nullable=True),
        sa.Column("approved_date", sa.Date(), nullable=True),
        # Additional context
        sa.Column("business_justification", sa.String(length=300), nullable=True),
        sa.Column("next_review_required", sa.Date(), nullable=True),
        # Audit fields
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["risk_id"],
            ["risks.risk_id"],
        ),
        sa.PrimaryKeyConstraint("log_entry_id"),
    )
    op.create_index(op.f("ix_risk_log_entries_log_entry_id"), "risk_log_entries", ["log_entry_id"], unique=False)
    op.create_index(op.f("ix_risk_log_entries_risk_id"), "risk_log_entries", ["risk_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new tables
    op.drop_table("risk_log_entries")
    op.drop_table("risks")
    op.drop_table("dropdown_values")
