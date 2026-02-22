"""
Privacy-Preserving AI-Based Cheating Detection System
Main FastAPI Application

Optimized for fast startup on platforms like Render that require quick port binding.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import time

from app.core.config import settings

# Track initialization state
_app_state = {
    "database_ready": False,
    "initializing": False,
    "error": None,
    "start_time": time.time(),
}

# ── Observability counters ──
_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "active_sessions": 0,
    "events_processed": 0,
}


async def _background_init():
    """Initialize heavy components in background after server starts."""
    global _app_state
    
    if _app_state["initializing"]:
        return
    
    _app_state["initializing"] = True
    
    try:
        # Small delay to ensure server is fully up
        await asyncio.sleep(0.1)
        
        print("📦 Initializing database in background...")
        from app.core.database import init_db, SessionLocal
        init_db()
        _app_state["database_ready"] = True
        print("✅ Database ready!")
        
        # Seed default admin user if none exists
        try:
            from app.core.auth import seed_admin_user
            db = SessionLocal()
            seed_admin_user(db)
            db.close()
        except Exception as e:
            print(f"⚠️ Admin seed skipped: {e}")
        
    except Exception as e:
        _app_state["error"] = str(e)
        print(f"❌ Initialization error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup - fast path, defer heavy init
    print("🚀 Starting Cheating Detection API...")
    
    # Start background initialization (non-blocking)
    asyncio.create_task(_background_init())
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Cheating Detection API",
    description="Privacy-preserving AI-based cheating detection using behavioral biometrics",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting & security middleware
from app.core.security import (
    limiter,
    rate_limit_middleware,
    security_headers_middleware,
    validate_request_size,
)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(validate_request_size)


# ── Request logging middleware ──
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
import logging

logger = logging.getLogger("cheating_detector")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        start = time.time()
        _metrics["total_requests"] += 1
        response: StarletteResponse = await call_next(request)  # type: ignore[assignment]
        duration_ms = (time.time() - start) * 1000
        status = response.status_code
        if status >= 400:
            _metrics["total_errors"] += 1
        logger.info(
            "%s %s → %d (%.1fms)",
            request.method,
            request.url.path,
            status,
            duration_ms,
        )
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response


app.add_middleware(RequestLoggingMiddleware)


# Import routers lazily to speed up startup
def _include_routers():
    """Include API routers - called after app is created."""
    from app.api import events, sessions, exams, analysis, simulation, evaluation, code_execution, auth_routes, websocket, reviews, models
    
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(events.router, prefix="/api/events", tags=["Events"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
    app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
    app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
    app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])
    app.include_router(code_execution.router, prefix="/api/code", tags=["Code Execution"])
    app.include_router(models.router, prefix="/api/models", tags=["Models"])
    app.include_router(websocket.router, tags=["WebSocket"])


_include_routers()


@app.get("/")
async def root():
    """Health check endpoint - always returns 200 for platform health checks."""
    return {
        "status": "healthy",
        "service": "Cheating Detection API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with initialization status."""
    return {
        "status": "healthy",
        "database": "ready" if _app_state["database_ready"] else "initializing",
        "initialization_complete": _app_state["database_ready"],
        "error": _app_state["error"]
    }


@app.get("/metrics")
async def metrics():
    """Basic observability counters for monitoring."""
    uptime = time.time() - _app_state["start_time"]
    return {
        "total_requests": _metrics["total_requests"],
        "total_errors": _metrics["total_errors"],
        "active_sessions": _metrics["active_sessions"],
        "events_processed": _metrics["events_processed"],
        "uptime_seconds": round(uptime, 1),
        "database_ready": _app_state["database_ready"],
    }

