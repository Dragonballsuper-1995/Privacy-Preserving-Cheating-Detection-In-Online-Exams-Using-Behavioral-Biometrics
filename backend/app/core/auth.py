"""
Authentication and Authorization

JWT-based authentication with role-based access control.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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


class User(BaseModel):
    """User model."""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "student"
    is_active: bool = True


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT utilities
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
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


# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from the token.
    
    Args:
        token: JWT token from request
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    token_data = decode_access_token(token)
    
    # TODO: Fetch user from database
    # For now, return user from token data
    user = User(
        id=token_data.user_id or "unknown",
        email=token_data.email or "",
        role=token_data.role or "student"
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


# Role-based access control
class RoleChecker:
    """Check if user has required role."""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
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


# Authentication function
async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        User if authentication successful, None otherwise
    """
    # TODO: Fetch user from database
    # For now, accept test credentials
    if email == "admin@example.com" and password == "admin123":
        return User(
            id="admin-001",
            email=email,
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
    
    return None


# Login function
async def login(email: str, password: str) -> Token:
    """
    Authenticate user and create access token.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Token with access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user = await authenticate_user(email, password)
    
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
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60
    )
