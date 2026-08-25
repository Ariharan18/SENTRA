"""
SENTRA Alert Schemas
Pydantic schemas for alert creation, status updates, and retrieval.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    alert_type: str = Field(..., min_length=1, max_length=50, description="Type of alert generated")
    priority: str = Field(..., max_length=20, description="Alert priority (LOW, MEDIUM, HIGH, CRITICAL)")
    status: str = Field(default="new", max_length=30, description="Status (new, acknowledged, investigating, resolved)")


class AlertCreate(BaseModel):
    event_id: int = Field(..., description="Foreign key to associated event")
    user_id: int = Field(..., description="Foreign key to associated user")
    alert_type: str = Field(..., min_length=1, max_length=50, description="Type of alert")
    priority: str = Field(..., max_length=20, description="Alert priority level")
    status: Optional[str] = Field("new", max_length=30, description="Initial alert status")


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=30, description="Updated status (acknowledged, investigating, resolved)")
    priority: Optional[str] = Field(None, max_length=20, description="Updated priority level")


class AlertResponse(BaseModel):
    alert_id: int
    event_id: int
    user_id: int
    alert_type: str
    priority: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
