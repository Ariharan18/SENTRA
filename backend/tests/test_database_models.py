"""
SENTRA – Database Foundation, SQLAlchemy Models, and Pydantic Schemas Test Suite
Validates database engine configuration, table metadata, model relationships,
and schema serializations.
"""

from decimal import Decimal
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db, init_db
from app.core.config import settings
from app.models import (
    User,
    EmergencyContact,
    Event,
    Alert,
    Location,
    AuditLog,
)
from app.schemas import (
    UserCreate,
    UserResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    EventCreate,
    EventResponse,
    SOSTriggerRequest,
    AlertCreate,
    AlertResponse,
    LocationCreate,
    LocationResponse,
    AuditLogCreate,
    AuditLogResponse,
)


@pytest.fixture
def test_db_session():
    """
    Creates an isolated SQLite in-memory database session for testing models and DDL.
    """
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_database_metadata_tables():
    """
    Verify that all documented tables exist in Base.metadata.
    """
    expected_tables = {
        "users",
        "emergency_contacts",
        "events",
        "alerts",
        "locations",
        "audit_logs",
    }
    registered_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(registered_tables), f"Missing tables: {expected_tables - registered_tables}"


def test_user_table_columns():
    """
    Verify columns and constraints on users table.
    """
    table = Base.metadata.tables["users"]
    col_names = {c.name for c in table.columns}
    expected_cols = {"user_id", "name", "email", "phone", "password_hash", "role", "created_at"}
    assert expected_cols.issubset(col_names)
    assert table.columns["user_id"].primary_key is True
    assert table.columns["email"].unique is True


def test_events_and_alerts_foreign_keys():
    """
    Verify foreign keys on events, alerts, and contacts tables.
    """
    events_table = Base.metadata.tables["events"]
    alerts_table = Base.metadata.tables["alerts"]
    contacts_table = Base.metadata.tables["emergency_contacts"]

    # Verify ForeignKey targets
    events_fk_targets = {fk.target_fullname for fk in events_table.foreign_keys}
    assert "users.user_id" in events_fk_targets

    alerts_fk_targets = {fk.target_fullname for fk in alerts_table.foreign_keys}
    assert "events.event_id" in alerts_fk_targets
    assert "users.user_id" in alerts_fk_targets

    contacts_fk_targets = {fk.target_fullname for fk in contacts_table.foreign_keys}
    assert "users.user_id" in contacts_fk_targets


def test_model_crud_and_relationships(test_db_session):
    """
    Test creation, querying, and relational linking across all 6 models.
    """
    # 1. Create User
    user = User(
        name="Officer Jane Doe",
        email="jane.doe@sentra.local",
        phone="1234567890",
        password_hash="hashed_pw_test",
        role="admin",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    assert user.user_id is not None
    assert user.role == "admin"

    # 2. Create Emergency Contact
    contact = EmergencyContact(
        user_id=user.user_id,
        contact_name="John Doe",
        phone="9876543210",
        relationship="Spouse",
    )
    test_db_session.add(contact)

    # 3. Create Event
    event = Event(
        user_id=user.user_id,
        event_type="sos",
        risk_level="CRITICAL",
        latitude=Decimal("13.0827000"),
        longitude=Decimal("80.2707000"),
        description="Emergency SOS triggered",
        status="new",
    )
    test_db_session.add(event)
    test_db_session.commit()
    test_db_session.refresh(event)

    # 4. Create Alert
    alert = Alert(
        event_id=event.event_id,
        user_id=user.user_id,
        alert_type="sos_alert",
        priority="CRITICAL",
        status="new",
    )
    test_db_session.add(alert)

    # 5. Create Location
    loc = Location(
        user_id=user.user_id,
        latitude=Decimal("13.0827000"),
        longitude=Decimal("80.2707000"),
    )
    test_db_session.add(loc)

    # 6. Create Audit Log
    log = AuditLog(
        user_id=user.user_id,
        action="SOS_TRIGGERED",
        details="User initiated SOS distress signal",
    )
    test_db_session.add(log)
    test_db_session.commit()

    # Query back and verify relationships
    queried_user = test_db_session.query(User).filter_by(email="jane.doe@sentra.local").first()
    assert len(queried_user.emergency_contacts) == 1
    assert queried_user.emergency_contacts[0].contact_name == "John Doe"
    assert len(queried_user.events) == 1
    assert queried_user.events[0].risk_level == "CRITICAL"
    assert len(queried_user.events[0].alerts) == 1
    assert queried_user.events[0].alerts[0].priority == "CRITICAL"
    assert len(queried_user.locations) == 1
    assert len(queried_user.audit_logs) == 1
    assert queried_user.audit_logs[0].action == "SOS_TRIGGERED"


def test_cascade_delete_behavior(test_db_session):
    """
    Verify that deleting a user cascades and removes child records.
    """
    user = User(
        name="Test User",
        email="cascade.test@sentra.local",
        password_hash="hashed_pw",
        role="user",
    )
    test_db_session.add(user)
    test_db_session.commit()

    contact = EmergencyContact(user_id=user.user_id, contact_name="Mom", phone="1112223333")
    test_db_session.add(contact)
    test_db_session.commit()

    # Delete user
    test_db_session.delete(user)
    test_db_session.commit()

    # Verify contact is deleted
    assert test_db_session.query(EmergencyContact).filter_by(contact_name="Mom").first() is None


def test_pydantic_schema_validation_and_orm_mode(test_db_session):
    """
    Verify Pydantic schemas validate input and properly serialize from SQLAlchemy ORM models.
    """
    # Create test ORM user
    orm_user = User(
        name="Alex Smith",
        email="alex@example.com",
        phone="5551234567",
        password_hash="secret_hash",
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    test_db_session.add(orm_user)
    test_db_session.commit()
    test_db_session.refresh(orm_user)

    # Validate Pydantic serialization via from_attributes
    user_dto = UserResponse.model_validate(orm_user)
    assert user_dto.user_id == orm_user.user_id
    assert user_dto.name == "Alex Smith"
    assert user_dto.email == "alex@example.com"
    assert user_dto.role == "user"

    # Validate Schema Input Validation
    sos_input = SOSTriggerRequest(
        latitude=Decimal("12.9716"),
        longitude=Decimal("77.5946"),
        description="Assistance needed",
    )
    assert sos_input.latitude == Decimal("12.9716")

    event_input = EventCreate(
        event_type="hazard",
        risk_level="HIGH",
        latitude=Decimal("12.9716"),
        longitude=Decimal("77.5946"),
        description="Hazard detected",
    )
    assert event_input.event_type == "hazard"


def test_get_db_session_dependency():
    """
    Verify get_db dependency yields and closes sessions properly.
    """
    generator = get_db()
    session = next(generator)
    assert session is not None
    try:
        next(generator)
    except StopIteration:
        pass  # Expected cleanup
