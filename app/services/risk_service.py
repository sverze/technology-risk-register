from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.sync import sync_database_after_write
from app.models.risk import Risk, RiskLogEntry

# Legacy import for backward compatibility
from app.schemas.risk import RiskCreate, RiskLogEntryCreate, RiskLogEntryUpdate
from app.schemas.risk import RiskUpdate as RiskUpdateSchema


class RiskService:
    def __init__(self, db: Session):
        self.db = db

    def get_risks(
        self,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> list[Risk]:
        """Get risks with optional filtering, searching, and sorting."""
        query = self.db.query(Risk)

        # Apply filters
        if category:
            query = query.filter(Risk.risk_category == category)
        if status:
            query = query.filter(Risk.risk_status == status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(Risk.risk_title.ilike(search_term) | Risk.risk_description.ilike(search_term))

        # Apply sorting
        if sort_by:
            sort_column = getattr(Risk, sort_by, None)
            if sort_column is not None:
                if sort_order.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            # Default sorting by net exposure (Critical first), then by risk_id
            query = query.order_by(Risk.business_disruption_net_exposure.desc(), Risk.risk_id)

        return query.offset(skip).limit(limit).all()

    def get_risks_count(
        self,
        category: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> int:
        """Get total count of risks with same filtering as get_risks."""
        query = self.db.query(Risk)

        # Apply same filters as get_risks
        if category:
            query = query.filter(Risk.risk_category == category)
        if status:
            query = query.filter(Risk.risk_status == status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(Risk.risk_title.ilike(search_term) | Risk.risk_description.ilike(search_term))

        return query.count()

    def get_risk(self, risk_id: str) -> Risk | None:
        """Get a single risk by ID."""
        return self.db.query(Risk).filter(Risk.risk_id == risk_id).first()

    @sync_database_after_write
    def create_risk(self, risk_data: RiskCreate) -> Risk:
        """Create a new risk."""
        # Use provided risk_id or generate one if not provided
        risk_id = risk_data.risk_id or self._generate_risk_id()

        # Create risk with calculated net exposure
        risk_dict = risk_data.dict(exclude={"risk_id"})
        db_risk = Risk(risk_id=risk_id, **risk_dict)
        db_risk.calculate_net_exposure()

        self.db.add(db_risk)
        self.db.commit()
        self.db.refresh(db_risk)

        # Create initial log entry
        self._create_log_entry(
            risk_id=risk_id,
            entry_type="Risk Creation",
            entry_summary="Risk initially created in the system",
            created_by=risk_data.risk_owner,
            new_net_exposure=str(db_risk.business_disruption_net_exposure),
            new_impact_rating=str(db_risk.business_disruption_impact_rating),
            new_likelihood_rating=str(db_risk.business_disruption_likelihood_rating),
            risk_owner_at_time=risk_data.risk_owner,
        )
        self.db.commit()

        return db_risk

    @sync_database_after_write
    def update_risk(self, risk_id: str, risk_data: RiskUpdateSchema) -> Risk | None:
        """Update an existing risk."""
        db_risk = self.get_risk(risk_id)
        if not db_risk:
            return None

        # Store previous net exposure for audit
        previous_exposure = db_risk.business_disruption_net_exposure

        # Update risk fields
        for field, value in risk_data.dict(exclude_unset=True).items():
            setattr(db_risk, field, value)

        # Recalculate net exposure
        db_risk.calculate_net_exposure()
        db_risk.updated_at = datetime.utcnow()  # type: ignore[assignment]

        # Create log entry if net exposure changed
        if db_risk.business_disruption_net_exposure != previous_exposure:
            self._create_log_entry(
                risk_id=risk_id,
                entry_type="Risk Assessment Update",
                entry_summary=(
                    f"Net exposure changed from {previous_exposure} to {db_risk.business_disruption_net_exposure} via direct risk update"
                ),
                created_by=risk_data.risk_owner,
                previous_net_exposure=str(previous_exposure),
                new_net_exposure=str(db_risk.business_disruption_net_exposure),
                previous_impact_rating=str(
                    db_risk.business_disruption_impact_rating
                ),  # Note: we don't track previous values in direct updates
                new_impact_rating=str(db_risk.business_disruption_impact_rating),
                previous_likelihood_rating=str(db_risk.business_disruption_likelihood_rating),
                new_likelihood_rating=str(db_risk.business_disruption_likelihood_rating),
                risk_owner_at_time=risk_data.risk_owner,
                entry_status="Approved",  # Direct risk updates are auto-approved
            )

        self.db.commit()
        self.db.refresh(db_risk)
        return db_risk

    @sync_database_after_write
    def delete_risk(self, risk_id: str) -> bool:
        """Delete a risk."""
        db_risk = self.get_risk(risk_id)
        if not db_risk:
            return False

        self.db.delete(db_risk)
        self.db.commit()
        return True

    def _generate_risk_id(self) -> str:
        """Generate a unique risk ID in format TR-YYYY-###."""
        # Get current year
        year = datetime.now().year

        # Find next sequence number for this year
        like_pattern = f"TR-{year}-%"
        existing_count = self.db.query(Risk).filter(Risk.risk_id.like(like_pattern)).count()

        sequence = existing_count + 1

        return f"TR-{year}-{sequence:03d}"

    def _get_category_abbreviation(self, category: str) -> str:
        """Get 3-letter abbreviation for risk category."""
        abbreviations = {
            "Cybersecurity": "CYB",
            "Infrastructure": "INF",
            "Application": "APP",
            "Data Management": "DAT",
            "Cloud Services": "CLD",
            "Vendor/Third Party": "VEN",
            "Regulatory/Compliance": "REG",
            "Operational": "OPS",
        }
        return abbreviations.get(category, "GEN")

    def _get_risk_level(self, rating: int) -> str:
        """Convert risk rating to level."""
        if 1 <= rating <= 3:
            return "Low"
        elif 4 <= rating <= 6:
            return "Medium"
        elif 8 <= rating <= 12:
            return "High"
        elif 15 <= rating <= 25:
            return "Critical"
        else:
            return "Unknown"

    def _create_log_entry(
        self,
        risk_id: str,
        entry_type: str,
        entry_summary: str,
        created_by: str,
        previous_net_exposure: str | None = None,
        new_net_exposure: str | None = None,
        previous_impact_rating: str | None = None,
        new_impact_rating: str | None = None,
        previous_likelihood_rating: str | None = None,
        new_likelihood_rating: str | None = None,
        risk_owner_at_time: str | None = None,
        entry_status: str = "Draft",
        business_justification: str | None = None,
        mitigation_actions_taken: str | None = None,
        supporting_evidence: str | None = None,
    ) -> None:
        """Create a log entry (internal helper method)."""
        # Generate log entry ID
        existing_count = self.db.query(RiskLogEntry).filter(RiskLogEntry.risk_id == risk_id).count()
        log_entry_id = f"LOG-{risk_id}-{existing_count + 1:03d}"

        log_entry = RiskLogEntry(
            log_entry_id=log_entry_id,
            risk_id=risk_id,
            entry_date=date.today(),
            entry_type=entry_type,
            entry_summary=entry_summary,
            previous_net_exposure=previous_net_exposure,
            new_net_exposure=new_net_exposure,
            previous_impact_rating=previous_impact_rating,
            new_impact_rating=new_impact_rating,
            previous_likelihood_rating=previous_likelihood_rating,
            new_likelihood_rating=new_likelihood_rating,
            mitigation_actions_taken=mitigation_actions_taken,
            risk_owner_at_time=risk_owner_at_time,
            supporting_evidence=supporting_evidence,
            entry_status=entry_status,
            created_by=created_by,
            business_justification=business_justification,
        )

        self.db.add(log_entry)
        # Note: Don't commit here, let the caller handle it

    # Legacy methods for backward compatibility
    def get_risk_updates(self, risk_id: str) -> list[RiskLogEntry]:
        """Get all update logs for a specific risk (legacy method)."""
        return self.get_risk_log_entries(risk_id)

    def get_recent_risk_updates(self, limit: int = 50) -> list[RiskLogEntry]:
        """Get recent risk updates across all risks (legacy method)."""
        return (
            self.db.query(RiskLogEntry)
            .order_by(RiskLogEntry.entry_date.desc(), RiskLogEntry.created_at.desc())
            .limit(limit)
            .all()
        )

    # New RiskLogEntry methods
    @sync_database_after_write
    def create_risk_log_entry(self, log_entry_data: RiskLogEntryCreate) -> RiskLogEntry:
        """Create a new log entry for a risk."""
        # Generate log entry ID
        existing_count = self.db.query(RiskLogEntry).filter(RiskLogEntry.risk_id == log_entry_data.risk_id).count()
        log_entry_id = f"LOG-{log_entry_data.risk_id}-{existing_count + 1:03d}"

        # Get current risk data for context
        current_risk = self.get_risk(log_entry_data.risk_id)
        if current_risk:
            # Auto-populate previous values if not provided
            if log_entry_data.previous_net_exposure is None:
                log_entry_data.previous_net_exposure = str(current_risk.business_disruption_net_exposure)  # type: ignore[assignment]
            if log_entry_data.previous_impact_rating is None:
                log_entry_data.previous_impact_rating = str(current_risk.business_disruption_impact_rating)  # type: ignore[assignment]
            if log_entry_data.previous_likelihood_rating is None:
                log_entry_data.previous_likelihood_rating = str(current_risk.business_disruption_likelihood_rating)  # type: ignore[assignment]
            if log_entry_data.risk_owner_at_time is None:
                log_entry_data.risk_owner_at_time = str(current_risk.risk_owner)  # type: ignore[assignment]

        db_log_entry = RiskLogEntry(log_entry_id=log_entry_id, **log_entry_data.dict())

        self.db.add(db_log_entry)
        self.db.commit()
        self.db.refresh(db_log_entry)

        return db_log_entry

    def get_risk_log_entries(self, risk_id: str) -> list[RiskLogEntry]:
        """Get all log entries for a specific risk, ordered by most recent first."""
        return (
            self.db.query(RiskLogEntry)
            .filter(RiskLogEntry.risk_id == risk_id)
            .order_by(RiskLogEntry.entry_date.desc(), RiskLogEntry.created_at.desc())
            .all()
        )

    def get_risk_log_entry(self, log_entry_id: str) -> RiskLogEntry | None:
        """Get a specific log entry by ID."""
        return self.db.query(RiskLogEntry).filter(RiskLogEntry.log_entry_id == log_entry_id).first()

    @sync_database_after_write
    def update_risk_log_entry(self, log_entry_id: str, log_entry_data: RiskLogEntryUpdate) -> RiskLogEntry | None:
        """Update an existing log entry."""
        db_log_entry = self.get_risk_log_entry(log_entry_id)
        if not db_log_entry:
            return None

        # Update only provided fields
        for field, value in log_entry_data.dict(exclude_unset=True).items():
            setattr(db_log_entry, field, value)

        self.db.commit()
        self.db.refresh(db_log_entry)

        return db_log_entry

    def approve_risk_log_entry(self, log_entry_id: str, reviewed_by: str) -> RiskLogEntry | None:
        """Approve a log entry and update the parent risk's current rating."""
        db_log_entry = self.get_risk_log_entry(log_entry_id)
        if not db_log_entry:
            return None

        # Update approval status
        db_log_entry.entry_status = "Approved"  # type: ignore[assignment]
        db_log_entry.reviewed_by = reviewed_by  # type: ignore[assignment]
        db_log_entry.approved_date = date.today()  # type: ignore[assignment]

        # Apply the rating changes to the parent risk
        db_log_entry.update_parent_risk_rating()

        self.db.commit()
        self.db.refresh(db_log_entry)

        return db_log_entry

    def reject_risk_log_entry(self, log_entry_id: str, reviewed_by: str) -> RiskLogEntry | None:
        """Reject a log entry."""
        db_log_entry = self.get_risk_log_entry(log_entry_id)
        if not db_log_entry:
            return None

        # Update rejection status
        db_log_entry.entry_status = "Rejected"  # type: ignore[assignment]
        db_log_entry.reviewed_by = reviewed_by  # type: ignore[assignment]
        db_log_entry.approved_date = date.today()  # type: ignore[assignment]  # Date of decision

        self.db.commit()
        self.db.refresh(db_log_entry)

        return db_log_entry

    @sync_database_after_write
    def delete_risk_log_entry(self, log_entry_id: str) -> bool:
        """Delete a log entry."""
        db_log_entry = self.get_risk_log_entry(log_entry_id)
        if not db_log_entry:
            return False

        self.db.delete(db_log_entry)
        self.db.commit()
        return True
