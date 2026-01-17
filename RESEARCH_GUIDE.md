# Research Paper Support Guide

This document provides guidance for writing a research paper based on the Cheating Detection System.

---

## Suggested Paper Structure

### 1. Abstract
- Problem: Online exam proctoring often requires invasive camera monitoring
- Solution: Privacy-preserving behavioral biometrics approach
- Key Results: Report accuracy, precision, recall from evaluation metrics

### 2. Introduction
- Growth of online education and exams
- Privacy concerns with traditional proctoring
- Research questions:
  - RQ1: Can behavioral signals alone detect cheating?
  - RQ2: What behavioral patterns indicate cheating?
  - RQ3: How do different feature types contribute to detection?

### 3. Related Work
- Traditional proctoring systems (ProctorU, Examity)
- Keystroke dynamics research
- Anomaly detection in education
- Answer similarity/plagiarism detection

### 4. Methodology

#### 4.1 System Architecture
Reference the architecture diagram in README.md

#### 4.2 Feature Extraction
| Category | Features |
|----------|----------|
| Keystroke | Inter-key delay, hold time, typing speed, rhythm variance |
| Hesitation | Pause count, duration, time to first key |
| Paste | Paste count, length, correlation with tab switching |
| Focus | Blur count, unfocused time, extended absences |

#### 4.3 Machine Learning Pipeline
1. **Anomaly Detection**: Isolation Forest trained on honest sessions
2. **Answer Similarity**: Sentence embeddings (all-MiniLM-L6-v2)
3. **Risk Fusion**: Weighted combination with optional Random Forest

#### 4.4 Risk Score Formula
```
Score = 0.35 × behavioral + 0.35 × anomaly + 0.30 × similarity
```

### 5. Experiments

#### 5.1 Dataset
- Generated using simulation mode
- Parameters: honest_count, cheater_count
- Behavioral differences between honest/cheating simulations

#### 5.2 Evaluation Metrics
Use the evaluation API to get:
- Accuracy, Precision, Recall, F1 Score
- AUC-ROC
- Confusion Matrix

#### 5.3 Threshold Analysis
Use `/api/evaluation/optimal-threshold` to find best threshold

### 6. Results
Include:
- Classification performance table
- Feature importance analysis
- Threshold sensitivity analysis
- Comparison with baseline methods

### 7. Discussion
- Strengths: Privacy-preserving, explainable, extensible
- Limitations: Simulated data, single-session training
- Future work: Real student data, multi-session patterns

### 8. Conclusion
Summarize contributions and findings

---

## Data Collection Notes

### Simulated Data
The system can generate synthetic data for initial experiments:
```bash
POST /api/simulation/generate-training-data
{"honest_count": 100, "cheater_count": 50}
```

### Real Data Collection (IRB Approval Required)
If collecting real data:
1. Obtain IRB approval
2. Get informed consent
3. Anonymize student IDs
4. Collect during controlled exams
5. Have proctors label sessions

---

## Evaluation Workflow

1. **Generate Data**:
```bash
curl -X POST http://localhost:8000/api/simulation/generate-training-data \
  -H "Content-Type: application/json" \
  -d '{"honest_count": 100, "cheater_count": 40}'
```

2. **Train Models**:
```bash
curl -X POST http://localhost:8000/api/simulation/train-models
```

3. **Evaluate**:
```bash
curl http://localhost:8000/api/evaluation/evaluate -X POST \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.75}'
```

4. **Find Optimal Threshold**:
```bash
curl http://localhost:8000/api/evaluation/optimal-threshold
```

5. **Generate Report**:
```bash
curl http://localhost:8000/api/evaluation/report
```

---

## Tables for Paper

### Table 1: System Features
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 14 | Exam interface |
| Backend | FastAPI | API & ML pipeline |
| Database | SQLite/PostgreSQL | Session storage |
| ML | scikit-learn | Anomaly detection |
| NLP | sentence-transformers | Answer similarity |

### Table 2: Feature Categories
| Category | Count | Key Features |
|----------|-------|--------------|
| Keystroke | 8 | Inter-key delay, speed, rhythm |
| Hesitation | 6 | Pause count, duration |
| Paste | 5 | Count, length, timing |
| Focus | 5 | Blur count, absence time |

### Table 3: Comparison with Related Work
| System | Camera | Audio | Keystroke | Similarity | Privacy |
|--------|--------|-------|-----------|------------|---------|
| ProctorU | ✓ | ✓ | ✗ | ✗ | Low |
| Examity | ✓ | ✓ | ✗ | ✗ | Low |
| Turnitin | ✗ | ✗ | ✗ | ✓ | Medium |
| **Ours** | ✗ | ✗ | ✓ | ✓ | **High** |

---

## Citation

```bibtex
@software{cheating_detection_2024,
  title = {Privacy-Preserving AI-Based Cheating Detection 
           in Online Exams Using Behavioral Biometrics 
           and Answer Similarity},
  author = {Your Name},
  year = {2024},
  institution = {Your University},
  type = {Research Software}
}
```

---

## Helpful Resources

- [Keystroke Dynamics Research](https://www.sciencedirect.com/topics/computer-science/keystroke-dynamics)
- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)
- [CMU Keystroke Dataset](https://www.cs.cmu.edu/~keystroke/)
