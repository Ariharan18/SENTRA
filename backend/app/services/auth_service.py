"""
SENTRA Authentication Service
Encapsulates business logic for user registration, credential authentication, and JWT token issuance.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Registers a new user account.
        Enforces unique email constraint and securely hashes the password.
        """
        clean_email = user_data.email.strip().lower()

        # Check for existing email account
        existing_user = db.query(User).filter(User.email == clean_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists."
            )

        # Hash password securely
        hashed_password = hash_password(user_data.password)

        new_user = User(
            name=user_data.name.strip(),
            email=clean_email,
            phone=user_data.phone.strip() if user_data.phone else None,
            password_hash=hashed_password,
            role="user",
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Validates user credentials against stored bcrypt hash.
        """
        clean_email = email.strip().lower()
        user = db.query(User).filter(User.email == clean_email).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> TokenResponse:
        """
        Authenticates the user and returns an access token.
        """
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)

        # Build JWT payload
        token_payload = {
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role,
        }

        token = create_access_token(data=token_payload)
        return TokenResponse(access_token=token, token_type="bearer")


auth_service = AuthService()
