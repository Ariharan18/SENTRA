"""
SENTRA Database Foundation
SQLAlchemy engine, sessionmaker, and Base declarative model.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Create engine with connection pooling settings suitable for MySQL
# pool_pre_ping ensures stale connections are detected and refreshed
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency generator for obtaining isolated database sessions per request.
    Ensures safe session closure on request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine=None):
    """
    Safely creates all database tables defined in SQLAlchemy models if they do not exist.
    Non-destructive: will not drop tables or delete existing data.
    """
    import app.models  # noqa: F401 - Register models with Base.metadata
    active_engine = target_engine or engine
    Base.metadata.create_all(bind=active_engine)
