"""
SENTRA Location Model
Stores geographical coordinates recorded for users and safety events.
"""

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    recorded_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    # Relationship back to User
    user = relationship("User", back_populates="locations")

    def __repr__(self) -> str:
        return f"<Location(location_id={self.location_id}, user_id={self.user_id}, lat={self.latitude}, lon={self.longitude})>"
