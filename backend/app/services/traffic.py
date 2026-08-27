"""Business rules for traffic readings and CSV imports."""

import csv
import io
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    CongestionRecord,
    Location,
    TrafficImport,
    TrafficImportError,
    TrafficReading,
    TrafficSource,
    User,
)
from app.repositories.traffic import TrafficImportRepository, TrafficReadingRepository
from app.schemas.traffic import TrafficReadingCreate

FORMULA_VERSION = "v1"
REQUIRED_CSV_COLUMNS = {
    "location_id",
    "source_id",
    "recorded_at",
    "vehicle_count",
    "average_speed_kmh",
    "occupancy_percent",
}


def _utc(value: datetime) -> datetime:
    return value.astimezone(timezone.utc)


def calculate_congestion(reading: TrafficReading, location: Location) -> tuple[Decimal, str]:
    """Calculate the documented normalized congestion score and level."""

    score = (
        (Decimal(reading.vehicle_count) / Decimal(location.road_capacity) * Decimal(40))
        + (
            Decimal(1)
            - Decimal(reading.average_speed_kmh) / Decimal(location.speed_limit_kmh)
        )
        * Decimal(35)
        + (Decimal(reading.occupancy_percent) / Decimal(100) * Decimal(25))
    )
    score = max(Decimal(0), min(Decimal(100), score)).quantize(Decimal("0.01"))
    if score <= 25:
        level = "Low"
    elif score <= 50:
        level = "Moderate"
    elif score <= 75:
        level = "High"
    else:
        level = "Severe"
    return score, level


def _validate_references(db: Session, payload: TrafficReadingCreate) -> tuple[Location, TrafficSource]:
    location = db.scalar(
        select(Location).where(Location.id == payload.location_id, Location.is_active.is_(True))
    )
    if location is None:
        raise ValueError("Location does not exist or is inactive")
    source = db.scalar(
        select(TrafficSource).where(
            TrafficSource.id == payload.source_id, TrafficSource.is_active.is_(True)
        )
    )
    if source is None:
        raise ValueError("Traffic source does not exist or is inactive")
    if source.location_id != location.id:
        raise ValueError("Traffic source does not belong to the selected location")
    return location, source


def create_reading(db: Session, payload: TrafficReadingCreate, user: User) -> TrafficReading:
    """Validate and persist one reading and its congestion result."""

    location, _ = _validate_references(db, payload)
    recorded_at = _utc(payload.recorded_at)
    repository = TrafficReadingRepository(db)
    if repository.exists_duplicate(payload.location_id, payload.source_id, recorded_at):
        raise ConflictError("A reading already exists for this location, source, and timestamp")
    now = datetime.now(timezone.utc)
    reading = TrafficReading(
        **payload.model_dump(exclude={"recorded_at"}),
        recorded_at=recorded_at,
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now,
    )
    repository.add(reading)
    score, level = calculate_congestion(reading, location)
    repository.add_congestion(
        CongestionRecord(
            traffic_reading_id=reading.id,
            congestion_score=score,
            congestion_level=level,
            calculated_at=datetime.now(timezone.utc),
            formula_version=FORMULA_VERSION,
        )
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A duplicate reading already exists") from exc
    db.refresh(reading)
    return repository.get(reading.id) or reading


class ConflictError(ValueError):
    """A business conflict that should be returned as HTTP 409."""


def _row_payload(row: dict[str, str]) -> dict:
    payload = dict(row)
    for key in ("location_id", "source_id", "vehicle_count", "car_count", "bike_count",
                "bus_count", "truck_count", "emergency_count"):
        if key in payload and payload[key] == "":
            payload[key] = None
    return payload


def process_import(
    db: Session,
    *,
    file_name: str,
    rows: Iterable[dict[str, str]],
    user: User,
) -> TrafficImport:
    """Validate every row and commit accepted records plus rejection feedback."""

    rows = list(rows)
    now = datetime.now(timezone.utc)
    traffic_import = TrafficImport(
        file_name=file_name[:255],
        uploaded_by_user_id=user.id,
        uploaded_at=now,
        total_rows=len(rows),
        status="Processing",
        created_at=now,
        updated_at=now,
    )
    imports = TrafficImportRepository(db)
    imports.add(traffic_import)
    reading_repo = TrafficReadingRepository(db)
    seen: set[tuple[int, int, datetime]] = set()
    accepted = 0
    errors: list[TrafficImportError] = []
    for row_number, row in enumerate(rows, start=2):
        raw = {str(key): value for key, value in row.items() if key is not None}
        try:
            payload = TrafficReadingCreate.model_validate(_row_payload(raw))
            location, _ = _validate_references(db, payload)
            recorded_at = _utc(payload.recorded_at)
            key = (payload.location_id, payload.source_id, recorded_at)
            if key in seen or reading_repo.exists_duplicate(*key):
                raise ConflictError(
                    "Duplicate reading for location, source, and timestamp"
                )
            seen.add(key)
            reading = TrafficReading(
                **payload.model_dump(exclude={"recorded_at"}),
                recorded_at=recorded_at,
                created_by_user_id=user.id,
                created_at=now,
                updated_at=now,
            )
            reading_repo.add(reading)
            score, level = calculate_congestion(reading, location)
            reading_repo.add_congestion(
                CongestionRecord(
                    traffic_reading_id=reading.id,
                    congestion_score=score,
                    congestion_level=level,
                    calculated_at=datetime.now(timezone.utc),
                    formula_version=FORMULA_VERSION,
                )
            )
            accepted += 1
        except (ValidationError, ValueError, TypeError) as exc:
            reason = str(exc)
            if isinstance(exc, ValidationError):
                reason = "; ".join(
                    f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                    for error in exc.errors()
                )
            errors.append(
                TrafficImportError(
                    traffic_import_id=traffic_import.id,
                    row_number=row_number,
                    reason=reason[:1000],
                    raw_row_json=raw,
                )
            )
    rejected = len(errors)
    traffic_import.accepted_rows = accepted
    traffic_import.rejected_rows = rejected
    traffic_import.status = "Completed"
    traffic_import.error_summary = (
        f"{rejected} row(s) rejected" if rejected else None
    )
    for error in errors:
        imports.add_error(error)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Import could not be persisted because of a duplicate reading") from exc
    return imports.get(traffic_import.id) or traffic_import


def parse_csv(content: bytes) -> list[dict[str, str]]:
    """Decode and validate CSV structure before row-level processing."""

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames:
        reader.fieldnames = [header.strip() if header else "" for header in reader.fieldnames]
    headers = {header.strip() for header in (reader.fieldnames or []) if header}
    missing = REQUIRED_CSV_COLUMNS - headers
    if missing:
        raise ValueError(f"Missing required CSV column(s): {', '.join(sorted(missing))}")
    return [dict(row) for row in reader]
