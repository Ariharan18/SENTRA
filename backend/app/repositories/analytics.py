"""Efficient SQL aggregation queries used by dashboard analytics."""

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session
from app.models import CongestionRecord, Location, TrafficReading, TrafficSource


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base(self, filters: dict) -> Select:
        query = (select(
                    TrafficReading.id, TrafficReading.location_id, TrafficReading.recorded_at,
                    TrafficReading.vehicle_count, TrafficReading.average_speed_kmh,
                    TrafficReading.occupancy_percent, TrafficReading.source_id,
                    TrafficReading.car_count, TrafficReading.bike_count, TrafficReading.bus_count,
                    TrafficReading.truck_count, TrafficReading.emergency_count,
                    Location.name, Location.road_name, Location.city, Location.zone,
                    TrafficSource.source_type,
                    CongestionRecord.congestion_score, CongestionRecord.congestion_level)
                 .join(Location, TrafficReading.location_id == Location.id)
                 .join(TrafficSource, TrafficReading.source_id == TrafficSource.id)
                 .outerjoin(CongestionRecord,
                            CongestionRecord.traffic_reading_id == TrafficReading.id))
        conditions = [Location.is_active.is_(True)]
        if filters.get("date_from") is not None:
            conditions.append(TrafficReading.recorded_at >= filters["date_from"])
        if filters.get("date_to") is not None:
            conditions.append(TrafficReading.recorded_at < filters["date_to"])
        if filters.get("location_id") is not None:
            conditions.append(TrafficReading.location_id == filters["location_id"])
        if filters.get("city"):
            conditions.append(Location.city == filters["city"])
        if filters.get("zone"):
            conditions.append(Location.zone == filters["zone"])
        if filters.get("source_id") is not None:
            conditions.append(TrafficReading.source_id == filters["source_id"])
        source_type = filters.get("source_type") or filters.get("source")
        if source_type:
            conditions.append(TrafficSource.source_type == source_type)
        if filters.get("congestion_level"):
            conditions.append(CongestionRecord.congestion_level == filters["congestion_level"])
        return query.where(*conditions)

    def export(self, filters: dict):
        """Return filtered readings for the analytics CSV export."""
        return self.db.execute(self._base(filters).order_by(
            TrafficReading.recorded_at, TrafficReading.id
        )).all()

    def summary(self, filters: dict) -> dict:
        q = self._base(filters).subquery()
        # The subquery keeps all filtering in SQL and avoids loading readings.
        row = self.db.execute(select(
            func.count(q.c.id), func.coalesce(func.sum(q.c.vehicle_count), 0),
            func.avg(q.c.average_speed_kmh), func.avg(q.c.congestion_score),
            func.count(func.distinct(case((q.c.congestion_level == "Severe", q.c.location_id))))
        )).one()
        active = self.db.execute(select(func.count(func.distinct(q.c.location_id)))).scalar() or 0
        return {"active_locations": active, "severe_locations": int(row[4] or 0),
                "reading_count": int(row[0] or 0), "total_readings": int(row[0] or 0),
                "total_vehicle_count": int(row[1] or 0),
                "average_speed_kmh": row[2], "average_congestion_score": row[3]}

    def trends(self, filters: dict):
        q = self._base(filters).subquery()
        return self.db.execute(select(
            func.date(q.c.recorded_at).label("period"),
            func.coalesce(func.sum(q.c.vehicle_count), 0).label("traffic_volume"),
            func.avg(q.c.average_speed_kmh).label("average_speed_kmh"),
            func.avg(q.c.congestion_score).label("average_congestion_score"),
        ).group_by(func.date(q.c.recorded_at)).order_by(func.date(q.c.recorded_at))).all()

    def by_location(self, filters: dict):
        q = self._base(filters).subquery()
        return self.db.execute(select(
            q.c.location_id, q.c.name.label("location_name"), q.c.road_name,
            q.c.city, q.c.zone, func.count(q.c.id).label("reading_count"),
            func.coalesce(func.sum(q.c.vehicle_count), 0).label("traffic_volume"),
            func.avg(q.c.average_speed_kmh).label("average_speed_kmh"),
            func.avg(q.c.congestion_score).label("average_congestion_score"),
        ).group_by(q.c.location_id, q.c.name, q.c.road_name, q.c.city, q.c.zone)
        .order_by(func.sum(q.c.vehicle_count).desc())).all()

    def peak_hours(self, filters: dict):
        q = self._base(filters).subquery()
        hour = func.hour(q.c.recorded_at)
        dow = func.dayofweek(q.c.recorded_at)
        return self.db.execute(select(
            hour.label("hour"), dow.label("day_of_week"),
            func.coalesce(func.sum(q.c.vehicle_count), 0).label("traffic_volume"),
            func.avg(q.c.congestion_score).label("average_congestion_score"),
        ).group_by(
            func.hour(q.c.recorded_at),
            func.dayofweek(q.c.recorded_at),
        ).order_by(func.sum(q.c.vehicle_count).desc())).all()

    def vehicle_mix(self, filters: dict):
        q = self._base(filters).subquery()
        expressions = [("car", q.c.car_count), ("bike", q.c.bike_count),
                       ("bus", q.c.bus_count), ("truck", q.c.truck_count),
                       ("emergency", q.c.emergency_count)]
        row = self.db.execute(select(*(func.coalesce(func.sum(column), 0) for _, column in expressions))).one()
        rows = [(name, int(count or 0)) for (name, _), count in zip(expressions, row)]
        denominator = sum(item[1] for item in rows)
        return [(name, count, (count * 100 / denominator if denominator else 0))
                for name, count in rows if count or denominator == 0]

    def status_distribution(self, filters: dict):
        q = self._base(filters).subquery()
        rows = self.db.execute(select(q.c.congestion_level, func.count(q.c.id))
                               .where(q.c.congestion_level.is_not(None))
                               .group_by(q.c.congestion_level)
                               .order_by(q.c.congestion_level)).all()
        total = sum(int(row[1]) for row in rows)
        return [(row[0], int(row[1]), (int(row[1]) * 100 / total if total else 0))
                for row in rows]
