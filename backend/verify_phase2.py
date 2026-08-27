"""Verify Phase 2 tables, indexes, constraints, and referential integrity."""

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine


TABLES = ["roles", "users", "locations", "traffic_sources", "audit_logs"]


def main() -> None:
    try:
        inspector = inspect(engine)
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Database connection failed: {exc}") from exc
    missing = [table for table in TABLES if not inspector.has_table(table)]
    if missing:
        raise RuntimeError(f"Missing Phase 2 tables: {', '.join(missing)}")
    expected_indexes = {
        "locations": "ix_locations_city_zone_active",
        "traffic_sources": "ix_traffic_sources_location_active",
        "audit_logs": "ix_audit_logs_entity",
    }
    for table, index_name in expected_indexes.items():
        if index_name not in {item["name"] for item in inspector.get_indexes(table)}:
            raise RuntimeError(f"Missing index {index_name} on {table}")
    with engine.connect() as connection:
        counts = {
            table: connection.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one()
            for table in TABLES
        }
        total = sum(counts.values())
        broken = connection.execute(
            text(
                "SELECT (SELECT COUNT(*) FROM users u LEFT JOIN roles r ON r.id=u.role_id "
                "WHERE r.id IS NULL) + (SELECT COUNT(*) FROM traffic_sources s "
                "LEFT JOIN locations l ON l.id=s.location_id WHERE l.id IS NULL) + "
                "(SELECT COUNT(*) FROM audit_logs a LEFT JOIN users u ON u.id=a.actor_user_id "
                "WHERE u.id IS NULL)"
            )
        ).scalar_one()
        duplicates = connection.execute(
            text(
                "SELECT (SELECT COUNT(*)-COUNT(DISTINCT email) FROM users) + "
                "(SELECT COUNT(*)-COUNT(DISTINCT code) FROM locations) + "
                "(SELECT COUNT(*)-COUNT(DISTINCT CONCAT(source_type, ':', source_identifier)) "
                "FROM traffic_sources)"
            )
        ).scalar_one()
    print("Counts:", counts)
    print("Total records:", total)
    print("Database connection: OK")
    print("Foreign-key violations:", broken)
    print("Duplicate unique values:", duplicates)
    if total < 800:
        raise RuntimeError("TOTAL RECORDS >= 800 check failed")
    if broken or duplicates:
        raise RuntimeError("Phase 2 validation failed")
    print("TOTAL RECORDS >= 800: YES")
    print("Foreign-key integrity: PASS")
    print("Unique constraints: PASS")
    print("Indexes: PASS")


if __name__ == "__main__":
    main()
