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
    use_real_data: bool = True
) -> Dict[str, float]:
    """
    Generate training data and train ML models.
    
    Args:
        n_samples: Total number of samples (split 50/50) for synthetic only
        save_data: Whether to save training data
        use_real_data: Whether to use real datasets (BB-MAS, etc.)
        
    Returns:
        Training metrics
    """
    from app.ml.predictor import MLPredictor
    
    print("=" * 50)
    print("ML MODEL TRAINING")
    print("=" * 50)
    
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
    
    # Train models
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


if __name__ == "__main__":
    # Run training with real data when executed directly
    train_ml_models(use_real_data=True, save_data=True)
