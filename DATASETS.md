# Datasets Master Document

> **Purpose**: Comprehensive inventory of all datasets in `backend/data/datasets` with source attribution, content summaries, and project relevance.

---

## Summary Statistics

| Category | Datasets | Total Files |
|----------|----------|-------------|
| Exam Behavior | 2 | ~61 |
| Keystroke Dynamics | 7 | ~600+ |
| Mouse Dynamics | 3 | ~200+ |
| Plagiarism Detection | 3 | ~40,000+ |

---

## Exam Behavior Datasets

### 1. Student Suspicious Behaviors Detection Dataset

| Field | Value |
|-------|-------|
| **Local Path** | `exam_behavior/student_suspicion/` |
| **Matched Source** | [Kaggle: Student Suspicious Behaviors Detection](https://www.kaggle.com/datasets/gsmohamedu/students-suspicious-behaviors-detection-dataset) |
| **Data Type** | CSV (tabular) |
| **Content Summary** | Face tracking data with columns: `face_present`, `face_x`, `face_y`, `face_pitch`, `face_roll`, `gaze_on_script`, `phone_in_hand`, `label`. Tracks student behavior during exams. |
| **Relevance** | **HIGH** - Direct cheating detection via behavioral biometrics |

### 2. Cheating Scenarios

| Field | Value |
|-------|-------|
| **Local Path** | `exam_behavior/cheating_scenarios/` |
| **Matched Source** | [UNIDENTIFIED] |
| **Data Type** | 60 scenario subdirectories |
| **Content Summary** | Labeled cheating scenario data organized by scenario number (Scenario_1 through Scenario_60) |
| **Relevance** | **HIGH** - Ground truth labeled cheating scenarios |

> [!NOTE]
> Unable to match to external source. May be internally generated or from unpublished research.

---

## Keystroke Dynamics Datasets

### 1. CMU Keystroke Dynamics (DSL-StrongPasswordData)

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/cmu/DSL-StrongPasswordData.csv` |
| **Matched Source** | [CMU Keystroke Dynamics Benchmark](https://www.cs.cmu.edu/~keystroke/) |
| **Data Type** | CSV (tabular) |
| **Content Summary** | Password entry timing data: `subject`, `sessionIndex`, `rep`, H.period, DD.period.t, UD.period.t timing features for ".tie5Roanl" password |
| **Relevance** | **HIGH** - Benchmark dataset for keystroke authentication |

### 2. IKDD Keystroke Dynamics

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/ikdd/` |
| **Matched Source** | [IKDD Challenge 2015](http://www.ikdd.acm.org/?page_id=454) |
| **Data Type** | CSV with README documentation |
| **Content Summary** | User typing data with digram latencies for user classification. Contains 34 users, 26 unique digrams |
| **Relevance** | **HIGH** - User classification/authentication |

### 3. KeyRecs Dataset

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/keyrecs/` |
| **Matched Source** | [Clarkson KeyRecs Dataset](https://www.clarkson.edu/student-life/student-center/student-center-keyrecs) |
| **Data Type** | CSV (demographics + keystroke data) |
| **Content Summary** | 100 participants with demographics (handedness, age, gender) and keystroke recordings |
| **Relevance** | **MEDIUM** - Demographic diversity in keystroke patterns |

### 4. UEBA Keystroke Data

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/ueba/` |
| **Matched Source** | [UNIDENTIFIED] |
| **Data Type** | Mixed |
| **Content Summary** | User Entity Behavior Analytics keystroke data |
| **Relevance** | **MEDIUM** - Behavioral analytics for user profiling |

> [!NOTE]
> UEBA dataset source unconfirmed. May relate to enterprise behavioral analytics platforms.

### 5. Raw Users Data

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/raw_users/` |
| **Matched Source** | [UNIDENTIFIED] - Internal/Processed |
| **Data Type** | Raw keystroke recordings |
| **Content Summary** | Unprocessed user keystroke capture data |
| **Relevance** | **MEDIUM** - Raw data for preprocessing pipeline |

### 6. Processed NumPy Files

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/processed_npy/` |
| **Matched Source** | Internal - Derived from other keystroke datasets |
| **Data Type** | NumPy arrays (.npy) |
| **Content Summary** | Preprocessed keystroke features ready for ML models |
| **Relevance** | **HIGH** - Direct input for ML training |

### 7. Unidentified TIE5 Data

| Field | Value |
|-------|-------|
| **Local Path** | `keystroke/unidentified_tie5/` |
| **Matched Source** | [UNIDENTIFIED] |
| **Data Type** | Unknown |
| **Content Summary** | Possibly related to CMU ".tie5Roanl" password dataset variant |
| **Relevance** | **LOW** - Requires manual review |

---

## Mouse Dynamics Datasets

### 1. Balabit Mouse Dynamics Challenge

| Field | Value |
|-------|-------|
| **Local Path** | `mouse_dynamics/challenge/` |
| **Matched Source** | [GitHub: Balabit Mouse Dynamics Challenge](https://github.com/balabit/Mouse-Dynamics-Challenge) |
| **Data Type** | CSV + session files |
| **Content Summary** | Mouse movement tracking: timestamps, button states, x/y coordinates. 10 users with training/test sessions for user authentication |
| **Relevance** | **HIGH** - Benchmark for mouse-based authentication |

### 2. Mouse Authentication Challenge

| Field | Value |
|-------|-------|
| **Local Path** | `mouse_dynamics/auth_challenge/` |
| **Matched Source** | [Kaggle: User Authentication Challenge](https://www.kaggle.com/c/user-authentication-challenge) |
| **Data Type** | CSV (Train_Mouse.csv) |
| **Content Summary** | Columns: `uid`, `session_id`, `user_id`, `timestamp`, `event_type`, `screen_x`, `screen_y`. Over 11,000 records |
| **Relevance** | **HIGH** - User authentication via mouse patterns |

### 3. Mouse Tracking Log Data

| Field | Value |
|-------|-------|
| **Local Path** | `mouse_dynamics/log_data/` |
| **Matched Source** | [Academic Research - Kumamoto University](https://md.hicc.cs.kumamoto-u.ac.jp/) |
| **Data Type** | CSV (mouse_tracking_logdata.csv) |
| **Content Summary** | 223,000+ records: mouse/keyboard events during online quizzes. Includes x/y, click types, scrolling, keyboard input, URL context, tab focus state |
| **Relevance** | **CRITICAL** - Direct exam cheating detection scenario |

---

## Plagiarism Detection Datasets

### 1. PAN Plagiarism Corpus 2009

| Field | Value |
|-------|-------|
| **Local Path** | `plagiarism/pan_09/` |
| **Matched Source** | [PAN@CLEF 2009 Plagiarism Detection](https://pan.webis.de/data.html) |
| **Data Type** | TXT + XML (40,000+ documents) |
| **Content Summary** | 20,611 suspicious + 20,612 source documents. Includes artificial plagiarism with obfuscation (paraphrasing, POS-reordering, text operations). Based on Project Gutenberg |
| **Relevance** | **HIGH** - Benchmark for text plagiarism algorithms |

### 2. PAN Plagiarism Corpus 2011

| Field | Value |
|-------|-------|
| **Local Path** | `plagiarism/pan_11/` |
| **Matched Source** | [PAN@CLEF 2011 Plagiarism Detection](https://pan.webis.de/data.html) |
| **Data Type** | TXT + XML |
| **Content Summary** | Extended version of PAN-09 with additional obfuscation strategies |
| **Relevance** | **HIGH** - Extended plagiarism benchmarks |

### 3. Student Code Plagiarism Dataset

| Field | Value |
|-------|-------|
| **Local Path** | `plagiarism/student_code/` |
| **Matched Source** | [UNIDENTIFIED] |
| **Data Type** | CSV (cheating_dataset.csv) + Python files |
| **Content Summary** | 293 file pair comparisons with binary labels (1=plagiarism, 0=not). Columns: `File_1`, `File_2`, `Label`. Covers 174 submissions |
| **Relevance** | **CRITICAL** - Code plagiarism ground truth for academic integrity |

> [!NOTE]
> Student code dataset appears custom-generated or from internal research. Manual verification recommended.

---

## Reference URL Mapping

| URL | Matched Dataset | Status |
|-----|-----------------|--------|
| CMU Keystroke | `keystroke/cmu/` | ✅ Confirmed |
| Kaggle Suspicious Behaviors | `exam_behavior/student_suspicion/` | ✅ Confirmed |
| Balabit GitHub | `mouse_dynamics/challenge/` | ✅ Confirmed |
| PAN@CLEF 2009 | `plagiarism/pan_09/` | ✅ Confirmed |
| PAN@CLEF 2011 | `plagiarism/pan_11/` | ✅ Confirmed |
| IKDD Challenge | `keystroke/ikdd/` | ✅ Confirmed |
| Clarkson KeyRecs | `keystroke/keyrecs/` | ⚠️ Likely Match |
| Kaggle Auth Challenge | `mouse_dynamics/auth_challenge/` | ⚠️ Likely Match |

---

## Unidentified Datasets Summary

| Dataset | Location | Notes for Manual Review |
|---------|----------|------------------------|
| Cheating Scenarios | `exam_behavior/cheating_scenarios/` | 60 labeled scenarios - check internal documentation |
| UEBA Data | `keystroke/ueba/` | Enterprise behavioral analytics format |
| Raw Users | `keystroke/raw_users/` | May be project-generated collection |
| TIE5 Data | `keystroke/unidentified_tie5/` | Possibly CMU variant |
| Student Code | `plagiarism/student_code/` | Custom academic integrity dataset |

---

## Usage Recommendations

1. **For Keystroke Authentication**: Use CMU DSL + IKDD datasets
2. **For Mouse Dynamics**: Prioritize `mouse_dynamics/log_data/` for exam context
3. **For Exam Monitoring**: Combine student suspicion + cheating scenarios
4. **For Code Plagiarism**: Use PAN corpora for text, student_code for source code
5. **For ML Pipeline**: Leverage `processed_npy/` for ready-to-use features

---

*Generated: Dataset Inventory Task*
*Last Updated: Auto-generated during curation*
