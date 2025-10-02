"""Authentication routes for login, token verification, and logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, get_current_user, verify_password

router = APIRouter()
security = HTTPBasic()


class Token(BaseModel):
    """Response model for successful login."""

    access_token: str
    token_type: str


class TokenVerifyResponse(BaseModel):
    """Response model for token verification."""

    valid: bool
    username: str


class LogoutResponse(BaseModel):
    """Response model for logout."""

    message: str


@router.post("/login", response_model=Token)
async def login(credentials: HTTPBasicCredentials = Depends(security)) -> Token:
    """
    Authenticate user and return JWT access token.

    This endpoint accepts HTTP Basic Auth credentials:
    - Username and password in Authorization header
    - Returns JWT token valid for 12 hours

    Args:
        credentials: HTTP Basic Auth credentials

    Returns:
        Token object with access_token and token_type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Get configured username and password from settings
    configured_username = settings.AUTH_USERNAME
    configured_password = settings.AUTH_PASSWORD

    # Check if username matches
    if credentials.username != configured_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Verify password (plain text comparison for simplicity)
    # In a real system with multiple users, we'd hash passwords
    if credentials.password != configured_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Create JWT token with username as subject
    access_token = create_access_token(data={"sub": credentials.username})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(username: str = Depends(get_current_user)) -> TokenVerifyResponse:
    """
    Verify JWT token is valid and return username.

    This endpoint requires a valid JWT token in Authorization header.

    Args:
        username: Username extracted from valid JWT token

    Returns:
        TokenVerifyResponse with valid status and username

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    return TokenVerifyResponse(valid=True, username=username)


@router.post("/logout", response_model=LogoutResponse)
async def logout(username: str = Depends(get_current_user)) -> LogoutResponse:
    """
    Logout endpoint (client-side token removal).

    Since JWT tokens are stateless, this endpoint primarily serves
    as a signal to the client to remove the token from storage.
    The token will still be valid until it expires (12 hours).

    Args:
        username: Username extracted from valid JWT token

    Returns:
        LogoutResponse with success message

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    return LogoutResponse(message="Successfully logged out")
