"""
Authentication API Routes

Provides registration, login, and user profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.auth import (
    UserCreate,
    UserResponse,
    Token,
    create_user,
    login,
    get_current_active_user,
    require_admin,
)

router = APIRouter()


class RegisterRequest(BaseModel):
    """Registration request body."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"


class LoginRequest(BaseModel):
    """Login request body (JSON-based)."""
    email: EmailStr
    password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterRequest,
    db: DBSession = Depends(get_db)
):
    """
    Register a new user.

    - Students can self-register
    - Instructor/admin roles require admin approval (future)
    """
    user_data = UserCreate(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
    )

    user = create_user(db, user_data)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if user.role else "student",
        is_active=user.is_active,
    )


@router.post("/login", response_model=Token)
async def login_user(
    request: LoginRequest,
    db: DBSession = Depends(get_db)
):
    """
    Authenticate and receive a JWT token.

    Use the returned `access_token` in the `Authorization: Bearer <token>` header.
    """
    token = await login(request.email, request.password, db)
    return token


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DBSession = Depends(get_db)
):
    """
    OAuth2-compatible login endpoint (form-based).
    Used by Swagger UI's Authorize button.
    """
    token = await login(form_data.username, form_data.password, db)
    return token


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the current authenticated user's profile."""
    return current_user
