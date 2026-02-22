"""
Training Data Generator

Generates synthetic labeled training data for ML model training.
Uses the simulation module to create both honest and cheating sessions.
"""

from typing import List, Dict, Any, Tuple
import random
import json
import os

from app.features.pipeline import FeatureExtractor
from app.core.config import settings


def generate_honest_session() -> Dict[str, Any]:
    """Generate synthetic events for an honest test-taker."""
    events = []
    current_time = 0
    
    # Typing ~40-80 WPM, consistent rhythm
    typing_speed = random.uniform(60, 150)  # ms between keys
    
    # Type 200-500 characters
    chars_to_type = random.randint(200, 500)
    
    for _ in range(chars_to_type):
        delay = random.gauss(typing_speed, typing_speed * 0.2)
        delay = max(30, delay)  # Min 30ms
        current_time += delay
        
        events.append({
            "type": "keydown",
            "key": chr(random.randint(97, 122)),  # a-z
            "timestamp": current_time,
        })
    
    # Maybe 0-2 small pastes (copying own variable names)
    paste_count = random.randint(0, 2)
    for _ in range(paste_count):
        paste_time = random.uniform(0, current_time)
        events.append({
            "type": "paste",
            "length": random.randint(5, 30),  # Small pastes
            "timestamp": paste_time,
        })
    
    # 0-3 brief blurs (checking time, calculator, etc.)
    blur_count = random.randint(0, 3)
    for _ in range(blur_count):
        blur_time = random.uniform(0, current_time)
        events.append({
            "type": "blur",
            "timestamp": blur_time,
        })
        # Quick focus back
        events.append({
            "type": "focus",
            "timestamp": blur_time + random.uniform(500, 3000),
        })
    
    return {
        "session_id": f"honest_{random.randint(10000, 99999)}",
        "events": sorted(events, key=lambda e: e.get("timestamp", 0)),
        "is_cheating": False,
    }


def generate_cheating_session() -> Dict[str, Any]:
    """Generate synthetic events for a cheating test-taker."""
    events = []
    current_time = 0
    
    # Less typing, more pausing
    typing_speed = random.uniform(150, 400)  # Slower, more erratic
    
    # Type only 50-150 characters (less effort)
    chars_to_type = random.randint(50, 150)
    
    for _ in range(chars_to_type):
        delay = random.gauss(typing_speed, typing_speed * 0.5)  # More variance
        delay = max(30, delay)
        current_time += delay
        
        events.append({
            "type": "keydown",
            "key": chr(random.randint(97, 122)),
            "timestamp": current_time,
        })
    
    # Multiple large pastes (copied answers)
    paste_count = random.randint(3, 8)
    for _ in range(paste_count):
        paste_time = random.uniform(0, current_time * 1.5)
        events.append({
            "type": "paste",
            "length": random.randint(100, 500),  # Large pastes
            "timestamp": paste_time,
        })
    
    # Many tab switches (looking up answers)
    blur_count = random.randint(5, 15)
    for i in range(blur_count):
        blur_time = random.uniform(0, current_time * 1.5)
        events.append({
            "type": "blur",
            "timestamp": blur_time,
        })
        # Longer absence
        events.append({
            "type": "focus",
            "timestamp": blur_time + random.uniform(5000, 30000),
        })
        
        # Sometimes paste right after returning (copy-paste pattern)
        if random.random() > 0.4:
            events.append({
                "type": "paste",
                "length": random.randint(50, 300),
                "timestamp": blur_time + random.uniform(5000, 35000),
            })
    
    return {
        "session_id": f"cheat_{random.randint(10000, 99999)}",
        "events": sorted(events, key=lambda e: e.get("timestamp", 0)),
        "is_cheating": True,
    }


def generate_training_data(
    n_honest: int = 500,
    n_cheating: int = 500,
    save_path: str = None
) -> List[Tuple[Dict[str, Any], int]]:
    """
    Generate labeled training data for ML models.
    
    Args:
        n_honest: Number of honest sessions to generate
        n_cheating: Number of cheating sessions to generate
        save_path: Optional path to save the data as JSON
        
    Returns:
        List of (features_dict, label) tuples
    """
    extractor = FeatureExtractor()
    training_data = []
    
    # Generate honest sessions
    for i in range(n_honest):
        session = generate_honest_session()
        features = extractor.extract_features(
            events=session["events"],
            session_id=session["session_id"]
        )
        training_data.append((features.to_dict(), 0))  # Label 0 = honest
    
    # Generate cheating sessions
    for i in range(n_cheating):
        session = generate_cheating_session()
        features = extractor.extract_features(
            events=session["events"],
            session_id=session["session_id"]
        )
        training_data.append((features.to_dict(), 1))  # Label 1 = cheating
    
    # Shuffle
    random.shuffle(training_data)
    
    # Save if path provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(training_data, f, indent=2)
    
    return training_data


