"""
Models API - Endpoints for MLOps and Model Drift Monitoring
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ml.monitoring import get_model_health_metrics
from app.ml.retraining_pipeline import run_retraining_pipeline

router = APIRouter()

@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Fetch MLOps metrics including data drift K-S test on the core heuristic features."""
    metrics = get_model_health_metrics(db)
    return metrics

@router.post("/retrain")
async def trigger_retraining(background_tasks: BackgroundTasks):
    """Trigger the Risk Fusion retraining pipeline asynchronously."""
    # Run the retraining logic in the background
    background_tasks.add_task(run_retraining_pipeline)
    return {"status": "started", "message": "Model retraining pipeline has been triggered in the background."}
