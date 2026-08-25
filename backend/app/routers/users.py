"""
SENTRA User Management Router
Handles user profile inspection, profile updates, and password changes.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserProfileUpdate, UserPasswordUpdate
from app.schemas.auth import MessageResponse
from app.services.user_service import user_service
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the safe profile details of the currently authenticated user. Never exposes password hash."
)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns authenticated user's profile.
    """
    return user_service.get_profile(user=current_user)


@router.put(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Updates permitted profile fields (name, phone) for the authenticated user. Role and email cannot be changed."
)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates profile information for the authenticated user.
    """
    return user_service.update_profile(
        db=db,
        user=current_user,
        update_data=update_data
    )


@router.put(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Validates the current password and securely hashes and updates the new password."
)
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Changes account password for authenticated user.
    """
    return user_service.change_password(
        db=db,
        user=current_user,
        password_data=password_data
    )
