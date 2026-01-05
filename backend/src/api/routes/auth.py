"""Authentication endpoints: login, signup, logout, me."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.api.models.auth_schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse,
    SignupResponse,
    LogoutResponse
)
from src.api.dependencies import get_current_user
from src.database import get_db, get_user_by_email, create_user
from src.models.user import User
from src.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token
)
from src.utils.logger import get_logger
from src.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None
    )


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Signup response with user information
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = create_user(
            db=db,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        logger.info(f"New user registered: {user.email}")
        
        return SignupResponse(
            message="User created successfully",
            user=user_to_response(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login user and set authentication cookie.
    
    Args:
        user_data: User login credentials
        response: FastAPI response object (for setting cookies)
        db: Database session
        
    Returns:
        Login response with user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Get user by email
        user = get_user_by_email(db, user_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        # Set HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.is_production,  # HTTPS only in production
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return LoginResponse(
            message="Login successful",
            user=user_to_response(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response):
    """
    Logout user by clearing authentication cookie.
    
    Args:
        response: FastAPI response object
        
    Returns:
        Logout response
    """
    # Clear cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.is_production,
        samesite="lax"
    )
    
    return LogoutResponse(message="Logout successful")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        User information
    """
    return user_to_response(current_user)


@router.get("/verify", response_model=dict)
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify if authentication token is valid.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Verification status
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }

