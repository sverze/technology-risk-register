from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.risk import Risk, RiskUpdate
from app.schemas.risk import RiskCreate
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
            query = query.filter(
                Risk.risk_title.ilike(search_term) | Risk.risk_description.ilike(search_term)
            )

        # Apply sorting
        if sort_by:
            sort_column = getattr(Risk, sort_by, None)
            if sort_column is not None:
                if sort_order.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            # Default sorting by current risk rating (highest first), then by risk_id
            query = query.order_by(Risk.current_risk_rating.desc(), Risk.risk_id)

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
            query = query.filter(
                Risk.risk_title.ilike(search_term) | Risk.risk_description.ilike(search_term)
            )

        return query.count()

    def get_risk(self, risk_id: str) -> Risk | None:
        """Get a single risk by ID."""
        return self.db.query(Risk).filter(Risk.risk_id == risk_id).first()

    def create_risk(self, risk_data: RiskCreate) -> Risk:
        """Create a new risk."""
        # Generate risk ID
        risk_id = self._generate_risk_id(risk_data.risk_category)

        # Create risk with calculated ratings
        db_risk = Risk(risk_id=risk_id, **risk_data.dict())
        db_risk.calculate_risk_ratings()

        self.db.add(db_risk)
        self.db.commit()
        self.db.refresh(db_risk)

        # Create initial update log entry
        self._create_update_log(
            risk_id=risk_id,
            update_type="Risk Creation",
            update_summary="Risk initially created in the system",
            updated_by=risk_data.risk_owner,
            new_risk_rating=(
                f"{db_risk.current_risk_rating} "
                f"({self._get_risk_level(db_risk.current_risk_rating)})"
            ),
        )
        self.db.commit()

        return db_risk

    def update_risk(self, risk_id: str, risk_data: RiskUpdateSchema) -> Risk | None:
        """Update an existing risk."""
        db_risk = self.get_risk(risk_id)
        if not db_risk:
            return None

        # Store previous rating for audit
        previous_rating = db_risk.current_risk_rating
        previous_level = self._get_risk_level(previous_rating)

        # Update risk fields
        for field, value in risk_data.dict(exclude_unset=True).items():
            setattr(db_risk, field, value)

        # Recalculate risk ratings
        db_risk.calculate_risk_ratings()
        db_risk.updated_at = datetime.utcnow()

        # Create update log if rating changed
        if db_risk.current_risk_rating != previous_rating:
            new_level = self._get_risk_level(db_risk.current_risk_rating)
            self._create_update_log(
                risk_id=risk_id,
                update_type="Risk Assessment Change",
                update_summary=(
                    f"Risk rating changed from {previous_level} to {new_level}"
                ),
                updated_by=risk_data.risk_owner,
                previous_risk_rating=f"{previous_rating} ({previous_level})",
                new_risk_rating=f"{db_risk.current_risk_rating} ({new_level})",
            )

        self.db.commit()
        self.db.refresh(db_risk)
        return db_risk

    def delete_risk(self, risk_id: str) -> bool:
        """Delete a risk."""
        db_risk = self.get_risk(risk_id)
        if not db_risk:
            return False

        self.db.delete(db_risk)
        self.db.commit()
        return True

    def _generate_risk_id(self, category: str) -> str:
        """Generate a unique risk ID."""
        # Get category abbreviation
        category_abbr = self._get_category_abbreviation(category)

        # Get current year
        year = datetime.now().year

        # Find next sequence number for this year and category
        like_pattern = f"TR-{year}-{category_abbr}-%"
        existing_count = (
            self.db.query(Risk).filter(Risk.risk_id.like(like_pattern)).count()
        )

        sequence = existing_count + 1

        return f"TR-{year}-{category_abbr}-{sequence:03d}"

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

    def _create_update_log(
        self,
        risk_id: str,
        update_type: str,
        update_summary: str,
        updated_by: str,
        previous_risk_rating: str | None = None,
        new_risk_rating: str | None = None,
    ) -> None:
        """Create an update log entry."""
        # Generate update ID
        existing_count = (
            self.db.query(RiskUpdate).filter(RiskUpdate.risk_id == risk_id).count()
        )
        update_id = f"UPD-{risk_id}-{existing_count + 1:02d}"

        update_log = RiskUpdate(
            update_id=update_id,
            risk_id=risk_id,
            update_date=date.today(),
            updated_by=updated_by,
            update_type=update_type,
            update_summary=update_summary,
            previous_risk_rating=previous_risk_rating,
            new_risk_rating=new_risk_rating,
        )

        self.db.add(update_log)
        # Note: Don't commit here, let the caller handle it

    def get_risk_updates(self, risk_id: str) -> list[RiskUpdate]:
        """Get all update logs for a specific risk."""
        return (
            self.db.query(RiskUpdate)
            .filter(RiskUpdate.risk_id == risk_id)
            .order_by(RiskUpdate.update_date.desc(), RiskUpdate.created_at.desc())
            .all()
        )

    def get_recent_risk_updates(self, limit: int = 50) -> list[RiskUpdate]:
        """Get recent risk updates across all risks."""
        return (
            self.db.query(RiskUpdate)
            .order_by(RiskUpdate.update_date.desc(), RiskUpdate.created_at.desc())
            .limit(limit)
            .all()
        )
