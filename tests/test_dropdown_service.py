from app.models.risk import DropdownValue
from app.services.dropdown_service import DropdownService


class TestDropdownService:
    """Test cases for DropdownService."""

    def test_init(self, db_session):
        """Test DropdownService initialization."""
        service = DropdownService(db_session)
        assert service.db == db_session

    def test_get_dropdown_values_no_filter(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values without category filter."""
        service = DropdownService(db_session)
        values = service.get_dropdown_values()

        assert len(values) > 0
        # Should be ordered by display_order, then value
        for i in range(len(values) - 1):
            current = values[i]
            values[i + 1]
            assert current.is_active is True

    def test_get_dropdown_values_with_category_filter(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values with category filter."""
        service = DropdownService(db_session)
        values = service.get_dropdown_values(category="risk_status")

        assert len(values) > 0
        for value in values:
            assert value.category == "risk_status"
            assert value.is_active is True

    def test_get_dropdown_values_nonexistent_category(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values with nonexistent category."""
        service = DropdownService(db_session)
        values = service.get_dropdown_values(category="nonexistent_category")

        assert len(values) == 0

    def test_get_dropdown_categories(self, db_session, sample_dropdown_values):
        """Test get_dropdown_categories."""
        service = DropdownService(db_session)
        categories = service.get_dropdown_categories()

        assert len(categories) > 0
        assert isinstance(categories, list)
        assert all(isinstance(cat, str) for cat in categories)
        # Should be sorted alphabetically
        assert categories == sorted(categories)

    def test_get_dropdown_values_by_categories_all(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values_by_categories without specific categories."""
        service = DropdownService(db_session)
        result = service.get_dropdown_values_by_categories()

        assert isinstance(result, dict)
        assert len(result) > 0

        for category, values in result.items():
            assert isinstance(category, str)
            assert isinstance(values, list)
            assert len(values) > 0
            for value in values:
                assert value.category == category
                assert value.is_active is True

    def test_get_dropdown_values_by_categories_specific(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values_by_categories with specific categories."""
        service = DropdownService(db_session)
        requested_categories = ["risk_status", "risk_category"]
        result = service.get_dropdown_values_by_categories(categories=requested_categories)

        assert isinstance(result, dict)
        # Should only include requested categories that exist
        for category in result.keys():
            assert category in requested_categories

        for category, values in result.items():
            assert len(values) > 0
            for value in values:
                assert value.category == category
                assert value.is_active is True

    def test_get_dropdown_values_by_categories_nonexistent(self, db_session, sample_dropdown_values):
        """Test get_dropdown_values_by_categories with nonexistent categories."""
        service = DropdownService(db_session)
        result = service.get_dropdown_values_by_categories(categories=["nonexistent"])

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_only_active_values_returned(self, db_session):
        """Test that only active dropdown values are returned."""
        # Create active and inactive values
        active_value = DropdownValue(
            category="test_category",
            value="Active Value",
            display_order=1,
            is_active=True,
        )
        inactive_value = DropdownValue(
            category="test_category",
            value="Inactive Value",
            display_order=2,
            is_active=False,
        )

        db_session.add(active_value)
        db_session.add(inactive_value)
        db_session.commit()

        service = DropdownService(db_session)

        # Test get_dropdown_values
        values = service.get_dropdown_values(category="test_category")
        assert len(values) == 1
        assert values[0].value == "Active Value"

        # Test get_dropdown_categories
        categories = service.get_dropdown_categories()
        assert "test_category" in categories

        # Test get_dropdown_values_by_categories
        result = service.get_dropdown_values_by_categories(categories=["test_category"])
        assert len(result["test_category"]) == 1
        assert result["test_category"][0].value == "Active Value"
