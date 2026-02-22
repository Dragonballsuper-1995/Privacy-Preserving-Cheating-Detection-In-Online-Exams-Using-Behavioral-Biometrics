# Admin Dashboard Guide

> Administrator features and functionality documentation

---

## Overview

The Admin Dashboard is a Next.js page accessible at `/admin` that provides visibility into exam sessions and cheating risk assessments.

**Location**: `frontend/src/app/admin/page.tsx`

---

## Features

### 1. Session Summary View

| Metric | Description |
|--------|-------------|
| **Total Sessions** | Count of all exam sessions |
| **Flagged Sessions** | Sessions exceeding risk threshold |
| **Risk Distribution** | Visual breakdown by risk level |

### 2. Session List

Each session displays:

| Field | Description |
|-------|-------------|
| `session_id` | Unique identifier |
| `risk_score` | Overall risk (0.0–1.0) |
| `is_flagged` | Boolean flag status |
| `event_count` | Number of behavioral events |
| `flag_reasons` | Array of specific concerns |
| `created_at` | Session timestamp |
| `is_simulated` | Whether session is synthetic |

### 3. Score Breakdown

Per-session scores for:
- **Typing Score**: Keystroke dynamics anomalies
- **Hesitation Score**: Pause pattern anomalies
- **Paste Score**: Copy-paste behavior
- **Focus Score**: Tab switching behavior

### 4. Session Drill-Down

Click a session to view:
- Complete event timeline
- Feature extraction details
- Per-question analysis

---

## Risk Level Color Coding

Based on code logic in `AdminDashboard`:

```typescript
function getRiskColor(score: number) {
    if (score >= 0.75) return 'red';     // Critical
    if (score >= 0.5) return 'orange';   // High
    if (score >= 0.3) return 'yellow';   // Medium
    return 'green';                       // Low
}
```

| Score Range | Level | Color |
|-------------|-------|-------|
| ≥0.75 | Critical | Red |
| 0.50–0.74 | High | Orange |
| 0.30–0.49 | Medium | Yellow |
| <0.30 | Low | Green |

---

## API Endpoints Used

The dashboard relies on endpoints from the [Analysis API](API.md#analysis-api) and the [Dashboard API](API.md#dashboard-api).

| Purpose | References |
|---------|---------|
| Admin Summary & Analytics | `GET /api/dashboard/...` |
| Session Analysis | `POST /api/analysis/analyze` |
| Event Timeline | `GET /api/analysis/timeline/{session_id}` |
| Extracted Features | `GET /api/analysis/features/{session_id}` |

---

## Risk Scoring Formula

The risk scoring logic is documented in [ARCHITECTURE.md](ARCHITECTURE.md#ml-risk-scoring). It combines the behavioral extraction score, anomaly score (Isolation Forest), and answer similarity into a single risk classification.

---

## Data Types

```typescript
interface SessionSummary {
    session_id: string;
    risk_score: number;
    is_flagged: boolean;
    event_count: number;
    flag_reasons: string[];
    scores: {
        typing: number;
        hesitation: number;
        paste: number;
        focus: number;
    };
    created_at?: string;
    is_simulated?: boolean;
}

interface DashboardData {
    total_sessions: number;
    flagged_sessions: number;
    sessions: SessionSummary[];
}
```

---

## Accessing the Dashboard

1. Start the frontend: `npm run dev`
2. Navigate to: `http://localhost:3000/admin`

---

## Export Functionality

The dashboard supports exporting session data for further analysis.

---

## Limitations

1. **No authentication gate** (currently): Dashboard is publicly accessible
2. **No real-time updates**: Requires page refresh to see new sessions
3. **No pagination**: All sessions loaded at once (may be slow for large datasets)
