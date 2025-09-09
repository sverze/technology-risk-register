from sqlalchemy.orm import Session

from app.models.risk import DropdownValue
from app.schemas.risk import DropdownValue as DropdownValueSchema


class DropdownService:
    def __init__(self, db: Session):
        self.db = db

    def get_dropdown_values(self, category: str | None = None) -> list[DropdownValueSchema]:
        """Get dropdown values, optionally filtered by category."""
        query = self.db.query(DropdownValue).filter(DropdownValue.is_active == True)
        
        if category:
            query = query.filter(DropdownValue.category == category)
        
        return query.order_by(DropdownValue.display_order, DropdownValue.value).all()

    def get_dropdown_categories(self) -> list[str]:
        """Get all available dropdown categories."""
        categories = (
            self.db.query(DropdownValue.category)
            .filter(DropdownValue.is_active == True)
            .distinct()
            .order_by(DropdownValue.category)
            .all()
        )
        return [category[0] for category in categories]

    def get_dropdown_values_by_categories(self, categories: list[str] | None = None) -> dict[str, list[DropdownValueSchema]]:
        """Get dropdown values grouped by category."""
        if categories:
            # Get specific categories
            query = (
                self.db.query(DropdownValue)
                .filter(
                    DropdownValue.is_active == True,
                    DropdownValue.category.in_(categories)
                )
            )
        else:
            # Get all categories
            query = self.db.query(DropdownValue).filter(DropdownValue.is_active == True)
        
        dropdown_values = query.order_by(DropdownValue.category, DropdownValue.display_order, DropdownValue.value).all()
        
        # Group by category
        result = {}
        for dropdown_value in dropdown_values:
            if dropdown_value.category not in result:
                result[dropdown_value.category] = []
            result[dropdown_value.category].append(dropdown_value)
        
        return result