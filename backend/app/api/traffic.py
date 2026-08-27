"""Traffic reading and CSV import endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import TrafficImport, TrafficReading, User
from app.repositories.traffic import TrafficImportRepository, TrafficReadingRepository
from app.schemas.traffic import (
    TrafficImportDetailResponse,
    TrafficImportListResponse,
    TrafficImportResponse,
    TrafficReadingCreate,
    TrafficReadingListResponse,
    TrafficReadingResponse,
)
from app.services.traffic import ConflictError, create_reading, parse_csv, process_import

router = APIRouter(tags=["traffic"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
) -> tuple[int, int]:
    return page, page_size


@router.get("/traffic-readings", response_model=TrafficReadingListResponse)
def list_traffic_readings(
    page_data: tuple[int, int] = Depends(pagination),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    location_id: int | None = Query(None, gt=0),
    city: str | None = None,
    zone: str | None = None,
    source_id: int | None = Query(None, gt=0),
    source: str | None = None,
    congestion_level: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TrafficReadingListResponse:
    page, page_size = page_data
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must not be after date_to")
    items, total = TrafficReadingRepository(db).list(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        location_id=location_id,
        city=city,
        zone=zone,
        source_id=source_id,
        source_type=source,
        congestion_level=congestion_level,
    )
    return TrafficReadingListResponse(items=items, page=page, page_size=page_size, total=total)


@router.post(
    "/traffic-readings",
    response_model=TrafficReadingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_traffic_reading(
    payload: TrafficReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrafficReading:
    try:
        return create_reading(db, payload, user)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/traffic-readings/upload",
    response_model=TrafficImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_traffic_readings(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrafficImport:
    if file.content_type not in {
        "text/csv",
        "application/csv",
        "application/vnd.ms-excel",
        None,
    }:
        raise HTTPException(status_code=400, detail="Upload must be a CSV file")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="CSV file exceeds the 10 MB limit")
    try:
        rows = parse_csv(content)
        return process_import(db, file_name=file.filename or "upload.csv", rows=rows, user=user)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/traffic-readings/{reading_id}", response_model=TrafficReadingResponse)
def get_traffic_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TrafficReading:
    reading = TrafficReadingRepository(db).get(reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Traffic reading not found")
    return reading


@router.get("/traffic-imports", response_model=TrafficImportListResponse)
def list_traffic_imports(
    page_data: tuple[int, int] = Depends(pagination),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TrafficImportListResponse:
    page, page_size = page_data
    items, total = TrafficImportRepository(db).list(page=page, page_size=page_size)
    return TrafficImportListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/traffic-imports/{import_id}", response_model=TrafficImportDetailResponse)
def get_traffic_import(
    import_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TrafficImport:
    traffic_import = TrafficImportRepository(db).get(import_id)
    if traffic_import is None:
        raise HTTPException(status_code=404, detail="Traffic import not found")
    return traffic_import
