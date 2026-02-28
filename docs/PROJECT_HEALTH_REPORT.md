# 📊 Project Health Report — Cheating Detector

> **Generated**: 2026-02-28 11:31:35

## Executive Summary

| Dimension | Key Metric | Grade |
|-----------|-----------|-------|
| Test Coverage | 57.9% | **C** |
| Code Quality | 9.04/10 | **A** |
| Complexity | Avg CC: 15.7 | **C** |
| Security | 0 vulns | **A** |
| ML Performance | F1: 1.0 | **A** |
| API Traceability | 100.0% | **A** |
| **Overall** | | **A-** |

<details>
<summary>Grading Rubric</summary>

| Grade | Test Coverage | Pylint | Complexity | Security | ML F1 |
|-------|-------------|--------|-----------|----------|-------|
| A | ≥80% | ≥8.0/10 | Avg CC ≤5 | 0 high/critical | ≥0.85 |
| B | ≥60% | ≥6.0/10 | Avg CC ≤10 | 0 critical | ≥0.70 |
| C | ≥40% | ≥4.0/10 | Avg CC ≤20 | ≤2 high | ≥0.55 |
| D | <40% | <4.0/10 | Avg CC >20 | >2 high | <0.55 |

</details>

---

## Section 1: Test Coverage
**Overall Backend Coverage: 57.9%** — Grade: **C**

| Metric | Value |
|--------|-------|
| Tests Passed | 172 |
| Tests Failed | 28 |
| Tests Errors | 0 |
| Coverage | 57.9% |

### Per-Module Coverage

| Module | Avg Coverage | Files |
|--------|-------------|-------|
| `api` | 67.2% | 14 |
| `app` | 100.0% | 1 |
| `core` | 74.2% | 6 |
| `features` | 73.3% | 12 |
| `main.py` | 72.7% | 1 |
| `ml` | 52.1% | 14 |
| `models` | 95.6% | 5 |
| `utils` | 74.2% | 1 |


---

## Section 2: Code Quality
**Backend Pylint Score: 9.04/10** — Grade: **A**

### Backend (Python)

| Tool | Metric | Value |
|------|--------|-------|
| Pylint | Overall Score | 9.04/10 |
| Pylint | Errors | 3 |
| Pylint | Warnings | 212 |
| Pylint | Refactor | 86 |
| Pylint | Convention | 171 |
| Flake8 | Issues | 0 |

### Frontend (TypeScript)

| Tool | Metric | Value |
|------|--------|-------|
| ESLint | Errors | 0 |
| ESLint | Warnings | 0 |


---

## Section 3: Code Complexity
**Average Cyclomatic Complexity: 15.7** — Grade: **C**

> Complexity grades: A (1-5), B (6-10), C (11-20), D (21+)

### High-Complexity Functions (CC > 10)

| File | Function | Complexity | Rank |
|------|----------|-----------|------|
| `app/features/editing_patterns.py` | `extract_editing_features` | 28 | D |
| `app/features/paste.py` | `extract_paste_features` | 26 | D |
| `app/features/text_analysis.py` | `analyze_text` | 26 | D |
| `app/features/navigation.py` | `extract_navigation_features` | 25 | D |
| `app/api/analysis.py` | `get_dashboard_summary` | 23 | D |
| `app/features/keystroke.py` | `extract_keystroke_features` | 23 | D |
| `app/features/pipeline.py` | `_generate_flag_reasons` | 20 | C |
| `app/ml/data_loader.py` | `load_keystroke_reverse_problem_data` | 19 | C |
| `app/ml/data_loader.py` | `load_behacom_data` | 18 | C |
| `app/ml/predictor.py` | `predict` | 18 | C |
| `app/features/focus.py` | `extract_focus_features` | 17 | C |
| `app/ml/explainability.py` | `_fallback_explanation` | 17 | C |
| `app/features/hesitation.py` | `extract_hesitation_features` | 16 | C |
| `app/features/mouse_advanced.py` | `_analyze_movements` | 16 | C |
| `app/features/pipeline.py` | `extract_features` | 16 | C |
| `app/features/similarity.py` | `detect` | 16 | C |
| `app/ml/data_loader.py` | `load_emosurv_keystroke_data` | 15 | C |
| `app/ml/evaluation.py` | `cross_validate_model` | 15 | C |
| `app/ml/explainability.py` | `_shap_explanation` | 15 | C |
| `app/utils/question_loader.py` | `filter_questions` | 15 | C |


---

## Section 4: Security Audit
**Total Vulnerabilities Found: 0** — Grade: **A**

### Backend (pip-audit)

✅ No known vulnerabilities found in Python dependencies.

### Frontend (npm audit)

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Moderate | 0 |
| Low | 0 |
| **Total** | **0** |


---

## Section 5: ML Model Evaluation
**Training Dataset**: 3 sessions (2 honest, 1 cheating)

### Classification Metrics (threshold = 0.75)

| Metric | Value |
|--------|-------|
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 Score | 1.000 |
| AUC-ROC | 1.000 |

### Confusion Matrix

| | Predicted Honest | Predicted Cheating |
|---|---|---|
| **Actual Honest** | 2 (TN) | 0 (FP) |
| **Actual Cheating** | 0 (FN) | 1 (TP) |

### Optimal Threshold

**Best threshold: 0.4** (F1 = 1.000)

