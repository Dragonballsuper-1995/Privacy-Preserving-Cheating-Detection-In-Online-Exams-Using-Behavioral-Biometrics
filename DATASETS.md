# Research Datasets Guide

## Quick Start

Download these datasets and place them in the `data/datasets/` folder in the backend project.

---

## Keystroke Dynamics

### CMU Keystroke Dynamics Benchmark (Recommended)
**Best for**: Baseline typing pattern analysis
- **Link**: https://www.cs.cmu.edu/~keystroke/
- **Kaggle Mirror**: https://www.kaggle.com/datasets/carnegiecylab/keystroke-dynamics-benchmark-data-set
- **Size**: 51 typists × 400 entries
- **Format**: CSV with timing data
- **Use**: Train anomaly detection on normal typing

### KeyRecs Dataset
**Best for**: Multi-demographic typing analysis
- **Link**: https://zenodo.org/records/6805690
- **Size**: 100 participants, 20 nationalities
- **Format**: JSON with inter-key latencies
- **Use**: Validate across diverse typing styles

---

## Exam Cheating Detection

### Cheating Scenario Dataset (Mendeley)
**Best for**: Behavioral cheating patterns in online exams
- **Link**: https://data.mendeley.com/datasets/jm7gxsxbdd/1
- **Size**: 30 participants, webcam recordings
- **Features**: Head pose, eye gaze, lip movement categories
- **Use**: Train behavior-based cheating classifiers

> **Note**: For behavioral keystroke data during exams, use the **simulation mode** built into this project to generate synthetic training data:
> ```bash
> POST /api/simulation/generate-training-data
> {"honest_count": 50, "cheater_count": 20}
> ```

---

## Plagiarism & Similarity

### PAN Plagiarism Corpus
**Best for**: Text similarity benchmarks
- **Link**: https://pan.webis.de/
- **Versions**: PAN-PC-09, PAN-PC-11
- **Use**: Validate answer similarity detection

### Student Code Similarity & Plagiarism Labels (Kaggle)
**Best for**: Code plagiarism detection
- **Link**: https://www.kaggle.com/datasets/ehsankhani/student-code-similarity-and-plagiarism-labels
- **Size**: Python student submissions with labels
- **Format**: Python code + cheating/not-cheating labels
- **Use**: Train code similarity models, detect plagiarism

---

## Folder Structure

```
backend/
└── data/
    └── datasets/
        ├── cmu_keystroke/
        │   └── DSL-StrongPasswordData.csv
        ├── exam_behavior/
        │   └── cheating_scenarios/
        └── plagiarism/
            └── pan_corpus/
```

---

## Integration Notes

1. **Download** datasets from the links above
2. **Place** in the appropriate `data/datasets/` subfolder
3. **Use synthetic data** for initial development via simulation API

The system will automatically detect and use available datasets for:
- Training the anomaly detection model
- Validating similarity thresholds
- Benchmarking against published results
