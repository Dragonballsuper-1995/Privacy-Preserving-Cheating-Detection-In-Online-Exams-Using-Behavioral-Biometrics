
# Cheating Detector ML Module

This module contains the machine learning pipeline for the Cheating Detector application.

## Components

### Data Loading
- **`ieee_loaders.py`**: 
  - Contains specific loader functions for IEEE datasets (Authcode, Ensemble, Liveness, etc.) and some local project datasets.
  - Handles parsing of various formats (CSV, ARFF, TXT).
- **`data_loader.py`**:
  - The main entry point for loading data.
  - Aggregates data from all sources via `load_all_training_data()`.
  - Handles synthetic data generation for balancing (if needed).

### Analysis & Feature Engineering
- **`eda_analysis.py`**:
  - Performs Exploratory Data Analysis (EDA) on the full dataset.
  - Generates `eda_report.txt` with class balance, missing values, and feature correlations.
- **`derived_features.py`**:
  - Computes additional behavioral metrics (ratios, combined scores).
- **`embeddings.py`**:
  - Uses sentence-transformers to generate embeddings for similarity detection.

### Training & Simulation
- **`train_model.py` / `training.py`**:
  - Loads the full dataset using `data_loader.py`.
  - Preprocesses data (Flattening -> Imputation -> Scaling).
  - Trains Random Forest classifiers and Isolation Forests.
  - Evaluates performance (Accuracy, Precision, Recall, F1).
  - Saves the trained model and scaler to `models/`.
- **`simulation.py`**:
  - Generates synthetic "honest" and "cheater" sessions for ML training pipeline.

### Inference & Explainability
- **`predictor.py`**:
  - Main inference interface for predicting risk scores from extracted features.
- **`explainability.py`**:
  - Tree SHAP implementation to interpret why a session was flagged and assign risk factor weights.
- **`fusion.py`**:
  - Combines multiple risk signals (anomaly, behavioral, similarity) into a final unified risk score.
- **`anomaly.py`**:
  - Isolation Forest implementation for unsupervised behavioral anomaly detection.

## Usage

1. **Analyze Data**:
   ```bash
   python backend/app/ml/eda_analysis.py
   ```

2. **Train Model**:
   ```bash
   python backend/app/ml/train_model.py
   ```

## Model Artifacts
Trained models are saved in the `models/` directory with timestamps. The latest model is always symlinked/copied to:
- `models/rf_model_latest.pkl`
- `models/scaler_latest.pkl`
