# 🔧 Quick Fixes for Admin Dashboard Issues

## Issues Found in Your Screenshot

![Admin Dashboard](C:/Users/sujal/.gemini/antigravity/brain/bcad8c0f-72bb-4f15-bc82-b91e7405e2d2/uploaded_image_1768721641295.png)

### Problem 1: ❌ No Timestamps on Sessions
**Issue:** Sessions only show IDs like "3a92f7fd..." with no date/time  
**Impact:** Can't find recent sessions

### Problem 2: ❌ 0 Flagged Sessions Despite High Risk
**Issue:** Sessions with 60-85% risk scores aren't flagged  
**Root Cause:** `risk_threshold` is set to **0.75 (75%)**  
**Current Behavior:** Only sessions >75% get flagged  
**Your Session:** 60% risk → NOT flagged (below 75%)

### Problem 3: ❌ Flag Logic Issue
**Issue:** Even sessions with 85% paste detection aren't flagged  
**Root Cause:** Overall risk is weighted average, not individual feature max

---

## 🚀 Solutions

### Solution 1: Lower the Risk Threshold

**Current:** 0.75 (75%) - Too strict!  
**Recommended:** 0.50 (50%) - More realistic

**Edit:** `backend/app/core/config.py`

```python
# ML Model Settings
similarity_threshold: float = 0.85
risk_threshold: float = 0.50  # ← Change from 0.75 to 0.50
```

**This will flag sessions with:**
- ✅ 50%+ overall risk
- ✅ Your 60% session will be flagged
- ✅ Any suspicious behavior

### Solution 2: Add Timestamps to Frontend

The frontend needs to display `start_time/created_at` for each session.

**Need to:**
1. Ensure backend returns timestamps
2. Format and display in frontend session list
3. Add sorting by most recent

### Solution 3: Add Individual Feature Flagging

**Option:** Flag if ANY individual feature >80%

```python
# Flag if overall risk >50% OR any single feature >80%
if risk_score > 0.50 or any(feature > 0.80 for feature in features):
    is_flagged = True
```

---

## 🎯 Quick Fix (Right Now)

### Step 1: Lower Threshold

```bash
# Edit config file
code backend/app/core/config.py

# Change line 24:
risk_threshold: float = 0.50  # was 0.75
```

### Step 2: Restart Backend

```bash
# The server should auto-reload
# Check terminal for: "Reloading..."
```

### Step 3: Create New Test Session

1. Go to student exam page
2. Do some suspicious behavior:
   - Paste content (Ctrl+V)
   - Switch tabs a few times
   - Pause for 30+ seconds
3. Check admin dashboard
4. Should now see flagged session!

---

## 📊 Understanding the Risk Scores

Looking at your selected session:

| Metric | Score | What it Means |
|--------|-------|---------------|
| **Overall Risk** | 60% | Weighted average of all features |
| **Typing** | 20% | Normal typing patterns |
| **Hesitation** | 65% | Moderate pausing |
| **Paste** | 85% | ⚠️ HIGH paste activity! |
| **Focus** | 65% | Moderate tab switching |

**Flag Reasons Detected:**
- ✅ Long pauses: 149 pauses > 15s
- ✅ Extended pause: 30.1s
- ✅ Content pasted: 6 paste events
- ✅ Large paste: 2144 characters

**With 0.50 threshold:** This session WILL be flagged ✅

---

## 🔍 Why 0 Flagged Sessions Currently

**Calculation:**
- 618 sessions total
- Average risk: 1%
- Your test session: 60%
- Threshold: 75%

**Result:** 60% < 75% → Not flagged

**After changing to 50%:**
- All sessions >50% risk will be flagged
- Your 60% session: ✅ Flagged!
- Expected: ~10-15 flagged sessions

---

## 📅 Adding Timestamps (Frontend Fix)

I'll need to see your frontend code to add timestamps. The sessions need to show:

```
Session: 3a92f7fd...
Created: Jan 18, 2026 1:04 PM
Events: 1302
Risk: 62%
```

Would you like me to:
1. ✅ Update the threshold configuration?
2. ✅ Create frontend code to display timestamps?
3. ✅ Add better flagging logic?

---

## 🎯 Immediate Action

**Run this command:**

```bash
# Edit config
notepad backend\app\core\config.py

# Find line ~24 and change:
# FROM: risk_threshold: float = 0.75
# TO:   risk_threshold: float = 0.50

# Save and backend will auto-reload
```

**Then test again!** Your sessions should start getting flagged.

Let me know if you want me to make these changes directly!
