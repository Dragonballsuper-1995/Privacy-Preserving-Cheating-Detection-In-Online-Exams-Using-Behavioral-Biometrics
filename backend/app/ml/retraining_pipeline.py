"""
ML Retraining Pipeline

This script retrieves sessions that have been manually reviewed by instructors
(Human-in-the-loop feedback) and uses them to fine-tune the risk thresholds
and potentially train a supervised model in the future.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session as DbSession

from app.core.database import SessionLocal
from app.models.session import Session, ReviewStatus
from app.core.config import settings
from app.features.pipeline import FeatureExtractor

def load_reviewed_sessions(db: DbSession) -> List[Session]:
    """Retrieve all sessions that have a confirmed review status."""
    return db.query(Session).filter(
        Session.review_status.in_([ReviewStatus.CONFIRMED_CHEATING, ReviewStatus.FALSE_POSITIVE])
    ).all()

def extract_features_for_session(session_id: str) -> Dict:
    """Load events and extract feature vector for a single session."""
    log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
    if not os.path.exists(log_file):
        return None
        
    events = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
                
    if not events:
        return None
        
    extractor = FeatureExtractor(
        pause_threshold_ms=settings.min_pause_duration,
        risk_threshold=settings.risk_threshold
    )
    
    features = extractor.extract_features(events, session_id)
    return {
        "overall_score": features.overall_score,
        "typing_score": features.typing_score,
        "hesitation_score": features.hesitation_score,
        "paste_score": features.paste_score,
        "focus_score": features.focus_score,
        "similarity_score": features.similarity_score
    }

def run_retraining_pipeline():
    """
    Main pipeline to run retraining.
    Currently, this analyzes the shift in features to recommend new thresholds.
    """
    db = SessionLocal()
    try:
        print("🔍 Starting ML Retraining Pipeline...")
        reviewed_sessions = load_reviewed_sessions(db)
        
        if len(reviewed_sessions) < 10:
            print(f"⚠️ Not enough reviewed sessions ({len(reviewed_sessions)}). Need at least 10 to safely adjust thresholds.")
            return
            
        print(f"✅ Found {len(reviewed_sessions)} manually reviewed sessions.")
        
        dataset = []
        labels = []
        
        for session in reviewed_sessions:
            features = extract_features_for_session(session.id)
            if features:
                dataset.append(features)
                labels.append(1 if session.review_status == ReviewStatus.CONFIRMED_CHEATING else 0)
                
        if not dataset:
            print("❌ Could not extract features for any reviewed sessions.")
            return
            
        df = pd.DataFrame(dataset)
        df['label'] = labels
        
        # Calculate statistics
        cheaters = df[df['label'] == 1]
        honest = df[df['label'] == 0]
        
        print("\n--- Shift Analysis ---")
        for col in df.columns:
            if col != 'label':
                mean_cheat = cheaters[col].mean() if not cheaters.empty else 0
                mean_honest = honest[col].mean() if not honest.empty else 0
                print(f"{col}:")
                print(f"  Confirmed Cheating Mean: {mean_cheat:.3f}")
                print(f"  False Positive Mean:     {mean_honest:.3f}")
                
        # Basic optimal threshold finding for overall_score
        if not cheaters.empty and not honest.empty:
            best_thresh = settings.risk_threshold
            best_acc = 0
            
            # Simple line search for optimal threshold
            for thresh in np.arange(0.1, 0.9, 0.05):
                # Predict 1 if score >= thresh, else 0
                preds = (df['overall_score'] >= thresh).astype(int)
                acc = (preds == df['label']).mean()
                if acc > best_acc:
                    best_acc = acc
                    best_thresh = thresh
            
            print(f"\n📈 Recommended Risk Threshold Update: {best_thresh:.2f} (Estimated Accuracy: {best_acc*100:.1f}%)")
            print("To apply, update 'RISK_THRESHOLD' in your .env file.")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_retraining_pipeline()
