"""Monitored locations and traffic-source models."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.identity import User


class Location(TimestampMixin, Base):
    __tablename__ = "locations"
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_locations_latitude"),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180", name="ck_locations_longitude"
        ),
        CheckConstraint("road_capacity > 0", name="ck_locations_capacity_positive"),
        CheckConstraint("lane_count > 0", name="ck_locations_lanes_positive"),
        CheckConstraint("speed_limit_kmh > 0", name="ck_locations_speed_positive"),
        Index("ix_locations_city_zone_active", "city", "zone", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    road_name: Mapped[str] = mapped_column(String(150), nullable=False)
    junction_name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    zone: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    road_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    lane_count: Mapped[int] = mapped_column(Integer, nullable=False)
    speed_limit_kmh: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    traffic_sources: Mapped[list["TrafficSource"]] = relationship(
        back_populates="location"
    )


class TrafficSource(TimestampMixin, Base):
    __tablename__ = "traffic_sources"
    __table_args__ = (
        UniqueConstraint(
            "source_type", "source_identifier", name="uq_traffic_sources_type_identifier"
        ),
        Index("ix_traffic_sources_location_active", "location_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    location: Mapped[Location] = relationship(back_populates="traffic_sources")
