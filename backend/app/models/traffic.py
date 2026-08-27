"""Traffic readings, congestion calculations, and import history models."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.identity import User
    from app.models.network import Location, TrafficSource


class TrafficReading(TimestampMixin, Base):
    """A timestamped traffic measurement from one source."""

    __tablename__ = "traffic_readings"
    __table_args__ = (
        UniqueConstraint(
            "location_id", "source_id", "recorded_at",
            name="uq_traffic_readings_location_source_time",
        ),
        CheckConstraint("vehicle_count >= 0", name="ck_readings_vehicle_count_nonnegative"),
        CheckConstraint("average_speed_kmh >= 0", name="ck_readings_speed_nonnegative"),
        CheckConstraint(
            "occupancy_percent >= 0 AND occupancy_percent <= 100",
            name="ck_readings_occupancy_range",
        ),
        CheckConstraint("car_count >= 0", name="ck_readings_car_count_nonnegative"),
        CheckConstraint("bike_count >= 0", name="ck_readings_bike_count_nonnegative"),
        CheckConstraint("bus_count >= 0", name="ck_readings_bus_count_nonnegative"),
        CheckConstraint("truck_count >= 0", name="ck_readings_truck_count_nonnegative"),
        CheckConstraint(
            "emergency_count >= 0", name="ck_readings_emergency_count_nonnegative"
        ),
        Index("ix_traffic_readings_location_time", "location_id", "recorded_at"),
        Index("ix_traffic_readings_source_time", "source_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("traffic_sources.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vehicle_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_speed_kmh: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), nullable=False)
    occupancy_percent: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    car_count: Mapped[int | None] = mapped_column(Integer)
    bike_count: Mapped[int | None] = mapped_column(Integer)
    bus_count: Mapped[int | None] = mapped_column(Integer)
    truck_count: Mapped[int | None] = mapped_column(Integer)
    emergency_count: Mapped[int | None] = mapped_column(Integer)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    location: Mapped["Location"] = relationship()
    source: Mapped["TrafficSource"] = relationship()
    created_by: Mapped["User"] = relationship()
    congestion: Mapped["CongestionRecord | None"] = relationship(
        back_populates="traffic_reading", uselist=False, cascade="all, delete-orphan"
    )


class CongestionRecord(Base):
    """The congestion calculation produced for a traffic reading."""

    __tablename__ = "congestion_records"
    __table_args__ = (
        CheckConstraint(
            "congestion_score >= 0 AND congestion_score <= 100",
            name="ck_congestion_score_range",
        ),
        Index("ix_congestion_records_level_time", "congestion_level", "calculated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    traffic_reading_id: Mapped[int] = mapped_column(
        ForeignKey("traffic_readings.id"), nullable=False, unique=True
    )
    congestion_score: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    congestion_level: Mapped[str] = mapped_column(String(20), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    formula_version: Mapped[str] = mapped_column(String(30), nullable=False)

    traffic_reading: Mapped[TrafficReading] = relationship(back_populates="congestion")


class TrafficImport(TimestampMixin, Base):
    """Summary and lifecycle information for an uploaded CSV."""

    __tablename__ = "traffic_imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_summary: Mapped[str | None] = mapped_column(String(1000))

    uploaded_by: Mapped["User"] = relationship()
    errors: Mapped[list["TrafficImportError"]] = relationship(
        back_populates="traffic_import", cascade="all, delete-orphan"
    )


class TrafficImportError(Base):
    """A rejected CSV row and a user-readable reason."""

    __tablename__ = "traffic_import_errors"

    id: Mapped[int] = mapped_column(primary_key=True)
    traffic_import_id: Mapped[int] = mapped_column(
        ForeignKey("traffic_imports.id"), nullable=False
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_row_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    traffic_import: Mapped[TrafficImport] = relationship(back_populates="errors")
