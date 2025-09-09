"""
Integration tests for the Technology Risk Register API.

These tests can run against:
1. Local development server: uvicorn app.main:app --host 0.0.0.0 --port 8000
2. Docker container: docker-compose up

Set the API_BASE_URL environment variable to test against different endpoints:
- Local: API_BASE_URL=http://localhost:8000
- Docker: API_BASE_URL=http://localhost:8000 (default)

Run with: pytest tests/integration/ -v
"""

import os
import requests
import pytest
from typing import Dict, Any


# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_BASE = f"{API_BASE_URL}/api/v1"


class TestHealthAndBasics:
    """Test basic API health and connectivity."""
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = requests.get(API_BASE_URL)
        assert response.status_code == 200
        assert "Technology Risk Register API" in response.json()["message"]
    
    def test_openapi_docs(self):
        """Test that OpenAPI docs are accessible."""
        response = requests.get(f"{API_BASE_URL}/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestDropdownEndpoints:
    """Test dropdown value endpoints."""
    
    def test_get_dropdown_categories(self):
        """Test retrieving all dropdown categories."""
        response = requests.get(f"{API_V1_BASE}/dropdown/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Should include standard risk categories
        expected_categories = ["risk_category", "risk_status", "risk_response_strategy"]
        for expected in expected_categories:
            assert expected in categories
    
    def test_get_dropdown_values_all(self):
        """Test retrieving all dropdown values."""
        response = requests.get(f"{API_V1_BASE}/dropdown/values")
        assert response.status_code == 200
        
        values = response.json()
        assert isinstance(values, list)
        assert len(values) > 0
        
        # Verify structure
        for value in values[:5]:  # Check first 5
            assert "id" in value
            assert "category" in value
            assert "value" in value
            assert "display_order" in value
            assert "is_active" in value
            assert value["is_active"] is True
    
    def test_get_dropdown_values_filtered(self):
        """Test retrieving dropdown values filtered by category."""
        response = requests.get(f"{API_V1_BASE}/dropdown/values?category=risk_status")
        assert response.status_code == 200
        
        values = response.json()
        assert isinstance(values, list)
        assert len(values) > 0
        
        # All values should be for risk_status category
        for value in values:
            assert value["category"] == "risk_status"
    
    def test_get_dropdown_values_by_category(self):
        """Test retrieving dropdown values grouped by category."""
        response = requests.get(f"{API_V1_BASE}/dropdown/values/by-category")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Should include risk categories
        assert "risk_category" in data
        assert "risk_status" in data
        
        # Each category should have values
        for category, values in data.items():
            assert isinstance(values, list)
            assert len(values) > 0
            for value in values:
                assert value["category"] == category


class TestDashboardEndpoints:
    """Test dashboard endpoints."""
    
    def test_get_dashboard_data(self):
        """Test retrieving dashboard data."""
        response = requests.get(f"{API_V1_BASE}/dashboard/")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify main dashboard structure
        assert "total_active_risks" in data
        assert "critical_high_risk_count" in data
        assert "risk_trend_change" in data
        assert "risk_severity_distribution" in data
        assert "technology_domain_risks" in data
        assert "control_posture" in data
        assert "top_priority_risks" in data
        assert "risk_response_breakdown" in data
        assert "total_financial_exposure" in data
        assert "business_service_exposure" in data
        
        # Verify data types
        assert isinstance(data["total_active_risks"], int)
        assert isinstance(data["critical_high_risk_count"], int)
        assert isinstance(data["risk_trend_change"], (int, float))
        
        # Verify risk severity distribution
        severity = data["risk_severity_distribution"]
        assert "critical" in severity
        assert "high" in severity
        assert "medium" in severity
        assert "low" in severity
        
        # Verify top priority risks structure
        top_risks = data["top_priority_risks"]
        assert isinstance(top_risks, list)
        for risk in top_risks[:3]:  # Check first 3 if they exist
            if risk:  # Only check if risk exists
                assert "risk_id" in risk
                assert "risk_title" in risk
                assert "current_risk_rating" in risk


class TestRiskEndpoints:
    """Test risk management endpoints."""
    
    @pytest.fixture(scope="class")
    def test_risk_data(self):
        """Sample risk data for testing."""
        return {
            "risk_title": "Integration Test Risk",
            "risk_description": "A test risk created during integration testing",
            "risk_category": "Operational",
            "risk_owner": "Integration Test Suite",
            "risk_owner_department": "Information Technology",
            "technology_domain": "Applications",
            "inherent_probability": 3,
            "inherent_impact": 3,
            "current_probability": 2,
            "current_impact": 2,
            "risk_status": "Active",
            "risk_response_strategy": "Mitigate",
            "preventative_controls_status": "Adequate",
            "detective_controls_status": "Adequate",
            "corrective_controls_status": "Adequate",
            "ibs_impact": False,
            "business_criticality": "Medium",
            "date_identified": "2025-01-09",
            "last_reviewed": "2025-01-09",
            "next_review_date": "2025-02-09"
        }
    
    def test_get_risks_paginated(self):
        """Test retrieving risks with pagination."""
        response = requests.get(f"{API_V1_BASE}/risks/")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "pagination" in data
        
        pagination = data["pagination"]
        assert "total" in pagination
        assert "page" in pagination
        assert "per_page" in pagination
        assert "pages" in pagination
        assert "has_prev" in pagination
        assert "has_next" in pagination
        
        # Verify data types
        assert isinstance(pagination["total"], int)
        assert isinstance(pagination["page"], int)
        assert isinstance(pagination["per_page"], int)
        assert isinstance(pagination["pages"], int)
        assert isinstance(pagination["has_prev"], bool)
        assert isinstance(pagination["has_next"], bool)
        
        # First page should not have previous
        assert pagination["page"] == 1
        assert pagination["has_prev"] is False
        
        # Verify items structure
        items = data["items"]
        assert isinstance(items, list)
        
        if len(items) > 0:
            first_risk = items[0]
            assert "risk_id" in first_risk
            assert "risk_title" in first_risk
            assert "risk_category" in first_risk
            assert "current_risk_rating" in first_risk
    
    def test_get_risks_with_search(self):
        """Test searching risks."""
        response = requests.get(f"{API_V1_BASE}/risks/?search=cybersecurity")
        assert response.status_code == 200
        
        data = response.json()
        items = data["items"]
        
        # Should find risks with "cybersecurity" in title or description
        for risk in items:
            title = risk["risk_title"].lower()
            description = risk["risk_description"].lower()
            assert "cybersecurity" in title or "cybersecurity" in description
    
    def test_get_risks_with_category_filter(self):
        """Test filtering risks by category."""
        response = requests.get(f"{API_V1_BASE}/risks/?category=Cybersecurity")
        assert response.status_code == 200
        
        data = response.json()
        items = data["items"]
        
        # All risks should be in Cybersecurity category
        for risk in items:
            assert risk["risk_category"] == "Cybersecurity"
    
    def test_get_risks_with_sorting(self):
        """Test sorting risks."""
        # Test sorting by title ascending
        response = requests.get(f"{API_V1_BASE}/risks/?sort_by=risk_title&sort_order=asc&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        items = data["items"]
        
        if len(items) > 1:
            # Should be sorted alphabetically
            titles = [risk["risk_title"] for risk in items]
            assert titles == sorted(titles)
    
    def test_get_risks_pagination_limits(self):
        """Test pagination limits."""
        # Test limit too high
        response = requests.get(f"{API_V1_BASE}/risks/?limit=1000")
        assert response.status_code == 400
        assert "cannot exceed 500" in response.json()["detail"]
        
        # Test limit of 0
        response = requests.get(f"{API_V1_BASE}/risks/?limit=0")
        assert response.status_code == 400
        assert "must be greater than 0" in response.json()["detail"]
    
    def test_get_specific_risk(self):
        """Test retrieving a specific risk."""
        # First get list of risks to find a valid ID
        response = requests.get(f"{API_V1_BASE}/risks/?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) > 0:
            risk_id = data["items"][0]["risk_id"]
            
            # Now get the specific risk
            response = requests.get(f"{API_V1_BASE}/risks/{risk_id}")
            assert response.status_code == 200
            
            risk = response.json()
            assert risk["risk_id"] == risk_id
            assert "risk_title" in risk
            assert "risk_description" in risk
    
    def test_get_nonexistent_risk(self):
        """Test retrieving a non-existent risk."""
        response = requests.get(f"{API_V1_BASE}/risks/NONEXISTENT-RISK-ID")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_create_update_delete_risk_flow(self, test_risk_data):
        """Test creating, updating, and deleting a risk."""
        # Create risk
        response = requests.post(f"{API_V1_BASE}/risks/", json=test_risk_data)
        assert response.status_code == 200
        
        created_risk = response.json()
        risk_id = created_risk["risk_id"]
        
        try:
            # Verify risk was created
            assert created_risk["risk_title"] == test_risk_data["risk_title"]
            assert created_risk["current_risk_rating"] == 4  # 2 * 2
            assert "risk_id" in created_risk
            
            # Get the created risk
            response = requests.get(f"{API_V1_BASE}/risks/{risk_id}")
            assert response.status_code == 200
            
            # Update the risk
            update_data = test_risk_data.copy()
            update_data["risk_title"] = "Updated Integration Test Risk"
            update_data["current_probability"] = 3
            
            response = requests.put(f"{API_V1_BASE}/risks/{risk_id}", json=update_data)
            assert response.status_code == 200
            
            updated_risk = response.json()
            assert updated_risk["risk_title"] == "Updated Integration Test Risk"
            assert updated_risk["current_risk_rating"] == 6  # 3 * 2
            
        finally:
            # Clean up - delete the test risk
            response = requests.delete(f"{API_V1_BASE}/risks/{risk_id}")
            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]
            
            # Verify risk is deleted
            response = requests.get(f"{API_V1_BASE}/risks/{risk_id}")
            assert response.status_code == 404


class TestRiskUpdateEndpoints:
    """Test risk update endpoints."""
    
    def test_get_risk_updates(self):
        """Test retrieving updates for a specific risk."""
        # First get a risk ID
        response = requests.get(f"{API_V1_BASE}/risks/?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) > 0:
            risk_id = data["items"][0]["risk_id"]
            
            # Get updates for this risk
            response = requests.get(f"{API_V1_BASE}/risks/{risk_id}/updates")
            assert response.status_code == 200
            
            updates = response.json()
            assert isinstance(updates, list)
            
            # If updates exist, verify structure
            for update in updates:
                assert "update_id" in update
                assert "risk_id" in update
                assert "update_date" in update
                assert "updated_by" in update
                assert "update_type" in update
                assert update["risk_id"] == risk_id
    
    def test_get_recent_risk_updates(self):
        """Test retrieving recent risk updates."""
        response = requests.get(f"{API_V1_BASE}/risks/updates/recent?limit=5")
        assert response.status_code == 200
        
        updates = response.json()
        assert isinstance(updates, list)
        
        # Verify structure of updates
        for update in updates:
            assert "update_id" in update
            assert "risk_id" in update
            assert "update_date" in update
            assert "updated_by" in update
            assert "update_type" in update
    
    def test_get_recent_updates_limit_validation(self):
        """Test recent updates endpoint limit validation."""
        # Test limit too high
        response = requests.get(f"{API_V1_BASE}/risks/updates/recent?limit=200")
        assert response.status_code == 400
        assert "cannot exceed 100" in response.json()["detail"]
    
    def test_get_updates_for_nonexistent_risk(self):
        """Test getting updates for non-existent risk."""
        response = requests.get(f"{API_V1_BASE}/risks/NONEXISTENT/updates")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_endpoints(self):
        """Test invalid API endpoints return 404."""
        invalid_endpoints = [
            "/api/v1/invalid",
            "/api/v1/risks/invalid/endpoint",
            "/api/v1/dropdown/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            assert response.status_code == 404
    
    def test_invalid_http_methods(self):
        """Test invalid HTTP methods."""
        # Try POST on dropdown categories (should be GET only)
        response = requests.post(f"{API_V1_BASE}/dropdown/categories", json={})
        assert response.status_code == 405
        
        # Try PUT on dashboard (should be GET only)  
        response = requests.put(f"{API_V1_BASE}/dashboard/", json={})
        assert response.status_code == 405
    
    def test_malformed_json_requests(self):
        """Test handling of malformed JSON in requests."""
        response = requests.post(
            f"{API_V1_BASE}/risks/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields in risk creation."""
        incomplete_risk = {
            "risk_title": "Incomplete Risk",
            # Missing required fields
        }
        
        response = requests.post(f"{API_V1_BASE}/risks/", json=incomplete_risk)
        assert response.status_code == 422
        
        error_details = response.json()
        assert "detail" in error_details


if __name__ == "__main__":
    print(f"Running integration tests against: {API_BASE_URL}")
    print("Make sure the API server is running before executing tests!")
    print("Local: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("Docker: docker-compose up")