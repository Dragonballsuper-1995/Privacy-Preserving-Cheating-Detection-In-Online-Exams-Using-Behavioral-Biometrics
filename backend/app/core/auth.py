"""
Authentication and Authorization

JWT-based authentication with role-based access control.
Uses database-backed user management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User as UserModel, UserRole


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme — auto_error=False allows optional auth on some endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)
oauth2_scheme_required = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# ---- Pydantic schemas ----

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Decoded token data."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """User response model (no password)."""
    id: str
    email: str
    full_name: Optional[str] = None
    role: str = "student"
    is_active: bool = True


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"


# ---- Password utilities ----

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ---- JWT utilities ----

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, user_id=user_id, role=role)

    except JWTError:
        raise credentials_exception

    return token_data


# ---- User CRUD operations ----

def get_user_by_email(db: DBSession, email: str) -> Optional[UserModel]:
    """Fetch a user from the database by email."""
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_id(db: DBSession, user_id: str) -> Optional[UserModel]:
    """Fetch a user from the database by ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def create_user(db: DBSession, user_data: UserCreate) -> UserModel:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists
    """
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate role
    try:
        role = UserRole(user_data.role)
    except ValueError:
        role = UserRole.STUDENT

    db_user = UserModel(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---- Dependencies for route protection ----

async def get_current_user(
    token: str = Depends(oauth2_scheme_required),
    db: DBSession = Depends(get_db)
) -> UserResponse:
    """
    Get the current authenticated user from the token.
    Fetches the actual user from the database.

    Args:
        token: JWT token from request
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If authentication fails or user not found
    """
    token_data = decode_access_token(token)

    user = get_user_by_id(db, token_data.user_id)

    if user is None:
        # Fallback: try email lookup
        user = get_user_by_email(db, token_data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if user.role else "student",
        is_active=user.is_active,
    )


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: DBSession = Depends(get_db)
) -> Optional[UserResponse]:
    """
    Optionally get the current user. Returns None if no token provided.
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if token is None:
        return None

    try:
        token_data = decode_access_token(token)
        user = get_user_by_id(db, token_data.user_id)
        if user and user.is_active:
            return UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value if user.role else "student",
                is_active=user.is_active,
            )
    except HTTPException:
        pass

    return None


# ---- Role-based access control ----

class RoleChecker:
    """Check if user has required role."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserResponse = Depends(get_current_active_user)) -> UserResponse:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user


# Common role checkers
require_admin = RoleChecker(["admin"])
require_instructor = RoleChecker(["admin", "instructor"])
require_authenticated = Depends(get_current_active_user)


# ---- Authentication functions ----

async def authenticate_user(email: str, password: str, db: DBSession) -> Optional[UserModel]:
    """
    Authenticate a user with email and password.

    Args:
        email: User email
        password: User password
        db: Database session

    Returns:
        User if authentication successful, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def login(email: str, password: str, db: DBSession) -> Token:
    """
    Authenticate user and create access token.

    Args:
        email: User email
        password: User password
        db: Database session

    Returns:
        Token with access token

    Raises:
        HTTPException: If authentication fails
    """
    user = await authenticate_user(email, password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value if user.role else "student"
        },
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


def seed_admin_user(db: DBSession) -> None:
    """
    Create the default admin user if no admin exists.
    Uses ADMIN_EMAIL and ADMIN_PASSWORD environment variables.
    """
    import os

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@cheatingdetector.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

    existing_admin = db.query(UserModel).filter(UserModel.role == UserRole.ADMIN).first()
    if existing_admin:
        return

    admin = UserModel(
        email=admin_email,
        full_name="System Administrator",
        hashed_password=get_password_hash(admin_password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print(f"✅ Default admin user created: {admin_email}")
