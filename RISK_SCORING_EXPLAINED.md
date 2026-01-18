# Risk Scoring Formula Explained

## 🎯 How Risk Scores Are Calculated

### **Formula:**

```python
# Weighted average of 3 components
final_risk_score = (
    behavioral_score * 0.35 +
    anomaly_score * 0.35 +
    similarity_score * 0.30
)
```

### **Component Breakdown:**

#### 1. **Behavioral Score (35% weight)**
Combines individual feature scores:

```python
behavioral_score = weighted_average([
    typing_score * weight_typing,
    hesitation_score * weight_hesitation,
    paste_score * weight_paste,
    focus_score * weight_focus
])
```

**Individual Feature Scoring:**
- **Typing:** Abnormal typing patterns (speed, rhythm)
- **Hesitation:** Unusual pauses (too many or too long)
- **Paste:** Copy-paste behavior detected
- **Focus:** Tab switching, window blur events

Each feature is scored 0-1:
- 0.0 = Normal behavior
- 1.0 = Highly suspicious behavior

#### 2. **Anomaly Score (35% weight)**
From Isolation Forest ML model:

```python
# Detects patterns that deviate from normal student behavior
anomaly_score = isolation_forest.decision_function(features)
# Normalized to 0-1 range
```

**What it detects:**
- Unusual combinations of behaviors
- Outliers compared to normal students
- Statistical anomalies

#### 3. **Similarity Score (30% weight)**
Answer similarity detection:

```python
# Compares answers between students
similarity_score = max(
    similarity_to_other_students
)
```

**Currently:** Uses semantic text similarity
**Note:** Requires multiple students for comparison

---

## 📊 Risk Levels

| Risk Score | Level | Action |
|------------|-------|--------|
| 0% - 30% | **Low** | No action needed |
| 30% - 60% | **Medium** | Monitor |
| 60% - 80% | **High** | Review recommended |
| 80% - 100% | **Critical** | Manual review required |

---

## 🚩 Flagging Threshold

**Current Setting:** `risk_threshold = 0.50` (50%)

**Formula:**
```python
is_flagged = final_risk_score >= risk_threshold
```

**Your case:**
- Final risk score: 60%
- Threshold: 50%
- Result: ✅ **FLAGGED** (60% >= 50%)

---

## 📐 Example Calculation

**Your Session:**
```
Typing Score: 20% (0.20)
Hesitation Score: 65% (0.65)
Paste Score: 85% (0.85)
Focus Score: 65% (0.65)

Step 1: Calculate Behavioral Score
behavioral = (0.20 + 0.65 + 0.85 + 0.65) / 4 = 0.5875 (59%)

Step 2: Calculate Anomaly Score
anomaly = 0.65 (65% - from Isolation Forest)

Step 3: Calculate Similarity Score
similarity = 0.30 (30% - no similar answers found)

Step 4: Weighted Fusion
final_risk = (0.5875 * 0.35) + (0.65 * 0.35) + (0.30 * 0.30)
           = 0.2056 + 0.2275 + 0.09
           = 0.5231 → 52.3%

However, your dashboard shows 60%...
```

**Note:** The actual calculation might use different weights or additional factors. Let me check your specific case.

---

## 🔧 Why Sorting Might Not Work

**Issue:** Backend might not be returning `created_at` field

**Solutions:**
1. Backend needs to include timestamps in API response
2. Generate timestamp from session_id if needed
3. Use fallback sorting method

---

## 📂 Session Categorization

**To split into Real vs Simulated:**

### Option 1: Add `is_simulated` flag in backend
```python
session = {
    "session_id": "...",
    "is_simulated": True,  # ← Add this flag
    "risk_score": 0.60,
    # ...
}
```

### Option 2: Use naming convention
- Real sessions: `session-{uuid}`
- Simulated: `sim-{uuid}` or `test-{uuid}`

### Option 3: Track in separate endpoint
- `/api/sessions/real` - Only real exams
- `/api/sessions/simulated` - Only generated

---

**Would you like me to:**
1. ✅ Fix the timestamp sorting issue?
2. ✅ Add session categorization (Real vs Simulated)?
3. ✅ Show the exact formula being used in your case?

Let me implement these fixes!
