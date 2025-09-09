from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    updates = relationship(
        "RiskUpdate", back_populates="risk", cascade="all, delete-orphan"
    )

    def calculate_risk_ratings(self) -> None:
        """Calculate inherent and current risk ratings."""
        self.inherent_risk_rating = self.inherent_probability * self.inherent_impact
        self.current_risk_rating = self.current_probability * self.current_impact


class RiskUpdate(Base):
    __tablename__ = "risk_updates"

    update_id = Column(String(15), primary_key=True, index=True)
    risk_id = Column(
        String(12), ForeignKey("risks.risk_id"), nullable=False, index=True
    )
    update_date = Column(Date, nullable=False)
    updated_by = Column(String(50), nullable=False)
    update_type = Column(String(50), nullable=False)
    update_summary = Column(String(300), nullable=False)
    previous_risk_rating = Column(String(20))
    new_risk_rating = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    risk = relationship("Risk", back_populates="updates")


class DropdownValue(Base):
    __tablename__ = "dropdown_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
