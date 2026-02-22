"""
IEEE and Project Dataset Loaders

This module implements data loaders for:
1. Student Suspicion Behavior (Project Local) - Critical
2. Authcode Multi-Device Authentication (IEEE) - High Priority
3. Ensemble Keystroke Dynamics (IEEE) - High Priority
4. Other additional datasets as needed.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import glob
import logging

logger = logging.getLogger(__name__)

# Base Paths — configurable via environment variables
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IEEE_DATASETS_PATH = os.environ.get("IEEE_DATASETS_PATH", os.path.join(_BACKEND_DIR, "data", "datasets"))
PROJECT_DATASETS_PATH = os.environ.get("PROJECT_DATASETS_PATH", os.path.join(_BACKEND_DIR, "data", "datasets"))

def load_student_suspicion_data(max_rows: Optional[int] = None) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load the Student Suspicion Behaviors dataset (Project Local).
    
    Path: exam_behavior/student_suspicion/Students suspicious behaviors detection dataset_V1.csv
    Content: Video-derived features (face, gaze, hands, phone)
    Labels: 0 (Normal), 1 (Suspicious)
    
    Returns:
        List of (features_dict, label) tuples.
    """
    file_path = os.path.join(PROJECT_DATASETS_PATH, "exam_behavior", "student_suspicion", 
                             "Students suspicious behaviors detection dataset_V1.csv")
    
    if not os.path.exists(file_path):
        logger.error(f"Student Suspicion dataset not found at {file_path}")
        return []

    try:
        logger.info(f"Loading Student Suspicion dataset from {file_path}")
        df = pd.read_csv(file_path)
        
        if max_rows:
            df = df.head(max_rows)
            
        data = []
        for _, row in df.iterrows():
            # Extract features (all columns except label)
            features = row.drop("label").to_dict()
            label = int(row["label"])
            data.append((features, label))
            
        logger.info(f"Loaded {len(data)} samples from Student Suspicion dataset")
        return data
        
    except Exception as e:
        logger.error(f"Error loading Student Suspicion dataset: {str(e)}")
        return []

def load_authcode_data(dataset_num: int = 1, max_rows: Optional[int] = 10000) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Authcode Multi-Device Authentication dataset (IEEE).
    
    Content: Rich PC behavioral features (keystroke, mouse, app usage, network).
    Dimensions: 5 datasets (Dataset1-5), huge files (~2GB each).
    Labels: 'USER' column (0-11). We treat this as a multi-class anomaly detection 
            or simplify to (clean behavior) if using one-class SVM.
            For Cheating Detection, we'll treat all as 'clean' baseline samples (label=0).
            
    Args:
        dataset_num: 1 to 5 (Corresponds to Dataset1, Dataset2, etc.)
        max_rows: Limit rows to load due to file size (default 10000)
    
    Returns:
        List of (features_dict, label=0) tuples.
    """
    # Fix dataset folder naming convention based on actual structure
    # Structure: Authcode/datasets_multidevice_auth/Dataset1/dataset1.csv
    dataset_folder = f"Dataset{dataset_num}"
    filename = f"dataset{dataset_num}.csv"
    
    file_path = os.path.join(IEEE_DATASETS_PATH, "Authcode", "datasets_multidevice_auth", 
                             dataset_folder, filename)
                             
    if not os.path.exists(file_path):
        logger.error(f"Authcode dataset {dataset_num} not found at {file_path}")
        return []

    try:
        logger.info(f"Loading Authcode dataset {dataset_num} from {file_path}")
        # Using a chunks because these files are huge (~2GB)
        chunk_size = max_rows if max_rows else 10000
        
        # Read just the first chunk to get the data
        # Fix encoding issue (utf-8 error reported)
        df_iterator = pd.read_csv(file_path, chunksize=chunk_size, encoding='latin-1', on_bad_lines='skip')
        df = next(df_iterator)
        
        data = []
        for _, row in df.iterrows():
            features = row.drop("USER").to_dict() # USER is the subject ID
            # In context of cheating detection, reference data is label 0 (clean)
            data.append((features, 0))
            
        logger.info(f"Loaded {len(data)} samples from Authcode dataset {dataset_num}")
        return data

    except Exception as e:
        logger.error(f"Error loading Authcode dataset: {str(e)}")
        return []

def load_ensemble_keystroke_data(label_type: str = "legitimate", max_rows: Optional[int] = None) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Ensemble Method Keystroke Dynamics dataset (IEEE).
    
    Content: Word-level keystroke timing scores.
    Files: RESULTS_WORDS_LEGITIMATE.csv, RESULTS_WORDS_IMPOSTORS.csv
    Labels: 
        - Legitimate -> 0 (Clean)
        - Impostor -> 1 (Cheating/Anomaly)
        
    Args:
        label_type: 'legitimate' or 'impostor' (or 'both' to handle externally)
    
    Returns:
        List of (features_dict, label) tuples.
    """
    folder_path = os.path.join(IEEE_DATASETS_PATH, 
                              "Dataset for An Ensemble Method for Keystroke Dynamics Authentication in Free-Text Using Word Boundaries(low priority)")
    
    # Handle pluralization in filename (IMPOSTORS vs LEGITIMATE)
    suffix = "IMPOSTORS" if "impostor" in label_type.lower() else "LEGITIMATE"
    filename = f"RESULTS_WORDS_{suffix}.csv"
    file_path = os.path.join(folder_path, filename)
    
    if not os.path.exists(file_path):
        logger.error(f"Ensemble Keystroke file not found: {file_path}")
        return []
        
    try:
        logger.info(f"Loading Ensemble Keystroke ({label_type}) from {file_path}")
        # Analysis showed header: user_id, session_id, word, score, label_text
        # But actually file has no header, just columns. 
        # Based on view_file: 2085887,2780617,DIA,74.18,legitimate
        column_names = ["user_id", "session_id", "word", "score", "label_text"]
        
        df = pd.read_csv(file_path, names=column_names)
        
        if max_rows:
            df = df.head(max_rows)
            
        data = []
        target_label = 0 if label_type == "legitimate" else 1
        
        for _, row in df.iterrows():
            features = {
                "user_id": row["user_id"],
                "word": row["word"],
                "score": row["score"]
            }
            data.append((features, target_label))
            
        logger.info(f"Loaded {len(data)} samples from Ensemble Keystroke ({label_type})")
        return data
        
    except Exception as e:
        logger.error(f"Error loading Ensemble Keystroke dataset: {str(e)}")
        return []

