"""
Privacy-Preserving AI-Based Cheating Detection System
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import events, sessions, exams, analysis, simulation, evaluation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Cheating Detection API...")
    print("📦 Initializing database...")
    init_db()
    print("✅ Database ready!")
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

# Include routers
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Cheating Detection API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded"
    }
