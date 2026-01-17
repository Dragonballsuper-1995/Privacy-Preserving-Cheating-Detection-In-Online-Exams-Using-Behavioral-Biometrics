"""
Evaluation Metrics and Model Performance Analysis

Provides tools for evaluating the cheating detection system:
- Classification metrics (accuracy, precision, recall, F1)
- Confusion matrix visualization
- ROC curve and AUC computation
- Per-category analysis
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json
import os

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    classification_report,
)

from app.core.config import settings
from app.features.pipeline import extract_all_features


@dataclass
class EvaluationResult:
    """Results from model evaluation."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc_roc: float
    confusion_matrix: List[List[int]]
    total_samples: int
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "auc_roc": self.auc_roc,
            "confusion_matrix": self.confusion_matrix,
            "total_samples": self.total_samples,
            "true_positives": self.true_positives,
            "true_negatives": self.true_negatives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
        }
    
    def __str__(self) -> str:
        return f"""
=== Evaluation Results ===
Total Samples: {self.total_samples}

Classification Metrics:
  Accuracy:  {self.accuracy:.4f}
  Precision: {self.precision:.4f}
  Recall:    {self.recall:.4f}
  F1 Score:  {self.f1:.4f}
  AUC-ROC:   {self.auc_roc:.4f}

Confusion Matrix:
  TN: {self.true_negatives}  FP: {self.false_positives}
  FN: {self.false_negatives}  TP: {self.true_positives}
"""


def load_labeled_dataset() -> List[Tuple[str, int]]:
    """
    Load the labeled training dataset from manifest.
    
    Returns:
        List of (session_id, label) tuples
    """
    manifest_path = os.path.join(settings.data_dir, "training_manifest.json")
    
    if not os.path.exists(manifest_path):
        return []
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    return [
        (s["session_id"], s["label"]) 
        for s in manifest.get("sessions", [])
    ]


def evaluate_model(threshold: float = 0.75) -> EvaluationResult:
    """
    Evaluate the cheating detection model on the training dataset.
    
    Args:
        threshold: Risk score threshold for classification
        
    Returns:
        EvaluationResult with all metrics
    """
    dataset = load_labeled_dataset()
    
    if not dataset:
        raise ValueError("No labeled dataset found. Generate training data first.")
    
    y_true = []
    y_pred = []
    y_scores = []
    
    for session_id, label in dataset:
        # Load events
        log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
        
        if not os.path.exists(log_file):
            continue
        
        events = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue
        
        if not events:
            continue
        
        # Extract features and get risk score
        features = extract_all_features(events, session_id)
        risk_score = features.overall_score
        
        y_true.append(label)
        y_scores.append(risk_score)
        y_pred.append(1 if risk_score >= threshold else 0)
    
    if len(y_true) < 2:
        raise ValueError("Not enough valid samples for evaluation")
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)
    
    # Compute metrics
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    
    # Handle edge cases for AUC
    try:
        auc = roc_auc_score(y_true, y_scores)
    except ValueError:
        auc = 0.5  # Default when only one class present
    
    return EvaluationResult(
        accuracy=accuracy_score(y_true, y_pred),
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        f1=f1_score(y_true, y_pred, zero_division=0),
        auc_roc=auc,
        confusion_matrix=cm.tolist(),
        total_samples=len(y_true),
        true_positives=int(tp),
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
    )


def find_optimal_threshold(
    thresholds: List[float] = None
) -> Tuple[float, EvaluationResult]:
    """
    Find the optimal classification threshold.
    
    Args:
        thresholds: List of thresholds to try
        
    Returns:
        Tuple of (optimal_threshold, results)
    """
    if thresholds is None:
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
    
    best_threshold = 0.75
    best_f1 = 0.0
    best_result = None
    
    for threshold in thresholds:
        try:
            result = evaluate_model(threshold)
            if result.f1 > best_f1:
                best_f1 = result.f1
                best_threshold = threshold
                best_result = result
        except Exception:
            continue
    
    return best_threshold, best_result


def generate_evaluation_report(output_path: str = None) -> str:
    """
    Generate a comprehensive evaluation report.
    
    Args:
        output_path: Optional path to save the report
        
    Returns:
        Report as a markdown string
    """
    try:
        result = evaluate_model()
        optimal_threshold, optimal_result = find_optimal_threshold()
    except ValueError as e:
        return f"# Evaluation Report\n\nError: {str(e)}\n\nGenerate training data first using the simulation API."
    
    report = f"""# Cheating Detection Evaluation Report

Generated: {__import__('datetime').datetime.now().isoformat()}

## Dataset Summary

- **Total Samples**: {result.total_samples}
- **Positive (Cheating)**: {result.true_positives + result.false_negatives}
- **Negative (Honest)**: {result.true_negatives + result.false_positives}

## Performance at Default Threshold (0.75)

| Metric | Value |
|--------|-------|
| Accuracy | {result.accuracy:.4f} |
| Precision | {result.precision:.4f} |
| Recall | {result.recall:.4f} |
| F1 Score | {result.f1:.4f} |
| AUC-ROC | {result.auc_roc:.4f} |

## Confusion Matrix

|  | Predicted Honest | Predicted Cheating |
|--|------------------|-------------------|
| **Actual Honest** | {result.true_negatives} | {result.false_positives} |
| **Actual Cheating** | {result.false_negatives} | {result.true_positives} |

## Optimal Threshold Analysis

The optimal threshold based on F1 score is: **{optimal_threshold}**

| Metric | Value |
|--------|-------|
| Accuracy | {optimal_result.accuracy:.4f} |
| Precision | {optimal_result.precision:.4f} |
| Recall | {optimal_result.recall:.4f} |
| F1 Score | {optimal_result.f1:.4f} |

## Interpretation

- **Precision**: {result.precision:.1%} of flagged sessions are actually cheating
- **Recall**: {result.recall:.1%} of cheating sessions are correctly detected
- **False Positive Rate**: {result.false_positives / (result.false_positives + result.true_negatives):.1%} of honest students wrongly flagged

## Recommendations

{"✅ Model performance is good (F1 > 0.7)" if result.f1 > 0.7 else "⚠️ Consider adjusting threshold or collecting more training data"}
"""
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
    
    return report
