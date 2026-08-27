"""Seed deterministic Phase 2 demo records.

Run from ``backend`` after configuring ``.env``:
    python seed_demo.py
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import AuditLog, Location, Role, TrafficSource, User


SEED = 20260827
ROLE_DATA = [
    ("Admin", "Full system administration and data access."),
    ("Traffic Operator", "Operational monitoring, alerts, and incidents."),
    ("Analyst", "Historical analytics and permitted exports."),
    ("Viewer", "Read-only dashboard and authorized traffic data."),
]
SOURCE_TYPES = ["Sensor", "Camera Metadata", "CSV Upload", "Manual Entry", "API Integration"]
CITIES = ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru"]
ZONES = ["North", "South", "East", "West", "Central"]
FIRST_NAMES = ["Aarav", "Ananya", "Vikram", "Meera", "Rohan", "Kavya", "Ishaan", "Nisha"]
LAST_NAMES = ["Sharma", "Patel", "Rao", "Nair", "Iyer", "Khan", "Desai", "Menon"]


def get_or_create(session, model, filters, values):
    instance = session.scalar(select(model).filter_by(**filters))
    if instance is None:
        instance = model(**values)
        session.add(instance)
        session.flush()
    return instance


def seed() -> dict[str, int]:
    rng = random.Random(SEED)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    with SessionLocal.begin() as session:
        roles = {
            name: get_or_create(
                session, Role, {"name": name}, {"name": name, "description": description}
            )
            for name, description in ROLE_DATA
        }
        users = []
        for index in range(12):
            role_name = list(roles)[index % len(roles)]
            name = f"{FIRST_NAMES[index % len(FIRST_NAMES)]} {LAST_NAMES[index % len(LAST_NAMES)]}"
            users.append(
                get_or_create(
                    session,
                    User,
                    {"email": f"demo.user{index + 1:02d}@traffic.example"},
                    {
                        "role_id": roles[role_name].id,
                        "email": f"demo.user{index + 1:02d}@traffic.example",
                        "password_hash": "$2b$12$C6UzMDM.H6dfI/f/IKcEe.4Y5p4x2x8m9qQfTQ5y1sQh4f7VqL2eW",
                        "full_name": name,
                        "is_active": True,
                    },
                )
            )
        locations = []
        for index in range(60):
            city = CITIES[index % len(CITIES)]
            zone = ZONES[index % len(ZONES)]
            locations.append(
                get_or_create(
                    session,
                    Location,
                    {"code": f"JCT-{index + 1:03d}"},
                    {
                        "code": f"JCT-{index + 1:03d}",
                        "name": f"{city} {zone} Junction {index + 1:02d}",
                        "road_name": f"{city} Ring Road {index % 15 + 1}",
                        "junction_name": f"{zone} Corridor Crossing {index + 1:02d}",
                        "city": city,
                        "zone": zone,
                        "latitude": Decimal(str(round(12.80 + rng.random() * 0.45, 6))),
                        "longitude": Decimal(str(round(74.75 + rng.random() * 1.8, 6))),
                        "road_capacity": 350 + (index % 6) * 75,
                        "lane_count": 2 + index % 4,
                        "speed_limit_kmh": Decimal(str(40 + (index % 4) * 10)),
                        "is_active": index % 17 != 0,
                    },
                )
            )
        sources = []
        for index, location in enumerate(locations):
            source_type = SOURCE_TYPES[index % len(SOURCE_TYPES)]
            sources.append(
                get_or_create(
                    session,
                    TrafficSource,
                    {"source_type": source_type, "source_identifier": f"{source_type[:3].upper()}-{index + 1:04d}"},
                    {
                        "location_id": location.id,
                        "source_type": source_type,
                        "source_identifier": f"{source_type[:3].upper()}-{index + 1:04d}",
                        "name": f"{source_type} feed for {location.code}",
                        "is_active": True,
                        "last_seen_at": now - timedelta(minutes=index * 7),
                    },
                )
            )
        # Each deterministic action key prevents duplicate audit rows on reruns.
        for index in range(800):
            action = f"DEMO_SEED_RECORD_{index + 1:04d}"
            if session.scalar(select(AuditLog.id).filter_by(action=action)) is None:
                entity = locations[index % len(locations)]
                session.add(
                    AuditLog(
                        actor_user_id=users[index % len(users)].id,
                        action=action,
                        entity_type="Location",
                        entity_id=entity.id,
                        before_json=None,
                        after_json={"code": entity.code, "seed": SEED},
                        created_at=now - timedelta(minutes=index),
                    )
                )
        session.flush()
        return {
            "roles": session.query(Role).count(),
            "users": session.query(User).count(),
            "locations": session.query(Location).count(),
            "traffic_sources": session.query(TrafficSource).count(),
            "audit_logs": session.query(AuditLog).count(),
        }


if __name__ == "__main__":
    counts = seed()
    print("Seed complete:", counts)
    print("Total records:", sum(counts.values()))
