"""
Seed Admin User Script

Creates the default admin user if none exists.
Can be run standalone or called during app startup.

Usage:
    python -m scripts.seed_admin

Environment variables:
    ADMIN_EMAIL: Admin email (default: admin@cheatingdetector.com)
    ADMIN_PASSWORD: Admin password (default: admin123)
"""

import os
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db
from app.core.auth import seed_admin_user


def main():
    print("🔧 Initializing database...")
    init_db()

    print("👤 Seeding admin user...")
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()

    print("✅ Done!")


if __name__ == "__main__":
    main()
