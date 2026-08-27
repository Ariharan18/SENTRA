"""Create Phase 3 traffic reading, congestion, and import tables."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_phase3_traffic_data"
down_revision: Union[str, None] = "0002_phase2_core_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "traffic_readings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("traffic_sources.id"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vehicle_count", sa.Integer(), nullable=False),
        sa.Column("average_speed_kmh", sa.Numeric(8, 2), nullable=False),
        sa.Column("occupancy_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("car_count", sa.Integer(), nullable=True),
        sa.Column("bike_count", sa.Integer(), nullable=True),
        sa.Column("bus_count", sa.Integer(), nullable=True),
        sa.Column("truck_count", sa.Integer(), nullable=True),
        sa.Column("emergency_count", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.utc_timestamp()),
        sa.UniqueConstraint(
            "location_id", "source_id", "recorded_at",
            name="uq_traffic_readings_location_source_time",
        ),
        sa.CheckConstraint("vehicle_count >= 0", name="ck_readings_vehicle_count_nonnegative"),
        sa.CheckConstraint("average_speed_kmh >= 0", name="ck_readings_speed_nonnegative"),
        sa.CheckConstraint(
            "occupancy_percent >= 0 AND occupancy_percent <= 100",
            name="ck_readings_occupancy_range",
        ),
        sa.CheckConstraint("car_count >= 0", name="ck_readings_car_count_nonnegative"),
        sa.CheckConstraint("bike_count >= 0", name="ck_readings_bike_count_nonnegative"),
        sa.CheckConstraint("bus_count >= 0", name="ck_readings_bus_count_nonnegative"),
        sa.CheckConstraint("truck_count >= 0", name="ck_readings_truck_count_nonnegative"),
        sa.CheckConstraint("emergency_count >= 0", name="ck_readings_emergency_count_nonnegative"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index(
        "ix_traffic_readings_location_time", "traffic_readings", ["location_id", "recorded_at"]
    )
    op.create_index(
        "ix_traffic_readings_source_time", "traffic_readings", ["source_id", "recorded_at"]
    )

    op.create_table(
        "congestion_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "traffic_reading_id", sa.Integer(), sa.ForeignKey("traffic_readings.id"),
            nullable=False, unique=True,
        ),
        sa.Column("congestion_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("congestion_level", sa.String(length=20), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("formula_version", sa.String(length=30), nullable=False),
        sa.CheckConstraint(
            "congestion_score >= 0 AND congestion_score <= 100",
            name="ck_congestion_score_range",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index(
        "ix_congestion_records_level_time",
        "congestion_records",
        ["congestion_level", "calculated_at"],
    )

    op.create_table(
        "traffic_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("uploaded_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_summary", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.utc_timestamp()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "traffic_import_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("traffic_import_id", sa.Integer(), sa.ForeignKey("traffic_imports.id"), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("raw_row_json", sa.JSON(), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )


def downgrade() -> None:
    op.drop_table("traffic_import_errors")
    op.drop_table("traffic_imports")
    op.drop_index("ix_congestion_records_level_time", table_name="congestion_records")
    op.drop_table("congestion_records")
    op.drop_index("ix_traffic_readings_source_time", table_name="traffic_readings")
    op.drop_index("ix_traffic_readings_location_time", table_name="traffic_readings")
    op.drop_table("traffic_readings")
