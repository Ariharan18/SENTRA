"""
SENTRA User Service
Encapsulates business logic for user profile retrieval, profile updates, and secure password changes.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserPasswordUpdate
from app.core.security import hash_password, verify_password


class UserService:
    @staticmethod
    def get_profile(user: User) -> User:
        """
        Returns the user entity (safe serialization handled by Pydantic response schema).
        """
        return user

    @staticmethod
    def update_profile(db: Session, user: User, update_data: UserProfileUpdate) -> User:
        """
        Updates permitted user profile fields (name, phone).
        Role, email, and security fields cannot be modified through this endpoint.
        """
        if update_data.name is not None:
            user.name = update_data.name.strip()

        if update_data.phone is not None:
            user.phone = update_data.phone.strip()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, password_data: UserPasswordUpdate) -> dict:
        """
        Changes the user's password after verifying their current password.
        """
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password."
            )

        # Prevent setting the exact same password
        if verify_password(password_data.new_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be identical to the current password."
            )

        # Hash and persist new password
        user.password_hash = hash_password(password_data.new_password)
        db.add(user)
        db.commit()

        return {"message": "Password changed successfully"}


user_service = UserService()
