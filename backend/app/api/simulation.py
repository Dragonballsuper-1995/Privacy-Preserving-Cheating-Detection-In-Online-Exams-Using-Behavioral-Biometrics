"""
Simulation API - Generate test data and train models
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.auth import require_admin, UserResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from app.core.config import settings
from app.ml.simulation import (
    simulate_session,
    save_simulated_session,
    generate_training_dataset,
)
from app.ml.anomaly import BehaviorAnomalyDetector
from app.ml.fusion import RiskFusionModel
from app.features.pipeline import extract_all_features

router = APIRouter()


class SimulateRequest(BaseModel):
    """Request to simulate sessions."""
    is_cheater: bool = False
    count: int = 1
    question_count: int = 6


class TrainingRequest(BaseModel):
    """Request to generate training data and train models."""
    honest_count: int = 50
    cheater_count: int = 20


@router.post("/simulate")
async def generate_simulated_sessions(request: SimulateRequest, user: UserResponse = Depends(require_admin)):
    """
    Generate simulated exam sessions for testing.
    
    Args:
        is_cheater: Generate cheating behavior
        count: Number of sessions to generate
        question_count: Questions per session
    """
    if request.count > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 sessions at once")
    
    sessions = []
    for _ in range(request.count):
        session = simulate_session(
            is_cheater=request.is_cheater,
            question_count=request.question_count,
        )
        file_path = save_simulated_session(session)
        sessions.append({
            "session_id": session["session_id"],
            "is_cheater": session["is_cheater"],
            "event_count": session["total_events"],
            "file": os.path.basename(file_path),
        })
    
    return {
        "generated": len(sessions),
        "type": "cheater" if request.is_cheater else "honest",
        "sessions": sessions,
    }


@router.post("/generate-training-data")
async def generate_training_data(request: TrainingRequest, user: UserResponse = Depends(require_admin)):
    """
    Generate a labeled training dataset.
    
    Creates simulated honest and cheating sessions,
    saves them to JSONL files, and creates a manifest.
    """
    if request.honest_count + request.cheater_count > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 total sessions")
    
    dataset = generate_training_dataset(
        honest_count=request.honest_count,
        cheater_count=request.cheater_count,
    )
    
    return {
        "message": "Training dataset generated",
        "honest_sessions": request.honest_count,
        "cheater_sessions": request.cheater_count,
        "total_sessions": len(dataset),
        "manifest_path": os.path.join(settings.data_dir, "training_manifest.json"),
    }


@router.post("/train-models")
async def train_models(user: UserResponse = Depends(require_admin)):
    """
    Train ML models on the generated training data.
    
    1. Loads the training manifest
    2. Extracts features for each session
    3. Trains anomaly detector and fusion model
    """
    manifest_path = os.path.join(settings.data_dir, "training_manifest.json")
    
    if not os.path.exists(manifest_path):
        raise HTTPException(
            status_code=404, 
            detail="Training manifest not found. Generate training data first."
        )
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    sessions = manifest.get("sessions", [])
    if not sessions:
        raise HTTPException(status_code=400, detail="No sessions in manifest")
    
    # Extract features for each session
    feature_vectors = []
    fusion_training_data = []
    
    for session_info in sessions:
        session_id = session_info["session_id"]
        label = session_info["label"]
        
        # Load events
        log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
        if not os.path.exists(log_file):
            continue
        
        events = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue
        
        if not events:
            continue
        
        # Extract features
        features = extract_all_features(events, session_id)
        feature_dict = features.to_dict()
        
        feature_vectors.append(feature_dict)
        fusion_training_data.append((
            {
                "behavioral": features.overall_score,
                "anomaly": 0.0,  # Will be filled after anomaly training
                "similarity": 0.0,  # No similarity for simulated data
            },
            label
        ))
    
    if len(feature_vectors) < 10:
        raise HTTPException(status_code=400, detail="Not enough valid sessions for training")
    
    # Train anomaly detector
    print("🔧 Training anomaly detector...")
    anomaly_detector = BehaviorAnomalyDetector()
    # Train on honest sessions only
    honest_features = [f for f, (_, label) in zip(feature_vectors, zip(feature_vectors, [s["label"] for s in sessions])) if sessions[feature_vectors.index(f)]["label"] == 0]
    anomaly_detector.fit(honest_features[:len(honest_features)])
    
    # Update fusion training data with anomaly scores
    for i, feature_dict in enumerate(feature_vectors):
        if i < len(fusion_training_data):
            anomaly_result = anomaly_detector.detect(feature_dict, "")
            fusion_training_data[i][0]["anomaly"] = anomaly_result.normalized_score
    
    # Train fusion model
    print("🔧 Training fusion model...")
    fusion_model = RiskFusionModel()
    fusion_model.fit(fusion_training_data)
    
    return {
        "message": "Models trained successfully",
        "sessions_used": len(feature_vectors),
        "anomaly_model_path": anomaly_detector.model_path,
        "fusion_model_path": fusion_model.model_path,
    }


@router.get("/status")
async def get_simulation_status(user: UserResponse = Depends(require_admin)):
    """Get the current status of simulation and models."""
    # Check for training data
    manifest_path = os.path.join(settings.data_dir, "training_manifest.json")
    has_training_data = os.path.exists(manifest_path)
    
    training_info = None
    if has_training_data:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            training_info = {
                "generated_at": manifest.get("generated_at"),
                "honest_count": manifest.get("honest_count"),
                "cheater_count": manifest.get("cheater_count"),
            }
    
    # Check for trained models
    anomaly_path = os.path.join(settings.models_dir, "anomaly_detector.pkl")
    fusion_path = os.path.join(settings.models_dir, "fusion_model.pkl")
    
    return {
        "training_data_exists": has_training_data,
        "training_info": training_info,
        "anomaly_model_exists": os.path.exists(anomaly_path),
        "fusion_model_exists": os.path.exists(fusion_path),
        "event_logs_dir": settings.event_logs_dir,
        "models_dir": settings.models_dir,
    }
