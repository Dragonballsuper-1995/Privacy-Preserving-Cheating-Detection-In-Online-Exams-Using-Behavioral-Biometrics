"""
Master Training Script

Runs all model training pipelines in sequence:
1. Keystroke anomaly detection (Isolation Forest)
2. Behavioral cheating classification (Random Forest, Gradient Boosting)
3. Answer similarity detection (Sentence Transformers)
4. Comprehensive evaluation

This is the main entry point for training all models on real datasets.
"""

import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import training scripts
try:
    from scripts.train_keystroke_models import train_keystroke_models
    from scripts.train_behavioral_models import train_behavioral_models
    from scripts.train_similarity_models import train_similarity_models
    from scripts.comprehensive_evaluation import ModelEvaluator
except ImportError:
    # If running from scripts directory
    from train_keystroke_models import train_keystroke_models
    from train_behavioral_models import train_behavioral_models
    from train_similarity_models import train_similarity_models
    from comprehensive_evaluation import ModelEvaluator


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def train_all_models(models_dir: str = "models", skip_existing: bool = False):
    """
    Train all models in sequence.
    
    Args:
        models_dir: Base directory for saving models
        skip_existing: If True, skip training if model already exists
    """
    start_time = datetime.now()
    
    print_header("🚀 MASTER TRAINING PIPELINE")
    print(f"Starting at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Models directory: {os.path.abspath(models_dir)}")
    print("=" * 70)
    
    results = {
        'start_time': start_time.isoformat(),
        'models_trained': [],
        'models_skipped': [],
        'models_failed': [],
    }
    
    # ============== 1. KEYSTROKE MODELS ==============
    print_header("1/3: KEYSTROKE ANOMALY DETECTION")
    keystroke_dir = os.path.join(models_dir, "keystroke")
    
    if skip_existing and os.path.exists(os.path.join(keystroke_dir, "isolation_forest.pkl")):
        print("⏭️  Keystroke model already exists, skipping...")
        results['models_skipped'].append('keystroke')
    else:
        try:
            print("Training keystroke anomaly detection models...")
            train_keystroke_models(output_dir=keystroke_dir)
            results['models_trained'].append('keystroke')
            print("✅ Keystroke training complete!")
        except Exception as e:
            print(f"❌ Keystroke training failed: {e}")
            results['models_failed'].append(('keystroke', str(e)))
            import traceback
            traceback.print_exc()
    
    # ============== 2. BEHAVIORAL MODELS ==============
    print_header("2/3: BEHAVIORAL CHEATING DETECTION")
    behavioral_dir = os.path.join(models_dir, "behavioral")
    
    if skip_existing and os.path.exists(os.path.join(behavioral_dir, "random_forest.pkl")):
        print("⏭️  Behavioral models already exist, skipping...")
        results['models_skipped'].append('behavioral')
    else:
        try:
            print("Training behavioral cheating detection models...")
            train_behavioral_models(output_dir=behavioral_dir)
            results['models_trained'].append('behavioral')
            print("✅ Behavioral training complete!")
        except Exception as e:
            print(f"❌ Behavioral training failed: {e}")
            results['models_failed'].append(('behavioral', str(e)))
            import traceback
            traceback.print_exc()
    
    # ============== 3. SIMILARITY MODELS ==============
    print_header("3/3: ANSWER SIMILARITY DETECTION")
    similarity_dir = os.path.join(models_dir, "similarity")
    
    if skip_existing and os.path.exists(os.path.join(similarity_dir, "training_metadata.json")):
        print("⏭️  Similarity model already exists, skipping...")
        results['models_skipped'].append('similarity')
    else:
        try:
            print("Training answer similarity detection models...")
            train_similarity_models(output_dir=similarity_dir)
            results['models_trained'].append('similarity')
            print("✅ Similarity training complete!")
        except Exception as e:
            print(f"❌ Similarity training failed: {e}")
            results['models_failed'].append(('similarity', str(e)))
            import traceback
            traceback.print_exc()
    
    # ============== 4. COMPREHENSIVE EVALUATION ==============
    print_header("📊 COMPREHENSIVE EVALUATION")
    
    try:
        evaluator = ModelEvaluator(results_dir="data/results")
        report_path = evaluator.generate_comprehensive_report()
        results['evaluation_report'] = report_path
        print("✅ Evaluation complete!")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # ============== SUMMARY ==============
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("✨ TRAINING PIPELINE COMPLETE")
    print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration}")
    print()
    print("📊 Summary:")
    print(f"   ✅ Models trained: {len(results['models_trained'])}")
    if results['models_trained']:
        for model in results['models_trained']:
            print(f"      - {model}")
    
    print(f"   ⏭️  Models skipped: {len(results['models_skipped'])}")
    if results['models_skipped']:
        for model in results['models_skipped']:
            print(f"      - {model}")
    
    print(f"   ❌ Models failed: {len(results['models_failed'])}")
    if results['models_failed']:
        for model, error in results['models_failed']:
            print(f"      - {model}: {error}")
    
    if results.get('evaluation_report'):
        print(f"\n📄 Evaluation report: {results['evaluation_report']}")
    
    print("=" * 70)
    
    # Save results
    import json
    results['end_time'] = end_time.isoformat()
    results['duration_seconds'] = duration.total_seconds()
    
    results_path = os.path.join("data", "results", "training_summary.json")
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Training summary saved: {results_path}")
    
    return results


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(description='Train all cheating detection models')
    parser.add_argument('--models-dir', type=str, default='models',
                       help='Base directory for saving models (default: models)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip training if model already exists')
    parser.add_argument('--only', type=str, choices=['keystroke', 'behavioral', 'similarity', 'eval'],
                       help='Train only specific model type')
    
    args = parser.parse_args()
    
    if args.only:
        # Train only specific model
        print(f"Training only: {args.only}")
        
        if args.only == 'keystroke':
            train_keystroke_models(output_dir=os.path.join(args.models_dir, 'keystroke'))
        elif args.only == 'behavioral':
            train_behavioral_models(output_dir=os.path.join(args.models_dir, 'behavioral'))
        elif args.only == 'similarity':
            train_similarity_models(output_dir=os.path.join(args.models_dir, 'similarity'))
        elif args.only == 'eval':
            evaluator = ModelEvaluator()
            evaluator.generate_comprehensive_report()
    else:
        # Train all models
        train_all_models(models_dir=args.models_dir, skip_existing=args.skip_existing)


if __name__ == "__main__":
    main()
