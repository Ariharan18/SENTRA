"""
SENTRA Authentication Router
Handles user registration, login (JWT token generation), and logout.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.auth import LogoutResponse
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers a new user account with unique email validation and secure password hashing."
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registers a new user with standard 'user' role.
    Rejects duplicate emails and returns safe user profile.
    """
    return auth_service.register_user(db=db, user_data=user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
    description="Validates credentials and issues a signed JWT Bearer access token containing user identity and role claims."
)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticates user with email and password.
    Returns access_token and token_type.
    """
    return auth_service.login_user(db=db, login_data=login_data)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user session",
    description="Stateless logout confirmation endpoint. Clients should discard their JWT token upon calling this endpoint."
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Validates token and returns successful logout message.
    """
    return LogoutResponse(message="Successfully logged out")
