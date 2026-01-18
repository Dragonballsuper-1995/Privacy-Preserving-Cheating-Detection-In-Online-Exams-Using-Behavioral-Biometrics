# Training Scripts Documentation

This directory contains all the training scripts for the Cheating Detection System models.

## 📋 Overview

The training pipeline consists of three main models:
1. **Keystroke Anomaly Detection** - Isolation Forest for unusual typing patterns
2. **Behavioral Cheating Classification** - Random Forest & Gradient Boosting for suspicious behaviors
3. **Answer Similarity Detection** - Fine-tuned Sentence Transformers for plagiarism

## 🚀 Quick Start

### 1. Prerequisites

Ensure datasets are downloaded and placed in `backend/data/datasets/`:
```
backend/data/datasets/
├── keystroke/
│   ├── cmu/
│   │   └── DSL-StrongPasswordData.csv
│   └── keyrecs/
│       └── fixed-text.csv
├── exam_behavior/
│   └── student_suspicion/
│       └── dataset.csv
└── plagiarism/
    └── student_code/
        └── cheating_dataset.csv
```

See `DATASETS.md` in the project root for download links.

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Train All Models

```bash
# Train all models at once
python scripts/train_all_models.py

# Or train individual models
python scripts/train_keystroke_models.py
python scripts/train_behavioral_models.py
python scripts/train_similarity_models.py
```

### 4. Evaluate Models

```bash
python scripts/comprehensive_evaluation.py
```

## 📁 Script Descriptions

### Core Training Scripts

#### `train_keystroke_models.py`
Trains Isolation Forest for keystroke anomaly detection.
- **Datasets Used:** CMU Keystroke Benchmark, KeyRecs
- **Output:** `models/keystroke/`
  - `isolation_forest.pkl` - Trained Isolation Forest model
  - `scaler.pkl` - Feature scaler
  - `feature_names.json` - List of features
  - `training_metadata.json` - Training statistics

**Usage:**
```bash
python train_keystroke_models.py
```

#### `train_behavioral_models.py`
Trains Random Forest and Gradient Boosting for behavioral cheating detection.
- **Datasets Used:** Student Suspicious Behaviors dataset
- **Output:** `models/behavioral/`
  - `random_forest.pkl` - Random Forest classifier
  - `gradient_boosting.pkl` - Gradient Boosting classifier
  - `scaler.pkl` - Feature scaler
  - `label_encoder.pkl` - Label encoder
  - `feature_importance.csv` - Feature importance scores
  - `training_metadata.json` - Training statistics

**Usage:**
```bash
python train_behavioral_models.py
```

#### `train_similarity_models.py`
Fine-tunes sentence transformers for answer similarity detection.
- **Datasets Used:** Student Code Similarity dataset
- **Output:** `models/similarity/`
  - Fine-tuned sentence transformer model
  - `optimal_threshold.json` - Best similarity threshold
  - `training_metadata.json` - Training statistics

**Usage:**
```bash
python train_similarity_models.py
```

### Orchestration & Utilities

#### `train_all_models.py`
Master script that runs all training pipelines in sequence.

**Usage:**
```bash
# Train all models
python train_all_models.py

# Skip models that already exist
python train_all_models.py --skip-existing

# Train only specific model
python train_all_models.py --only keystroke
python train_all_models.py --only behavioral
python train_all_models.py --only similarity

# Specify custom models directory
python train_all_models.py --models-dir /path/to/models
```

#### `comprehensive_evaluation.py`
Evaluates all trained models and generates reports.

**Output:** `data/results/`
- `evaluation_report.md` - Comprehensive evaluation report
- `visualizations/` - Charts and plots
  - `feature_importance.png`
  - `model_comparison.png`
  - `anomaly_distribution.png`

**Usage:**
```bash
python comprehensive_evaluation.py
```

#### `hyperparameter_tuning.py`
Performs hyperparameter optimization for all models.

**Output:** `models/configs/`
- `isolation_forest_best.json` - Best Isolation Forest params
- `random_forest_best.json` - Best Random Forest params
- `gradient_boosting_best.json` - Best Gradient Boosting params
- `similarity_thresholds.json` - Optimal similarity thresholds

**Usage:**
```bash
python hyperparameter_tuning.py
```

## 📊 Expected Results

### Keystroke Anomaly Detection
- **Metric:** Anomaly Detection Rate
- **Target:** 10% anomaly rate (contamination parameter)
- **Use Case:** Detect unusual typing patterns (e.g., copy-paste, sudden speed changes)

### Behavioral Classification
- **Metrics:** Accuracy, Precision, Recall, F1, ROC-AUC
- **Target:** >85% accuracy, >80% F1 score
- **Use Case:** Classify cheating vs. honest behavior based on gaze, focus, etc.

### Similarity Detection
- **Metrics:** Accuracy, Precision, Recall, F1, ROC-AUC
- **Target:** >90% precision (low false positives)
- **Use Case:** Detect copied/similar answers between students

## 🔧 Troubleshooting

### "Dataset not found" errors
- Ensure datasets are downloaded to correct directories
- Check `DATASETS.md` for download links
- Verify directory structure matches expected layout

### Memory errors during training
- Reduce batch size for similarity training
- Limit dataset size during development
- Close other applications to free RAM

### sentence-transformers import errors
```bash
pip install sentence-transformers torch
```

### Slow training
- Use `--skip-existing` flag if retrying
- Train models individually instead of all at once
- Consider using GPU for similarity model training

## 🎯 Next Steps After Training

1. **Integration**: Update `app/ml/` modules to use trained models
2. **Testing**: Run integration tests with real exam data
3. **Deployment**: Copy models to production environment
4. **Monitoring**: Set up model performance tracking

## 📚 Additional Resources

- **Implementation Plan:** `../brain/.../implementation_plan.md`
- **Dataset Guide:** `../../DATASETS.md`
- **Research Guide:** `../../RESEARCH_GUIDE.md`
- **API Documentation:** See FastAPI docs at `http://localhost:8000/docs`

## 🤝 Contributing

When modifying training scripts:
1. Keep feature extraction consistent with production code
2. Save all model metadata for reproducibility
3. Document any new hyperparameters
4. Update this README accordingly
