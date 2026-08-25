"""
SENTRA Audit Log Schemas
Pydantic schemas for creating and reviewing security audit log entries.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100, description="Action identifier (e.g., USER_REGISTERED, SOS_TRIGGERED)")
    details: Optional[str] = Field(None, description="Detailed contextual payload or notes")


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = Field(None, description="User identifier triggering the action")


class AuditLogResponse(AuditLogBase):
    log_id: int
    user_id: Optional[int] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
