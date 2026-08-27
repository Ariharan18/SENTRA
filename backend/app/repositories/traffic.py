"""Database access for Phase 3 traffic records."""

from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    CongestionRecord,
    Location,
    TrafficImport,
    TrafficImportError,
    TrafficReading,
)


class TrafficReadingRepository:
    """Queries and persistence for readings."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, reading_id: int) -> TrafficReading | None:
        return self.db.scalar(
            select(TrafficReading)
            .options(selectinload(TrafficReading.congestion))
            .where(TrafficReading.id == reading_id)
        )

    def exists_duplicate(self, location_id: int, source_id: int, recorded_at: datetime) -> bool:
        return self.db.scalar(
            select(TrafficReading.id).where(
                TrafficReading.location_id == location_id,
                TrafficReading.source_id == source_id,
                TrafficReading.recorded_at == recorded_at,
            )
        ) is not None

    def add(self, reading: TrafficReading) -> TrafficReading:
        self.db.add(reading)
        self.db.flush()
        return reading

    def add_congestion(self, record: CongestionRecord) -> CongestionRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def list(
        self,
        *,
        page: int,
        page_size: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        location_id: int | None = None,
        city: str | None = None,
        zone: str | None = None,
        source_id: int | None = None,
        source_type: str | None = None,
        congestion_level: str | None = None,
    ) -> tuple[list[TrafficReading], int]:
        query: Select = (
            select(TrafficReading)
            .join(TrafficReading.location)
            .join(TrafficReading.source)
            .outerjoin(TrafficReading.congestion)
            .options(selectinload(TrafficReading.congestion))
        )
        count_query = (
            select(func.count(TrafficReading.id))
            .join(TrafficReading.location)
            .join(TrafficReading.source)
            .outerjoin(TrafficReading.congestion)
        )
        filters = []
        if date_from is not None:
            filters.append(TrafficReading.recorded_at >= date_from)
        if date_to is not None:
            filters.append(TrafficReading.recorded_at <= date_to)
        if location_id is not None:
            filters.append(TrafficReading.location_id == location_id)
        if city:
            filters.append(Location.city == city)
        if zone:
            filters.append(Location.zone == zone)
        if source_id is not None:
            filters.append(TrafficReading.source_id == source_id)
        if source_type:
            filters.append(TrafficReading.source.has(source_type=source_type))
        if congestion_level:
            filters.append(CongestionRecord.congestion_level == congestion_level)
        query = query.where(*filters).order_by(TrafficReading.recorded_at.desc(), TrafficReading.id.desc())
        count_query = count_query.where(*filters)
        total = self.db.scalar(count_query) or 0
        items = list(
            self.db.scalars(query.offset((page - 1) * page_size).limit(page_size)).unique()
        )
        return items, total


class TrafficImportRepository:
    """Database access for import summaries and row errors."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, traffic_import: TrafficImport) -> TrafficImport:
        self.db.add(traffic_import)
        self.db.flush()
        return traffic_import

    def add_error(self, error: TrafficImportError) -> TrafficImportError:
        self.db.add(error)
        return error

    def get(self, import_id: int) -> TrafficImport | None:
        return self.db.scalar(
            select(TrafficImport)
            .options(selectinload(TrafficImport.errors))
            .where(TrafficImport.id == import_id)
        )

    def list(self, *, page: int, page_size: int) -> tuple[list[TrafficImport], int]:
        query = select(TrafficImport).order_by(TrafficImport.uploaded_at.desc(), TrafficImport.id.desc())
        count = self.db.scalar(select(func.count(TrafficImport.id))) or 0
        items = list(self.db.scalars(query.offset((page - 1) * page_size).limit(page_size)))
        return items, count
