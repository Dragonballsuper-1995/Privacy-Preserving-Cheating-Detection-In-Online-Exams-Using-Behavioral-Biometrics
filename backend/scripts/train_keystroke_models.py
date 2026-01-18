"""
Train Keystroke Anomaly Detection Models

This script trains Isolation Forest models on real keystroke datasets
(CMU and KeyRecs) to detect anomalous typing patterns during exams.
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader.keystroke_loader import KeystrokeLoader


class KeystrokeFeatureExtractor:
    """Extract features from raw keystroke data for anomaly detection."""
    
    @staticmethod
    def extract_cmu_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from CMU keystroke dataset.
        
        CMU Dataset columns typically include:
        - subject: User identifier
        - sessionIndex: Session number
        - rep: Repetition number
        - H.period through H.Return: Hold times for each key
        - DD.period.t through DD.l.Return: Down-Down times between keys
        - UD.period.t through UD.l.Return: Up-Down times between keys
        
        Args:
            df: CMU dataset DataFrame
            
        Returns:
            Features DataFrame with one row per session
        """
        features_list = []
        
        # Group by subject and session
        for (subject, session), group in df.groupby(['subject', 'sessionIndex']):
            try:
                # Extract hold time columns (H.*)
                hold_cols = [col for col in df.columns if col.startswith('H.')]
                hold_times = group[hold_cols].values.flatten()
                hold_times = hold_times[~np.isnan(hold_times)]
                
                # Extract inter-key delay columns (DD.* and UD.*)
                dd_cols = [col for col in df.columns if col.startswith('DD.')]
                ud_cols = [col for col in df.columns if col.startswith('UD.')]
                
                dd_times = group[dd_cols].values.flatten()
                dd_times = dd_times[~np.isnan(dd_times)]
                
                ud_times = group[ud_cols].values.flatten()
                ud_times = ud_times[~np.isnan(ud_times)]
                
                # Calculate statistical features
                features = {
                    'subject': subject,
                    'session': session,
                    
                    # Hold time statistics
                    'hold_mean': np.mean(hold_times) if len(hold_times) > 0 else 0,
                    'hold_std': np.std(hold_times) if len(hold_times) > 0 else 0,
                    'hold_median': np.median(hold_times) if len(hold_times) > 0 else 0,
                    'hold_min': np.min(hold_times) if len(hold_times) > 0 else 0,
                    'hold_max': np.max(hold_times) if len(hold_times) > 0 else 0,
                    
                    # Down-Down (DD) time statistics
                    'dd_mean': np.mean(dd_times) if len(dd_times) > 0 else 0,
                    'dd_std': np.std(dd_times) if len(dd_times) > 0 else 0,
                    'dd_median': np.median(dd_times) if len(dd_times) > 0 else 0,
                    'dd_cv': np.std(dd_times) / np.mean(dd_times) if len(dd_times) > 0 and np.mean(dd_times) > 0 else 0,
                    
                    # Up-Down (UD) time statistics  
                    'ud_mean': np.mean(ud_times) if len(ud_times) > 0 else 0,
                    'ud_std': np.std(ud_times) if len(ud_times) > 0 else 0,
                    'ud_median': np.median(ud_times) if len(ud_times) > 0 else 0,
                    
                    # Typing rhythm features
                    'typing_speed': 1000 / np.mean(dd_times) if len(dd_times) > 0 and np.mean(dd_times) > 0 else 0,  # keys per second
                    'rhythm_consistency': 1 / (1 + np.std(dd_times)) if len(dd_times) > 0 else 0,
                }
                
                features_list.append(features)
                
            except Exception as e:
                print(f"Error extracting features for subject {subject}, session {session}: {e}")
                continue
        
        return pd.DataFrame(features_list)
    
    @staticmethod
    def extract_keyrecs_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from KeyRecs dataset.
        
        KeyRecs typically contains:
        - participant_id
        - session_id
        - key transition timings
        
        Args:
            df: KeyRecs dataset DataFrame
            
        Returns:
            Features DataFrame
        """
        # KeyRecs structure varies, adapt based on actual columns
        features_list = []
        
        # This is a placeholder - adjust based on actual KeyRecs structure
        if 'participant_id' in df.columns:
            group_cols = ['participant_id']
            if 'session_id' in df.columns:
                group_cols.append('session_id')
                
            for group_key, group in df.groupby(group_cols):
                # Extract numeric timing columns
                numeric_cols = group.select_dtypes(include=[np.number]).columns
                timing_data = group[numeric_cols].values.flatten()
                timing_data = timing_data[~np.isnan(timing_data)]
                
                if len(timing_data) > 0:
                    features = {
                        'participant': group_key if isinstance(group_key, str) else group_key[0],
                        'mean_timing': np.mean(timing_data),
                        'std_timing': np.std(timing_data),
                        'median_timing': np.median(timing_data),
                        'cv_timing': np.std(timing_data) / np.mean(timing_data) if np.mean(timing_data) > 0 else 0,
                    }
                    features_list.append(features)
        
        return pd.DataFrame(features_list) if features_list else pd.DataFrame()


def train_keystroke_models(output_dir: str = "models/keystroke"):
    """
    Train keystroke anomaly detection models on real datasets.
    
    Args:
        output_dir: Directory to save trained models
    """
    print("=" * 60)
    print("🚀 KEYSTROKE ANOMALY DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize data loader
    loader = KeystrokeLoader()
    extractor = KeystrokeFeatureExtractor()
    
    all_features = []
    
    # ================== Load CMU Dataset ==================
    print("\n📚 Loading CMU Keystroke Dataset...")
    try:
        cmu_df = loader.load_cmu_dataset()
        print(f"   ✅ Loaded {len(cmu_df)} records from CMU dataset")
        
        print("   🔧 Extracting features...")
        cmu_features = extractor.extract_cmu_features(cmu_df)
        print(f"   ✅ Extracted features for {len(cmu_features)} sessions")
        
        cmu_features['dataset'] = 'CMU'
        all_features.append(cmu_features)
        
    except FileNotFoundError as e:
        print(f"   ⚠️  CMU dataset not found: {e}")
    except Exception as e:
        print(f"   ❌ Error loading CMU dataset: {e}")
    
    # ================== Load KeyRecs Dataset ==================
    print("\n📚 Loading KeyRecs Dataset...")
    try:
        keyrecs_df = loader.load_keyrecs_dataset(file_type='fixed')
        print(f"   ✅ Loaded {len(keyrecs_df)} records from KeyRecs dataset")
        
        print("   🔧 Extracting features...")
        keyrecs_features = extractor.extract_keyrecs_features(keyrecs_df)
        
        if not keyrecs_features.empty:
            print(f"   ✅ Extracted features for {len(keyrecs_features)} sessions")
            keyrecs_features['dataset'] = 'KeyRecs'
            all_features.append(keyrecs_features)
        else:
            print("   ⚠️  No features extracted (check dataset structure)")
            
    except FileNotFoundError as e:
        print(f"   ⚠️  KeyRecs dataset not found: {e}")
    except Exception as e:
        print(f"   ❌ Error loading KeyRecs dataset: {e}")
    
    # ================== Combine Features ==================
    if not all_features:
        print("\n❌ No datasets loaded! Please download datasets to backend/data/datasets/keystroke/")
        print("   See DATASETS.md for download links")
        return
    
    combined_features = pd.concat(all_features, ignore_index=True)
    print(f"\n📊 Combined Features: {len(combined_features)} sessions from {len(all_features)} dataset(s)")
    
    # Select only numeric features for training
    feature_columns = combined_features.select_dtypes(include=[np.number]).columns.tolist()
    X = combined_features[feature_columns].fillna(0)
    
    print(f"   Feature dimensions: {X.shape}")
    print(f"   Features: {feature_columns}")
    
    # ================== Train/Test Split ==================
    print("\n🔀 Splitting data (80% train, 20% test)...")
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # ================== Scaling ==================
    print("\n⚖️  Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ================== Train Isolation Forest ==================
    print("\n🤖 Training Isolation Forest model...")
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        verbose=1
    )
    
    model.fit(X_train_scaled)
    print("   ✅ Model trained!")
    
    # ================== Evaluation ==================
    print("\n📈 Evaluating model...")
    
    # Predict on training set
    train_predictions = model.predict(X_train_scaled)
    train_scores = model.score_samples(X_train_scaled)
    train_anomalies = (train_predictions == -1).sum()
    train_normal = (train_predictions == 1).sum()
    
    print(f"   Training Set:")
    print(f"      Normal: {train_normal} ({train_normal/len(X_train)*100:.1f}%)")
    print(f"      Anomalies: {train_anomalies} ({train_anomalies/len(X_train)*100:.1f}%)")
    
    # Predict on test set
    test_predictions = model.predict(X_test_scaled)
    test_scores = model.score_samples(X_test_scaled)
    test_anomalies = (test_predictions == -1).sum()
    test_normal = (test_predictions == 1).sum()
    
    print(f"   Test Set:")
    print(f"      Normal: {test_normal} ({test_normal/len(X_test)*100:.1f}%)")
    print(f"      Anomalies: {test_anomalies} ({test_anomalies/len(X_test)*100:.1f}%)")
    
    # ================== Save Model ==================
    print(f"\n💾 Saving model to {output_dir}/...")
    
    # Save Isolation Forest model
    model_path = os.path.join(output_dir, 'isolation_forest.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"   ✅ Model saved: {model_path}")
    
    # Save scaler
    scaler_path = os.path.join(output_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"   ✅ Scaler saved: {scaler_path}")
    
    # Save feature names
    feature_names_path = os.path.join(output_dir, 'feature_names.json')
    with open(feature_names_path, 'w') as f:
        json.dump(feature_columns, f, indent=2)
    print(f"   ✅ Feature names saved: {feature_names_path}")
    
    # Save training metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'datasets_used': [feat['dataset'].iloc[0] for feat in all_features],
        'total_samples': len(combined_features),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_count': len(feature_columns),
        'contamination': 0.1,
        'train_anomaly_rate': float(train_anomalies / len(X_train)),
        'test_anomaly_rate': float(test_anomalies / len(X_test)),
    }
    
    metadata_path = os.path.join(output_dir, 'training_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Metadata saved: {metadata_path}")
    
    # ================== Summary ==================
    print("\n" + "=" * 60)
    print("✨ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"📁 Models saved to: {output_dir}/")
    print(f"📊 Training samples: {len(X_train)}")
    print(f"🎯 Test anomaly rate: {test_anomalies/len(X_test)*100:.1f}%")
    print("=" * 60)
    
    return model, scaler, feature_columns, metadata


if __name__ == "__main__":
    # Train models
    train_keystroke_models()
