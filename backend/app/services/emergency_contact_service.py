"""
SENTRA Emergency Contact Service
Encapsulates business logic and ownership authorization for user emergency contact management.
"""

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate


class EmergencyContactService:
    @staticmethod
    def create_contact(
        db: Session,
        user: User,
        contact_data: EmergencyContactCreate
    ) -> EmergencyContact:
        """
        Creates a new emergency contact associated strictly with the authenticated user.
        """
        new_contact = EmergencyContact(
            user_id=user.user_id,
            contact_name=contact_data.contact_name.strip(),
            phone=contact_data.phone.strip(),
            relationship=contact_data.relationship.strip() if contact_data.relationship else None,
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact

    @staticmethod
    def get_user_contacts(
        db: Session,
        user: User
    ) -> List[EmergencyContact]:
        """
        Retrieves all emergency contacts belonging to the authenticated user.
        """
        return db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user.user_id
        ).all()

    @staticmethod
    def get_contact_by_id(
        db: Session,
        user: User,
        contact_id: int
    ) -> EmergencyContact:
        """
        Retrieves a single emergency contact by ID.
        Enforces ownership: returns 404 Not Found if contact does not exist or belongs to another user.
        """
        contact = db.query(EmergencyContact).filter(
            EmergencyContact.contact_id == contact_id,
            EmergencyContact.user_id == user.user_id
        ).first()

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        return contact

    @staticmethod
    def update_contact(
        db: Session,
        user: User,
        contact_id: int,
        update_data: EmergencyContactUpdate
    ) -> EmergencyContact:
        """
        Updates an existing emergency contact belonging to the authenticated user.
        """
        contact = EmergencyContactService.get_contact_by_id(db, user, contact_id)

        if update_data.contact_name is not None:
            contact.contact_name = update_data.contact_name.strip()

        if update_data.phone is not None:
            contact.phone = update_data.phone.strip()

        if update_data.relationship is not None:
            contact.relationship = update_data.relationship.strip() if update_data.relationship else None

        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def delete_contact(
        db: Session,
        user: User,
        contact_id: int
    ) -> dict:
        """
        Deletes an emergency contact belonging to the authenticated user.
        """
        contact = EmergencyContactService.get_contact_by_id(db, user, contact_id)

        db.delete(contact)
        db.commit()
        return {
            "message": "Emergency contact deleted successfully",
            "contact_id": contact_id
        }


emergency_contact_service = EmergencyContactService()
