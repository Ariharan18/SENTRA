"""
SENTRA Safety Event Model
Represents safety events, incident logs, and SOS activations.
"""

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="new", server_default="new", index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), index=True)

    # Relationships
    user = relationship("User", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Event(event_id={self.event_id}, user_id={self.user_id}, type='{self.event_type}', risk='{self.risk_level}')>"
