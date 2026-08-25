"""
SENTRA Emergency Contact Schemas
Pydantic schemas for creating, updating, and returning user emergency contacts.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmergencyContactBase(BaseModel):
    contact_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the emergency contact"
    )
    phone: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^\+?[0-9\s\-\(\)\.]{3,20}$",
        description="Phone number of the emergency contact"
    )
    relationship: Optional[str] = Field(
        None,
        max_length=50,
        description="Relationship to user (e.g., Parent, Spouse, Sibling, Friend)"
    )


class EmergencyContactCreate(EmergencyContactBase):
    pass


class EmergencyContactUpdate(BaseModel):
    contact_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated contact name"
    )
    phone: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        pattern=r"^\+?[0-9\s\-\(\)\.]{3,20}$",
        description="Updated phone number"
    )
    relationship: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated relationship"
    )


class EmergencyContactResponse(EmergencyContactBase):
    contact_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class EmergencyContactDeleteResponse(BaseModel):
    message: str = "Emergency contact deleted successfully"
    contact_id: int
