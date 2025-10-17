"""
Integration tests for the Chat API endpoint.

These tests verify end-to-end functionality with real database queries
and the Risk SME Agent.
"""


class TestChatIntegrationE2E:
    """End-to-end integration tests for chat functionality."""

    def test_chat_simple_filter_query(self, client, dashboard_sample_risks):
        """Test a simple filter query returns expected results."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all active risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should find 4 active risks from dashboard_sample_risks fixture
        # (TR-2024-CYB-001, TR-2024-INF-001, TR-2024-APP-001, TR-2024-OPS-001)
        assert data["status"] == "success"
        assert "answer" in data
        assert "4" in data["answer"] or "four" in data["answer"].lower()

    def test_chat_count_query(self, client, dashboard_sample_risks):
        """Test counting query returns correct count."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "How many total risks are in the system?"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        # Should have 5 total risks (4 active + 1 closed)
        assert "5" in data["answer"] or "five" in data["answer"].lower()

    def test_chat_group_by_domain(self, client, dashboard_sample_risks):
        """Test grouping risks by technology domain."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "How many risks are in each technology domain?"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["answer_rows"] is not None
        assert len(data["answer_rows"]) > 0

        # Verify structure of results
        for row in data["answer_rows"]:
            assert "technology_domain" in str(row) or "domain" in str(row).lower()

    def test_chat_financial_impact_filter(self, client, dashboard_sample_risks):
        """Test filtering by financial impact."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks with financial impact over $100,000"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success":
            # dashboard_sample_risks has 2 risks with financial_impact_high > $100k
            # (TR-2024-CYB-001: $2M, TR-2024-INF-001: $800k)
            assert data["answer_rows"] is not None
            assert len(data["answer_rows"]) >= 2

    def test_chat_exposure_filter(self, client, dashboard_sample_risks):
        """Test filtering by risk exposure level."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all critical risks"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # All returned risks should have "Critical" in exposure
            for row in data["answer_rows"]:
                if "exposure" in row:
                    assert "Critical" in row["exposure"]

    def test_chat_owner_filter(self, client, dashboard_sample_risks):
        """Test filtering by risk owner."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks owned by Security Team"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # Verify owner matches
            for row in data["answer_rows"]:
                if "owner" in row:
                    assert "Security" in row["owner"]

    def test_chat_date_range_query(self, client, dashboard_sample_risks):
        """Test date range filtering."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks reviewed in the last 30 days"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should find risks based on last_reviewed date
        assert data["status"] in ["success", "no_results"]

    def test_chat_multi_condition_query(self, client, dashboard_sample_risks):
        """Test query with multiple filter conditions."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me active Infrastructure risks with high or critical exposure"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # Verify all conditions are met
            for row in data["answer_rows"]:
                if "status" in row:
                    assert row["status"] == "Active"
                if "domain" in str(row).lower() or "technology_domain" in row:
                    domain_value = row.get("domain") or row.get("technology_domain")
                    assert "Infrastructure" in str(domain_value)

    def test_chat_text_search(self, client, dashboard_sample_risks):
        """Test text search in risk titles."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Find risks with 'security' in the title"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # All returned risks should have "security" in title
            for row in data["answer_rows"]:
                if "title" in row:
                    assert "security" in row["title"].lower()

    def test_chat_log_entries_relationship(self, client, dashboard_sample_risks):
        """Test querying risks with log entries."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks that have log entries"},
        )

        assert response.status_code == 200
        data = response.json()

        # dashboard_sample_risks creates 2 log entries
        # (for TR-2024-CYB-001 and TR-2024-INF-001)
        assert data["status"] in ["success", "no_results"]

    def test_chat_aggregation_by_status(self, client, dashboard_sample_risks):
        """Test aggregation query grouping by status."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Count risks grouped by status"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["answer_rows"] is not None

        # Should have at least 2 groups (Active and Closed)
        assert len(data["answer_rows"]) >= 2

    def test_chat_top_n_query(self, client, dashboard_sample_risks):
        """Test top N query with limit."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me the top 3 risks by financial impact"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            # Should return at most 3 risks
            assert len(data["answer_rows"]) <= 3

    def test_chat_with_code_visibility(self, client, dashboard_sample_risks):
        """Test that generated code is visible when requested."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "question": "How many active risks are there?",
                "show_code": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should include the generated SQLAlchemy code
        assert data["code"] is not None
        assert "session.query" in data["code"]
        assert "Risk" in data["code"]
        assert "filter" in data["code"].lower()

    def test_chat_invalid_question_handling(self, client, dashboard_sample_risks):
        """Test handling of ambiguous or invalid questions."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "blah blah gibberish nonsense xyz"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should handle gracefully
        assert data["status"] in ["success", "no_results", "invalid_request", "error"]

    def test_chat_with_different_temperatures(self, client, dashboard_sample_risks):
        """Test that different temperatures still produce valid results."""
        temperatures = [0.0, 0.2, 0.5, 0.8]

        for temp in temperatures:
            response = client.post(
                "/api/v1/chat/",
                json={
                    "question": "Count active risks",
                    "temperature": temp,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["success", "no_results"]

    def test_chat_overdue_review_query(self, client, dashboard_sample_risks):
        """Test finding overdue risks (next_review_date in the past)."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me risks that are overdue for review"},
        )

        assert response.status_code == 200
        data = response.json()

        # dashboard_sample_risks has TR-2024-OPS-001 with overdue review
        assert data["status"] in ["success", "no_results"]
        if data["status"] == "success" and data["answer_rows"]:
            assert len(data["answer_rows"]) >= 1

    def test_chat_health_check_integration(self, client):
        """Test that health check endpoint is accessible."""
        response = client.get("/api/v1/chat/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "risk-sme-chat"
        assert "message" in data


class TestChatPerformance:
    """Performance and edge case tests for chat endpoint."""

    def test_chat_with_large_result_set(self, client, dashboard_sample_risks):
        """Test chat handles queries that return many results."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should handle all results gracefully
        assert data["status"] == "success"

    def test_chat_concurrent_requests(self, client, dashboard_sample_risks):
        """Test chat can handle multiple concurrent requests."""
        import concurrent.futures

        def make_request():
            return client.post(
                "/api/v1/chat/",
                json={"question": "Count active risks"},
            )

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        for response in results:
            assert response.status_code == 200

    def test_chat_execution_log_captured(self, client, dashboard_sample_risks):
        """Test that execution logs are properly captured."""
        response = client.post(
            "/api/v1/chat/",
            json={"question": "Show me all active risks"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should have execution log
        assert "execution_log" in data
        if data["execution_log"]:
            assert "LOG:" in data["execution_log"]
            assert "STATUS=" in data["execution_log"]
