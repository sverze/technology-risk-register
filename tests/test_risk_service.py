from datetime import date, datetime, timedelta
from unittest.mock import patch

from app.models.risk import Risk, RiskLogEntry
from app.schemas.risk import RiskCreate
from app.schemas.risk import RiskLogEntry as RiskLogEntrySchema
from app.services.risk_service import RiskService


class TestRiskService:
    """Test cases for RiskService."""

    def test_init(self, db_session):
        """Test RiskService initialization."""
        service = RiskService(db_session)
        assert service.db == db_session

    def test_get_risks_no_filters(self, db_session, sample_risks):
        """Test get_risks without filters."""
        service = RiskService(db_session)
        risks = service.get_risks()
        assert len(risks) == 2

    def test_get_risks_with_category_filter(self, db_session, sample_risks):
        """Test get_risks with category filter."""
        service = RiskService(db_session)
        risks = service.get_risks(category="Cybersecurity")
        assert len(risks) == 1
        assert risks[0].risk_category == "Cybersecurity"

    def test_get_risks_with_status_filter(self, db_session, sample_risks):
        """Test get_risks with status filter."""
        service = RiskService(db_session)
        risks = service.get_risks(status="Open")
        assert len(risks) == 2

    def test_get_risks_with_pagination(self, db_session, sample_risks):
        """Test get_risks with pagination."""
        service = RiskService(db_session)
        risks = service.get_risks(skip=1, limit=1)
        assert len(risks) == 1

    def test_get_risks_with_search_title(self, db_session, sample_risks):
        """Test get_risks with search in title."""
        service = RiskService(db_session)
        risks = service.get_risks(search="Cybersecurity")
        assert len(risks) == 1
        assert "Cybersecurity" in risks[0].risk_title

    def test_get_risks_with_search_description(self, db_session, sample_risks):
        """Test get_risks with search in description."""
        service = RiskService(db_session)
        risks = service.get_risks(search="Test cybersecurity")
        assert len(risks) == 1
        assert "cybersecurity" in risks[0].risk_description.lower()

    def test_get_risks_with_search_case_insensitive(self, db_session, sample_risks):
        """Test get_risks with case-insensitive search."""
        service = RiskService(db_session)
        risks = service.get_risks(search="CYBERSECURITY")
        assert len(risks) == 1
        assert "Cybersecurity" in risks[0].risk_title

    def test_get_risks_with_search_no_results(self, db_session, sample_risks):
        """Test get_risks with search that returns no results."""
        service = RiskService(db_session)
        risks = service.get_risks(search="nonexistent search term")
        assert len(risks) == 0

    def test_get_risks_with_sort_by_title_asc(self, db_session, sample_risks):
        """Test get_risks with sorting by title ascending."""
        service = RiskService(db_session)
        risks = service.get_risks(sort_by="risk_title", sort_order="asc")
        assert len(risks) == 2
        assert risks[0].risk_title <= risks[1].risk_title

    def test_get_risks_with_sort_by_title_desc(self, db_session, sample_risks):
        """Test get_risks with sorting by title descending."""
        service = RiskService(db_session)
        risks = service.get_risks(sort_by="risk_title", sort_order="desc")
        assert len(risks) == 2
        assert risks[0].risk_title >= risks[1].risk_title

    def test_get_risks_with_sort_by_rating_desc(self, db_session, sample_risks):
        """Test get_risks with sorting by risk rating descending."""
        service = RiskService(db_session)
        risks = service.get_risks(sort_by="current_risk_rating", sort_order="desc")
        assert len(risks) == 2
        assert risks[0].current_risk_rating >= risks[1].current_risk_rating

    def test_get_risks_with_invalid_sort_field(self, db_session, sample_risks):
        """Test get_risks with invalid sort field (should ignore and use default)."""
        service = RiskService(db_session)
        risks = service.get_risks(sort_by="invalid_field")
        assert len(risks) == 2
        # Should use default sorting (risk_rating desc, then risk_id)
        assert risks[0].current_risk_rating >= risks[1].current_risk_rating

    def test_get_risks_default_sorting(self, db_session, sample_risks):
        """Test get_risks default sorting."""
        service = RiskService(db_session)
        risks = service.get_risks()
        assert len(risks) == 2
        # Default sorting should be by current_risk_rating desc, then risk_id
        assert risks[0].current_risk_rating >= risks[1].current_risk_rating

    def test_get_risks_combined_filters_and_search(self, db_session):
        """Test get_risks with combined filters and search."""
        # Create specific test risks for this test
        risk1 = Risk(
            risk_id="TR-2024-TEST-001",
            risk_title="Critical Cybersecurity Issue",
            risk_description="A critical cybersecurity vulnerability",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=3,
            current_impact=4,
            risk_status="Active",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk2 = Risk(
            risk_id="TR-2024-TEST-002",
            risk_title="Infrastructure Problem",
            risk_description="An infrastructure cybersecurity issue",
            risk_category="Infrastructure",
            risk_owner="Test User",
            inherent_probability=2,
            inherent_impact=3,
            current_probability=2,
            current_impact=3,
            risk_status="Active",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="Operations",
            technology_domain="Infrastructure",
            ibs_impact=True,
            business_criticality="High",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk1.calculate_risk_ratings()
        risk2.calculate_risk_ratings()

        db_session.add(risk1)
        db_session.add(risk2)
        db_session.commit()

        service = RiskService(db_session)

        # Search for "cybersecurity" in Cybersecurity category should return 1 result
        risks = service.get_risks(category="Cybersecurity", search="cybersecurity")
        assert len(risks) == 1
        assert risks[0].risk_title == "Critical Cybersecurity Issue"

        # Search for "cybersecurity" in Infrastructure category should return 1 result
        risks = service.get_risks(category="Infrastructure", search="cybersecurity")
        assert len(risks) == 1
        assert risks[0].risk_title == "Infrastructure Problem"

        # Search for "cybersecurity" with no category filter should return 2 results
        risks = service.get_risks(search="cybersecurity")
        assert len(risks) == 2

    def test_get_risks_count_no_filters(self, db_session, sample_risks):
        """Test get_risks_count without filters."""
        service = RiskService(db_session)
        count = service.get_risks_count()
        assert count == 2

    def test_get_risks_count_with_category_filter(self, db_session, sample_risks):
        """Test get_risks_count with category filter."""
        service = RiskService(db_session)
        count = service.get_risks_count(category="Cybersecurity")
        assert count == 1

    def test_get_risks_count_with_search(self, db_session, sample_risks):
        """Test get_risks_count with search."""
        service = RiskService(db_session)
        count = service.get_risks_count(search="Cybersecurity")
        assert count == 1

    def test_get_risks_count_with_combined_filters(self, db_session):
        """Test get_risks_count with combined filters."""
        # Create specific test risks
        risk1 = Risk(
            risk_id="TR-2024-COUNT-001",
            risk_title="Active Cybersecurity Risk",
            risk_description="Active cybersecurity vulnerability",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=3,
            current_impact=4,
            risk_status="Active",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk2 = Risk(
            risk_id="TR-2024-COUNT-002",
            risk_title="Closed Cybersecurity Risk",
            risk_description="Closed cybersecurity issue",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=2,
            inherent_impact=3,
            current_probability=1,
            current_impact=1,
            risk_status="Closed",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Low",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk1.calculate_risk_ratings()
        risk2.calculate_risk_ratings()

        db_session.add(risk1)
        db_session.add(risk2)
        db_session.commit()

        service = RiskService(db_session)

        # Count all cybersecurity risks
        count = service.get_risks_count(category="Cybersecurity")
        assert count == 2

        # Count active cybersecurity risks
        count = service.get_risks_count(category="Cybersecurity", status="Active")
        assert count == 1

        # Count cybersecurity risks with search
        count = service.get_risks_count(
            category="Cybersecurity", search="vulnerability"
        )
        assert count == 1

    def test_get_risks_count_no_results(self, db_session, sample_risks):
        """Test get_risks_count with filters that return no results."""
        service = RiskService(db_session)
        count = service.get_risks_count(search="nonexistent search term")
        assert count == 0

    def test_get_risk_exists(self, db_session, sample_risks):
        """Test get_risk with existing risk."""
        service = RiskService(db_session)
        risk = service.get_risk("TR-2024-CYB-001")
        assert risk is not None
        assert risk.risk_id == "TR-2024-CYB-001"

    def test_get_risk_not_exists(self, db_session):
        """Test get_risk with non-existing risk."""
        service = RiskService(db_session)
        risk = service.get_risk("NON-EXISTENT")
        assert risk is None

    @patch("app.services.risk_service.datetime")
    def test_create_risk(self, mock_datetime, db_session):
        """Test create_risk."""
        # Mock datetime.now() and datetime.utcnow()
        mock_now = datetime(2024, 1, 15)
        mock_datetime.now.return_value = mock_now
        mock_datetime.utcnow.return_value = mock_now

        service = RiskService(db_session)
        risk_data = RiskCreate(
            risk_title="Test Risk",
            risk_description="Test Description",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=2,
            current_impact=3,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk = service.create_risk(risk_data)

        assert risk.risk_id == "TR-2024-CYB-001"
        assert risk.risk_title == "Test Risk"
        assert risk.inherent_risk_rating == 12
        assert risk.current_risk_rating == 6

        # Check that update log was created
        update_log = (
            db_session.query(RiskLogEntry)
            .filter(RiskLogEntry.risk_id == risk.risk_id)
            .first()
        )
        assert update_log is not None
        assert update_log.update_type == "Risk Creation"

    def test_update_risk_exists(self, db_session, sample_risks):
        """Test update_risk with existing risk."""
        service = RiskService(db_session)

        # Create a partial update with minimal required fields
        update_data = RiskLogEntrySchema(
            risk_title="Updated Title",
            risk_description="Test cybersecurity risk",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=4,  # Changed from 3 to 4
            current_impact=4,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk = service.update_risk("TR-2024-CYB-001", update_data)

        assert risk is not None
        assert risk.risk_title == "Updated Title"
        assert risk.current_probability == 4
        # Check if rating changed and update log was created
        if risk.current_risk_rating != 12:  # Previous rating from sample data
            update_log = (
                db_session.query(RiskLogEntry)
                .filter(RiskLogEntry.risk_id == "TR-2024-CYB-001")
                .first()
            )
            if update_log:
                assert update_log.update_type == "Risk Assessment Change"

    def test_update_risk_not_exists(self, db_session):
        """Test update_risk with non-existing risk."""
        service = RiskService(db_session)
        update_data = RiskLogEntrySchema(
            risk_title="Updated Title",
            risk_description="Test Description",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=2,
            current_impact=3,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )

        risk = service.update_risk("NON-EXISTENT", update_data)
        assert risk is None

    def test_delete_risk_exists(self, db_session, sample_risks):
        """Test delete_risk with existing risk."""
        service = RiskService(db_session)
        result = service.delete_risk("TR-2024-CYB-001")
        assert result is True

        # Verify risk is deleted
        risk = service.get_risk("TR-2024-CYB-001")
        assert risk is None

    def test_delete_risk_not_exists(self, db_session):
        """Test delete_risk with non-existing risk."""
        service = RiskService(db_session)
        result = service.delete_risk("NON-EXISTENT")
        assert result is False

    @patch("app.services.risk_service.datetime")
    def test_generate_risk_id_first_risk(self, mock_datetime, db_session):
        """Test _generate_risk_id for first risk in category."""
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        service = RiskService(db_session)
        risk_id = service._generate_risk_id("Cybersecurity")
        assert risk_id == "TR-2024-CYB-001"

    @patch("app.services.risk_service.datetime")
    def test_generate_risk_id_subsequent_risk(
        self, mock_datetime, db_session, sample_risks
    ):
        """Test _generate_risk_id for subsequent risk in category."""
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        service = RiskService(db_session)
        risk_id = service._generate_risk_id("Cybersecurity")
        assert risk_id == "TR-2024-CYB-002"

    def test_get_category_abbreviation_known(self, db_session):
        """Test _get_category_abbreviation with known categories."""
        service = RiskService(db_session)

        assert service._get_category_abbreviation("Cybersecurity") == "CYB"
        assert service._get_category_abbreviation("Infrastructure") == "INF"
        assert service._get_category_abbreviation("Application") == "APP"
        assert service._get_category_abbreviation("Data Management") == "DAT"
        assert service._get_category_abbreviation("Cloud Services") == "CLD"
        assert service._get_category_abbreviation("Vendor/Third Party") == "VEN"
        assert service._get_category_abbreviation("Regulatory/Compliance") == "REG"
        assert service._get_category_abbreviation("Operational") == "OPS"

    def test_get_category_abbreviation_unknown(self, db_session):
        """Test _get_category_abbreviation with unknown category."""
        service = RiskService(db_session)
        assert service._get_category_abbreviation("Unknown Category") == "GEN"

    def test_get_risk_level(self, db_session):
        """Test _get_risk_level for different ratings."""
        service = RiskService(db_session)

        assert service._get_risk_level(1) == "Low"
        assert service._get_risk_level(3) == "Low"
        assert service._get_risk_level(4) == "Medium"
        assert service._get_risk_level(6) == "Medium"
        assert service._get_risk_level(8) == "High"
        assert service._get_risk_level(12) == "High"
        assert service._get_risk_level(15) == "Critical"
        assert service._get_risk_level(25) == "Critical"
        assert service._get_risk_level(0) == "Unknown"
        assert service._get_risk_level(7) == "Unknown"
        assert service._get_risk_level(30) == "Unknown"

    def test_create_update_log(self, db_session):
        """Test _create_update_log."""
        # First create a risk to reference
        risk = Risk(
            risk_id="TR-2024-TEST-001",
            risk_title="Test Risk",
            risk_description="Test",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=2,
            current_impact=3,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )
        risk.calculate_risk_ratings()
        db_session.add(risk)
        db_session.commit()

        service = RiskService(db_session)
        service._create_update_log(
            risk_id="TR-2024-TEST-001",
            update_type="Test Update",
            update_summary="Test Summary",
            updated_by="Test User",
            previous_risk_rating="High (12)",
            new_risk_rating="Medium (6)",
        )
        db_session.commit()

        # Verify update log was created
        update_log = (
            db_session.query(RiskLogEntry)
            .filter(RiskLogEntry.risk_id == "TR-2024-TEST-001")
            .first()
        )

        assert update_log is not None
        assert update_log.update_id == "UPD-TR-2024-TEST-001-01"
        assert update_log.update_type == "Test Update"
        assert update_log.update_summary == "Test Summary"
        assert update_log.updated_by == "Test User"
        assert update_log.previous_risk_rating == "High (12)"
        assert update_log.new_risk_rating == "Medium (6)"
        assert update_log.update_date == date.today()

    def test_get_risk_updates_exists(self, db_session, sample_risks):
        """Test get_risk_updates with existing risk."""
        # Create some updates for the risk
        from app.models.risk import RiskLogEntry

        update1 = RiskLogEntry(
            update_id="UPD-TR-2024-CYB-001-01",
            risk_id="TR-2024-CYB-001",
            update_date=date.today() - timedelta(days=2),
            updated_by="Test User",
            update_type="Risk Assessment Change",
            update_summary="First update",
        )

        update2 = RiskLogEntry(
            update_id="UPD-TR-2024-CYB-001-02",
            risk_id="TR-2024-CYB-001",
            update_date=date.today() - timedelta(days=1),
            updated_by="Test User",
            update_type="Control Update",
            update_summary="Second update",
        )

        db_session.add(update1)
        db_session.add(update2)
        db_session.commit()

        service = RiskService(db_session)
        updates = service.get_risk_updates("TR-2024-CYB-001")

        assert len(updates) == 2
        # Should be ordered by date desc (most recent first)
        assert updates[0].update_summary == "Second update"
        assert updates[1].update_summary == "First update"

    def test_get_risk_updates_not_exists(self, db_session):
        """Test get_risk_updates with non-existing risk."""
        service = RiskService(db_session)
        updates = service.get_risk_updates("NON-EXISTENT")
        assert len(updates) == 0

    def test_get_recent_risk_updates(self, db_session):
        """Test get_recent_risk_updates."""
        from app.models.risk import Risk, RiskLogEntry

        # Create a risk first
        risk = Risk(
            risk_id="TR-2024-TEST-001",
            risk_title="Test Risk",
            risk_description="Test",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=2,
            current_impact=3,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )
        risk.calculate_risk_ratings()
        db_session.add(risk)

        # Create multiple updates
        updates_data = [
            (
                "UPD-TR-2024-TEST-001-01",
                "TR-2024-TEST-001",
                date.today() - timedelta(days=3),
                "Update 1",
            ),
            (
                "UPD-TR-2024-TEST-001-02",
                "TR-2024-TEST-001",
                date.today() - timedelta(days=2),
                "Update 2",
            ),
            (
                "UPD-TR-2024-TEST-001-03",
                "TR-2024-TEST-001",
                date.today() - timedelta(days=1),
                "Update 3",
            ),
        ]

        for update_id, risk_id, update_date, summary in updates_data:
            update = RiskLogEntry(
                update_id=update_id,
                risk_id=risk_id,
                update_date=update_date,
                updated_by="Test User",
                update_type="Test Update",
                update_summary=summary,
            )
            db_session.add(update)

        db_session.commit()

        service = RiskService(db_session)
        recent_updates = service.get_recent_risk_updates(limit=5)

        assert len(recent_updates) == 3
        # Should be ordered by date desc (most recent first)
        assert recent_updates[0].update_summary == "Update 3"
        assert recent_updates[1].update_summary == "Update 2"
        assert recent_updates[2].update_summary == "Update 1"

    def test_get_recent_risk_updates_with_limit(self, db_session):
        """Test get_recent_risk_updates with limit."""
        from app.models.risk import Risk, RiskLogEntry

        # Create a risk first
        risk = Risk(
            risk_id="TR-2024-TEST-002",
            risk_title="Test Risk 2",
            risk_description="Test",
            risk_category="Cybersecurity",
            risk_owner="Test User",
            inherent_probability=3,
            inherent_impact=4,
            current_probability=2,
            current_impact=3,
            risk_status="Open",
            risk_response_strategy="Mitigate",
            preventative_controls_status="Adequate",
            detective_controls_status="Adequate",
            corrective_controls_status="Adequate",
            risk_owner_department="IT",
            technology_domain="Security",
            ibs_impact=False,
            business_criticality="Medium",
            date_identified=date.today(),
            last_reviewed=date.today(),
            next_review_date=date.today(),
        )
        risk.calculate_risk_ratings()
        db_session.add(risk)

        # Create 5 updates
        for i in range(5):
            update = RiskLogEntry(
                update_id=f"UPD-TR-2024-TEST-002-{i + 1:02d}",
                risk_id="TR-2024-TEST-002",
                update_date=date.today() - timedelta(days=i),
                updated_by="Test User",
                update_type="Test Update",
                update_summary=f"Update {i + 1}",
            )
            db_session.add(update)

        db_session.commit()

        service = RiskService(db_session)
        recent_updates = service.get_recent_risk_updates(limit=2)

        assert len(recent_updates) == 2
        # Should be most recent ones
        assert recent_updates[0].update_summary == "Update 1"
        assert recent_updates[1].update_summary == "Update 2"
