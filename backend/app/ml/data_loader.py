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
import sys

# Ensure backend module is found
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ml.ieee_loaders import (
    load_student_suspicion_data,
    load_authcode_data,
    load_ensemble_keystroke_data,
    load_tchad100_data,
    load_ikdd_data,
    load_liveness_detection_data,
    load_balabit_mouse_data,
    load_pan11_plagiarism_data
)

logger = logging.getLogger(__name__)


# Dataset paths — configurable via environment variables
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IEEE_DATASETS_PATH = os.environ.get("IEEE_DATASETS_PATH", os.path.join(_BACKEND_DIR, "data", "datasets"))
PROJECT_DATASETS_PATH = os.environ.get("PROJECT_DATASETS_PATH", os.path.join(_BACKEND_DIR, "data", "datasets"))


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


def load_emosurv_keystroke_data(max_rows: int = 5000) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load EmoSurv keystroke dynamics dataset.
    
    Contains typing data with timing intervals and emotion labels.
    All samples treated as clean (normal typing under different emotions).
    
    Returns:
        List of (features_dict, label) tuples
    """
    emosurv_path = os.path.join(
        IEEE_DATASETS_PATH,
        "EmoSurv A typing biometric (Keystroke dynamics) dataset with emotion labels created using computer keyboards(medium priotity)"
    )
    
    training_samples = []
    csv_files = ["Fixed Text Typing Dataset.csv", "Free Text Typing Dataset.csv"]
    
    for csv_file in csv_files:
        filepath = os.path.join(emosurv_path, csv_file)
        if not os.path.exists(filepath):
            continue
        
        try:
            user_sessions = {}  # Group by userId
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                row_count = 0
                
                for row in reader:
                    if row_count >= max_rows:
                        break
                    
                    try:
                        user_id = row.get('userId', '0')
                        # D1U1: key hold time (press to release same key)
                        d1u1 = float(row.get('D1U1', 0).replace(',', '.'))
                        # D1D2: key-to-key interval (press to press)
                        d1d2_str = row.get('D1D2', '0')
                        if d1d2_str and d1d2_str.strip():
                            d1d2 = float(d1d2_str.replace(',', '.'))
                        else:
                            d1d2 = 0
                        
                        if user_id not in user_sessions:
                            user_sessions[user_id] = {'holds': [], 'intervals': []}
                        
                        user_sessions[user_id]['holds'].append(d1u1)
                        if d1d2 > 0 and d1d2 < 5000:  # Filter outliers
                            user_sessions[user_id]['intervals'].append(d1d2)
                        
                        row_count += 1
                    except (ValueError, TypeError):
                        continue
            
            # Create features per user
            for user_id, data in user_sessions.items():
                if len(data['holds']) < 20:
                    continue
                
                holds = np.array(data['holds'])
                intervals = np.array(data['intervals']) if data['intervals'] else np.array([100])
                
                features = {
                    "session_id": f"emosurv_{user_id}_{csv_file[:4]}",
                    "keystroke": {
                        "mean_inter_key_delay": float(np.mean(intervals)),
                        "std_inter_key_delay": float(np.std(intervals)),
                        "typing_speed_wpm": float(60000 / max(np.mean(intervals), 1) / 5),
                        "total_chars_typed": len(holds),
                        "key_hold_mean": float(np.mean(holds)),
                        "key_hold_std": float(np.std(holds)),
                    },
                    "hesitation": {
                        "long_pause_count": int(np.sum(intervals > 1000)),
                        "tab_switch_count": 0,
                    },
                    "paste": {"paste_count": 0, "total_paste_length": 0, "paste_after_blur_count": 0},
                    "focus": {"blur_count": 0, "total_absence_time": 0, "max_absence_duration": 0},
                    "typing_score": 0.1,
                    "hesitation_score": 0.05,
                    "paste_score": 0.0,
                    "focus_score": 0.0,
                    "text_score": 0.0,
                }
                
                training_samples.append((features, 0))  # Clean label
                
        except Exception as e:
            logger.warning(f"Error loading EmoSurv {csv_file}: {e}")
    
    logger.info(f"Loaded {len(training_samples)} samples from EmoSurv")
    return training_samples


def load_keystroke_reverse_problem_data(max_files: int = 100) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Keystroke Reverse Problem dataset (ARFF format).
    
    Contains typing features with legitimate/impostor labels.
    This provides direct cheating detection signals!
    
    Returns:
        List of (features_dict, label) tuples where impostor=1
    """
    base_path = os.path.join(
        IEEE_DATASETS_PATH,
        "Dataset for The Reverse Problem of Keystroke Dynamics Guessing Typed Text with Keystroke Timings(high priority)"
    )
    
    training_samples = []
    
    # Check both subject folders
    for folder in ["BetweenSubject", "WithinSubject"]:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            continue
        
        # Get subfolders (FT, etc.)
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            
            arff_files = [f for f in os.listdir(subfolder_path) if f.endswith('.arff')][:max_files]
            
            for arff_file in arff_files:
                try:
                    filepath = os.path.join(subfolder_path, arff_file)
                    
                    # Parse ARFF file
                    with open(filepath, 'r') as f:
                        in_data = False
                        for line in f:
                            line = line.strip()
                            if line.upper() == '@DATA':
                                in_data = True
                                continue
                            if not in_data or not line or line.startswith('%'):
                                continue
                            
                            parts = line.split(',')
                            if len(parts) < 5:
                                continue
                            
                            try:
                                ft_dm = float(parts[0])
                                ft_de = float(parts[1])
                                ft_rmix = float(parts[2])
                                ft_dil = float(parts[3])
                                label_str = parts[4].strip().lower()
                                
                                # Map label
                                label = 1 if label_str == 'impostor' else 0
                                
                                features = {
                                    "session_id": f"reverse_{arff_file}_{len(training_samples)}",
                                    "keystroke": {
                                        "mean_inter_key_delay": ft_dm * 1000,  # Convert to ms
                                        "std_inter_key_delay": ft_de * 1000,
                                        "typing_speed_wpm": 60000 / max(ft_dm * 1000, 1) / 5,
                                        "total_chars_typed": 100,
                                        "ft_rmix": ft_rmix,
                                        "ft_dil": ft_dil,
                                    },
                                    "hesitation": {
                                        "long_pause_count": int(ft_dil * 10),
                                        "tab_switch_count": 0,
                                    },
                                    "paste": {"paste_count": 0, "total_paste_length": 0, "paste_after_blur_count": 0},
                                    "focus": {"blur_count": 0, "total_absence_time": 0, "max_absence_duration": 0},
                                    "typing_score": 0.1 if label == 0 else 0.5,
                                    "hesitation_score": 0.05 if label == 0 else 0.4,
                                    "paste_score": 0.0,
                                    "focus_score": 0.0,
                                    "text_score": 0.0,
                                }
                                
                                training_samples.append((features, label))
                                
                            except (ValueError, IndexError):
                                continue
                                
                except Exception as e:
                    logger.debug(f"Error parsing {arff_file}: {e}")
                    continue
    
    logger.info(f"Loaded {len(training_samples)} samples from Keystroke Reverse Problem")
    return training_samples


