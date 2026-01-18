"""
Train Behavioral Cheating Detection Models

This script trains supervised classification models on exam behavior datasets
to detect cheating patterns (gaze, head pose, suspicious behaviors).
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pickle
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader.exam_loader import ExamLoader


class BehavioralFeatureExtractor:
    """Extract features from exam behavior datasets."""
    
    @staticmethod
    def extract_suspicion_features(df: pd.DataFrame) -> tuple:
        """
        Extract features from student suspicion logs dataset.
        
        Args:
            df: Suspicion logs DataFrame
            
        Returns:
            Tuple of (features_df, labels, label_encoder)
        """
        # This depends on the actual structure of the dataset
        # Common features might include: gaze_away_count, head_turn_frequency, etc.
        
        # Identify feature columns (numeric) and label column
        # Look for common label column names
        label_col = None
        for col in ['label', 'is_cheating', 'cheating', 'suspicious', 'class']:
            if col in df.columns:
                label_col = col
                break
        
        if label_col is None:
            print("   ⚠️  No label column found, using heuristic approach")
            # Create synthetic labels based on behavior patterns
            # This is a fallback - real datasets should have labels
            return df.select_dtypes(include=[np.number]), None, None
        
        # Extract features and labels
        feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if label_col in feature_cols:
            feature_cols.remove(label_col)
        
        X = df[feature_cols].fillna(0)
        y = df[label_col]
        
        # Encode labels if categorical
        label_encoder = LabelEncoder()
        if y.dtype == 'object' or y.dtype.name == 'category':
            y_encoded = label_encoder.fit_transform(y)
        else:
            y_encoded = y.values
            label_encoder = None
        
        return X, y_encoded, label_encoder


def train_behavioral_models(output_dir: str = "models/behavioral"):
    """
    Train behavioral cheating detection models on exam datasets.
    
    Args:
        output_dir: Directory to save trained models
    """
    print("=" * 60)
    print("🚀 BEHAVIORAL CHEATING DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize data loader
    loader = ExamLoader()
    extractor = BehavioralFeatureExtractor()
    
    # ================== Load Suspicion Logs ==================
    print("\n📚 Loading Student Suspicion Dataset...")
    try:
        suspicion_df = loader.load_suspicion_logs()
        print(f"   ✅ Loaded {len(suspicion_df)} records")
        print(f"   Columns: {list(suspicion_df.columns)[:10]}...")
        
        print("\n   🔧 Extracting features and labels...")
        X, y, label_encoder = extractor.extract_suspicion_features(suspicion_df)
        
        if y is None:
            print("   ❌ No labels found in dataset. Cannot train supervised model.")
            print("   💡 Tip: Ensure dataset has a label column (e.g., 'is_cheating', 'label')")
            return
        
        print(f"   ✅ Features shape: {X.shape}")
        print(f"   ✅ Labels shape: {y.shape}")
        
        # Check class distribution
        unique, counts = np.unique(y, return_counts=True)
        print(f"\n   📊 Class distribution:")
        for cls, count in zip(unique, counts):
            label_name = label_encoder.inverse_transform([cls])[0] if label_encoder else cls
            print(f"      {label_name}: {count} ({count/len(y)*100:.1f}%)")
        
    except FileNotFoundError as e:
        print(f"   ⚠️  Suspicion dataset not found: {e}")
        print("   💡 Download datasets to backend/data/datasets/exam_behavior/")
        return
    except Exception as e:
        print(f"   ❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ================== Train/Test Split ==================
    print("\n🔀 Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # ================== Scaling ==================
    print("\n⚖️  Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ================== Train Random Forest ==================
    print("\n🌲 Training Random Forest Classifier...")
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced',  # Handle class imbalance
        n_jobs=-1,
        verbose=1
    )
    
    rf_model.fit(X_train_scaled, y_train)
    print("   ✅ Random Forest trained!")
    
    # Evaluate Random Forest
    print("\n   📈 Evaluating Random Forest...")
    train_score = rf_model.score(X_train_scaled, y_train)
    test_score = rf_model.score(X_test_scaled, y_test)
    print(f"      Training accuracy: {train_score:.3f}")
    print(f"      Test accuracy: {test_score:.3f}")
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
    print(f"      Cross-val accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # ================== Train Gradient Boosting ==================
    print("\n🚀 Training Gradient Boosting Classifier...")
    
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbose=1
    )
    
    gb_model.fit(X_train_scaled, y_train)
    print("   ✅ Gradient Boosting trained!")
    
    # Evaluate Gradient Boosting
    print("\n   📈 Evaluating Gradient Boosting...")
    gb_train_score = gb_model.score(X_train_scaled, y_train)
    gb_test_score = gb_model.score(X_test_scaled, y_test)
    print(f"      Training accuracy: {gb_train_score:.3f}")
    print(f"      Test accuracy: {gb_test_score:.3f}")
    
    # ================== Detailed Evaluation ==================
    print("\n📊 Detailed Test Set Evaluation:")
    print("\n" + "=" * 60)
    print("RANDOM FOREST RESULTS")
    print("=" * 60)
    
    y_pred_rf = rf_model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred_rf, 
                                target_names=label_encoder.classes_ if label_encoder else None))
    
    print("\nConfusion Matrix (Random Forest):")
    print(confusion_matrix(y_test, y_pred_rf))
    
    # ROC-AUC if binary
    if len(unique) == 2:
        y_pred_proba_rf = rf_model.predict_proba(X_test_scaled)[:, 1]
        roc_auc_rf = roc_auc_score(y_test, y_pred_proba_rf)
        print(f"\nROC-AUC Score: {roc_auc_rf:.3f}")
    
    print("\n" + "=" * 60)
    print("GRADIENT BOOSTING RESULTS")
    print("=" * 60)
    
    y_pred_gb = gb_model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred_gb,
                                target_names=label_encoder.classes_ if label_encoder else None))
    
    print("\nConfusion Matrix (Gradient Boosting):")
    print(confusion_matrix(y_test, y_pred_gb))
    
    if len(unique) == 2:
        y_pred_proba_gb = gb_model.predict_proba(X_test_scaled)[:, 1]
        roc_auc_gb = roc_auc_score(y_test, y_pred_proba_gb)
        print(f"\nROC-AUC Score: {roc_auc_gb:.3f}")
    
    # ================== Feature Importance ==================
    print("\n🎯 Top 10 Most Important Features (Random Forest):")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10).to_string(index=False))
    
    # ================== Save Models ==================
    print(f"\n💾 Saving models to {output_dir}/...")
    
    # Save Random Forest
    rf_path = os.path.join(output_dir, 'random_forest.pkl')
    with open(rf_path, 'wb') as f:
        pickle.dump(rf_model, f)
    print(f"   ✅ Random Forest saved: {rf_path}")
    
    # Save Gradient Boosting
    gb_path = os.path.join(output_dir, 'gradient_boosting.pkl')
    with open(gb_path, 'wb') as f:
        pickle.dump(gb_model, f)
    print(f"   ✅ Gradient Boosting saved: {gb_path}")
    
    # Save scaler
    scaler_path = os.path.join(output_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"   ✅ Scaler saved: {scaler_path}")
    
    # Save label encoder
    if label_encoder:
        encoder_path = os.path.join(output_dir, 'label_encoder.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(label_encoder, f)
        print(f"   ✅ Label encoder saved: {encoder_path}")
    
    # Save feature names
    feature_names_path = os.path.join(output_dir, 'feature_names.json')
    with open(feature_names_path, 'w') as f:
        json.dump(list(X.columns), f, indent=2)
    print(f"   ✅ Feature names saved: {feature_names_path}")
    
    # Save feature importance
    importance_path = os.path.join(output_dir, 'feature_importance.csv')
    feature_importance.to_csv(importance_path, index=False)
    print(f"   ✅ Feature importance saved: {importance_path}")
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'total_samples': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_count': X.shape[1],
        'class_distribution': {str(k): int(v) for k, v in zip(unique, counts)},
        'models': {
            'random_forest': {
                'test_accuracy': float(test_score),
                'cv_accuracy_mean': float(cv_scores.mean()),
                'cv_accuracy_std': float(cv_scores.std()),
                'roc_auc': float(roc_auc_rf) if len(unique) == 2 else None,
            },
            'gradient_boosting': {
                'test_accuracy': float(gb_test_score),
                'roc_auc': float(roc_auc_gb) if len(unique) == 2 else None,
            }
        }
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
    print(f"📊 Best model: {'Random Forest' if test_score >= gb_test_score else 'Gradient Boosting'}")
    print(f"🎯 Best test accuracy: {max(test_score, gb_test_score):.3f}")
    if len(unique) == 2:
        print(f"📈 Best ROC-AUC: {max(roc_auc_rf, roc_auc_gb):.3f}")
    print("=" * 60)
    
    return rf_model, gb_model, scaler, metadata


if __name__ == "__main__":
    # Train models
    train_behavioral_models()
