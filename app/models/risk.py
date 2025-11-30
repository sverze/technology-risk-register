from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: Any = declarative_base()


class Risk(Base):
    __tablename__ = "risks"

    # Core Risk Identification Fields
    risk_id = Column(String(12), primary_key=True, index=True)
    risk_title = Column(String(100), nullable=False)
    risk_category = Column(String(50), nullable=False)
    risk_description = Column(String(500), nullable=False)  # Increased from 400

    # Risk Management Fields
    risk_status = Column(String(20), nullable=False)
    risk_response_strategy = Column(String(20), nullable=False)
    planned_mitigations = Column(String(200))

    # Control Management Fields - Updated naming and increased description length
    preventative_controls_coverage = Column(String(30), nullable=False)
    preventative_controls_effectiveness = Column(String(30), nullable=False)
    preventative_controls_description = Column(String(500))  # Increased from 150
    detective_controls_coverage = Column(String(30), nullable=False)
    detective_controls_effectiveness = Column(String(30), nullable=False)
    detective_controls_description = Column(String(500))  # Increased from 150
    corrective_controls_coverage = Column(String(30), nullable=False)
    corrective_controls_effectiveness = Column(String(30), nullable=False)
    corrective_controls_description = Column(String(500))  # Increased from 150

    # Ownership & Systems Fields
    risk_owner = Column(String(50), nullable=False)
    risk_owner_department = Column(String(50), nullable=False)
    systems_affected = Column(String(150))
    technology_domain = Column(String(50), nullable=False)

    # Business Disruption Assessment Fields - New model
    ibs_affected = Column(String(200))  # Replaced boolean ibs_impact
    business_disruption_impact_rating = Column(String(20), nullable=False)  # Low/Moderate/Major/Catastrophic
    business_disruption_impact_description = Column(String(400), nullable=False)
    business_disruption_likelihood_rating = Column(String(20), nullable=False)  # Remote/Unlikely/Possible/Probable
    business_disruption_likelihood_description = Column(String(400), nullable=False)
    business_disruption_net_exposure = Column(String(30), nullable=False)  # Auto-calculated

    # Financial Impact Fields - Keep existing with addition
    financial_impact_low = Column(Numeric(12, 2))
    financial_impact_high = Column(Numeric(12, 2))
    financial_impact_notes = Column(String(200))  # New field

    # Review & Timeline Fields
    date_identified = Column(Date, nullable=False)
    last_reviewed = Column(Date, nullable=False)
    next_review_date = Column(Date, nullable=False)

    # Audit Fields
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    log_entries = relationship(
        "RiskLogEntry",
        back_populates="risk",
        cascade="all, delete-orphan",
        order_by="desc(RiskLogEntry.created_at)",
    )

    def calculate_net_exposure(self) -> None:
        """Calculate business disruption net exposure based on impact and likelihood matrix."""
        # Impact × Likelihood matrix mapping
        impact_values = {"Low": 1, "Moderate": 2, "Major": 3, "Catastrophic": 4}

        likelihood_values = {"Remote": 1, "Unlikely": 2, "Possible": 3, "Probable": 4}

        # Matrix calculation: values 1-16
        matrix = {
            (1, 1): 1,  # Low-Remote
            (1, 2): 2,  # Low-Unlikely
            (1, 3): 3,  # Low-Possible
            (1, 4): 5,  # Low-Probable
            (2, 1): 4,  # Moderate-Remote
            (2, 2): 6,  # Moderate-Unlikely
            (2, 3): 7,  # Moderate-Possible
            (2, 4): 9,  # Moderate-Probable
            (3, 1): 8,  # Major-Remote
            (3, 2): 10,  # Major-Unlikely
            (3, 3): 11,  # Major-Possible
            (3, 4): 13,  # Major-Probable
            (4, 1): 12,  # Catastrophic-Remote
            (4, 2): 14,  # Catastrophic-Unlikely
            (4, 3): 15,  # Catastrophic-Possible
            (4, 4): 16,  # Catastrophic-Probable
        }

        impact_val = impact_values.get(str(self.business_disruption_impact_rating), 1)
        likelihood_val = likelihood_values.get(str(self.business_disruption_likelihood_rating), 1)

        exposure_number = matrix.get((impact_val, likelihood_val), 1)

        # Map to exposure categories
        if exposure_number <= 4:
            category = "Low"
        elif exposure_number <= 8:
            category = "Medium"
        elif exposure_number <= 12:
            category = "High"
        else:
            category = "Critical"

        self.business_disruption_net_exposure = f"{category} ({exposure_number})"  # type: ignore[assignment]


class RiskLogEntry(Base):
    __tablename__ = "risk_log_entries"

    # Primary identification
    log_entry_id = Column(String(15), primary_key=True, index=True)
    risk_id = Column(String(12), ForeignKey("risks.risk_id"), nullable=False, index=True)

    # Entry metadata
    entry_date = Column(Date, nullable=False)
    entry_type = Column(String(50), nullable=False)  # e.g., "Risk Assessment Update", "Mitigation Completed", "Review"
    entry_summary = Column(String(500), nullable=False)

    # Business Disruption rating changes
    previous_net_exposure = Column(String(30))  # Previous net exposure (e.g., "Critical (15)")
    new_net_exposure = Column(String(30))  # New net exposure (e.g., "Critical (15)")
    previous_impact_rating = Column(String(20))  # Previous impact rating (Low/Moderate/Major/Catastrophic)
    new_impact_rating = Column(String(20))  # New impact rating (Low/Moderate/Major/Catastrophic)
    previous_likelihood_rating = Column(String(20))  # Previous likelihood rating (Remote/Unlikely/Possible/Probable)
    new_likelihood_rating = Column(String(20))  # New likelihood rating (Remote/Unlikely/Possible/Probable)

    # Actions and context
    mitigation_actions_taken = Column(String(300))  # Actions taken as part of this update
    risk_owner_at_time = Column(String(50))  # Risk owner when this entry was made
    supporting_evidence = Column(String(200))  # Links to documents, tickets, etc.

    # Workflow and approval
    entry_status = Column(String(20), default="Draft")  # Draft, Submitted, Approved, Rejected
    created_by = Column(String(50), nullable=False)  # Person who created the entry
    reviewed_by = Column(String(50))  # Person who reviewed/approved
    approved_date = Column(Date)  # Date of approval

    # Additional context
    business_justification = Column(String(300))  # Why this change was made
    next_review_required = Column(Date)  # When this should be reviewed again

    # Audit fields
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    risk = relationship("Risk", back_populates="log_entries")

    def update_parent_risk_rating(self) -> None:
        """Update the parent Risk's business disruption assessment when this log entry is approved."""
        if self.entry_status == "Approved":
            # Update the risk's business disruption rating fields
            if self.new_impact_rating is not None:
                self.risk.business_disruption_impact_rating = self.new_impact_rating  # type: ignore[assignment]
            if self.new_likelihood_rating is not None:
                self.risk.business_disruption_likelihood_rating = self.new_likelihood_rating  # type: ignore[assignment]

            # Recalculate net exposure if either rating changed
            if self.new_impact_rating is not None or self.new_likelihood_rating is not None:
                self.risk.calculate_net_exposure()

            # Update the last reviewed date to the entry date
            self.risk.last_reviewed = self.entry_date  # type: ignore[assignment]


class DropdownValue(Base):
    __tablename__ = "dropdown_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
