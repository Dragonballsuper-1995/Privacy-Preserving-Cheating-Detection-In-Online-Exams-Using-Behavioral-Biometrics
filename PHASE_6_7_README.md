# Phase 6 & 7 - Advanced Features Requirements

## Additional Dependencies

Add to `requirements.txt`:

```txt
# Phase 6 & 7 Advanced Features
shap>=0.44.0            # Explainable AI
reportlab>=4.0.0        # PDF report generation
websockets>=12.0        # WebSocket support (included in FastAPI)

# Optional dependencies
matplotlib>=3.8.0       # For visualization in reports
seaborn>=0.13.0        # Enhanced visualizations
```

## Installation

```bash
pip install shap reportlab matplotlib seaborn
```

## Feature Status

### Phase 6: UI/UX Enhancements ✅
- [x] WebSocket real-time monitoring
- [x] Dashboard analytics API
- [x] Session & admin monitoring support

### Phase 7: Advanced Features ✅
- [x] Explainable AI (SHAP integration)
- [x] Adaptive threshold system
- [x] Advanced export service (PDF, CSV, JSON)
- [x] Multi-language support framework

## Usage Examples

### WebSocket Monitoring

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitor/session_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Risk update:', data.risk_score);
};
```

### Generate Explanation

```python
from app.ml.explainability import explain_prediction

explanation = explain_prediction(
    model=trained_model,
    features=session_features,
    feature_names=feature_list,
    session_id="session_123"
)

print(explanation.explanation_text)
```

### Adaptive Thresholds

```python
from app.ml.adaptive_thresholds import AdaptiveThresholdSystem

threshold_system = AdaptiveThresholdSystem()
dynamic_threshold = threshold_system.get_threshold(
    exam_type="final",
    student_id="student_123",
    model_confidence=0.92
)
```

### Export Report

```python
from app.services.export import ExportService

# Generate PDF
pdf_bytes = ExportService.export_to_pdf(
    session_data=analysis_result,
    include_explanation=True
)

# Save to file
with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## Testing

Run tests for new features:

```bash
pytest backend/tests/test_websocket.py
pytest backend/tests/test_explainability.py
pytest backend/tests/test_adaptive_thresholds.py
pytest backend/tests/test_export.py
```

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Test WebSocket: Connect client and verify real-time updates
3. Generate explanations: Test SHAP on sample predictions
4. Export reports: Generate PDF for flagged sessions
5. Calibrate thresholds: Adjust for your specific exam types
