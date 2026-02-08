"""
Real Data Loader for ML Training

Loads and processes real datasets from:
1. IEEE Datasets (BB-MAS keystroke, Plagiarism)
2. Project datasets (exam_behavior, keystroke)

Converts them to feature vectors for ML model training.
"""

import os
import csv
import json
import random
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


# Dataset paths
IEEE_DATASETS_PATH = r"D:\IDM Downloads\Misc\Datasets IEEE"
PROJECT_DATASETS_PATH = r"c:\Users\sujal\Documents\Projects\Cheating Detector\backend\data\datasets"


@dataclass
class RawSession:
    """Raw session data from any source."""
    session_id: str
    source: str  # "bbmas", "plagiarism", "exam_behavior", etc.
    label: int  # 0 = clean, 1 = cheating
    keystroke_data: Optional[List[Dict[str, Any]]] = None
    behavior_data: Optional[Dict[str, Any]] = None
    

def load_bbmas_keystroke_features(max_users: int = 50) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load BB-MAS keystroke features and convert to training format.
    
    BB-MAS contains keystroke biometric data from 117 users.
    We treat this as "normal" typing behavior (label=0) for Isolation Forest.
    
    Returns:
        List of (features_dict, label) tuples
    """
    bbmas_path = os.path.join(
        IEEE_DATASETS_PATH,
        "SU-AIS BB-MAS (Syracuse University and Assured Information Security - Behavioral Biometrics Multi-device and multi-Activity data from Same users) Dataset(high priority)",
        "BB-MAS_Dataset",
        "Keystroke_Features"
    )
    
    training_samples = []
    
    if not os.path.exists(bbmas_path):
        logger.warning(f"BB-MAS path not found: {bbmas_path}")
        return training_samples
    
    # Get list of CSV files (use Desktop Keyhold files for consistency)
    csv_files = [f for f in os.listdir(bbmas_path) if f.endswith("_Keyhold_Desktop.csv")]
    csv_files = csv_files[:max_users]  # Limit for training
    
    for csv_file in csv_files:
        try:
            user_id = csv_file.split("_")[0]
            filepath = os.path.join(bbmas_path, csv_file)
            
            # Parse keyhold data
            keyholds = []
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        keyhold = float(row.get('keyhold', 0))
                        keyholds.append(keyhold)
                    except (ValueError, TypeError):
                        continue
            
            if len(keyholds) < 10:
                continue
            
            # Calculate keystroke features
            keyholds_arr = np.array(keyholds)
            
            features = {
                "session_id": f"bbmas_{user_id}",
                "keystroke": {
                    "mean_inter_key_delay": float(np.mean(keyholds_arr)),
                    "std_inter_key_delay": float(np.std(keyholds_arr)),
                    "typing_speed_wpm": float(60000 / max(np.mean(keyholds_arr), 1) * 5 / 60),  # Rough WPM
                    "total_chars_typed": len(keyholds),
                },
                "hesitation": {
                    "long_pause_count": int(np.sum(keyholds_arr > 500)),
                    "tab_switch_count": 0,  # Not applicable
                },
                "paste": {
                    "paste_count": 0,  # Normal typing, no paste
                    "total_paste_length": 0,
                    "paste_after_blur_count": 0,
                },
                "focus": {
                    "blur_count": 0,  # Controlled environment
                    "total_absence_time": 0,
                    "max_absence_duration": 0,
                },
                "typing_score": 0.1,  # Low risk - normal typing
                "hesitation_score": 0.05,
                "paste_score": 0.0,  # No paste
                "focus_score": 0.0,
                "text_score": 0.0,
            }
            
            # Label 0 = clean/normal behavior
            training_samples.append((features, 0))
            
        except Exception as e:
            logger.warning(f"Error processing {csv_file}: {e}")
            continue
    
    logger.info(f"Loaded {len(training_samples)} samples from BB-MAS")
    return training_samples


def load_exam_behavior_data(max_scenarios: int = 60) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load exam behavior scenarios from project datasets.
    
    These are labeled cheating scenarios.
    
    Returns:
        List of (features_dict, label) tuples
    """
    exam_path = os.path.join(PROJECT_DATASETS_PATH, "exam_behavior", "cheating_scenarios")
    training_samples = []
    
    if not os.path.exists(exam_path):
        logger.warning(f"Exam behavior path not found: {exam_path}")
        return training_samples
    
    # List scenario folders
    scenarios = [d for d in os.listdir(exam_path) if d.startswith("Scenario")]
    scenarios = scenarios[:max_scenarios]
    
    for scenario in scenarios:
        scenario_path = os.path.join(exam_path, scenario)
        
        # Look for session files (json or csv)
        for filename in os.listdir(scenario_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(scenario_path, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Extract features from scenario data
                    features = convert_scenario_to_features(data, scenario)
                    
                    # Label 1 = cheating scenario
                    training_samples.append((features, 1))
                    
                except Exception as e:
                    logger.warning(f"Error processing {filename}: {e}")
                    continue
    
    logger.info(f"Loaded {len(training_samples)} samples from exam behavior")
    return training_samples


def convert_scenario_to_features(data: Dict[str, Any], scenario_name: str) -> Dict[str, Any]:
    """Convert scenario data to feature format."""
    
    # Default features for cheating scenario
    features = {
        "session_id": f"scenario_{scenario_name}",
        "keystroke": {
            "mean_inter_key_delay": data.get("mean_delay", 200),
            "std_inter_key_delay": data.get("std_delay", 150),
            "typing_speed_wpm": data.get("wpm", 40),
            "total_chars_typed": data.get("chars_typed", 50),
        },
        "hesitation": {
            "long_pause_count": data.get("long_pauses", 5),
            "tab_switch_count": data.get("tab_switches", 8),
        },
        "paste": {
            "paste_count": data.get("paste_count", 5),
            "total_paste_length": data.get("paste_length", 300),
            "paste_after_blur_count": data.get("paste_after_blur", 3),
        },
        "focus": {
            "blur_count": data.get("blur_count", 10),
            "total_absence_time": data.get("absence_time", 60000),
            "max_absence_duration": data.get("max_absence", 20000),
        },
        # Higher scores for cheating scenarios
        "typing_score": data.get("typing_score", 0.3),
        "hesitation_score": data.get("hesitation_score", 0.5),
        "paste_score": data.get("paste_score", 0.7),
        "focus_score": data.get("focus_score", 0.6),
        "text_score": data.get("text_score", 0.2),
    }
    
    return features


def generate_synthetic_cheating() -> List[Tuple[Dict[str, Any], int]]:
    """
    Generate synthetic cheating sessions to augment training data.
    
    Returns:
        List of (features_dict, label=1) tuples
    """
    samples = []
    
    for i in range(300):
        # High paste activity
        paste_count = random.randint(3, 15)
        paste_length = random.randint(100, 800)
        
        # High blur activity  
        blur_count = random.randint(5, 20)
        absence_time = random.randint(30000, 180000)
        
        # Less typing
        chars_typed = random.randint(30, 150)
        
        features = {
            "session_id": f"synth_cheat_{i}",
            "keystroke": {
                "mean_inter_key_delay": random.uniform(200, 500),
                "std_inter_key_delay": random.uniform(150, 400),
                "typing_speed_wpm": random.uniform(20, 50),
                "total_chars_typed": chars_typed,
            },
            "hesitation": {
                "long_pause_count": random.randint(5, 15),
                "tab_switch_count": blur_count,
            },
            "paste": {
                "paste_count": paste_count,
                "total_paste_length": paste_length,
                "paste_after_blur_count": random.randint(1, paste_count),
            },
            "focus": {
                "blur_count": blur_count,
                "total_absence_time": absence_time,
                "max_absence_duration": random.randint(5000, 30000),
            },
            "typing_score": random.uniform(0.3, 0.7),
            "hesitation_score": random.uniform(0.5, 0.9),
            "paste_score": random.uniform(0.6, 0.95),
            "focus_score": random.uniform(0.5, 0.85),
            "text_score": random.uniform(0.1, 0.4),
        }
        
        samples.append((features, 1))
    
    return samples


def generate_synthetic_clean() -> List[Tuple[Dict[str, Any], int]]:
    """
    Generate synthetic clean/honest sessions to augment training data.
    
    Returns:
        List of (features_dict, label=0) tuples
    """
    samples = []
    
    for i in range(300):
        # Low paste activity
        paste_count = random.randint(0, 2)
        
        # Low blur activity
        blur_count = random.randint(0, 3)
        
        # Normal typing
        chars_typed = random.randint(200, 600)
        
        features = {
            "session_id": f"synth_clean_{i}",
            "keystroke": {
                "mean_inter_key_delay": random.uniform(80, 180),
                "std_inter_key_delay": random.uniform(30, 80),
                "typing_speed_wpm": random.uniform(40, 90),
                "total_chars_typed": chars_typed,
            },
            "hesitation": {
                "long_pause_count": random.randint(0, 3),
                "tab_switch_count": blur_count,
            },
            "paste": {
                "paste_count": paste_count,
                "total_paste_length": random.randint(0, 50),
                "paste_after_blur_count": 0,
            },
            "focus": {
                "blur_count": blur_count,
                "total_absence_time": random.randint(0, 5000),
                "max_absence_duration": random.randint(0, 3000),
            },
            "typing_score": random.uniform(0.0, 0.2),
            "hesitation_score": random.uniform(0.0, 0.2),
            "paste_score": random.uniform(0.0, 0.15),
            "focus_score": random.uniform(0.0, 0.15),
            "text_score": random.uniform(0.0, 0.1),
        }
        
        samples.append((features, 0))
    
    return samples


def load_all_training_data() -> List[Tuple[Dict[str, Any], int]]:
    """
    Load training data from all available sources.
    
    Sources:
    1. BB-MAS Keystroke (clean behavior baseline)
    2. Exam Behavior Scenarios (cheating examples)
    3. Synthetic augmentation (both clean and cheating)
    
    Returns:
        Combined list of (features_dict, label) tuples
    """
    all_data = []
    
    # Load real datasets
    logger.info("Loading BB-MAS keystroke data...")
    bbmas_data = load_bbmas_keystroke_features(max_users=50)
    all_data.extend(bbmas_data)
    
    logger.info("Loading exam behavior scenarios...")
    exam_data = load_exam_behavior_data(max_scenarios=60)
    all_data.extend(exam_data)
    
    # Add synthetic data for balance
    logger.info("Generating synthetic training data...")
    
    # Calculate balance
    real_clean = sum(1 for _, label in all_data if label == 0)
    real_cheat = sum(1 for _, label in all_data if label == 1)
    
    logger.info(f"Real data: {real_clean} clean, {real_cheat} cheating")
    
    # Generate synthetic to reach target
    target_each = 500
    
    if real_clean < target_each:
        synth_clean = generate_synthetic_clean()
        all_data.extend(synth_clean[:target_each - real_clean])
    
    if real_cheat < target_each:
        synth_cheat = generate_synthetic_cheating()
        all_data.extend(synth_cheat[:target_each - real_cheat])
    
    # Shuffle
    random.shuffle(all_data)
    
    final_clean = sum(1 for _, label in all_data if label == 0)
    final_cheat = sum(1 for _, label in all_data if label == 1)
    
    logger.info(f"Total training data: {len(all_data)} samples ({final_clean} clean, {final_cheat} cheating)")
    
    return all_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Load all data
    data = load_all_training_data()
    print(f"\nLoaded {len(data)} total samples")
    
    # Show sample
    if data:
        sample, label = data[0]
        print(f"\nSample (label={label}):")
        print(f"  Session: {sample.get('session_id')}")
        print(f"  Paste score: {sample.get('paste_score')}")
        print(f"  Focus score: {sample.get('focus_score')}")
