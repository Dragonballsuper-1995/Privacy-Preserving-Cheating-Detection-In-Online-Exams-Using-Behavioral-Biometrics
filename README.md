# 🎓 Privacy-Preserving AI-Based Cheating Detection System

> **Camera-free, AI-powered online exam proctoring** using behavioral biometrics and answer similarity analysis.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [ML Pipeline](#ml-pipeline)
- [Research & Evaluation](#research--evaluation)
- [Contributing](#contributing)

---

## Overview

This system detects potential cheating in online exams **without invasive monitoring** (no camera or microphone). Instead, it analyzes:

| Signal | Description |
|--------|-------------|
| **Keystroke Dynamics** | Typing speed, rhythm, inter-key delays |
| **Hesitation Patterns** | Pauses, thinking time, delays |
| **Paste Behavior** | Copy-paste events, content length |
| **Focus/Blur** | Tab switching, window focus changes |
| **Answer Similarity** | Semantic similarity between student answers |

### Why Privacy-Preserving?

- ✅ No camera or microphone required
- ✅ No screen recording
- ✅ All ML processing happens locally
- ✅ Explainable results (human reviewable)
- ✅ GDPR-friendly design

---

## Features

### For Students
- Clean, distraction-free exam interface
- Monaco code editor for coding questions
- Timer and question navigation
- Immediate submission confirmation

### For Administrators
- Real-time session monitoring
- Risk score visualization (0-100%)
- Detailed behavioral analysis
- Event timeline viewer
- JSON export for research

### For Researchers
- Synthetic data generation
- Model training pipeline
- Configurable thresholds
- Extensible feature extraction

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │   Home   │  │   Exam   │  │  Admin   │  │ Behavior Logger  │ │
│  │   Page   │  │Interface │  │Dashboard │  │  (useBehavior)   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API │
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Events  │  │ Sessions │  │  Exams   │  │    Analysis      │ │
│  │   API    │  │   API    │  │   API    │  │   + Simulation   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ML PIPELINE                              ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐  ││
│  │  │ Keystroke │ │ Hesitation│ │   Paste   │ │    Focus    │  ││
│  │  │ Features  │ │ Features  │ │  Features │ │   Features  │  ││
│  │  └───────────┘ └───────────┘ └───────────┘ └─────────────┘  ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐                  ││
│  │  │ Anomaly   │ │ Similarity│ │  Fusion   │                  ││
│  │  │ Detection │ │  (NLP)    │ │  Model    │                  ││
│  │  └───────────┘ └───────────┘ └───────────┘                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │         STORAGE               │
              │  ┌─────────┐  ┌─────────────┐ │
              │  │ SQLite  │  │ JSONL Logs  │ │
              │  │   DB    │  │  (Events)   │ │
              │  └─────────┘  └─────────────┘ │
              └───────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Git

### 1. Clone & Setup

```bash
git clone <repository-url>
cd "Cheeating Detector"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Home Page |
| http://localhost:3000/exam/demo-exam-1 | Demo Exam |
| http://localhost:3000/admin | Admin Dashboard |
| http://localhost:8000/docs | API Documentation |

---

## API Documentation

### Core Endpoints

#### Events API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/events/log` | Log behavioral events |

#### Sessions API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/create` | Create exam session |
| POST | `/api/sessions/{id}/start` | Start session |
| POST | `/api/sessions/{id}/submit` | Submit exam |

#### Analysis API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/analyze` | Analyze session |
| GET | `/api/analysis/session/{id}/timeline` | Get event timeline |
| GET | `/api/analysis/dashboard/summary` | Dashboard stats |

#### Simulation API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simulation/simulate` | Generate test sessions |
| POST | `/api/simulation/generate-training-data` | Create training dataset |
| POST | `/api/simulation/train-models` | Train ML models |

---

## ML Pipeline

### Feature Extraction

| Module | Features |
|--------|----------|
| `keystroke.py` | Inter-key delay, hold time, typing speed, rhythm variance |
| `hesitation.py` | Pause count, duration, distribution, time to first keystroke |
| `paste.py` | Paste count, length, paste-after-blur correlation |
| `focus.py` | Blur count, unfocused time, extended absences |

### Risk Scoring Formula

```
Final Score = 0.35 × behavioral + 0.35 × anomaly + 0.30 × similarity
```

Where:
- **behavioral** = weighted feature scores from pipeline
- **anomaly** = Isolation Forest anomaly detection
- **similarity** = sentence-transformer cosine similarity

### Thresholds

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RISK_THRESHOLD` | 0.75 | Score for flagging |
| `SIMILARITY_THRESHOLD` | 0.85 | Answer similarity flag |
| `MIN_PAUSE_DURATION` | 2000ms | Pause detection |

---

## Research & Evaluation

### Generating Test Data

```bash
# Generate 50 honest + 20 cheating sessions
curl -X POST http://localhost:8000/api/simulation/generate-training-data \
  -H "Content-Type: application/json" \
  -d '{"honest_count": 50, "cheater_count": 20}'
```

### Training Models

```bash
curl -X POST http://localhost:8000/api/simulation/train-models
```

### Evaluation Metrics

The system supports the following evaluation metrics:

| Metric | Description |
|--------|-------------|
| **Accuracy** | Overall classification accuracy |
| **Precision** | True positives / (True + False positives) |
| **Recall** | True positives / (True + False negatives) |
| **F1 Score** | Harmonic mean of precision and recall |
| **AUC-ROC** | Area under ROC curve |

### Export for Analysis

Use the Admin Dashboard's "Export Data" button or:

```bash
curl http://localhost:8000/api/analysis/dashboard/summary > export.json
```

---

## Project Structure

```
Cheeating Detector/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Pages (home, exam, admin)
│   │   ├── components/      # React components
│   │   ├── hooks/           # useBehaviorLogger
│   │   └── lib/             # API client
│   └── package.json
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # REST endpoints
│   │   ├── core/            # Config, database
│   │   ├── features/        # Feature extraction
│   │   ├── ml/              # ML models
│   │   └── models/          # Database models
│   ├── data/                # Event logs, datasets
│   ├── models/              # Trained models
│   └── requirements.txt
│
├── DATASETS.md              # Research dataset guide
└── README.md                # This file
```

---

## Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=sqlite:///./data/cheating_detector.db

# Security
SECRET_KEY=your-secret-key

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# ML Thresholds
SIMILARITY_THRESHOLD=0.85
RISK_THRESHOLD=0.75

# Feature Extraction
MIN_PAUSE_DURATION=2000
MAX_TYPING_SPEED=150
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Citation

If you use this system in your research, please cite:

```bibtex
@software{cheating_detection_2024,
  title = {Privacy-Preserving AI-Based Cheating Detection System},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/your-repo}
}
```

---

<p align="center">
  Built with ❤️ for academic integrity research
</p>
