"""
SENTRA Core Module
Exports configuration, security utilities, and dependencies.
"""

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.dependencies import (
    oauth2_scheme,
    get_current_user,
    get_current_admin_user,
    require_roles,
)

__all__ = [
    "settings",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "oauth2_scheme",
    "get_current_user",
    "get_current_admin_user",
    "require_roles",
]
