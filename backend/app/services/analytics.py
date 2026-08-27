"""Analytics orchestration and validation."""

from datetime import date, datetime, time, timezone
from app.repositories.analytics import AnalyticsRepository


def build_filters(date_from: date | None = None, date_to: date | None = None, **values) -> dict:
    if date_from and date_to and date_from > date_to:
        raise ValueError("date_from must not be after date_to")
    filters = {
        key: value
        for key, value in values.items()
        if value is not None and value != ""
    }
    if date_from:
        filters["date_from"] = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
    if date_to:
        filters["date_to"] = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
    return filters


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def summary(self, filters): return self.repository.summary(filters)
    def trends(self, filters): return self.repository.trends(filters)
    def by_location(self, filters): return self.repository.by_location(filters)
    def peak_hours(self, filters): return self.repository.peak_hours(filters)
    def vehicle_mix(self, filters): return self.repository.vehicle_mix(filters)
    def status_distribution(self, filters): return self.repository.status_distribution(filters)
    def export(self, filters): return self.repository.export(filters)
