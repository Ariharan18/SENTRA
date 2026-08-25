"""
SENTRA API Routers Package
Exports API route modules for authentication, user management, and emergency contacts.
"""

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.emergency_contacts import router as emergency_contacts_router

__all__ = [
    "auth_router",
    "users_router",
    "emergency_contacts_router",
]
