"""Response contracts for dashboard analytics."""

from decimal import Decimal
from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    active_locations: int
    active_alerts: int = 0
    severe_locations: int
    average_speed_kmh: Decimal | None
    total_vehicle_count: int
    reading_count: int = 0
    total_readings: int = 0
    average_congestion_score: Decimal | None = None


class TrendPoint(BaseModel):
    period: str
    traffic_volume: int
    vehicle_count: int
    average_speed_kmh: Decimal | None
    average_congestion_score: Decimal | None


class LocationAnalytics(BaseModel):
    location_id: int
    location_name: str
    road_name: str
    city: str
    zone: str
    reading_count: int
    traffic_volume: int
    total_vehicle_count: int
    average_speed_kmh: Decimal | None
    average_congestion_score: Decimal | None


class PeakHourPoint(BaseModel):
    hour: int
    day_of_week: int | None
    traffic_volume: int
    vehicle_count: int
    average_congestion_score: Decimal | None


class VehicleMixPoint(BaseModel):
    vehicle_type: str
    count: int
    percentage: Decimal


class StatusDistributionPoint(BaseModel):
    congestion_level: str
    count: int
    reading_count: int
    percentage: Decimal


class AnalyticsListResponse(BaseModel):
    items: list
