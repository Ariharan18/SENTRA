"""Unit tests for analytics filter validation."""

import asyncio
from datetime import date, datetime, timezone

import pytest

from app.api import analytics as analytics_api
from app.services.analytics import build_filters


def test_build_filters_normalizes_date_bounds() -> None:
    filters = build_filters(date(2026, 8, 1), date(2026, 8, 27), location_id=14)

    assert filters["location_id"] == 14
    assert filters["date_from"] == datetime(2026, 8, 1, tzinfo=timezone.utc)
    assert filters["date_to"].date() == date(2026, 8, 27)


def test_build_filters_omits_empty_optional_values() -> None:
    assert build_filters(city=None, zone="", source_id=None) == {}


def test_build_filters_rejects_reversed_date_range() -> None:
    with pytest.raises(ValueError, match="date_from must not be after date_to"):
        build_filters(date(2026, 8, 28), date(2026, 8, 1))


def test_export_returns_csv_header_for_empty_result(monkeypatch) -> None:
    class EmptyAnalyticsService:
        def __init__(self, repository):
            pass

        def export(self, filters):
            return []

    monkeypatch.setattr(analytics_api, "AnalyticsService", EmptyAnalyticsService)
    response = analytics_api.export({}, object(), object())
    body = asyncio.run(response.body_iterator.__anext__())

    assert response.media_type == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == (
        'attachment; filename="analytics_export.csv"'
    )
    assert body.startswith(b"id,recorded_at,location_id")
