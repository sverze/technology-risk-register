"""Tests for authentication endpoints and refresh token functionality."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from app.main import app
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_login_success(client):
    """Test successful login returns both access and refresh tokens."""
    response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


def test_login_invalid_username(client):
    """Test login with invalid username fails."""
    response = client.post(
        "/api/v1/auth/login",
        auth=("wrong_user", settings.AUTH_PASSWORD),
    )

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_invalid_password(client):
    """Test login with invalid password fails."""
    response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, "wrong_password"),
    )

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_verify_token_success(client):
    """Test token verification with valid access token."""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )
    access_token = login_response.json()["access_token"]

    # Verify token
    response = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["username"] == settings.AUTH_USERNAME


def test_verify_token_invalid(client):
    """Test token verification with invalid token."""
    response = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


def test_refresh_token_success(client):
    """Test refreshing access token with valid refresh token."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_refresh_token_invalid(client):
    """Test refresh endpoint with invalid refresh token."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )

    assert response.status_code == 401


def test_refresh_token_with_access_token_fails(client):
    """Test that access token cannot be used to refresh."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )
    access_token = login_response.json()["access_token"]

    # Try to use access token as refresh token (should fail)
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


def test_logout_success(client):
    """Test logout with valid token."""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )
    access_token = login_response.json()["access_token"]

    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "Successfully logged out" in data["message"]


def test_logout_invalid_token(client):
    """Test logout with invalid token."""
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


def test_token_types_are_different():
    """Test that access and refresh tokens have different types."""
    from app.core.security import decode_access_token
    from jose import jwt

    access_token = create_access_token(data={"sub": "testuser"})
    refresh_token = create_refresh_token(data={"sub": "testuser"})

    # Decode without validation to check type field
    access_payload = jwt.decode(
        access_token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.AUTH_ALGORITHM],
    )
    refresh_payload = jwt.decode(
        refresh_token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.AUTH_ALGORITHM],
    )

    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert access_payload["sub"] == "testuser"
    assert refresh_payload["sub"] == "testuser"


def test_access_token_expiry():
    """Test that access tokens expire after configured time."""
    from jose import jwt

    access_token = create_access_token(data={"sub": "testuser"})

    payload = jwt.decode(
        access_token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.AUTH_ALGORITHM],
    )

    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)

    # Token should expire in approximately 30 minutes
    time_diff = (exp_time - now).total_seconds() / 60
    assert 29 <= time_diff <= 31  # Allow 1 minute tolerance


def test_refresh_token_expiry():
    """Test that refresh tokens expire after configured time."""
    from jose import jwt

    refresh_token = create_refresh_token(data={"sub": "testuser"})

    payload = jwt.decode(
        refresh_token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.AUTH_ALGORITHM],
    )

    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)

    # Token should expire in approximately 7 days
    time_diff = (exp_time - now).total_seconds() / 86400  # Convert to days
    assert 6.9 <= time_diff <= 7.1  # Allow small tolerance


def test_protected_endpoint_without_token(client):
    """Test that protected endpoints require authentication."""
    response = client.get("/api/v1/risks/")

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client):
    """Test that protected endpoints work with valid token."""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
    )
    access_token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/v1/risks/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Should succeed (200) or return empty list, not 401
    assert response.status_code == 200
