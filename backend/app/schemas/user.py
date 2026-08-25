"""
SENTRA User Schemas
Pydantic schemas for user registration, authentication, profile updates, and API responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: str = Field(..., min_length=3, max_length=150, description="Unique email address")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="User password (plain-text for registration)")


class UserLogin(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated name")
    phone: Optional[str] = Field(None, max_length=20, description="Updated phone number")


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(..., description="Existing account password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New account password")


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
