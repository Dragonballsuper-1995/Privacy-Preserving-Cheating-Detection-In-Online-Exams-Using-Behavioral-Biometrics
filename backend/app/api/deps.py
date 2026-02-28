"""
API Dependencies

Re-exports common dependencies for API route modules.
"""

from app.core.database import get_db  # noqa: F401

__all__ = ["get_db"]
