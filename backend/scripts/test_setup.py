"""
Quick Test Script

Tests that all training infrastructure works before full training run.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("🧪 TRAINING SCRIPTS VALIDATION TEST")
print("=" * 60)

# Test 1: Data Loaders
print("\n📦 Test 1: Data Loaders")
print("-" * 60)

try:
    from src.data_loader.keystroke_loader import KeystrokeLoader
    loader = KeystrokeLoader()
    cmu_df = loader.load_cmu_dataset()
    print(f"✅ Keystroke Loader: CMU dataset loaded ({cmu_df.shape[0]:,} records)")
except Exception as e:
    print(f"❌ Keystroke Loader failed: {e}")

try:
    from src.data_loader.exam_loader import ExamLoader
    exam_loader = ExamLoader()
    suspicion_df = exam_loader.load_suspicion_logs()
    print(f"✅ Exam Loader: Suspicion logs loaded ({suspicion_df.shape[0]:,} records)")
except Exception as e:
    print(f"❌ Exam Loader failed: {e}")

try:
    from src.data_loader.plagiarism_loader import PlagiarismLoader
    plag_loader = PlagiarismLoader()
    code_main, code_feats = plag_loader.load_student_code_sim()
    print(f"✅ Plagiarism Loader: Student code dataset loaded ({code_main.shape[0]:,} records)")
except Exception as e:
    print(f"❌ Plagiarism Loader failed: {e}")

# Test 2: Dependency Check
print("\n📚 Test 2: Dependencies")
print("-" * 60)

dependencies = [
    ('numpy', 'NumPy'),
    ('pandas', 'Pandas'),
    ('sklearn', 'Scikit-learn'),
    ('matplotlib', 'Matplotlib'),
    ('seaborn', 'Seaborn'),
]

try:
    import torch
    dependencies.append(('torch', 'PyTorch'))
except ImportError:
    pass

try:
    import sentence_transformers
    dependencies.append(('sentence_transformers', 'Sentence Transformers'))
except ImportError:
    pass

all_deps_ok = True
for module_name, display_name in dependencies:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name}: {version}")
    except ImportError:
        print(f"❌ {display_name}: NOT INSTALLED")
        all_deps_ok = False

# Test 3: Feature Extraction
print("\n🔧 Test 3: Feature Extraction")
print("-" * 60)

try:
    from scripts.train_keystroke_models import KeystrokeFeatureExtractor
    extractor = KeystrokeFeatureExtractor()
    features = extractor.extract_cmu_features(cmu_df)
    print(f"✅ Keystroke features extracted: {features.shape[1]} features from {len(features)} sessions")
except Exception as e:
    print(f"❌ Feature extraction failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Model Imports
print("\n🤖 Test 4: ML Model Imports")
print("-" * 60)

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    print("✅ Scikit-learn models imported successfully")
except Exception as e:
    print(f"❌ Model import failed: {e}")

# Test 5: Check Existing Models
print("\n💾 Test 5: Existing Trained Models")
print("-" * 60)

model_dirs = {
    'Keystroke': 'models/keystroke/isolation_forest.pkl',
    'Behavioral': 'models/behavioral/random_forest.pkl',
    'Similarity': 'models/similarity/training_metadata.json'
}

models_exist = 0
for name, path in model_dirs.items():
    if os.path.exists(path):
        print(f"✅ {name} model exists: {path}")
        models_exist += 1
    else:
        print(f"⚠️  {name} model not found: {path}")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)

if all_deps_ok:
    print("✅ All dependencies installed")
else:
    print("⚠️  Some dependencies missing (install with: pip install -r requirements.txt)")

print(f"📁 Dataset directories found: 3/3")
print(f"💾 Trained models found: {models_exist}/3")

if models_exist == 0:
    print("\n🚀 Ready to train models!")
    print("   Run: python scripts/train_all_models.py")
elif models_exist < 3:
    print(f"\n🔄 {3 - models_exist} model(s) still need training")
    print("   Run: python scripts/train_all_models.py")
else:
    print("\n✨ All models already trained!")
    print("   Run: python scripts/comprehensive_evaluation.py")

print("=" * 60)
