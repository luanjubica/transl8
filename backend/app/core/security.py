from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

# HTTP Bearer token scheme
security = HTTPBearer()


def decode_clerk_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate Clerk JWT token.

    Args:
        token: JWT token from Clerk

    Returns:
        Decoded token payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode JWT token with Clerk's public key
        payload = jwt.decode(
            token,
            settings.CLERK_JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False}  # Clerk doesn't always set audience
        )
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract current user ID from JWT token.

    This is a dependency that can be used in API endpoints to get the
    authenticated user's ID from Clerk.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        User ID (Clerk ID) from the token

    Raises:
        HTTPException: If token is invalid or missing user ID
    """
    token = credentials.credentials
    payload = decode_clerk_jwt(token)

    # Extract user ID from Clerk token (usually in 'sub' claim)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key for machine-to-machine authentication.

    This is used for API-only access (integrations, webhooks, etc.)
    without Clerk authentication.

    Args:
        api_key: API key from request header

    Returns:
        True if valid, False otherwise

    TODO: Implement proper API key validation against database
    """
    # Placeholder - implement API key validation
    return False