> ⚠️ Cross-validation error: Need at least 6 labeled samples for 3-fold CV


---

## Section 6: API Endpoint Traceability
**Endpoints with Test Coverage: 59/59 (100.0%)** — Grade: **A**

**Total Test Functions**: 200

### Endpoint Coverage Map

| Module | Method | Path | Tested |
|--------|--------|------|--------|
| `analysis.py` | POST | `/api/analysis/analyze` | ✅ |
| `analysis.py` | POST | `/api/analysis/analyze/questions` | ✅ |
| `analysis.py` | GET | `/api/analysis/session/{session_id}/features` | ✅ |
| `analysis.py` | GET | `/api/analysis/session/{session_id}/timeline` | ✅ |
| `analysis.py` | GET | `/api/analysis/dashboard/summary` | ✅ |
| `analysis.py` | GET | `/api/analysis/export/csv` | ✅ |
| `authentication.py` | POST | `/api/auth/register` | ✅ |
| `authentication.py` | POST | `/api/auth/login` | ✅ |
| `authentication.py` | POST | `/api/auth/login/form` | ✅ |
| `authentication.py` | GET | `/api/auth/me` | ✅ |
| `code_execution.py` | POST | `/api/code/execute` | ✅ |
| `code_execution.py` | POST | `/api/code/run-tests` | ✅ |
| `code_execution.py` | GET | `/api/code/languages` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/summary` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/risk-distribution` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/trends` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/flagged-sessions` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/exam-analytics/{exam_id}` | ✅ |
| `dashboard.py` | GET | `/api/dashboard/dashboard/realtime-stats` | ✅ |
| `evaluation.py` | POST | `/api/evaluation/evaluate` | ✅ |
| `evaluation.py` | GET | `/api/evaluation/optimal-threshold` | ✅ |
| `evaluation.py` | GET | `/api/evaluation/report` | ✅ |
| `evaluation.py` | GET | `/api/evaluation/dataset-info` | ✅ |
| `events.py` | POST | `/api/events/log` | ✅ |
| `events.py` | GET | `/api/events/session/{session_id}` | ✅ |
| `exams.py` | GET | `/api/exams/list` | ✅ |
| `exams.py` | GET | `/api/exams/{exam_id}` | ✅ |
| `exams.py` | POST | `/api/exams/create` | ✅ |
| `exams.py` | POST | `/api/exams/{exam_id}/questions` | ✅ |
| `exams.py` | PATCH | `/api/exams/{exam_id}` | ✅ |
| `exams.py` | DELETE | `/api/exams/{exam_id}` | ✅ |
| `exams.py` | PATCH | `/api/exams/{exam_id}/publish` | ✅ |
| `exams.py` | PATCH | `/api/exams/{exam_id}/schedule` | ✅ |
| `exams.py` | GET | `/api/exams/categories` | ✅ |
| `exams.py` | GET | `/api/exams/subjects` | ✅ |
| `exams.py` | GET | `/api/exams/topics` | ✅ |
| `exams.py` | GET | `/api/exams/questions/search` | ✅ |
| `exams.py` | GET | `/api/exams/questions/random` | ✅ |
| `exams.py` | GET | `/api/exams/{exam_id}/by-category` | ✅ |
| `main.py` | GET | `/` | ✅ |
| `main.py` | GET | `/health` | ✅ |
| `main.py` | GET | `/metrics` | ✅ |
| `models.py` | GET | `/api/models/metrics` | ✅ |
| `models.py` | POST | `/api/models/retrain` | ✅ |
| `reviews.py` | POST | `/api/reviews/{session_id}` | ✅ |
| `sessions.py` | POST | `/api/sessions/create` | ✅ |
| `sessions.py` | GET | `/api/sessions/{session_id}` | ✅ |
| `sessions.py` | POST | `/api/sessions/{session_id}/start` | ✅ |
| `sessions.py` | POST | `/api/sessions/{session_id}/submit` | ✅ |
| `sessions.py` | POST | `/api/sessions/{session_id}/answer` | ✅ |
| `sessions.py` | GET | `/api/sessions/list/all` | ✅ |
| `sessions.py` | GET | `/api/sessions/{session_id}/result` | ✅ |
| `simulation.py` | POST | `/api/simulation/simulate` | ✅ |
| `simulation.py` | POST | `/api/simulation/generate-training-data` | ✅ |
| `simulation.py` | POST | `/api/simulation/train-models` | ✅ |
| `simulation.py` | GET | `/api/simulation/status` | ✅ |
| `websocket.py` | WEBSOCKET | `/ws/monitor/{session_id}` | ✅ |
| `websocket.py` | WEBSOCKET | `/ws/admin` | ✅ |
| `websocket.py` | WEBSOCKET | `/ws/stream-events/{session_id}` | ✅ |

### Test Inventory

| Test File | Functions |
|-----------|----------|
| `test_all_endpoints.py` | 70 |
| `test_auth.py` | 14 |
| `test_feature_extractors.py` | 41 |
| `test_features.py` | 17 |
| `test_integration.py` | 12 |
| `test_ml_advanced.py` | 11 |
| `test_ml_modules.py` | 19 |
| `test_performance.py` | 6 |
| `test_smoke.py` | 5 |
| `test_utils.py` | 5 |


---

*This report was auto-generated by `scripts/generate_health_report.py` on 2026-02-28 11:31:35. Re-run the script to refresh all metrics.*
