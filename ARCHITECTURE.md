# Architecture

> System design documentation for the Cheating Detection System

---

## System Overview

The Cheating Detector is a **three-tier web application** that collects behavioral data from exam-takers, processes it through an ML pipeline, and presents risk assessments to administrators.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT TIER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Next.js Frontend (React 18 + TypeScript)                        │   │
│  │                                                                   │   │
│  │  /exam/[examId] ──► useBehaviorLogger hook ──► Event batching    │   │
│  │  /admin ──────────► Dashboard components ───► Risk visualization │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP/REST
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION TIER                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python 3.11+)                                  │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │  API Layer   │  │  Features    │  │  ML Layer            │   │   │
│  │  │              │  │              │  │                      │   │   │
│  │  │  /events     │  │  keystroke   │  │  BehaviorAnomaly     │   │   │
│  │  │  /sessions   │──►  hesitation  ├──►  Detector            │   │   │
│  │  │  /exams      │  │  paste       │  │  (Isolation Forest)  │   │   │
│  │  │  /analysis   │  │  focus       │  │                      │   │   │
│  │  │  /simulation │  │  pipeline    │  │  RiskFusionModel     │   │   │
│  │  │  /evaluation │  │              │  │  (Weighted Ensemble) │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             DATA TIER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐    │
│  │  SQLite/        │  │  JSONL Files    │  │  Pickle Models       │    │
│  │  PostgreSQL     │  │  (Event Logs)   │  │  (.pkl)              │    │
│  │                 │  │                 │  │                      │    │
│  │  Sessions       │  │  data/          │  │  models/             │    │
│  │  Exams          │  │  event_logs/    │  │  anomaly_detector    │    │
│  │  Answers        │  │  session_*.jsonl│  │  fusion_model        │    │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Communication

### Frontend → Backend Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│ useBehaviorLogger Hook (frontend/src/hooks/useBehaviorLogger.ts)     │
│                                                                       │
│ 1. Attach event listeners: keydown, keyup, paste, focus, blur        │
│ 2. Buffer events in memory (eventsBuffer: BehaviorEvent[])           │
│ 3. Flush when: batch size ≥ 50 OR interval ≥ 5000ms                  │
│ 4. POST to /api/events/log with { session_id, events }               │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Events API (backend/app/api/events.py)                               │
│                                                                       │
│ @router.post("/log")                                                 │
│ - Receives EventBatch { session_id, events[] }                       │
│ - Appends each event as JSONL to: data/event_logs/session_{id}.jsonl │
│ - Returns: { success, events_received, session_id }                  │
└──────────────────────────────────────────────────────────────────────┘
```

### Feature Extraction Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│ FeatureExtractor (backend/app/features/pipeline.py)                  │
│                                                                       │
│ WEIGHTS = { "typing": 0.25, "hesitation": 0.25,                      │
│             "paste": 0.25, "focus": 0.25 }                           │
│                                                                       │
│ Input: List[BehaviorEvent] from JSONL                                │
│                                                                       │
│ ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐     │
│ │ keystroke.py    │   │ hesitation.py   │   │ paste.py        │     │
│ │                 │   │                 │   │                 │     │
│ │ • typing_speed  │   │ • pause_count   │   │ • paste_count   │     │
│ │ • inter_key_ms  │   │ • max_pause_ms  │   │ • total_length  │     │
│ │ • std_deviation │   │ • backspace_cnt │   │ • paste_freq    │     │
│ └────────┬────────┘   └────────┬────────┘   └────────┬────────┘     │
│          │                     │                     │               │
│          └─────────────────────┼─────────────────────┘               │
│                                │                                     │
│                                ▼                                     │
│          ┌─────────────────────────────────────────────┐            │
│          │ SessionFeatures                              │            │
│          │ • typing_score, hesitation_score, etc.       │            │
│          │ • overall_score = weighted average           │            │
│          │ • is_flagged = overall_score > threshold     │            │
│          │ • flag_reasons = ["excessive paste", ...]    │            │
│          └─────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

### ML Risk Scoring

```
┌──────────────────────────────────────────────────────────────────────┐
│ BehaviorAnomalyDetector (backend/app/ml/anomaly.py)                  │
│                                                                       │
│ Model: sklearn.ensemble.IsolationForest(contamination=0.1)           │
│                                                                       │
│ Input: Feature vector (typing_speed, pause_count, paste_count, ...)  │
│ Output: AnomalyResult { is_anomaly, anomaly_score, factors[] }       │
│                                                                       │
│ Fallback: Heuristic detection if model not trained                   │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ RiskFusionModel (backend/app/ml/fusion.py)                           │
│                                                                       │
│ DEFAULT_WEIGHTS = { "behavioral": 0.35, "anomaly": 0.35,             │
│                     "similarity": 0.30 }                             │
│                                                                       │
│ final_risk = (behavioral × 0.35) + (anomaly × 0.35) + (sim × 0.30)   │
│                                                                       │
│ risk_level:                                                          │
│   • < 0.3  → "low"                                                   │
│   • < 0.5  → "medium"                                                │
│   • < 0.75 → "high"                                                  │
│   • ≥ 0.75 → "critical"                                              │
│                                                                       │
│ Output: FusionResult { final_risk_score, is_flagged, risk_level }    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Backend Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| `app/api/events.py` | `/api/events` | Event ingestion and storage |
| `app/api/sessions.py` | `/api/sessions` | Session lifecycle (create, start, submit) |
| `app/api/exams.py` | `/api/exams` | Exam and question management |
| `app/api/analysis.py` | `/api/analysis` | Feature extraction and risk scoring |
| `app/api/simulation.py` | `/api/simulation` | Training data generation |
| `app/api/evaluation.py` | `/api/evaluation` | Model performance metrics |
| `app/features/pipeline.py` | — | Feature extraction orchestration |
| `app/ml/anomaly.py` | — | Isolation Forest anomaly detection |
| `app/ml/fusion.py` | — | Multi-signal risk fusion |

### Frontend Components

| Component | Path | Responsibility |
|-----------|------|----------------|
| `useBehaviorLogger` | `hooks/useBehaviorLogger.ts` | DOM event capture and batching |
| `ExamPage` | `app/exam/[examId]/page.tsx` | Exam interface with behavior tracking |
| `AdminDashboard` | `app/admin/page.tsx` | Risk visualization and session drill-down |
| `QuestionRenderer` | `components/QuestionRenderer.tsx` | MCQ/Coding/Subjective question display |

---

## Data Storage

### Event Logs (JSONL Format)

Location: `data/event_logs/session_{uuid}.jsonl`

```json
{"session_id":"abc123","question_id":"q1","event_type":"key","data":{"key":"a","code":"KeyA"},"timestamp":1700000000000}
{"session_id":"abc123","question_id":"q1","event_type":"paste","data":{"content_length":150},"timestamp":1700000001000}
{"session_id":"abc123","question_id":"q1","event_type":"focus","data":{"type":"blur"},"timestamp":1700000002000}
```

### ML Models (Pickle Format)

Location: `models/`

| File | Model | Purpose |
|------|-------|---------|
| `anomaly_detector.pkl` | IsolationForest + StandardScaler | Behavioral anomaly detection |
| `fusion_model.pkl` | RandomForestClassifier | Final risk classification |

---

## Security Considerations

- **No content capture**: Only metadata (key codes, paste lengths) is logged—never actual text
- **JWT authentication**: Optional token-based auth via `python-jose`
- **CORS configuration**: Configurable allowed origins via environment variable
- **No webcam/microphone**: Privacy-preserving by design