def load_remouse_data(max_sessions: int = 50) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load ReMouse mouse dynamics dataset.
    
    Contains mouse movement and click patterns.
    All treated as clean (normal mouse behavior).
    
    Returns:
        List of (features_dict, label) tuples
    """
    remouse_path = os.path.join(
        IEEE_DATASETS_PATH,
        "ReMouse - Mouse Dynamic Dataset",
        "ReMouse Dataset-ShadiSadeghpour"
    )
    
    training_samples = []
    
    if not os.path.exists(remouse_path):
        logger.warning(f"ReMouse path not found: {remouse_path}")
        return training_samples
    
    csv_files = [f for f in os.listdir(remouse_path) if f.endswith('.csv')][:max_sessions]
    
    for csv_file in csv_files:
        try:
            filepath = os.path.join(remouse_path, csv_file)
            
            speeds = []
            clicks = 0
            drags = 0
            movements = 0
            
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event_type = row.get('Event Type', '')
                    speed_str = row.get('Speed', '0px/s')
                    
                    # Parse speed
                    try:
                        speed = float(speed_str.replace('px/s', ''))
                        if speed > 0:
                            speeds.append(speed)
                    except ValueError:
                        pass
                    
                    # Count events
                    if 'click' in event_type.lower() or 'mouseup' in event_type.lower():
                        clicks += 1
                    elif 'drag' in event_type.lower():
                        drags += 1
                    elif 'move' in event_type.lower():
                        movements += 1
            
            if len(speeds) < 10:
                continue
            
            speeds_arr = np.array(speeds)
            
            features = {
                "session_id": f"remouse_{csv_file}",
                "keystroke": {
                    "mean_inter_key_delay": 150,  # Default for mouse session
                    "std_inter_key_delay": 50,
                    "typing_speed_wpm": 50,
                    "total_chars_typed": 100,
                },
                "hesitation": {
                    "long_pause_count": 0,
                    "tab_switch_count": 0,
                },
                "paste": {"paste_count": 0, "total_paste_length": 0, "paste_after_blur_count": 0},
                "focus": {"blur_count": 0, "total_absence_time": 0, "max_absence_duration": 0},
                "mouse": {
                    "avg_speed": float(np.mean(speeds_arr)),
                    "std_speed": float(np.std(speeds_arr)),
                    "click_count": clicks,
                    "drag_count": drags,
                    "movement_count": movements,
                },
                "typing_score": 0.1,
                "hesitation_score": 0.05,
                "paste_score": 0.0,
                "focus_score": 0.0,
                "text_score": 0.0,
            }
            
            training_samples.append((features, 0))  # Clean label
            
        except Exception as e:
            logger.warning(f"Error loading ReMouse {csv_file}: {e}")
    
    logger.info(f"Loaded {len(training_samples)} samples from ReMouse")
    return training_samples


def load_behacom_data(max_users: int = 2) -> List[Tuple[Dict[str, Any], int]]:
    logger.warning("Skipping Behacom data due to loading issues.")
    return []

    """
    Load Behacom computer user behavior dataset.
    
    Contains pre-computed keystroke and mouse features from 12 users.
    All treated as clean (legitimate authenticated users).
    
    Returns:
        List of (features_dict, label) tuples
    """
    behacom_path = os.path.join(
        IEEE_DATASETS_PATH,
        "Behacom",
        "Behacom"
    )
    
    training_samples = []
    
    if not os.path.exists(behacom_path):
        logger.warning(f"Behacom path not found: {behacom_path}")
        return training_samples
    
    # Each user has a folder
    user_folders = [d for d in os.listdir(behacom_path) if d.startswith('User')][:max_users]
    
    for user_folder in user_folders:
        user_path = os.path.join(behacom_path, user_folder)
        if not os.path.isdir(user_path):
            continue
        
        csv_files = [f for f in os.listdir(user_path) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            try:
                filepath = os.path.join(user_path, csv_file)
                
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            # Extract key features from Behacom format
                            keystroke_count = int(row.get('keystroke_counter', 0) or 0)
                            if keystroke_count < 5:
                                continue
                            
                            pp_avg = float(row.get('press_press_average_interval', 150) or 150)
                            pp_std = float(row.get('press_press_stddev_interval', 50) or 50)
                            erase_pct = float(row.get('erase_keys_percentage', 0) or 0)
                            word_count = int(row.get('word_counter', 0) or 0)
                            
                            features = {
                                "session_id": f"behacom_{user_folder}_{len(training_samples)}",
                                "keystroke": {
                                    "mean_inter_key_delay": pp_avg,
                                    "std_inter_key_delay": pp_std,
                                    "typing_speed_wpm": 60000 / max(pp_avg, 1) / 5,
                                    "total_chars_typed": keystroke_count,
                                    "erase_percentage": erase_pct,
                                    "word_count": word_count,
                                },
                                "hesitation": {
                                    "long_pause_count": int(pp_avg > 500),
                                    "tab_switch_count": 0,
                                },
                                "paste": {"paste_count": 0, "total_paste_length": 0, "paste_after_blur_count": 0},
                                "focus": {"blur_count": 0, "total_absence_time": 0, "max_absence_duration": 0},
                                "typing_score": 0.1,
                                "hesitation_score": 0.05,
                                "paste_score": 0.0,
                                "focus_score": 0.0,
                                "text_score": 0.0,
                            }
                            
                            training_samples.append((features, 0))  # Clean label
                            
                        except (ValueError, TypeError):
                            continue
                            
            except Exception as e:
                logger.warning(f"Error loading Behacom {csv_file}: {e}")
    
    logger.info(f"Loaded {len(training_samples)} samples from Behacom")
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
    2. EmoSurv Keystroke (clean, various emotions)
    3. Keystroke Reverse Problem (labeled legitimate/impostor)
    4. ReMouse (clean mouse dynamics)
    5. Behacom (clean combined features)
    6. Exam Behavior Scenarios (cheating examples)
    7. Synthetic augmentation (balance if needed)
    
    Returns:
        Combined list of (features_dict, label) tuples
    """
    all_data = []
    
    # Load real datasets - Clean baseline
    logger.info("Loading BB-MAS keystroke data...")
    bbmas_data = load_bbmas_keystroke_features(max_users=50)
    all_data.extend(bbmas_data)
    
    logger.info("Loading EmoSurv keystroke data...")
    emosurv_data = load_emosurv_keystroke_data(max_rows=5000)
    all_data.extend(emosurv_data)
    
    logger.info("Loading Keystroke Reverse Problem data...")
    reverse_data = load_keystroke_reverse_problem_data(max_files=100)
    all_data.extend(reverse_data)
    
    logger.info("Loading ReMouse data...")
    remouse_data = load_remouse_data(max_sessions=50)
    all_data.extend(remouse_data)
    
    logger.info("Loading Behacom data...")
    behacom_data = load_behacom_data(max_users=12)
    all_data.extend(behacom_data)
    
    # Load cheating examples
    logger.info("Loading exam behavior scenarios...")
    exam_data = load_exam_behavior_data(max_scenarios=60)
    all_data.extend(exam_data)

    # --- NEW DATASETS INTEGRATION ---
    
    # 1. Student Suspicion (Critical)
    logger.info("Loading Student Suspicion data...")
    suspicion_data = load_student_suspicion_data()
    all_data.extend(suspicion_data)

    # 2. Authcode (High Priority)
    logger.info("Loading Authcode data (Dataset1)...")
    auth_data = load_authcode_data(dataset_num=1, max_rows=5000)
    all_data.extend(auth_data)

    # 3. Ensemble Keystroke (High Priority)
    logger.info("Loading Ensemble Keystroke data (Legitimate)...")
    ensemble_legit = load_ensemble_keystroke_data(label_type="legitimate", max_rows=5000)
    all_data.extend(ensemble_legit)
    
    logger.info("Loading Ensemble Keystroke data (Impostor)...")
    ensemble_impostor = load_ensemble_keystroke_data(label_type="impostor", max_rows=5000)
    all_data.extend(ensemble_impostor)

    # 4. TCHAD-100 (Medium)
    logger.info("Loading TCHAD-100 data...")
    tchad_data = load_tchad100_data(max_users=20)
    all_data.extend(tchad_data)

    # 5. IKDD (Medium - Local)
    logger.info("Loading IKDD data...")
    ikdd_data = load_ikdd_data(max_files=50)
    all_data.extend(ikdd_data)

    # 6. Liveness Detection (Medium)
    logger.info("Loading Liveness Detection data...")
    liveness_data = load_liveness_detection_data()
    all_data.extend(liveness_data)

    # 7. Balabit Mouse (Local)
    logger.info("Loading Balabit Mouse data...")
    balabit_data = load_balabit_mouse_data(max_users=10)
    all_data.extend(balabit_data)

    # 8. PAN-11 Plagiarism (Local)
    logger.info("Loading PAN-11 Plagiarism data...")
    pan11_data = load_pan11_plagiarism_data()
    all_data.extend(pan11_data)
    
    # Calculate balance
    real_clean = sum(1 for _, label in all_data if label == 0)
    real_cheat = sum(1 for _, label in all_data if label == 1)
    
    logger.info(f"Real data: {real_clean} clean, {real_cheat} cheating")
    
    # Generate synthetic to balance if needed
    target_each = max(real_clean, real_cheat)  # Target: larger class size
    target_each = max(target_each, 1000)  # Minimum 1000 per class
    
    logger.info(f"Balancing dataset to {target_each} per class...")
    
    if real_clean < target_each:
        synth_clean = generate_synthetic_clean()
        # Generate more if needed
        additional_needed = target_each - real_clean
        while len(synth_clean) < additional_needed:
            synth_clean.extend(generate_synthetic_clean())
        all_data.extend(synth_clean[:additional_needed])
    
    if real_cheat < target_each:
        synth_cheat = generate_synthetic_cheating()
        additional_needed = target_each - real_cheat
        while len(synth_cheat) < additional_needed:
            synth_cheat.extend(generate_synthetic_cheating())
        all_data.extend(synth_cheat[:additional_needed])
    
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
