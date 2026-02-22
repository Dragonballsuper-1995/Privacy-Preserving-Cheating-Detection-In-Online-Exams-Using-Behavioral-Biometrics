"""
Tests for the authentication system.

Tests cover:
- User registration
- User login
- JWT token validation
- Role-based access control
- Protected endpoint access
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.user import User, UserRole
from app.main import app


# --- Test database setup ---

TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create tables before tests and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# --- Unit tests ---

class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_and_verify(self):
        password = "secure_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct")
        assert not verify_password("wrong", hashed)

    def test_hash_is_unique(self):
        h1 = get_password_hash("same_password")
        h2 = get_password_hash("same_password")
        assert h1 != h2  # bcrypt salts are unique


class TestJWT:
    """Test JWT token creation and decoding."""

    def test_create_and_decode_token(self):
        token = create_access_token({
            "sub": "test@example.com",
            "user_id": "user-123",
            "role": "admin"
        })
        data = decode_access_token(token)
        assert data.email == "test@example.com"
        assert data.user_id == "user-123"
        assert data.role == "admin"

    def test_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_access_token("invalid.token.here")


# --- Integration tests ---

class TestRegistration:
    """Test user registration endpoint."""

    def test_register_new_user(self):
        response = client.post("/api/auth/register", json={
            "email": "student@test.com",
            "password": "testpass123",
            "full_name": "Test Student",
            "role": "student"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "student@test.com"
        assert data["role"] == "student"
        assert data["is_active"] is True

    def test_register_duplicate_email_fails(self):
        # First registration
        client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "pass123",
        })
        # Duplicate
        response = client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "pass456",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestLogin:
    """Test user login endpoint."""

    def test_login_success(self):
        # Register first
        client.post("/api/auth/register", json={
            "email": "logintest@test.com",
            "password": "mypassword",
        })
        # Login
        response = client.post("/api/auth/login", json={
            "email": "logintest@test.com",
            "password": "mypassword",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        client.post("/api/auth/register", json={
            "email": "wrongpw@test.com",
            "password": "correct",
        })
        response = client.post("/api/auth/login", json={
            "email": "wrongpw@test.com",
            "password": "wrong",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        response = client.post("/api/auth/login", json={
            "email": "noone@test.com",
            "password": "anything",
        })
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""

    def _get_admin_token(self) -> str:
        """Helper: register admin and get token."""
        client.post("/api/auth/register", json={
            "email": "admin@test.com",
            "password": "adminpass",
            "role": "admin",
        })
        resp = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "adminpass",
        })
        return resp.json()["access_token"]

    def _get_student_token(self) -> str:
        """Helper: register student and get token."""
        client.post("/api/auth/register", json={
            "email": "student@test.com",
            "password": "studentpass",
            "role": "student",
        })
        resp = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "studentpass",
        })
        return resp.json()["access_token"]

    def test_dashboard_requires_auth(self):
        response = client.get("/api/analysis/dashboard/summary")
        assert response.status_code in (401, 403)

    def test_dashboard_with_admin_token(self):
        token = self._get_admin_token()
        response = client.get(
            "/api/analysis/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_simulation_requires_admin(self):
        student_token = self._get_student_token()
        response = client.post(
            "/api/simulation/simulate",
            json={"is_cheater": False, "count": 1},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403

    def test_me_endpoint(self):
        token = self._get_admin_token()
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"
