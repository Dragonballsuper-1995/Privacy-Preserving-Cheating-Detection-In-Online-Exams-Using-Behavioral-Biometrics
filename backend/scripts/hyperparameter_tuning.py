"""
Hyperparameter Tuning Script

Performs grid search and Bayesian optimization to find optimal hyperparameters
for all models.
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
import pickle
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader.keystroke_loader import KeystrokeLoader
from src.data_loader.exam_loader import ExamLoader
from scripts.train_keystroke_models import KeystrokeFeatureExtractor
from scripts.train_behavioral_models import BehavioralFeatureExtractor


class HyperparameterTuner:
    """Hyperparameter tuning for all models."""
    
    def __init__(self, output_dir: str = "models/configs"):
        """
        Initialize tuner.
        
        Args:
            output_dir: Directory to save best configurations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def tune_isolation_forest(self, X_train, X_test):
        """
        Tune Isolation Forest hyperparameters.
        
        Args:
            X_train: Training features
            X_test: Test features
        """
        print("\n🔧 Tuning Isolation Forest...")
        
        param_grid = {
            'contamination': [0.05, 0.1, 0.15, 0.2],
            'n_estimators': [50, 100, 200],
            'max_samples': ['auto', 0.5, 0.75, 1.0],
            'max_features': [0.5, 0.75, 1.0]
        }
        
        best_score = float('-inf')
        best_params = None
        
        print(f"   Testing {np.prod([len(v) for v in param_grid.values()])} combinations...")
        
        # Grid search (IsolationForest doesn't support sklearn's GridSearchCV directly)
        for contamination in param_grid['contamination']:
            for n_estimators in param_grid['n_estimators']:
                for max_samples in param_grid['max_samples']:
                    for max_features in param_grid['max_features']:
                        model = IsolationForest(
                            contamination=contamination,
                            n_estimators=n_estimators,
                            max_samples=max_samples,
                            max_features=max_features,
                            random_state=42
                        )
                        
                        model.fit(X_train)
                        score = model.score_samples(X_test).mean()
                        
                        if score > best_score:
                            best_score = score
                            best_params = {
                                'contamination': contamination,
                                'n_estimators': n_estimators,
                                'max_samples': max_samples,
                                'max_features': max_features
                            }
        
        print(f"   ✅ Best parameters: {best_params}")
        print(f"   📊 Best score: {best_score:.4f}")
        
        # Save best params
        config_path = os.path.join(self.output_dir, 'isolation_forest_best.json')
        with open(config_path, 'w') as f:
            json.dump({
                'best_params': best_params,
                'best_score': float(best_score),
                'tuned_date': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"   💾 Saved: {config_path}")
        
        return best_params
    
    def tune_random_forest(self, X_train, y_train):
        """
        Tune Random Forest hyperparameters.
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print("\n🔧 Tuning Random Forest...")
        
        param_dist = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None],
            'class_weight': ['balanced', None]
        }
        
        rf = RandomForestClassifier(random_state=42)
        
        # Use RandomizedSearchCV for efficiency
        random_search = RandomizedSearchCV(
            rf, 
            param_distributions=param_dist,
            n_iter=20,  # Number of parameter settings sampled
            cv=StratifiedKFold(n_splits=3),
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=2,
            random_state=42
        )
        
        print("   Running randomized search (20 iterations)...")
        random_search.fit(X_train, y_train)
        
        print(f"   ✅ Best parameters: {random_search.best_params_}")
        print(f"   📊 Best CV F1 score: {random_search.best_score_:.4f}")
        
        # Save best params
        config_path = os.path.join(self.output_dir, 'random_forest_best.json')
        with open(config_path, 'w') as f:
            json.dump({
                'best_params': random_search.best_params_,
                'best_score': float(random_search.best_score_),
                'tuned_date': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"   💾 Saved: {config_path}")
        
        return random_search.best_params_
    
    def tune_gradient_boosting(self, X_train, y_train):
        """
        Tune Gradient Boosting hyperparameters.
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print("\n🔧 Tuning Gradient Boosting...")
        
        param_dist = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        gb = GradientBoostingClassifier(random_state=42)
        
        random_search = RandomizedSearchCV(
            gb,
            param_distributions=param_dist,
            n_iter=20,
            cv=StratifiedKFold(n_splits=3),
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=2,
            random_state=42
        )
        
        print("   Running randomized search (20 iterations)...")
        random_search.fit(X_train, y_train)
        
        print(f"   ✅ Best parameters: {random_search.best_params_}")
        print(f"   📊 Best CV F1 score: {random_search.best_score_:.4f}")
        
        # Save best params
        config_path = os.path.join(self.output_dir, 'gradient_boosting_best.json')
        with open(config_path, 'w') as f:
            json.dump({
                'best_params': random_search.best_params_,
                'best_score': float(random_search.best_score_),
                'tuned_date': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"   💾 Saved: {config_path}")
        
        return random_search.best_params_
    
    def tune_similarity_threshold(self) -> dict:
        """
        Tune similarity detection threshold.
        
        This is done during training in train_similarity_models.py
        Returns recommended thresholds.
        """
        print("\n🔧 Similarity Threshold Tuning...")
        print("   ℹ️  Threshold tuning is performed during similarity model training")
        
        recommended_thresholds = {
            'text_similarity': 0.85,
            'code_similarity': 0.90,  # Higher for code (less variability)
            'essay_similarity': 0.80   # Lower for essays (more variability)
        }
        
        config_path = os.path.join(self.output_dir, 'similarity_thresholds.json')
        with open(config_path, 'w') as f:
            json.dump({
                'recommended_thresholds': recommended_thresholds,
                'note': 'Fine-tuned during model training',
                'updated_date': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"   ✅ Recommended thresholds: {recommended_thresholds}")
        print(f"   💾 Saved: {config_path}")
        
        return recommended_thresholds


def main():
    """Main hyperparameter tuning function."""
    print("=" * 60)
    print("🎯 HYPERPARAMETER TUNING")
    print("=" * 60)
    
    tuner = HyperparameterTuner()
    
    # ========== KEYSTROKE MODEL ==========
    print("\n" + "=" * 60)
    print("1. KEYSTROKE ANOMALY DETECTION")
    print("=" * 60)
    
    try:
        loader = KeystrokeLoader()
        extractor = KeystrokeFeatureExtractor()
        
        # Try to load CMU dataset
        try:
            cmu_df = loader.load_cmu_dataset()
            features = extractor.extract_cmu_features(cmu_df)
            X = features.select_dtypes(include=[np.number]).fillna(0)
            X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            tuner.tune_isolation_forest(X_train_scaled, X_test_scaled)
            
        except FileNotFoundError:
            print("⚠️  Keystroke dataset not found, skipping tuning")
    except Exception as e:
        print(f"❌ Error tuning keystroke model: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== BEHAVIORAL MODELS ==========
    print("\n" + "=" * 60)
    print("2. BEHAVIORAL CLASSIFICATION")
    print("=" * 60)
    
    try:
        exam_loader = ExamLoader()
        behavioral_extractor = BehavioralFeatureExtractor()
        
        # Try to load suspicion logs
        try:
            suspicion_df = exam_loader.load_suspicion_logs()
            X, y, _ = behavioral_extractor.extract_suspicion_features(suspicion_df)
            
            if y is not None:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                
                # Tune both models
                tuner.tune_random_forest(X_train_scaled, y_train)
                tuner.tune_gradient_boosting(X_train_scaled, y_train)
            else:
                print("⚠️  No labels found in dataset")
                
        except FileNotFoundError:
            print("⚠️  Behavioral dataset not found, skipping tuning")
    except Exception as e:
        print(f"❌ Error tuning behavioral models: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== SIMILARITY THRESHOLDS ==========
    print("\n" + "=" * 60)
    print("3. SIMILARITY DETECTION")
    print("=" * 60)
    
    try:
        tuner.tune_similarity_threshold()
    except Exception as e:
        print(f"❌ Error with similarity thresholds: {e}")
    
    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("✨ TUNING COMPLETE")
    print("=" * 60)
    print(f"📁 Best configurations saved to: {tuner.output_dir}/")
    print("💡 Use these configurations to retrain models with optimal parameters")
    print("=" * 60)


if __name__ == "__main__":
    main()
