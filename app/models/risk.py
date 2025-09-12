from datetime import UTC, datetime

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

Base = declarative_base()


class Risk(Base):
    __tablename__ = "risks"

    # Core Risk Identification Fields
    risk_id = Column(String(12), primary_key=True, index=True)
    risk_title = Column(String(100), nullable=False)
    risk_category = Column(String(50), nullable=False)
    risk_description = Column(String(400), nullable=False)

    # Risk Assessment Fields
    inherent_probability = Column(Integer, nullable=False)  # 1-5
    inherent_impact = Column(Integer, nullable=False)  # 1-5
    inherent_risk_rating = Column(Integer, nullable=False)  # Calculated
    current_probability = Column(Integer, nullable=False)  # 1-5
    current_impact = Column(Integer, nullable=False)  # 1-5
    current_risk_rating = Column(Integer, nullable=False)  # Calculated

    # Risk Management Fields
    risk_status = Column(String(20), nullable=False)
    risk_response_strategy = Column(String(20), nullable=False)
    planned_mitigations = Column(String(200))

    # Control Management Fields
    preventative_controls_status = Column(String(20), nullable=False)
    preventative_controls_description = Column(String(150))
    detective_controls_status = Column(String(20), nullable=False)
    detective_controls_description = Column(String(150))
    corrective_controls_status = Column(String(20), nullable=False)
    corrective_controls_description = Column(String(150))
    control_gaps = Column(String(150))

    # Ownership & Systems Fields
    risk_owner = Column(String(50), nullable=False)
    risk_owner_department = Column(String(50), nullable=False)
    systems_affected = Column(String(150))
    technology_domain = Column(String(50), nullable=False)

    # Business Impact Fields
    ibs_impact = Column(Boolean, nullable=False)
    number_of_ibs_affected = Column(Integer)
    business_criticality = Column(String(20), nullable=False)
    financial_impact_low = Column(Numeric(12, 2))
    financial_impact_high = Column(Numeric(12, 2))
    rto_hours = Column(Integer)
    rpo_hours = Column(Integer)
    sla_impact = Column(String(100))
    slo_impact = Column(String(100))

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

    def calculate_risk_ratings(self) -> None:
        """Calculate inherent and current risk ratings."""
        self.inherent_risk_rating = self.inherent_probability * self.inherent_impact
        self.current_risk_rating = self.current_probability * self.current_impact


class RiskLogEntry(Base):
    __tablename__ = "risk_log_entries"

    # Primary identification
    log_entry_id = Column(String(15), primary_key=True, index=True)
    risk_id = Column(
        String(12), ForeignKey("risks.risk_id"), nullable=False, index=True
    )

    # Entry metadata
    entry_date = Column(Date, nullable=False)
    entry_type = Column(
        String(50), nullable=False
    )  # e.g., "Risk Assessment Update", "Mitigation Completed", "Review"
    entry_summary = Column(String(500), nullable=False)

    # Risk rating changes
    previous_risk_rating = Column(Integer)  # Previous overall risk rating
    new_risk_rating = Column(Integer)  # New overall risk rating
    previous_probability = Column(Integer)  # Previous probability (1-5)
    new_probability = Column(Integer)  # New probability (1-5)
    previous_impact = Column(Integer)  # Previous impact (1-5)
    new_impact = Column(Integer)  # New impact (1-5)

    # Actions and context
    mitigation_actions_taken = Column(
        String(300)
    )  # Actions taken as part of this update
    risk_owner_at_time = Column(String(50))  # Risk owner when this entry was made
    supporting_evidence = Column(String(200))  # Links to documents, tickets, etc.

    # Workflow and approval
    entry_status = Column(
        String(20), default="Draft"
    )  # Draft, Submitted, Approved, Rejected
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
        """Update the parent Risk's current rating when this log entry is approved."""
        if self.entry_status == "Approved" and self.new_risk_rating is not None:
            # Update the risk's current rating fields
            if self.new_probability is not None:
                self.risk.current_probability = self.new_probability
            if self.new_impact is not None:
                self.risk.current_impact = self.new_impact
            if self.new_risk_rating is not None:
                self.risk.current_risk_rating = self.new_risk_rating

            # Update the last reviewed date to the entry date
            self.risk.last_reviewed = self.entry_date


class DropdownValue(Base):
    __tablename__ = "dropdown_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
