"""Authenticated dashboard analytics endpoints."""

import csv
from io import StringIO
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import AnalyticsSummary, AnalyticsListResponse
from app.services.analytics import AnalyticsService, build_filters

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _filters(
    date_from,
    date_to,
    location_id,
    city,
    zone,
    source_id,
    source,
    source_type,
    congestion_level,
):
    try:
        return build_filters(
                             date_from,
                             date_to,
                             location_id=location_id,
                             city=city,
                             zone=zone,
                             source_id=source_id,
                             source=source,
                             source_type=source_type,
                             congestion_level=congestion_level)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def common_filters(date_from: date | None = None, date_to: date | None = None,
                   location_id: int | None = Query(None, gt=0),
                   source_id: int | None = Query(None, gt=0),
                   city: str | None = None,
                   zone: str | None = None, source: str | None = None,
                   source_type: str | None = None, congestion_level: str | None = None):
    return _filters(
        date_from,
        date_to,
        location_id,
        city,
        zone,
        source_id,
        source,
        source_type,
        congestion_level,
    )


@router.get("/summary", response_model=AnalyticsSummary)
def summary(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
            _: User = Depends(get_current_user)):
    return AnalyticsService(AnalyticsRepository(db)).summary(filters)


@router.get("/trends", response_model=AnalyticsListResponse)
def trends(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
           _: User = Depends(get_current_user)):
    items = [dict(row._mapping) for row in AnalyticsService(AnalyticsRepository(db)).trends(filters)]
    for item in items: item["vehicle_count"] = item["traffic_volume"]
    return {"items": items}


@router.get("/by-location", response_model=AnalyticsListResponse)
def by_location(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    items = [dict(row._mapping) for row in AnalyticsService(AnalyticsRepository(db)).by_location(filters)]
    for item in items: item["total_vehicle_count"] = item["traffic_volume"]
    return {"items": items}


@router.get("/peak-hours", response_model=AnalyticsListResponse)
def peak_hours(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
               _: User = Depends(get_current_user)):
    items = [dict(row._mapping) for row in AnalyticsService(AnalyticsRepository(db)).peak_hours(filters)]
    for item in items: item["vehicle_count"] = item["traffic_volume"]
    return {"items": items}


@router.get("/vehicle-mix", response_model=AnalyticsListResponse)
def vehicle_mix(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    return {"items": [{"vehicle_type": n, "count": c, "vehicle_count": c, "percentage": p}
            for n, c, p in AnalyticsService(AnalyticsRepository(db)).vehicle_mix(filters)]}


@router.get("/status-distribution", response_model=AnalyticsListResponse)
def status_distribution(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
                         _: User = Depends(get_current_user)):
    return {"items": [{"congestion_level": n, "count": c, "reading_count": c, "percentage": p}
            for n, c, p in AnalyticsService(AnalyticsRepository(db)).status_distribution(filters)]}


@router.get(
    "/export",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/csv": {}}}},
)
def export(filters: dict = Depends(common_filters), db: Session = Depends(get_db),
           _: User = Depends(get_current_user)):
    """Download filtered analytics readings as a CSV file."""
    fields = (
        "id", "recorded_at", "location_id", "location_name", "road_name", "city", "zone",
        "source_id", "source_type", "vehicle_count", "average_speed_kmh",
        "occupancy_percent", "car_count", "bike_count", "bus_count", "truck_count",
        "emergency_count", "congestion_score", "congestion_level",
    )
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(fields)
    for row in AnalyticsService(AnalyticsRepository(db)).export(filters):
        values = dict(row._mapping)
        values["location_name"] = values.pop("name", None)
        writer.writerow([values.get(field) for field in fields])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="analytics_export.csv"'},
    )
