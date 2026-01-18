"""
Rate Limiting and Security Middleware

Implements rate limiting, CORS, and security headers.
"""

from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
import time
from collections import defaultdict
from typing import Dict, Tuple

from app.core.config import settings


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


# In-memory rate limiting (for simple cases)
class InMemoryRateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests: Dict[str, list[float]] = defaultdict(list)
    
    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check if request should be rate limited.
        
        Args:
            key: Identifier (e.g., IP address, user ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            oldest = min(self.requests[key])
            retry_after = int(oldest + window_seconds - now + 1)
            return True, retry_after
        
        # Add current request
        self.requests[key].append(now)
        return False, 0


rate_limiter = InMemoryRateLimiter()


# Rate limiting middleware
async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting to requests.
    
    Different limits for different endpoints:
    - /api/events/log: 1000/minute per session
    - /api/analysis/*: 10/minute per user
    - Default: 60/minute per IP
    """
    client_ip = request.client.host
    path = request.url.path
    
    # Determine rate limit based on path
    if "/api/events/log" in path:
        max_requests, window = 1000, 60
        key = f"events_{client_ip}"
    elif "/api/analysis" in path:
        max_requests, window = 10, 60
        key = f"analysis_{client_ip}"
    else:
        max_requests, window = 60, 60
        key = f"default_{client_ip}"
    
    # Check rate limit
    is_limited, retry_after = rate_limiter.is_rate_limited(key, max_requests, window)
    
    if is_limited:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Window"] = str(window)
    
    return response


# Security headers middleware
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


# CORS configuration
def configure_cors(app):
    """Configure CORS middleware."""
    origins = settings.allowed_origins.split(",") if settings.allowed_origins else ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
    )


# Trusted host configuration
def configure_trusted_hosts(app):
    """Configure trusted host middleware."""
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_origins.split(",")
        )


# Session configuration (for CSRF protection)  
def configure_sessions(app):
    """Configure session middleware."""
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="session",
        max_age=3600,  # 1 hour
        same_site="lax",
        https_only=settings.environment == "production"
    )


# Request validation
async def validate_request_size(request: Request, call_next):
    """Limit request body size to prevent DoS."""
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
    
    content_length = request.headers.get("content-length")
    
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request body too large. Maximum size: {MAX_REQUEST_SIZE} bytes"
        )
    
    return await call_next(request)
