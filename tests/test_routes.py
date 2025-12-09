"""
Test route configuration to ensure API endpoints are mounted correctly.

These tests prevent configuration issues where frontend and backend routing
don't match, which can cause 404 errors in production.
"""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_auth_routes_not_at_root():
    """Verify auth routes are NOT accessible at root /auth path."""
    # Auth routes should NOT work at /auth/login (missing /api/v1 prefix)
    response = client.post("/auth/login")
    assert response.status_code == 404, (
        "Auth routes should NOT be at root /auth path. "
        "They must be mounted at /api/v1/auth to match frontend expectations."
    )


def test_auth_routes_mounted_at_api_v1():
    """Verify auth routes are correctly mounted at /api/v1/auth."""
    # Auth routes should work at /api/v1/auth/login
    response = client.post(f"{settings.API_V1_STR}/auth/login")

    # Should return 401 (unauthorized) or 422 (validation error), NOT 404
    assert response.status_code in [401, 422], (
        f"Auth route should exist at {settings.API_V1_STR}/auth/login. "
        f"Got status {response.status_code}, expected 401 or 422."
    )


def test_api_prefix_configuration():
    """Verify API_V1_STR is set to /api/v1."""
    assert (
        settings.API_V1_STR == "/api/v1"
    ), "API prefix must be /api/v1 to match frontend configuration. Frontend expects all API routes at /api/v1/*."


def test_health_endpoint_at_root():
    """Verify health endpoint is accessible at root level."""
    # Health endpoint should be at root, not under /api/v1
    response = client.get("/health")
    assert response.status_code == 200, "Health endpoint should be at /health"
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Verify root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Technology Risk Register API" in response.json()["message"]
