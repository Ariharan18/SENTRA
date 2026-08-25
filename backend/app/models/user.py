"""
SENTRA User Model
Represents registered users, administrators, and system actors.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="user", server_default="user")
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    # Relationships
    emergency_contacts = relationship(
        "EmergencyContact",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    events = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    locations = relationship(
        "Location",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email='{self.email}', role='{self.role}')>"