def train_ml_models(
    n_samples: int = 1000,
    save_data: bool = True,
    use_real_data: bool = True,
    data_source: str = "both",
    k_folds: int = 0,
) -> Dict[str, float]:
    """
    Generate training data and train ML models.
    
    Args:
        n_samples: Total number of samples (split 50/50) for synthetic only
        save_data: Whether to save training data
        use_real_data: Whether to use real datasets (BB-MAS, etc.)
        data_source: "real", "synthetic", or "both" (default)
        k_folds: If > 1, run k-fold cross-validation before final train
        
    Returns:
        Training metrics
    """
    from app.ml.predictor import MLPredictor
    
    print("=" * 50)
    print("ML MODEL TRAINING")
    print("=" * 50)
    
    # Resolve data_source vs legacy use_real_data
    if data_source == "synthetic":
        use_real_data = False
    elif data_source == "real":
        use_real_data = True
    # "both" keeps use_real_data as-is (default True)
    
    if use_real_data:
        # Use real data loader
        from app.ml.data_loader import load_all_training_data
        print("\nLoading real datasets (BB-MAS, exam behavior, etc.)...")
        training_data = load_all_training_data()
    else:
        # Use purely synthetic data
        n_each = n_samples // 2
        print(f"\nGenerating {n_each} honest and {n_each} cheating sessions...")
        
        save_path = None
        if save_data:
            save_path = os.path.join(settings.data_dir, "training_data.json")
        
        training_data = generate_training_data(
            n_honest=n_each,
            n_cheating=n_each,
            save_path=save_path
        )
    
    print(f"\nTotal training samples: {len(training_data)}")
    n_clean = sum(1 for _, label in training_data if label == 0)
    n_cheat = sum(1 for _, label in training_data if label == 1)
    print(f"  Clean: {n_clean}")
    print(f"  Cheating: {n_cheat}")
    
    # ── K-Fold Cross-Validation ──
    if k_folds > 1 and len(training_data) >= k_folds * 2:
        print(f"\nRunning {k_folds}-fold cross-validation...")
        cv_metrics = _run_cross_validation(training_data, k_folds)
        print(f"\n  CV Accuracy:  {cv_metrics['cv_accuracy_mean']:.1%} ± {cv_metrics['cv_accuracy_std']:.1%}")
        print(f"  CV F1 Score:  {cv_metrics['cv_f1_mean']:.1%} ± {cv_metrics['cv_f1_std']:.1%}")
        print(f"  CV Precision: {cv_metrics['cv_precision_mean']:.1%} ± {cv_metrics['cv_precision_std']:.1%}")
        print(f"  CV Recall:    {cv_metrics['cv_recall_mean']:.1%} ± {cv_metrics['cv_recall_std']:.1%}")
    
    # Train final model on full data
    print("\nTraining Random Forest + Isolation Forest...")
    predictor = MLPredictor()
    metrics = predictor.train(training_data, save_after=True)
    
    print("\n" + "=" * 50)
    print("TRAINING COMPLETE!")
    print("=" * 50)
    print(f"  Accuracy: {metrics['accuracy']:.1%}")
    print(f"  Total samples: {metrics['n_samples']}")
    print(f"  Cheating samples: {metrics['n_cheating']}")
    print(f"  Clean samples: {metrics['n_clean']}")
    
    return metrics


def _run_cross_validation(
    training_data: List[Tuple[Dict[str, Any], int]],
    k: int = 5,
) -> Dict[str, float]:
    """
    Run stratified k-fold cross-validation.

    Returns dict with cv_accuracy_mean, cv_accuracy_std, etc.
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

    # Flatten features
    flat_data = []
    labels = []
    for feat_dict, label in training_data:
        flat = {}
        for key, value in feat_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float, bool)):
                        flat[f"{key}_{sub_key}"] = float(sub_value)
            elif isinstance(value, (int, float, bool)):
                flat[key] = float(value)
        flat_data.append(flat)
        labels.append(label)

    import numpy as np
    y = np.array(labels)

    # Vectorize
    vec = DictVectorizer(sparse=False)
    X_raw = vec.fit_transform(flat_data)

    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    acc_scores, f1_scores, prec_scores, rec_scores = [], [], [], []

    for train_idx, val_idx in skf.split(X_raw, y):
        X_train, X_val = X_raw[train_idx], X_raw[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        imp = SimpleImputer(strategy="median")
        X_train = imp.fit_transform(X_train)
        X_val = imp.transform(X_val)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)

        rf = RandomForestClassifier(
            n_estimators=100, max_depth=12,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        acc_scores.append(accuracy_score(y_val, y_pred))
        f1_scores.append(f1_score(y_val, y_pred, zero_division=0))
        prec_scores.append(precision_score(y_val, y_pred, zero_division=0))
        rec_scores.append(recall_score(y_val, y_pred, zero_division=0))

    return {
        "cv_accuracy_mean": float(np.mean(acc_scores)),
        "cv_accuracy_std": float(np.std(acc_scores)),
        "cv_f1_mean": float(np.mean(f1_scores)),
        "cv_f1_std": float(np.std(f1_scores)),
        "cv_precision_mean": float(np.mean(prec_scores)),
        "cv_precision_std": float(np.std(prec_scores)),
        "cv_recall_mean": float(np.mean(rec_scores)),
        "cv_recall_std": float(np.std(rec_scores)),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train cheating detection ML models")
    parser.add_argument(
        "--data-source",
        choices=["real", "synthetic", "both"],
        default="both",
        help="Which data to train on (default: both)",
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=0,
        help="K-fold cross-validation folds (0 = skip CV, default: 0)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=1000,
        help="Number of synthetic samples when using synthetic data (default: 1000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    import logging
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    train_ml_models(
        n_samples=args.samples,
        save_data=True,
        data_source=args.data_source,
        k_folds=args.folds,
    )

