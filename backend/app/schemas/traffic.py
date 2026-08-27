"""Pydantic contracts for traffic ingestion and import history."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TrafficReadingCreate(BaseModel):
    location_id: int = Field(gt=0)
    source_id: int = Field(gt=0)
    recorded_at: datetime
    vehicle_count: int = Field(ge=0)
    average_speed_kmh: Decimal = Field(ge=0, max_digits=8, decimal_places=2)
    occupancy_percent: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    car_count: int | None = Field(default=None, ge=0)
    bike_count: int | None = Field(default=None, ge=0)
    bus_count: int | None = Field(default=None, ge=0)
    truck_count: int | None = Field(default=None, ge=0)
    emergency_count: int | None = Field(default=None, ge=0)

    @field_validator("recorded_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("recorded_at must include a timezone")
        return value


class CongestionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    congestion_score: Decimal
    congestion_level: str
    calculated_at: datetime
    formula_version: str


class TrafficReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    source_id: int
    recorded_at: datetime
    vehicle_count: int
    average_speed_kmh: Decimal
    occupancy_percent: Decimal
    car_count: int | None
    bike_count: int | None
    bus_count: int | None
    truck_count: int | None
    emergency_count: int | None
    created_by_user_id: int
    congestion: CongestionRecordResponse | None = None


class TrafficReadingListResponse(BaseModel):
    items: list[TrafficReadingResponse]
    page: int
    page_size: int
    total: int


class TrafficImportErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    row_number: int
    reason: str
    raw_row_json: dict


class TrafficImportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    import_id: int = Field(validation_alias="id")
    file_name: str
    uploaded_by_user_id: int
    uploaded_at: datetime
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    status: str
    error_summary: str | None


class TrafficImportDetailResponse(TrafficImportResponse):
    errors: list[TrafficImportErrorResponse] = Field(default_factory=list)


class TrafficImportListResponse(BaseModel):
    items: list[TrafficImportResponse]
    page: int
    page_size: int
    total: int
