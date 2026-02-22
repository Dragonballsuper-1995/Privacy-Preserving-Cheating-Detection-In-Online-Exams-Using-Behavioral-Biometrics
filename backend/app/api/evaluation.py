"""
API endpoint for evaluation and reporting.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.auth import require_instructor, UserResponse
from pydantic import BaseModel
from typing import Optional
import os

from app.ml.evaluation import (
    evaluate_model,
    find_optimal_threshold,
    generate_evaluation_report,
    load_labeled_dataset,
)
from app.core.config import settings

router = APIRouter()


class EvaluationRequest(BaseModel):
    """Evaluation request parameters."""
    threshold: float = 0.75


@router.post("/evaluate")
async def run_evaluation(request: EvaluationRequest, user: UserResponse = Depends(require_instructor)):
    """
    Evaluate the model on the training dataset.
    
    Returns classification metrics (accuracy, precision, recall, F1, AUC-ROC).
    """
    try:
        result = evaluate_model(threshold=request.threshold)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/optimal-threshold")
async def get_optimal_threshold(user: UserResponse = Depends(require_instructor)):
    """
    Find the optimal classification threshold.
    
    Tests multiple thresholds and returns the one with best F1 score.
    """
    try:
        threshold, result = find_optimal_threshold()
        return {
            "optimal_threshold": threshold,
            "f1_score": result.f1 if result else 0,
            "metrics": result.to_dict() if result else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report")
async def get_evaluation_report(user: UserResponse = Depends(require_instructor)):
    """
    Generate a markdown evaluation report.
    """
    report = generate_evaluation_report()
    return {"report": report}


@router.get("/dataset-info")
async def get_dataset_info(user: UserResponse = Depends(require_instructor)):
    """
    Get information about the current training dataset.
    """
    dataset = load_labeled_dataset()
    
    if not dataset:
        return {
            "exists": False,
            "message": "No training dataset found. Use /api/simulation/generate-training-data to create one.",
        }
    
    honest_count = sum(1 for _, label in dataset if label == 0)
    cheater_count = sum(1 for _, label in dataset if label == 1)
    
    return {
        "exists": True,
        "total_sessions": len(dataset),
        "honest_sessions": honest_count,
        "cheater_sessions": cheater_count,
        "balance_ratio": honest_count / cheater_count if cheater_count > 0 else float('inf'),
    }
