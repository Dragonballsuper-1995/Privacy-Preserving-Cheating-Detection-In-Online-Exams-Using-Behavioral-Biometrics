# Admin Dashboard Guide

Complete guide for using and understanding the Admin Dashboard for monitoring exam sessions and detecting cheating behavior.

## Table of Contents

1. [Overview](#overview)
2. [Accessing the Dashboard](#accessing-the-dashboard)
3. [Dashboard Features](#dashboard-features)
4. [Understanding Risk Scores](#understanding-risk-scores)
5. [Session Analysis](#session-analysis)
6. [Recent Fixes & Updates](#recent-fixes--updates)

---

## Overview

The Admin Dashboard provides real-time monitoring and analysis of exam sessions, allowing administrators to:

- View all exam sessions with risk scores
- Identify potentially suspicious behavior
- Analyze session details and behavioral patterns
- Review flagged sessions
- Distinguish between real and simulated sessions

**Access URL**: `http://localhost:3000/admin`

---

## Accessing the Dashboard

### Prerequisites

1. Backend server running: `uvicorn app.main:app --reload`
2. Frontend server running: `npm run dev`
3. At least one exam session completed

### Navigation

1. Start frontend: `cd frontend && npm run dev`
2. Open browser: `http://localhost:3000`
3. Click "Admin Dashboard" or navigate to `/admin`

---

## Dashboard Features

### 1. **Session Overview**

Displays all exam sessions with key metrics:

- **Session ID**: Unique identifier for each session
- **Risk Score**: Calculated behavioral risk (0-100)
- **Status**: Whether session is flagged
- **Event Count**: Number of tracked events
- **Timestamp**: When session was created
- **Session Type**: Real or Simulated

### 2. **Filtering & Sorting**

- Filter by flagged/not flagged
- Filter by simulated/real sessions
- Sort by risk score, timestamp, event count
- Search by session ID

### 3. **Risk Indicators**

Color-coded visual indicators:

- 🟢 **Green** (< 40): Low risk, normal behavior
- 🟡 **Yellow** (40-70): Medium risk, worth reviewing
- 🔴 **Red** (> 70): High risk, likely cheating

### 4. **Session Details**

Click any session to view:

- Detailed risk score breakdown
- Flag reasons
- Event timeline
- Individual metrics (typing, hesitation, paste, focus)

---

## Understanding Risk Scores

### Risk Score Components

The overall risk score is calculated from four behavioral metrics:

```
overall_score = (typing_score + hesitation_score + paste_score + focus_score) / 4
```

#### 1. **Typing Score** (0-100)
- Analyzes keystroke dynamics
- Unusual typing patterns
- Inconsistent timing

#### 2. **Hesitation Score** (0-100)
- Long pauses between actions
- Frequent hesitations
- Pattern interruptions

#### 3. **Paste Score** (0-100)
- Copy-paste behavior
- External content insertion
- Large text pastes

#### 4. **Focus Score** (0-100)
- Tab switching
- Window blur events
- Loss of focus during exam

### Flagging Thresholds

Sessions are flagged as suspicious when:

- **Overall score > 70**: High risk
- **Paste count > 5**: Excessive copying
- **Blur count > 10**: Frequent tab switching
- **Long pauses > 30s**: Extended idle time

### Risk Scoring Formula

**Detailed Formula** (from backend):

```python
# Keystroke Analysis
typing_score = deviation_from_baseline * 100

# Hesitation Analysis  
hesitation_score = (pause_count / total_events) * 100

# Paste Analysis
paste_score = (paste_count * 20) + (total_paste_length /  1000)

# Focus Analysis
focus_score = (blur_count * 10) + (unfocused_time / 60)

# Combined Score
overall_score = (typing + hesitation + paste + focus) / 4
```

---

## Session Analysis

### Analyzing a Flagged Session

**Step 1: Identify High-Risk Sessions**
- Look for red indicators (risk > 70)
- Check flag reasons

**Step 2: Review Metrics**
- **High paste score**: Check paste_count and total_paste_length
- **High focus score**: Look at blur_count and unfocused_time
- **High typing score**: Examine keystroke anomalies
- **High hesitation score**: Review pause patterns

**Step 3: Timeline Analysis**
- View event timeline
- Look for suspicious patterns
- Check timing of paste/blur events

**Step 4: Make Decision**
- Compare with other sessions from same student
- Consider context (question difficulty, time constraints)
- Flag for manual review if needed

### Common Patterns

**Normal Behavior:**
- ✅ Consistent typing speed
- ✅ Few pauses (thinking time)
- ✅ Minimal focus loss
- ✅ No paste events

**Suspicious Behavior:**
- 🚩 Many paste events
- 🚩 Frequent tab switching
- 🚩 Long idle periods followed by rapid answers
- 🚩 Inconsistent typing patterns

---

## Recent Fixes & Updates

### Session Timestamps ✅

**Fixed**: All sessions now display creation timestamps

**Implementation**:
- Uses file modification time for existing sessions
- Displays in human-readable format
- Sorted by most recent first

### Session Type Detection ✅

**Fixed**: Sessions correctly identified as "Real" or "Simulated"

**Detection Logic**:
1. Check for metadata file (`session_{id}.meta.json`)
2. Read `is_simulated` flag from metadata
3. Fallback: Check session ID pattern (`sim-` or `test-` prefix)

**Display**:
- 🎯 Real sessions: User-initiated exams
- 🔬 Simulated sessions: Testing/development data

### Flagging Accuracy ✅

**Fixed**: Sessions flagged correctly based on risk thresholds

**Threshold Configuration** (in `backend/app/core/config.py`):
```python
risk_threshold: float = 70.0  # Adjustable
```

**Flag Reasons**:
- High overall risk score (> 70)
- Excessive paste behavior
- Excessive tab switching
- Unusual typing patterns

### Risk Scoring Explanation ✅

**Added**: Clear documentation of scoring formula

**Location**: `RISK_SCORING_EXPLAINED.md` (merged into RESULTS.md)

**Features**:
- Mathematical formula breakdown
- Component weight distribution
- Example calculations
- Threshold justifications

---

## Dashboard Configuration

### Adjusting Risk Thresholds

Edit `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Risk scoring
    risk_threshold: float = 70.0  # Main threshold
    min_pause_duration: int = 2000  # ms
    
    # Flagging criteria
    max_allowed_pastes: int = 5
    max_allowed_blurs: int = 10
```

### Custom Dashboard Queries

Use the API directly for custom analysis:

```python
# Get all flagged sessions
GET /api/analysis/dashboard/summary

# Get specific session details
GET /api/analysis/session/{session_id}/features

# Get session timeline
GET /api/analysis/session/{session_id}/timeline
```

---

## Troubleshooting

### No Sessions Displayed

**Issue**: Dashboard is empty

**Solutions**:
1. Ensure backend is running (`uvicorn app.main:app --reload`)
2. Check that `backend/data/event_logs/` directory exists
3. Take a test exam to generate session data

### Incorrect Risk Scores

**Issue**: Scores don't match expectations

**Check**:
1. Event logs are being created (`backend/data/event_logs/session_*.jsonl`)
2. Events have correct timestamps
3. Risk threshold configuration

### Sessions Not Flagged

**Issue**: High-risk sessions not showing as flagged

**Verify**:
1. Risk threshold setting (`risk_threshold` in config)
2. Session score calculation
3. Backend logs for errors

---

## Best Practices

1. **Regular Review**: Check dashboard after each exam session
2. **Threshold Tuning**: Adjust based on your use case and student population
3. **Context Matters**: Consider question difficulty and time pressure
4. **Manual Review**: Always manually review flagged sessions before taking action
5. **Pattern Analysis**: Look for patterns across multiple sessions from same student
6. **Documentation**: Keep records of  flagged sessions and outcomes

---

## API Endpoints

For programmatic access:

```bash
# Dashboard summary
GET /api/analysis/dashboard/summary

# Analyze session
POST /api/analysis/analyze
Body: {"session_id": "...", "include_features": true}

# Session features
GET /api/analysis/session/{session_id}/features

# Session timeline
GET /api/analysis/session/{session_id}/timeline
```

---

## Future Enhancements

Planned improvements:

- [ ] Real-time session monitoring
- [ ] Advanced filtering and search
- [ ] Export functionality (CSV, PDF reports)
- [ ] Session comparison tools
- [ ] Historical trend analysis
- [ ] Email notifications for high-risk sessions
- [ ] Customizable dashboard widgets

---

**For detailed technical implementation**, see:
- Backend analysis: `backend/app/api/analysis.py`
- Frontend dashboard: `frontend/src/app/admin/page.tsx`
- Risk scoring: `RESULTS.md`
