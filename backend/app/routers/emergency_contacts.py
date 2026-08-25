"""
SENTRA Emergency Contacts Router
Provides REST endpoints for managing user emergency contacts.
All endpoints require authentication and enforce strict user data isolation.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactResponse,
    EmergencyContactDeleteResponse,
)
from app.services.emergency_contact_service import emergency_contact_service
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post(
    "",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create emergency contact",
    description="Creates a new emergency contact for the authenticated user."
)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates an emergency contact for the authenticated user.
    """
    return emergency_contact_service.create_contact(
        db=db,
        user=current_user,
        contact_data=contact_data
    )


@router.get(
    "",
    response_model=List[EmergencyContactResponse],
    status_code=status.HTTP_200_OK,
    summary="List all emergency contacts",
    description="Returns all emergency contacts registered by the authenticated user."
)
async def list_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all contacts belonging to the authenticated user.
    """
    return emergency_contact_service.get_user_contacts(
        db=db,
        user=current_user
    )


@router.get(
    "/{contact_id}",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get emergency contact by ID",
    description="Returns details for a specific emergency contact belonging to the authenticated user."
)
async def get_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific contact by ID.
    Returns 404 if the contact does not exist or belongs to another user.
    """
    return emergency_contact_service.get_contact_by_id(
        db=db,
        user=current_user,
        contact_id=contact_id
    )


@router.put(
    "/{contact_id}",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Update emergency contact",
    description="Updates permitted fields of an emergency contact belonging to the authenticated user."
)
async def update_emergency_contact(
    contact_id: int,
    update_data: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates an emergency contact.
    """
    return emergency_contact_service.update_contact(
        db=db,
        user=current_user,
        contact_id=contact_id,
        update_data=update_data
    )


@router.delete(
    "/{contact_id}",
    response_model=EmergencyContactDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete emergency contact",
    description="Deletes an emergency contact belonging to the authenticated user."
)
async def delete_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes an emergency contact.
    """
    return emergency_contact_service.delete_contact(
        db=db,
        user=current_user,
        contact_id=contact_id
    )