def load_tchad100_data(max_users: int = 50) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load TCHAD-100 Keystroke Dynamics Dataset (IEEE).
    
    Path: TCHAD-100 .../TCHAD-100/samples.csv
    Content: User demographics and phrase data.
    Note: Can be enriched with dwell_times.json and flight_times.json if needed.
    
    Returns:
        List of (features_dict, label=0) tuples.
    """
    base_folder = os.path.join(IEEE_DATASETS_PATH, 
                              "TCHAD-100 A Cross-Cultural Keystroke Dynamics Dataset from 100 Chadian Participants(low priority)",
                              "TCHAD-100")
    file_path = os.path.join(base_folder, "samples.csv")
    
    if not os.path.exists(file_path):
        logger.error(f"TCHAD-100 samples file not found: {file_path}")
        return []
        
    try:
        logger.info(f"Loading TCHAD-100 samples from {file_path}")
        df = pd.read_csv(file_path)
        
        # Determine unique users to limit simple loading
        unique_users = df['user_hash'].unique()
        if max_users:
            selected_users = unique_users[:max_users]
            df = df[df['user_hash'].isin(selected_users)]
            
        data = []
        for _, row in df.iterrows():
            features = row.to_dict()
            data.append((features, 0)) # Treat as clean baseline
            
        logger.info(f"Loaded {len(data)} samples from TCHAD-100")
        return data
        
    except Exception as e:
        logger.error(f"Error loading TCHAD-100 dataset: {str(e)}")
        return []

def load_ikdd_data(max_files: int = 50) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load IKDD (Indonesian Keystroke Dynamics Dataset) (Project Local).
    
    Path: keystroke/ikdd/IKDD/*.txt
    Content: Custom text format with aggregated timing features.
    Format:
        Line 1: Metadata
        Line 2+: FeatureID, Val1, Val2, ...
    
    Returns:
        List of (features_dict, label=0) tuples.
    """
    folder_path = os.path.join(PROJECT_DATASETS_PATH, "keystroke", "ikdd", "IKDD")
    
    if not os.path.exists(folder_path):
        logger.error(f"IKDD folder not found: {folder_path}")
        return []
        
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if max_files:
        txt_files = txt_files[:max_files]
        
    data = []
    
    try:
        for file_path in txt_files:
            features = {}
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if not lines:
                continue
                
            # Line 1: Metadata (e.g., user001_(1),Male,18-25...)
            meta_parts = lines[0].strip().split(',')
            if len(meta_parts) >= 1:
                features["user_id"] = meta_parts[0]
                features["gender"] = meta_parts[1] if len(meta_parts) > 1 else "Unknown"
                
            # Remaining lines: FeatureID, Val1, Val2...
            # We will aggregate these values (mean) to create a flat feature vector
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) < 2:
                    continue
                    
                feat_id = parts[0] # e.g. "8-0" or "69-82"
                # Parse numeric values
                try:
                    values = [float(v) for v in parts[1:] if v.replace('.','',1).isdigit()]
                    if values:
                        features[f"mean_{feat_id}"] = np.mean(values)
                        features[f"std_{feat_id}"] = np.std(values)
                except ValueError:
                    continue
            
            data.append((features, 0)) # Treat as clean
            
        logger.info(f"Loaded {len(data)} sessions from IKDD")
        return data
        
    except Exception as e:
        logger.error(f"Error loading IKDD dataset: {str(e)}")
        return []

