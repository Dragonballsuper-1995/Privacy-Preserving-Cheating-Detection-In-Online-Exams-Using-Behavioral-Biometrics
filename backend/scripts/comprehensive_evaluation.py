"""
Comprehensive Model Evaluation Framework

This script provides comprehensive evaluation of all trained models:
- Keystroke anomaly detection
- Behavioral cheating classification  
- Answer similarity detection

Generates detailed metrics, visualizations, and reports.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import pickle
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader.keystroke_loader import KeystrokeLoader
from src.data_loader.exam_loader import ExamLoader
from src.data_loader.plagiarism_loader import PlagiarismLoader


class ModelEvaluator:
    """Comprehensive model evaluation suite."""
    
    def __init__(self, results_dir: str = "data/results"):
        """
        Initialize evaluator.
        
        Args:
            results_dir: Directory to save results and visualizations
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(os.path.join(results_dir, 'visualizations'), exist_ok=True)
        
    def evaluate_isolation_forest(self, model_dir: str = "models/keystroke") -> Dict[str, Any]:
        """Evaluate keystroke anomaly detection model."""
        print("\n" + "=" * 60)
        print("📊 EVALUATING KEYSTROKE ANOMALY DETECTION")
        print("=" * 60)
        
        try:
            # Load model
            with open(os.path.join(model_dir, 'isolation_forest.pkl'), 'rb') as f:
                model = pickle.load(f)
            with open(os.path.join(model_dir, 'scaler.pkl'), 'rb') as f:
                scaler = pickle.load(f)
            with open(os.path.join(model_dir, 'training_metadata.json'), 'r') as f:
                metadata = json.load(f)
            
            print("✅ Model loaded successfully")
            print(f"   Training date: {metadata['training_date']}")
            print(f"   Training samples: {metadata['train_samples']}")
            print(f"   Contamination rate: {metadata.get('contamination', 0.1)}")
            
            results = {
                'model_type': 'Isolation Forest',
                'metadata': metadata,
                'status': 'success'
            }
            
            # Generate visualization if data available
            try:
                self._plot_anomaly_scores_distribution(model, scaler, model_dir)
            except Exception as e:
                print(f"   ⚠️ Could not generate visualization: {e}")
            
            return results
            
        except FileNotFoundError:
            print("❌ Keystroke model not found. Run train_keystroke_models.py first.")
            return {'status': 'not_found'}
        except Exception as e:
            print(f"❌ Error evaluating model: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def evaluate_behavioral_classifier(self, model_dir: str = "models/behavioral") -> Dict[str, Any]:
        """Evaluate behavioral cheating detection models."""
        print("\n" + "=" * 60)
        print("📊 EVALUATING BEHAVIORAL CLASSIFICATION")
        print("=" * 60)
        
        try:
            # Load models
            with open(os.path.join(model_dir, 'random_forest.pkl'), 'rb') as f:
                rf_model = pickle.load(f)
            with open(os.path.join(model_dir, 'gradient_boosting.pkl'), 'rb') as f:
                gb_model = pickle.load(f)
            with open(os.path.join(model_dir, 'training_metadata.json'), 'r') as f:
                metadata = json.load(f)
            
            print("✅ Models loaded successfully")
            print(f"   Training date: {metadata['training_date']}")
            print(f"   Training samples: {metadata['train_samples']}")
            
            # Display metrics
            print("\n📈 Random Forest Performance:")
            rf_metrics = metadata['models']['random_forest']
            print(f"   Test Accuracy: {rf_metrics['test_accuracy']:.3f}")
            print(f"   CV Accuracy:   {rf_metrics['cv_accuracy_mean']:.3f} ± {rf_metrics['cv_accuracy_std']:.3f}")
            if rf_metrics.get('roc_auc'):
                print(f"   ROC-AUC:       {rf_metrics['roc_auc']:.3f}")
            
            print("\n📈 Gradient Boosting Performance:")
            gb_metrics = metadata['models']['gradient_boosting']
            print(f"   Test Accuracy: {gb_metrics['test_accuracy']:.3f}")
            if gb_metrics.get('roc_auc'):
                print(f"   ROC-AUC:       {gb_metrics['roc_auc']:.3f}")
            
            # Generate visualizations
            try:
                self._plot_feature_importance(model_dir)
                self._plot_model_comparison(metadata)
            except Exception as e:
                print(f"   ⚠️ Could not generate visualizations: {e}")
            
            results = {
                'model_type': 'Behavioral Classification',
                'metadata': metadata,
                'status': 'success'
            }
            
            return results
            
        except FileNotFoundError:
            print("❌ Behavioral models not found. Run train_behavioral_models.py first.")
            return {'status': 'not_found'}
        except Exception as e:
            print(f"❌ Error evaluating models: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def evaluate_similarity_model(self, model_dir: str = "models/similarity") -> Dict[str, Any]:
        """Evaluate answer similarity detection model."""
        print("\n" + "=" * 60)
        print("📊 EVALUATING SIMILARITY DETECTION")
        print("=" * 60)
        
        try:
            # Check if model exists
            if not os.path.exists(os.path.join(model_dir, 'training_metadata.json')):
                raise FileNotFoundError("Model metadata not found")
            
            # Load metadata
            with open(os.path.join(model_dir, 'training_metadata.json'), 'r') as f:
                metadata = json.load(f)
            
            print("✅ Model metadata loaded")
            print(f"   Training date: {metadata['training_date']}")
            print(f"   Base model: {metadata['base_model']}")
            print(f"   Training pairs: {metadata['train_pairs']}")
            print(f"   Optimal threshold: {metadata['optimal_threshold']}")
            
            # Display metrics
            print("\n📈 Test Set Performance:")
            metrics = metadata['metrics']
            print(f"   Accuracy:  {metrics['accuracy']:.3f}")
            print(f"   Precision: {metrics['precision']:.3f}")
            print(f"   Recall:    {metrics['recall']:.3f}")
            print(f"   F1 Score:  {metrics['f1']:.3f}")
            if metrics.get('roc_auc'):
                print(f"   ROC-AUC:   {metrics['roc_auc']:.3f}")
            
            results = {
                'model_type': 'Similarity Detection',
                'metadata': metadata,
                'status': 'success'
            }
            
            return results
            
        except FileNotFoundError:
            print("❌ Similarity model not found. Run train_similarity_models.py first.")
            return {'status': 'not_found'}
        except Exception as e:
            print(f"❌ Error evaluating model: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _plot_anomaly_scores_distribution(self, model, scaler, model_dir: str):
        """Plot distribution of anomaly scores."""
        print("\n   📊 Generating anomaly score distribution plot...")
        
        # This would require test data - placeholder for now
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title("Anomaly Score Distribution")
        ax.set_xlabel("Anomaly Score")
        ax.set_ylabel("Frequency")
        
        plot_path = os.path.join(self.results_dir, 'visualizations', 'anomaly_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Saved: {plot_path}")
    
    def _plot_feature_importance(self, model_dir: str):
        """Plot feature importance for behavioral models."""
        print("\n   📊 Generating feature importance plot...")
        
        try:
            importance_df = pd.read_csv(os.path.join(model_dir, 'feature_importance.csv'))
            
            # Plot top 15 features
            top_features = importance_df.head(15)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(range(len(top_features)), top_features['importance'])
            ax.set_yticks(range(len(top_features)))
            ax.set_yticklabels(top_features['feature'])
            ax.set_xlabel('Importance')
            ax.set_title('Top 15 Most Important Features (Random Forest)')
            ax.invert_yaxis()
            
            plt.tight_layout()
            plot_path = os.path.join(self.results_dir, 'visualizations', 'feature_importance.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"   ✅ Saved: {plot_path}")
            
        except Exception as e:
            print(f"   ⚠️ Could not plot feature importance: {e}")
    
    def _plot_model_comparison(self, metadata: Dict):
        """Plot comparison of different models."""
        print("\n   📊 Generating model comparison plot...")
        
        try:
            models = metadata['models']
            model_names = list(models.keys())
            accuracies = [models[m]['test_accuracy'] for m in model_names]
            
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(model_names, accuracies, color=['#3498db', '#2ecc71'])
            ax.set_ylabel('Test Accuracy')
            ax.set_title('Model Performance Comparison')
            ax.set_ylim([0, 1])
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom')
            
            plt.tight_layout()
            plot_path = os.path.join(self.results_dir, 'visualizations', 'model_comparison.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"   ✅ Saved: {plot_path}")
            
        except Exception as e:
            print(f"   ⚠️ Could not plot model comparison: {e}")
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive evaluation report."""
        print("\n" + "=" * 60)
        print("📝 GENERATING COMPREHENSIVE EVALUATION REPORT")
        print("=" * 60)
        
        # Evaluate all models
        keystroke_results = self.evaluate_isolation_forest()
        behavioral_results = self.evaluate_behavioral_classifier()
        similarity_results = self.evaluate_similarity_model()
        
        # Create report
        report = []
        report.append("# Comprehensive Model Evaluation Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n")
        
        # Keystroke model
        report.append("## 1. Keystroke Anomaly Detection\n")
        if keystroke_results['status'] == 'success':
            meta = keystroke_results['metadata']
            report.append(f"- **Model Type:** Isolation Forest")
            report.append(f"- **Training Samples:** {meta['train_samples']}")
            report.append(f"- **Test Samples:** {meta['test_samples']}")
            report.append(f"- **Test Anomaly Rate:** {meta['test_anomaly_rate']:.2%}")
            report.append(f"- **Status:** ✅ Trained and ready\n")
        else:
            report.append(f"- **Status:** ❌ Not trained yet\n")
        
        # Behavioral model
        report.append("## 2. Behavioral Cheating Detection\n")
        if behavioral_results['status'] == 'success':
            meta = behavioral_results['metadata']
            rf_acc = meta['models']['random_forest']['test_accuracy']
            gb_acc = meta['models']['gradient_boosting']['test_accuracy']
            report.append(f"- **Models:** Random Forest, Gradient Boosting")
            report.append(f"- **Training Samples:** {meta['train_samples']}")
            report.append(f"- **Random Forest Accuracy:** {rf_acc:.3f}")
            report.append(f"- **Gradient Boosting Accuracy:** {gb_acc:.3f}")
            report.append(f"- **Status:** ✅ Trained and ready\n")
        else:
            report.append(f"- **Status:** ❌ Not trained yet\n")
        
        # Similarity model
        report.append("## 3. Answer Similarity Detection\n")
        if similarity_results['status'] == 'success':
            meta = similarity_results['metadata']
            f1 = meta['metrics']['f1']
            report.append(f"- **Model:** Fine-tuned Sentence Transformer")
            report.append(f"- **Training Pairs:** {meta['train_pairs']}")
            report.append(f"- **F1 Score:** {f1:.3f}")
            report.append(f"- **Optimal Threshold:** {meta['optimal_threshold']}")
            report.append(f"- **Status:** ✅ Trained and ready\n")
        else:
            report.append(f"- **Status:** ❌ Not trained yet\n")
        
        # Recommendations
        report.append("---\n")
        report.append("## Recommendations\n")
        
        trained_count = sum(1 for r in [keystroke_results, behavioral_results, similarity_results] 
                          if r['status'] == 'success')
        
        if trained_count == 0:
            report.append("⚠️ **No models trained yet.** Run training scripts to begin.\n")
        elif trained_count < 3:
            report.append(f"🚧 **{trained_count}/3 models trained.** Complete remaining model training.\n")
        else:
            report.append("✅ **All models trained!** Ready for integration and deployment.\n")
        
        # Save report
        report_text = '\n'.join(report)
        report_path = os.path.join(self.results_dir, 'evaluation_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n✅ Report saved: {report_path}")
        print("\n" + report_text)
        
        return report_path


def main():
    """Main evaluation function."""
    evaluator = ModelEvaluator()
    report_path = evaluator.generate_comprehensive_report()
    
    print("\n" + "=" * 60)
    print("✨ EVALUATION COMPLETE!")
    print("=" * 60)
    print(f"📄 Full report: {report_path}")
    print(f"📊 Visualizations: {os.path.join(evaluator.results_dir, 'visualizations')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
