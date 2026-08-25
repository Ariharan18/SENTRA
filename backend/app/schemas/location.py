"""
SENTRA Location Schemas
Pydantic schemas for recording and retrieving geographic coordinates.
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90, description="GPS Latitude (-90 to +90)")
    longitude: Decimal = Field(..., ge=-180, le=180, description="GPS Longitude (-180 to +180)")


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    location_id: int
    user_id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
