"""
SENTRA Authentication Schemas
Defines request and response schemas for user registration, login, token exchange, and logout.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse


class RegisterRequest(UserCreate):
    """Registration payload schema."""
    pass


class LoginRequest(UserLogin):
    """Login payload schema."""
    pass


class AuthResponse(BaseModel):
    """Response containing user profile and issued access token."""
    user: UserResponse
    token: TokenResponse


class LogoutResponse(BaseModel):
    """Stateless logout confirmation response."""
    message: str = "Successfully logged out"


class MessageResponse(BaseModel):
    """Standard message response."""
    message: str
