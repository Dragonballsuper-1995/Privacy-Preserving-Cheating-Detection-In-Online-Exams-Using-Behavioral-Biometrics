# Phase 1 Training Quick Start Guide

Get started training your cheating detection models in 5 minutes!

## 🚀 Step-by-Step Guide

### Step 1: Verify Prerequisites

```bash
cd backend
python --version  # Should be 3.10+
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** Installing `torch` and `sentence-transformers` may take a few minutes.

### Step 3: Download Datasets

Download datasets to `backend/data/datasets/`:

**Keystroke Datasets:**
- [CMU Keystroke Benchmark](https://www.kaggle.com/datasets/carnegiecylab/keystroke-dynamics-benchmark-data-set)
- Place in: `data/datasets/keystroke/cmu/DSL-StrongPasswordData.csv`

**Behavioral Datasets:**
- [Student Suspicious Behaviors](https://data.mendeley.com/datasets/jm7gxsxbdd/1)
- Place in: `data/datasets/exam_behavior/student_suspicion/`

**Plagiarism Datasets:**
- [Student Code Similarity](https://www.kaggle.com/datasets/ehsankhani/student-code-similarity-and-plagiarism-labels)
- Place in: `data/datasets/plagiarism/student_code/cheating_dataset.csv`

> See `DATASETS.md` for detailed download instructions and alternative datasets.

### Step 4: Train Models

#### Option A: Train Everything (Recommended)

```bash
python scripts/train_all_models.py
```

This will:
- ✅ Train keystroke anomaly detection
- ✅ Train behavioral classifiers 
- ✅ Train similarity detection
- ✅ Generate comprehensive evaluation report

⏱️ **Estimated Time:** 10-30 minutes (depending on dataset sizes)

#### Option B: Train Individual Models

```bash
# Keystroke anomaly detection (~5 min)
python scripts/train_keystroke_models.py

# Behavioral classification (~10 min)
python scripts/train_behavioral_models.py

# Similarity detection (~15 min, uses GPU if available)
python scripts/train_similarity_models.py
```

### Step 5: Evaluate Results

```bash
python scripts/comprehensive_evaluation.py
```

**Output:**
- 📄 `data/results/evaluation_report.md` - Comprehensive metrics
- 📊 `data/results/visualizations/` - Charts and plots

### Step 6: (Optional) Hyperparameter Tuning

```bash
python scripts/hyperparameter_tuning.py
```

This finds optimal parameters for all models. Can take 30-60 minutes.

## 📊 Expected Directory Structure After Training

```
backend/
├── models/
│   ├── keystroke/
│   │   ├── isolation_forest.pkl
│   │   ├── scaler.pkl
│   │   ├── feature_names.json
│   │   └── training_metadata.json
│   ├── behavioral/
│   │   ├── random_forest.pkl
│   │   ├── gradient_boosting.pkl
│   │   ├── scaler.pkl
│   │   ├── label_encoder.pkl
│   │   ├── feature_importance.csv
│   │   └── training_metadata.json
│   ├── similarity/
│   │   ├── [sentence-transformer model files]
│   │   ├── optimal_threshold.json
│   │   └── training_metadata.json
│   └── configs/
│       ├── isolation_forest_best.json
│       ├── random_forest_best.json
│       ├── gradient_boosting_best.json
│       └── similarity_thresholds.json
└── data/
    └── results/
        ├── evaluation_report.md
        ├── training_summary.json
        └── visualizations/
            ├── feature_importance.png
            ├── model_comparison.png
            └── anomaly_distribution.png
```

## ✅ Verification Checklist

After training, verify:

- [ ] All `.pkl` files exist in `models/` subdirectories
- [ ] `training_metadata.json` files contain valid metrics
- [ ] `evaluation_report.md` shows "✅ Trained and ready" for all models
- [ ] Visualizations generated in `data/results/visualizations/`
- [ ] No error messages in training output

## 🎯 Expected Performance Targets

| Model | Metric | Target | Use Case |
|-------|--------|--------|----------|
| Keystroke | Anomaly Rate | ~10% | Unusual typing patterns |
| Behavioral | Accuracy | >85% | Classify cheating behavior |
| Behavioral | F1 Score | >80% | Balanced cheating detection |
| Similarity | Precision | >90% | Low false positives |
| Similarity | F1 Score | >85% | Balanced plagiarism detection |

## 🐛 Troubleshooting

### "Dataset not found" errors

**Solution:** Verify datasets are in correct directories:
```bash
ls data/datasets/keystroke/cmu/
ls data/datasets/exam_behavior/student_suspicion/
ls data/datasets/plagiarism/student_code/
```

### Out of memory errors

**Solutions:**
1. Close other applications
2. Reduce dataset size for testing:
   ```python
   # In training scripts, add:
   df = df.sample(n=1000)  # Use only 1000 samples
   ```
3. Train models individually instead of all at once

### Slow similarity training

**Solutions:**
1. Use GPU if available (automatically detected)
2. Reduce epochs in `train_similarity_models.py` (line ~154):
   ```python
   epochs=1,  # Instead of 2
   ```

### Import errors

**Solution:** Reinstall dependencies:
```bash
pip install --force-reinstall -r requirements.txt
```

## 🔄 Re-training Models

To retrain models with new data:

```bash
# Skip existing models (faster)
python scripts/train_all_models.py --skip-existing

# Force retrain everything
rm -rf models/*
python scripts/train_all_models.py
```

## 📚 Next Steps

After training:

1. **Review Results** - Check `data/results/evaluation_report.md`
2. **Integrate Models** - Update `app/ml/` to load trained models
3. **Test Integration** - Run end-to-end tests with real exam data
4. **Proceed to Phase 2** - Testing & Validation

## 💡 Tips

- **Start small:** Test with subset of data first
- **Monitor progress:** Training scripts print progress updates
- **Save outputs:** Redirect output to log files for reference:
  ```bash
  python scripts/train_all_models.py 2>&1 | tee training.log
  ```
- **GPU acceleration:** Similarity training uses GPU automatically if available

## 🆘 Getting Help

1. Check `scripts/README.md` for detailed documentation
2. Review training script source code for advanced options
3. See `implementation_plan.md` for overall architecture
4. Check `DATASETS.md` for dataset-specific issues

---

**Ready to train?**

```bash
python scripts/train_all_models.py
```

Good luck! 🚀
