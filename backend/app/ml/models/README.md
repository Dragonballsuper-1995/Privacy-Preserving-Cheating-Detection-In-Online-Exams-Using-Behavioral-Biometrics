
# Trained Models

This directory contains trained machine learning models, scalers, and vectorizers for the Cheating Detector application.

Files are saved with timestamps to preserve history. The latest successful training run updates the `_latest.pkl` symlinks (copies).

## Key Files

- `rf_model_latest.pkl`: The current Random Forest Classifier.
- `scaler_latest.pkl`: StandardScaler for feature normalization.
- `vectorizer_latest.pkl`: DictVectorizer for feature extraction (sparse).
- `imputer_latest.pkl`: SimpleImputer for handling missing values.
- `feature_names_latest.pkl`: List of feature names corresponding to the model inputs.

## Usage

Load these artifacts using `joblib`:

```python
import joblib
import os

model_dir = "backend/app/ml/models"
model = joblib.load(os.path.join(model_dir, "rf_model_latest.pkl"))
vectorizer = joblib.load(os.path.join(model_dir, "vectorizer_latest.pkl"))

# Predict
features = vectorizer.transform([new_data_dict])
prediction = model.predict(features)
```
