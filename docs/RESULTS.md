# Results & Performance

> Model performance metrics and evaluation results

---

## Evaluation Framework

The system includes built-in evaluation capabilities via the Evaluation API and `app/ml/evaluation.py`.

---

## Available Metrics

From `app/ml/evaluation.py`:

| Metric | Description |
|--------|-------------|
| **Accuracy** | Overall correct predictions / total |
| **Precision** | True positives / (True positives + False positives) |
| **Recall** | True positives / (True positives + False negatives) |
| **F1 Score** | Harmonic mean of precision and recall |
| **AUC-ROC** | Area under ROC curve |

---

## Evaluation Endpoints

### Run Evaluation

```http
POST /api/evaluation/evaluate
{
  "threshold": 0.75
}
```

**Response**:
```json
{
  "accuracy": 0.85,
  "precision": 0.80,
  "recall": 0.90,
  "f1": 0.85,
  "auc_roc": 0.92,
  "confusion_matrix": [[40, 5], [2, 18]]
}
```

### Find Optimal Threshold

```http
GET /api/evaluation/optimal-threshold
```

**Response**:
```json
{
  "optimal_threshold": 0.65,
  "f1_score": 0.87,
  "metrics": {...}
}
```

---

## Simulation Statistics

Training data can be generated via:

```http
POST /api/simulation/generate-training-data
{
  "honest_count": 50,
  "cheater_count": 20
}
```

The simulation generates:
- **Honest sessions**: Normal typing speed (40-80 WPM), few pauses, no pasting, consistent focus
- **Cheater sessions**: Fast typing, large pastes, frequent blurs, irregular patterns

---

## Logging Structures

### Session Analysis Log

```json
{
  "session_id": "abc123",
  "overall_score": 0.65,
  "typing_score": 0.2,
  "hesitation_score": 0.5,
  "paste_score": 0.9,
  "focus_score": 0.6,
  "is_flagged": false,
  "flag_reasons": ["High paste content ratio"]
}
```

### Anomaly Detection Log

```json
{
  "session_id": "abc123",
  "is_anomaly": true,
  "anomaly_score": -0.25,
  "normalized_score": 0.73,
  "contributing_factors": ["high_paste_count", "low_keystroke_variance"]
}
```

---

## Model Persistence

Trained models are saved to `models/`:

| File | Model | Size |
|------|-------|------|
| `anomaly_detector.pkl` | IsolationForest + StandardScaler | ~1.2 MB |
| `fusion_model.pkl` | RandomForestClassifier (optional) | Variable |

---

## Generating Evaluation Report

```http
GET /api/evaluation/report
```

Returns a markdown-formatted report suitable for documentation or export.

---

## Limitations of Current Metrics

1. **Synthetic data dependency**: Initial evaluation relies on simulated sessions
2. **Class imbalance**: Cheating is rarer than honest behavior (typically 10-20%)
3. **No cross-validation**: Current evaluation is single-split
4. **No temporal validation**: Model doesn't account for user adaptation over time