def load_liveness_detection_data() -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Liveness Detection Dataset (IEEE).
    
    Path: Dataset for Towards Liveness Detection.../CFS/*.csv
    Content: Feature selection results (CFS) for forgery detection.
    
    Returns:
        List of (features_dict, label) tuples.
    """
    base_folder = os.path.join(IEEE_DATASETS_PATH, 
                              "Dataset for Towards Liveness Detection  of Keystroke Dynamics Using Feature Selection(low priority)")
    # Path correction: No CFS folder, check training_files
    cfs_folder = os.path.join(base_folder, "training_files")
    
    if not os.path.exists(cfs_folder):
        logger.error(f"Liveness Detection CFS folder not found: {cfs_folder}")
        return []
        
    # Try reading the labels file first to get filenames
    labels_file = os.path.join(base_folder, "public_labels.csv")
    
    if os.path.exists(labels_file):
        try:
            df = pd.read_csv(labels_file)
            # Assuming columns like filename, label
            # Just return the label info as "features" for now to verify connectivity
            data = []
            if max_rows:
                df = df.head(max_rows)
                
            for _, row in df.iterrows():
                data.append((row.to_dict(), 0))
            
            logger.info(f"Loaded {len(data)} samples from Liveness Detection labels")
            return data
        except Exception:
            pass

    # Fallback to listing files if labels not usable
    csv_files = glob.glob(os.path.join(cfs_folder, "*.csv"))
    if not csv_files:
         # Maybe txt files?
         csv_files = glob.glob(os.path.join(cfs_folder, "*.txt"))
         
    data = []
    
    try:
        for file_path in csv_files:
            # Filename might indicate source type but treating all as samples
            # If txt, might be specific format, but trying generic read
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    features = row.to_dict()
                    data.append((features, 0))
            except Exception:
                continue
                
        logger.info(f"Loaded {len(data)} samples from Liveness Detection dataset")
        return data
        
    except Exception as e:
        logger.error(f"Error loading Liveness Detection dataset: {str(e)}")
        return []

def load_balabit_mouse_data(split: str = "training", max_users: int = 5) -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Balabit Mouse Challenge Dataset (Project Local).
    
    Path: mouse_dynamics/challenge/
    Content: Session CSVs (time, button, state, x, y).
    
    Args:
        split: "training" or "test"
        
    Returns:
        List of (features_dict, label) tuples.
        For training: label=0 (Legal Owner).
    """
    base_folder = os.path.join(PROJECT_DATASETS_PATH, "mouse_dynamics", "challenge", f"{split}_files")
    
    if not os.path.exists(base_folder):
        logger.error(f"Balabit folder not found: {base_folder}")
        return []
        
    user_folders = glob.glob(os.path.join(base_folder, "user*"))
    if max_users:
        user_folders = user_folders[:max_users]
        
    data = []
    
    try:
        for user_folder in user_folders:
            user_id = os.path.basename(user_folder)
            # Files have no extension (e.g. session_12345)
            session_files = glob.glob(os.path.join(user_folder, "session*"))
            
            for sess_file in session_files:
                df = pd.read_csv(sess_file)
                # Aggregate features for the session
                # Simple aggregation for now
                features = {
                    "user_id": user_id,
                    "session_id": os.path.basename(sess_file),
                    "duration": df.iloc[-1, 0] if not df.empty else 0,
                    "mean_x": df.iloc[:, 4].mean() if not df.empty else 0,
                    "mean_y": df.iloc[:, 5].mean() if not df.empty else 0
                }
                data.append((features, 0)) # Training data is all 'legal' (0)
                
        logger.info(f"Loaded {len(data)} sessions from Balabit ({split})")
        return data
        
    except Exception as e:
        logger.error(f"Error loading Balabit dataset: {str(e)}")
        return []

def load_pan11_plagiarism_data(subcorpus: str = "external-detection-corpus") -> List[Tuple[Dict[str, Any], int]]:
    """
    Load PAN-11 Plagiarism Corpus (Project Local).
    
    Path: plagiarism/pan_11/
    
    Returns:
        List of (features, label=1) for suspicious docs.
    """
    base_folder = os.path.join(PROJECT_DATASETS_PATH, "plagiarism", "pan_11", subcorpus, "suspicious-document")
    
    # Check if nested part1 directory exists (valid for external structure)
    if not os.path.exists(base_folder):
         # Try intrinsic path which is direct
         base_folder = os.path.join(PROJECT_DATASETS_PATH, "plagiarism", "pan_11", "intrinsic-detection-corpus", "suspicious-document")
    
    if not os.path.exists(base_folder):
        # Fallback to recursively finding 'suspicious-documents'
        found = glob.glob(os.path.join(PROJECT_DATASETS_PATH, "plagiarism", "pan_11", "**", "suspicious-document"), recursive=True)
        if found:
            base_folder = found[0]
        else:
            logger.error(f"PAN-11 suspicious-documents not found")
            return []

    # Look for .txt files
    # Note: real corpus uses part1, part2 subfolders
    txt_files = glob.glob(os.path.join(base_folder, "**", "*.txt"), recursive=True)
    
    # Limit for demo
    if len(txt_files) > 20: 
        txt_files = txt_files[:20]
        
    data = []
    for txt_path in txt_files:
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            features = {
                "filename": os.path.basename(txt_path),
                "content_length": len(content),
                "preview": content[:100]
            }
            data.append((features, 1)) # Suspicious documents
        except Exception:
            continue
            
    logger.info(f"Loaded {len(data)} documents from PAN-11")
    return data

def load_timing_distributions_data() -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Timing Distributions Dataset (IEEE).
    Path: Timing distributions in free text keystroke dynamics profile(low priority)
    """
    base_folder = os.path.join(IEEE_DATASETS_PATH, 
                              "Timing distributions in free text keystroke dynamics profile(low priority)")
    
    # This dataset likely contains ARFF or textual files. 
    # Logic similar to generic loader.
    # Returning empty list placeholder until specific file format (ARFF content) is needed.
    # Analysis showed 'free_text' folder.
    
    return []

def load_mouse_to_image_data() -> List[Tuple[Dict[str, Any], int]]:
    """
    Load Mouse Dynamics to Image Dataset (IEEE).
    Returns paths to images.
    """
    base_folder = os.path.join(IEEE_DATASETS_PATH, "Mouse Dynamics_to_Image", "Dataset")
    
    if not os.path.exists(base_folder):
        return []
        
    # Walk and find images
    data = []
    # Just list some images as features
    # Not implementing full image loading to avoid heavy deps
    return data

if __name__ == "__main__":
    # simple test
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Student Suspicion Loader...")
    suspicion_data = load_student_suspicion_data(max_rows=5)
    if suspicion_data:
        print(f"Sample features: {list(suspicion_data[0][0].keys())[:5]}...")
        
    print("\nTesting Authcode Loader...")
    auth_data = load_authcode_data(dataset_num=1, max_rows=5)
    if auth_data:
        print(f"Sample features: {list(auth_data[0][0].keys())[:5]}...")
        
    print("\nTesting Ensemble Keystroke Loader...")
    ensemble_data = load_ensemble_keystroke_data(label_type="impostor", max_rows=5)
    if ensemble_data:
        print(f"Sample: {ensemble_data[0]}")

    print("\nTesting TCHAD-100 Loader...")
    tchad_data = load_tchad100_data(max_users=2)
    if tchad_data:
        print(f"Sample: {tchad_data[0]}")

    print("\nTesting IKDD Loader...")
    ikdd_data = load_ikdd_data(max_files=2)
    if ikdd_data:
        print(f"Sample keys: {list(ikdd_data[0][0].keys())[:5]}...")

    print("\nTesting Liveness Detection Loader...")
    liveness_data = load_liveness_detection_data()
    if liveness_data:
        print(f"Sample: {liveness_data[0]}")
        
    print("\nTesting Balabit Loader...")
    balabit_data = load_balabit_mouse_data(max_users=1)
    if balabit_data:
        print(f"Sample: {balabit_data[0]}")
        
    print("\nTesting PAN-11 Loader...")
    pan11_data = load_pan11_plagiarism_data()
    if pan11_data:
        print(f"Sample: {pan11_data[0]}")

