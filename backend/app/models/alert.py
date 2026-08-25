"""
SENTRA Alert Model
Represents alerts dispatched to administrators and responders for critical safety events.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="new", server_default="new", index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    # Relationships
    event = relationship("Event", back_populates="alerts")
    user = relationship("User", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(alert_id={self.alert_id}, event_id={self.event_id}, priority='{self.priority}', status='{self.status}')>"
