"""
Privacy-Preserving AI-Based Cheating Detection System
Main FastAPI Application

Optimized for fast startup on platforms like Render that require quick port binding.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.config import settings

# Track initialization state
_app_state = {
    "database_ready": False,
    "initializing": False,
    "error": None
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
        from app.core.database import init_db
        init_db()
        _app_state["database_ready"] = True
        print("✅ Database ready!")
        
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


# Import routers lazily to speed up startup
def _include_routers():
    """Include API routers - called after app is created."""
    from app.api import events, sessions, exams, analysis, simulation, evaluation, code_execution
    
    app.include_router(events.router, prefix="/api/events", tags=["Events"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
    app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
    app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])
    app.include_router(code_execution.router, prefix="/api/code", tags=["Code Execution"])


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

