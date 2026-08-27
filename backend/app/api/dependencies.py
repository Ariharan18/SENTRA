"""Shared API dependencies.

Phase 2 authentication is not part of this increment.  This dependency still
requires a bearer credential and resolves it to an active database user so
Phase 3 writes retain an accountable user ID.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve a simple bearer credential to an active user.

    Numeric tokens and ``user:<id>`` tokens select a user by ID; email tokens
    select by email. Invalid selectors are rejected.
    """

    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials.strip()
    user = None
    selector = token.removeprefix("user:")
    if selector.isdigit():
        user = db.scalar(select(User).where(User.id == int(selector), User.is_active.is_(True)))
    elif "@" in selector:
        user = db.scalar(select(User).where(User.email == selector, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
