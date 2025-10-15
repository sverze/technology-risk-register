"""
Unit tests for the Chat API endpoint.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.schemas.chat import ChatRequest, ChatResponse


class TestChatEndpoint:
    """Test the chat endpoint functionality."""

    def test_chat_with_valid_question(self, client, dashboard_sample_risks):
        """Test chat endpoint with a valid question."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all active risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "status" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

        # Status should be success or no_results
        assert data["status"] in ["success", "no_results"]

    def test_chat_with_empty_question(self, client):
        """Test chat endpoint rejects empty questions."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": ""},
        )

        assert response.status_code == 400

    def test_chat_with_show_code_true(self, client, dashboard_sample_risks):
        """Test chat endpoint returns code when show_code=True."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "Show me all risks",
                "show_code": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should include generated code
        assert "code" in data
        if data["status"] == "success":
            assert data["code"] is not None
            assert "session.query" in data["code"]

    def test_chat_with_custom_temperature(self, client, dashboard_sample_risks):
        """Test chat endpoint accepts custom temperature."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "How many risks are active?",
                "temperature": 0.5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_chat_with_aggregation_query(self, client, dashboard_sample_risks):
        """Test chat endpoint handles aggregation queries."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "How many risks does each owner have?"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success":
            # Should have structured results
            assert "answer_rows" in data

    def test_chat_with_filter_query(self, client, dashboard_sample_risks):
        """Test chat endpoint handles filtered queries."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me critical risks"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]

    def test_chat_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/v1/chat/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "risk-sme-chat"

    def test_chat_request_validation(self):
        """Test ChatRequest model validation."""
        # Valid request
        valid_request = ChatRequest(question="Test question")
        assert valid_request.question == "Test question"
        assert valid_request.temperature == 0.2  # Default
        assert valid_request.show_code is False  # Default

        # Temperature validation
        with pytest.raises(ValueError):
            ChatRequest(question="Test", temperature=1.5)  # > 1.0

        with pytest.raises(ValueError):
            ChatRequest(question="Test", temperature=-0.1)  # < 0.0

        # Question length validation
        with pytest.raises(ValueError):
            ChatRequest(question="x" * 1001)  # > 1000 chars

    def test_chat_response_structure(self):
        """Test ChatResponse model structure."""
        response = ChatResponse(
            answer="Test answer",
            status="success",
            answer_rows=[{"id": "TR-001", "title": "Test"}],
            code="test code",
            error=None,
            execution_log="LOG: Test",
        )

        assert response.answer == "Test answer"
        assert response.status == "success"
        assert len(response.answer_rows) == 1
        assert response.code == "test code"
        assert response.error is None

    def test_chat_with_no_results(self, client, dashboard_sample_risks):
        """Test chat endpoint when query returns no results."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks owned by NonexistentPerson"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should indicate no results found
        assert data["status"] in ["success", "no_results"]

    def test_chat_with_complex_query(self, client, dashboard_sample_risks):
        """Test chat endpoint with a complex multi-condition query."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "Show me active risks in Infrastructure domain with high exposure",
                "show_code": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success":
            # Should have logical operators in code
            assert data["code"] is not None
            assert "and_" in data["code"] or "filter" in data["code"]

    def test_chat_without_authentication(self, sample_risks):
        """Test chat endpoint requires authentication."""
        # Create a client without auth
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all risks"},
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

    @patch("app.api.endpoints.chat.risk_sme_agent")
    def test_chat_handles_agent_errors(self, mock_agent, client, dashboard_sample_risks):
        """Test chat endpoint handles errors from risk_sme_agent."""
        # Mock the agent to raise an exception
        mock_agent.side_effect = Exception("Test error")

        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all risks"},
        )

        # Should return 500 Internal Server Error
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    @patch("app.api.endpoints.chat.risk_sme_agent")
    def test_chat_handles_code_execution_errors(self, mock_agent, client, dashboard_sample_risks):
        """Test chat endpoint when generated code has execution errors."""
        # Mock agent to return error in exec results
        mock_agent.return_value = {
            "exec": {
                "answer": "Query failed",
                "status": "error",
                "answer_rows": None,
                "code": "bad code",
                "error": "NameError: name 'undefined_var' is not defined",
                "stdout": "LOG: Error occurred",
            }
        }

        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return error status
        assert data["status"] == "error"
        assert data["error"] is not None

    def test_chat_preserves_execution_log(self, client, dashboard_sample_risks):
        """Test that execution logs are included in response."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Count all active risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should have execution log
        assert "execution_log" in data

    def test_chat_question_max_length(self, client):
        """Test chat endpoint validates question max length."""
        # Create a question that's too long (> 1000 chars)
        long_question = "Show me all risks " + ("with details " * 100)

        response = client.post(
            "/api/v1/chat/",
            json={"question": long_question},
        )

        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_chat_with_date_range_query(self, client, dashboard_sample_risks):
        """Test chat endpoint handles date range queries."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks reviewed in the last 30 days"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]


class TestChatIntegration:
    """Integration tests for chat endpoint with real risk data."""

    def test_full_workflow_simple_query(self, client, dashboard_sample_risks):
        """Test complete workflow for a simple query."""
        # 1. Ask a question
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "How many active risks are there?",
                "show_code": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # 2. Verify answer structure
        assert "answer" in data
        assert isinstance(data["answer"], str)

        # 3. Verify generated code looks reasonable
        if data["code"]:
            assert "Risk" in data["code"]
            assert "Active" in data["code"] or "active" in data["code"].lower()

        # 4. Verify status
        assert data["status"] == "success"

    def test_full_workflow_aggregation(self, client, dashboard_sample_risks):
        """Test complete workflow for aggregation query."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Group risks by technology domain and count them"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # Verify structured results
            assert isinstance(data["answer_rows"], list)
            if len(data["answer_rows"]) > 0:
                # Each row should have relevant fields
                first_row = data["answer_rows"][0]
                assert isinstance(first_row, dict)

    def test_full_workflow_financial_query(self, client, dashboard_sample_risks):
        """Test complete workflow for financial impact query."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks with financial impact greater than $100,000"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
