"""
Alembic environment configuration.

Reads the database URL from app.core.config.settings so there's a single
source of truth for the connection string.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# -- Import app models so Alembic can inspect them --
from app.core.config import settings
from app.core.database import Base

# Register every model with Base.metadata
from app.models.exam import Exam, Question        # noqa: F401
from app.models.session import Session, Answer     # noqa: F401
from app.models.event import BehaviorEvent, FeatureVector, RiskScore  # noqa: F401
from app.models.user import User                   # noqa: F401

# Alembic Config object
config = context.config

# Logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from settings (overrides alembic.ini)
config.set_main_option("sqlalchemy.url", settings.database_url)

# MetaData for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL without connecting)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to DB and applies changes)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
