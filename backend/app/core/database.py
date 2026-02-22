"""
Database setup and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
import os


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Determine if using SQLite or PostgreSQL
is_sqlite = settings.database_url.startswith("sqlite")

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=False,
    # SQLite specific settings
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.

    For development convenience, this still calls create_all() on the first
    run and stamps the Alembic version table so that subsequent schema
    changes are tracked through proper migrations.

    Production deployments should use:
        alembic upgrade head
    """
    # Import models to register them with Base
    from app.models.exam import Exam, Question  # noqa: F401
    from app.models.session import Session, Answer  # noqa: F401
    from app.models.event import BehaviorEvent, FeatureVector, RiskScore  # noqa: F401
    from app.models.user import User  # noqa: F401

    # Create tables (idempotent — only creates missing tables)
    Base.metadata.create_all(bind=engine)

    # Stamp Alembic version so migrations know the current state
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini'))
        command.stamp(alembic_cfg, "head")
    except Exception:
        pass  # Alembic not configured yet — that's OK during early development
