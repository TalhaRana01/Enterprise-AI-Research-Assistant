"""Authentication schemas for user management."""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: int = Field(..., description="User ID")
    is_active: bool = Field(default=True, description="User active status")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")


class LoginResponse(BaseModel):
    """Schema for login response."""
    
    message: str = Field(default="Login successful", description="Response message")
    user: UserResponse = Field(..., description="User information")


class SignupResponse(BaseModel):
    """Schema for signup response."""
    
    message: str = Field(default="User created successfully", description="Response message")
    user: UserResponse = Field(..., description="User information")


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    
    message: str = Field(default="Logout successful", description="Response message")

