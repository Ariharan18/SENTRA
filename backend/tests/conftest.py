"""
Pytest configuration and shared fixtures for the SENTRA backend test suite.

Strategy:
- A single shared SQLite StaticPool engine is used for all HTTP-based tests.
- The `db_session` fixture creates/drops schema per test and wires the app's get_db override.
- The `client` fixture provides a TestClient on top of db_session.
- test_main.py tests don't need DB access, so they use their own module-level TestClient.
- test_database_models.py manages its own isolated engine per test.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db

# Isolated in-memory SQLite engine with StaticPool for thread-safe test execution
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session():
    """
    Creates a fresh database schema before each test and drops it after completion.
    Overrides FastAPI's get_db dependency to point to the shared StaticPool session.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass  # session lifecycle managed by fixture

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def client(db_session):
    """
    Returns a FastAPI TestClient wired to the isolated test database session.
    Depends on db_session to ensure schema and override are set up before any request.
    """
    with TestClient(app) as test_client:
        yield test_client
