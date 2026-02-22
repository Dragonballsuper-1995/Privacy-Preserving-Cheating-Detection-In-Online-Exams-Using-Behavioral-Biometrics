# Research Guide

> Theoretical approach and methodology documentation

---

## Core Premise

This system is based on the hypothesis that **behavioral biometrics can distinguish between organic exam-taking and copying/cheating behavior** without invasive monitoring (webcam, microphone, screen capture).

---

## Theoretical Foundations

### 1. Keystroke Dynamics

> The characteristic typing rhythm of individuals is measurable and distinctive.

**Key Features Extracted** (from `app/features/keystroke.py`):
- Inter-key delay (time between key presses)
- Hold time (key press duration)
- Typing speed (WPM)
- Standard deviation of timing patterns

**Cheating Indicators**:
- Abnormally fast typing (copy-paste velocity)
- Lack of timing variance (machine-like)
- Missing think-type-correct cycles

**Reference**: Killourhy & Maxion, "Comparing Anomaly-Detection Algorithms for Keystroke Dynamics" (2009)

---

### 2. Hesitation Patterns

> Natural writing involves pauses for thought; copied content does not.

**Key Features Extracted** (from `app/features/hesitation.py`):
- Pause count (pauses > threshold)
- Maximum pause duration
- Pause-to-keystroke ratio
- Backspace/correction patterns

**Cheating Indicators**:
- Few natural pauses (direct pasting)
- Unusually long pauses (searching external sources)
- Low correction rate (copied content doesn't need editing)

---

### 3. Paste Behavior Analysis

> Excessive pasting of text indicates external source usage.

**Key Features Extracted** (from `app/features/paste.py`):
- Paste event count
- Total paste content length
- Average paste size
- Paste frequency

**Cheating Indicators**:
- Multiple large pastes
- Paste content exceeding expected answer length
- Pastes occurring without preceding typing

---

### 4. Focus Patterns

> Tab switching and window blur events suggest reference lookup.

**Key Features Extracted** (from `app/features/focus.py`):
- Blur count
- Total unfocused time
- Average blur duration
- Blur frequency

**Cheating Indicators**:
- Frequent tab switching
- Long periods of unfocus during questions
- Blur-to-typing correlation

---

## ML Approach

### Anomaly Detection (Isolation Forest)

**Implemented in**: `app/ml/anomaly.py`

```python
model = IsolationForest(contamination=0.1)
```

**Why Isolation Forest**:
- Unsupervised (no labeled cheating data needed initially)
- Effective for high-dimensional behavioral features
- Returns interpretable anomaly scores

**Feature Vector**:
```
[typing_speed, inter_key_delay_std, pause_count, max_pause,
 paste_count, paste_length, blur_count, unfocused_time]
```

### Risk Fusion (Weighted Ensemble)

**Implemented in**: `app/ml/fusion.py`

```python
DEFAULT_WEIGHTS = {
    "behavioral": 0.35,
    "anomaly": 0.35,
    "similarity": 0.30
}
```

**Why Weighted Fusion**:
- Combines multiple signal types
- Tunable weights based on domain knowledge
- Interpretable final score

---

## Risk Thresholds

From `app/core/config.py`:

```python
risk_threshold: float = 0.50      # Flagging threshold (lowered from 0.75)
similarity_threshold: float = 0.85 # Answer similarity threshold
min_pause_duration: int = 2000     # 2 seconds
max_typing_speed: int = 150        # WPM
```

---

## Flagging Logic

From `app/features/pipeline.py`:

Sessions are flagged when:
1. Overall score > `risk_threshold`
2. OR any of these conditions:
   - Paste score > 0.8 ("Excessive pasting")
   - Focus score > 0.7 ("Extended unfocused time")
   - Typing score pattern matches copy behavior
   - Long pauses followed by rapid input

---

## Privacy-Preserving Design

| What IS Captured | What IS NOT Captured |
|-----------------|---------------------|
| Key codes (a-z, 0-9) | Actual text content |
| Timing information | Webcam images |
| Paste content length | Audio recordings |
| Window focus state | Screen content |

---

## Limitations

1. **Baseline dependency**: Anomaly detection improves with more honest sessions
2. **Typing style variance**: Some honest students type unusually
3. **No content analysis**: Can't detect if pasted code is original or plagiarized
4. **Browser dependency**: Focus events depend on browser visibility API
