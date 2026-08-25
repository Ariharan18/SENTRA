"""
SENTRA Safety Event Schemas
Pydantic schemas for event creation, updates, querying, and SOS trigger actions.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50, description="Type of event (e.g., sos, incident, hazard)")
    risk_level: str = Field(default="LOW", max_length=20, description="Risk classification (LOW, MEDIUM, HIGH, CRITICAL)")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="GPS Latitude (-90 to +90)")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="GPS Longitude (-180 to +180)")
    description: Optional[str] = Field(None, description="Detailed description of the safety event")


class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50, description="Event type identifier")
    risk_level: Optional[str] = Field("LOW", max_length=20, description="Initial risk level")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Event GPS Latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Event GPS Longitude")
    description: Optional[str] = Field(None, description="Detailed event summary")


class EventUpdate(BaseModel):
    risk_level: Optional[str] = Field(None, max_length=20, description="Updated risk level")
    status: Optional[str] = Field(None, max_length=30, description="Updated status (new, acknowledged, investigating, resolved)")
    description: Optional[str] = Field(None, description="Updated description")


class EventResponse(BaseModel):
    event_id: int
    user_id: int
    event_type: str
    risk_level: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SOSTriggerRequest(BaseModel):
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Available device latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Available device longitude")
    description: Optional[str] = Field(default="Emergency assistance required", description="SOS emergency description")


class SOSTriggerResponse(BaseModel):
    message: str = "SOS activated"
    event_id: int
    alert_id: int
    risk_level: str = "CRITICAL"
