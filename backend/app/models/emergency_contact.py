"""
SENTRA Emergency Contact Model
Represents emergency contacts associated with a specific user.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship as sa_relationship
from app.database import Base


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    contact_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    contact_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    relationship = Column(String(50), nullable=True)

    # Relationship back to User using sa_relationship alias
    user = sa_relationship("User", back_populates="emergency_contacts")

    def __repr__(self) -> str:
        return f"<EmergencyContact(contact_id={self.contact_id}, user_id={self.user_id}, name='{self.contact_name}')>"
