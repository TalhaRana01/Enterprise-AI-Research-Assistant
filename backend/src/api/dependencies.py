"""Dependencies for FastAPI routes (authentication, etc.)."""

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db, get_user_by_id
from src.models.user import User
from src.utils.auth import (
    get_token_from_cookie,
    get_token_from_header,
    get_current_user_id_from_token
)
from src.utils.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token (cookie or header).
    
    Args:
        access_token: JWT token from cookie
        credentials: HTTP Bearer credentials from header
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user is not authenticated
    """
    token = None
    
    # Try to get token from cookie first
    if access_token:
        token = access_token
    # Fallback to header
    elif credentials:
        token = get_token_from_header(credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode token and get user ID
        user_id = get_current_user_id_from_token(token)
        
        # Get user from database
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_current_user(
    access_token: Optional[str] = Cookie(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for optional authentication.
    
    Args:
        access_token: JWT token from cookie
        credentials: HTTP Bearer credentials from header
        db: Database session
        
    Returns:
        Current user or None
    """
    try:
        return await get_current_user(access_token, credentials, db)
    except HTTPException:
        return None

