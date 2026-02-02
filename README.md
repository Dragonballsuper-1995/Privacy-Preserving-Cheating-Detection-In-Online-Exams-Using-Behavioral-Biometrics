# Cheating Detector

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Privacy-Preserving AI-Based Cheating Detection System**

A behavioral biometrics-based online exam proctoring system that detects cheating through analysis of keyboard and mouse interaction patterns—without using webcams, microphones, or screen capture.

---

## What It Does

This system monitors **how** students interact with an exam interface, not what they look like or what's on their screen. It analyzes:

| Signal | What's Captured | Why It Matters |
|--------|-----------------|----------------|
| **Keystroke Dynamics** | Typing speed, inter-key delays, rhythm | Copied answers show unnatural typing patterns |
| **Paste Behavior** | Frequency, content length, timing | Excessive pasting indicates external sources |
| **Focus/Blur Events** | Tab switches, window focus loss | Frequent switching suggests reference lookup |
| **Hesitation Patterns** | Long pauses, backspacing | Natural writing has different rhythm than copying |

The system computes a **risk score (0.0–1.0)** using a weighted fusion of behavioral, anomaly, and similarity signals.

---

## How It Works

```
┌────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                         │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  useBehaviorLogger Hook                                      │  │
│  │  • Captures keydown/keyup events                             │  │
│  │  • Tracks paste events (content length only)                 │  │
│  │  • Monitors window focus/blur                                │  │
│  │  • Batches events → POST /api/events/log                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ REST API
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Events API → JSONL Storage per Session                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Feature Extraction Pipeline                                 │  │
│  │  • KeystrokeFeatures: WPM, delays, rhythm                    │  │
│  │  • HesitationFeatures: pauses, backspace patterns            │  │
│  │  • PasteFeatures: count, lengths, frequency                  │  │
│  │  • FocusFeatures: blur count, unfocused duration             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  ML Models                                                   │  │
│  │  • Isolation Forest (anomaly detection)                      │  │
│  │  • Risk Fusion Model (weighted ensemble)                     │  │
│  │  Formula: risk = behavioral×0.35 + anomaly×0.35 + sim×0.30   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Admin Dashboard API                                         │  │
│  │  • Session list with risk scores                             │  │
│  │  • Drill-down timeline visualization                         │  │
│  │  • Export and evaluation metrics                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ (production) |
| Redis | 7+ (optional, for caching) |

### Backend Dependencies

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
scikit-learn>=1.4.0
sentence-transformers>=2.2.2
pandas>=2.1.4
numpy>=1.26.3
pytest>=7.4.4
```

### Frontend Dependencies

- Next.js 14
- TypeScript 5
- React 18

---

## Quick Start

### 1. Clone & Setup Environment

```bash
git clone <repo-url>
cd Cheating-Detector

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

---

## Project Structure

```
Cheating-Detector/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers
│   │   ├── features/      # Feature extraction modules
│   │   ├── ml/            # ML models (anomaly, fusion)
│   │   └── models/        # Pydantic/SQLAlchemy models
│   ├── data/datasets/     # Training datasets
│   ├── tests/             # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks (useBehaviorLogger)
│   │   └── lib/           # API utilities
│   └── package.json
├── models/                # Trained ML models (.pkl)
├── docker-compose.yml     # Production deployment
└── nginx/                 # Reverse proxy config
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and module communication |
| [API.md](API.md) | Complete REST API reference |
| [DATASETS.md](DATASETS.md) | Training data sources and structure |
| [TESTING.md](TESTING.md) | Test suite and coverage |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker and production setup |
| [ADMIN_DASHBOARD.md](ADMIN_DASHBOARD.md) | Admin features guide |
| [RESEARCH_GUIDE.md](RESEARCH_GUIDE.md) | Theoretical approach |
| [RESULTS.md](RESULTS.md) | Performance metrics |

---

## License

MIT License - See [LICENSE](LICENSE) for details.
