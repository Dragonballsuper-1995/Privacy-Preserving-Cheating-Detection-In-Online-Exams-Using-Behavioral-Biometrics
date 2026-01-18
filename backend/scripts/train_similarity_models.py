"""
Train Answer Similarity Detection Models

This script fine-tunes sentence transformer models on plagiarism datasets
to improve detection of copied/similar answers in exam contexts.
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import pickle
import json
from datetime import datetime
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader.plagiarism_loader import PlagiarismLoader

# Import sentence transformers
try:
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
    from torch.utils.data import DataLoader
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers not installed")
    TRANSFORMERS_AVAILABLE = False


def prepare_training_pairs(df: pd.DataFrame) -> Tuple[List[InputExample], List[InputExample]]:
    """
    Prepare training pairs from plagiarism dataset.
    
    Args:
        df: Plagiarism dataset with labels
        
    Returns:
        Tuple of (train_examples, test_examples)
    """
    # Dataset should have: text1, text2, label (0=different, 1=plagiarized)
    # or: code1, code2, is_plagiarism
    
    examples = []
    
    # Try to identify the structure
    if 'code1' in df.columns and 'code2' in df.columns:
        text1_col, text2_col = 'code1', 'code2'
    elif 'text1' in df.columns and 'text2' in df.columns:
        text1_col, text2_col = 'text1', 'text2'
    elif 'answer1' in df.columns and 'answer2' in df.columns:
        text1_col, text2_col = 'answer1', 'answer2'
    else:
        # Look for any text columns
        text_cols = [col for col in df.columns if 'text' in col.lower() or 'code' in col.lower() or 'answer' in col.lower()]
        if len(text_cols) >= 2:
            text1_col, text2_col = text_cols[0], text_cols[1]
        else:
            raise ValueError("Cannot identify text pair columns in dataset")
    
    # Identify label column
    label_col = None
    for col in ['label', 'is_plagiarism', 'similarity', 'is_cheating', 'plagiarized']:
        if col in df.columns:
            label_col = col
            break
    
    if label_col is None:
        raise ValueError("Cannot identify label column")
    
    print(f"   Using columns: {text1_col}, {text2_col}, {label_col}")
    
    # Create InputExamples
    for idx, row in df.iterrows():
        text1 = str(row[text1_col])
        text2 = str(row[text2_col])
        
        # Convert label to similarity score (0-1)
        label = row[label_col]
        if isinstance(label, str):
            # Handle string labels like 'plagiarized', 'original'
            score = 1.0 if label.lower() in ['plagiarized', 'similar', 'yes', 'true', '1'] else 0.0
        else:
            # Numeric label
            score = float(label)
        
        examples.append(InputExample(texts=[text1, text2], label=score))
    
    # Split
    train_size = int(0.8 * len(examples))
    train_examples = examples[:train_size]
    test_examples = examples[train_size:]
    
    return train_examples, test_examples


def evaluate_similarity_model(model: SentenceTransformer, test_pairs: List[Tuple[str, str, float]], 
                               threshold: float = 0.85) -> dict:
    """
    Evaluate similarity model on test pairs.
    
    Args:
        model: Trained sentence transformer
        test_pairs: List of (text1, text2, label)
        threshold: Similarity threshold for classification
        
    Returns:
        Evaluation metrics dictionary
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    similarities = []
    labels = []
    
    for text1, text2, label in test_pairs:
        emb1 = model.encode([text1])[0]
        emb2 = model.encode([text2])[0]
        
        sim = cosine_similarity([emb1], [emb2])[0][0]
        similarities.append(sim)
        labels.append(label)
    
    # Convert to predictions using threshold
    predictions = [1 if sim >= threshold else 0 for sim in similarities]
    
    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    metrics = {
        'accuracy': accuracy_score(labels, predictions),
        'precision': precision_score(labels, predictions, zero_division=0),
        'recall': recall_score(labels, predictions, zero_division=0),
        'f1': f1_score(labels, predictions, zero_division=0),
        'mean_similarity': np.mean(similarities),
        'std_similarity': np.std(similarities),
    }
    
    # ROC-AUC
    if len(set(labels)) == 2:
        metrics['roc_auc'] = roc_auc_score(labels, similarities)
    
    return metrics


def train_similarity_models(output_dir: str = "models/similarity"):
    """
    Train answer similarity detection models on plagiarism datasets.
    
    Args:
        output_dir: Directory to save trained models
    """
    print("=" * 60)
    print("🚀 ANSWER SIMILARITY DETECTION MODEL TRAINING")
    print("=" * 60)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\n❌ sentence-transformers not installed!")
        print("   Install with: pip install sentence-transformers")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize data loader
    loader = PlagiarismLoader()
    
    # ================== Load Student Code Similarity Dataset ==================
    print("\n📚 Loading Student Code Similarity Dataset...")
    try:
        main_df, feats_df = loader.load_student_code_sim()
        
        if main_df.empty:
            print("   ❌ Dataset is empty or not found")
            print("   💡 Download dataset to backend/data/datasets/plagiarism/student_code/")
            return
        
        print(f"   ✅ Loaded {len(main_df)} code pairs")
        print(f"   Columns: {list(main_df.columns)}")
        
        # Prepare training pairs
        print("\n   🔧 Preparing training pairs...")
        train_examples, test_examples = prepare_training_pairs(main_df)
        
        print(f"   ✅ Training pairs: {len(train_examples)}")
        print(f"   ✅ Test pairs: {len(test_examples)}")
        
    except FileNotFoundError as e:
        print(f"   ⚠️  Dataset not found: {e}")
        return
    except Exception as e:
        print(f"   ❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ================== Load Pre-trained Model ==================
    print("\n🤖 Loading pre-trained sentence transformer...")
    base_model_name = "all-MiniLM-L6-v2"  # Fast, good quality
    # For code: "microsoft/codebert-base" or "sentence-transformers/all-mpnet-base-v2"
    
    model = SentenceTransformer(base_model_name)
    print(f"   ✅ Loaded: {base_model_name}")
    
    # ================== Fine-tune Model ==================
    print("\n🔧 Fine-tuning model on plagiarism dataset...")
    
    # Create data loader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    
    # Define loss function
    train_loss = losses.CosineSimilarityLoss(model)
    
    # Create evaluator
    sentences1 = [example.texts[0] for example in test_examples]
    sentences2 = [example.texts[1] for example in test_examples]
    scores = [example.label for example in test_examples]
    
    evaluator = EmbeddingSimilarityEvaluator(sentences1, sentences2, scores)
    
    # Fine-tune
    print("   Training for 2 epochs...")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=2,
        evaluation_steps=100,
        warmup_steps=100,
        output_path=output_dir,
        show_progress_bar=True
    )
    
    print("   ✅ Fine-tuning complete!")
    
    # ================== Evaluation ==================
    print("\n📈 Evaluating fine-tuned model...")
    
    # Prepare test pairs for evaluation
    test_pairs = [(ex.texts[0], ex.texts[1], int(ex.label)) for ex in test_examples]
    
    # Evaluate at different thresholds
    thresholds = [0.75, 0.80, 0.85, 0.90, 0.95]
    best_threshold = 0.85
    best_f1 = 0
    
    print("\n   Threshold tuning:")
    for threshold in thresholds:
        metrics = evaluate_similarity_model(model, test_pairs, threshold)
        print(f"      {threshold:.2f}: F1={metrics['f1']:.3f}, Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}")
        
        if metrics['f1'] > best_f1:
            best_f1 = metrics['f1']
            best_threshold = threshold
    
    print(f"\n   ✅ Best threshold: {best_threshold} (F1={best_f1:.3f})")
    
    # Final evaluation with best threshold
    final_metrics = evaluate_similarity_model(model, test_pairs, best_threshold)
    
    print("\n📊 Final Test Set Performance:")
    print(f"   Accuracy:  {final_metrics['accuracy']:.3f}")
    print(f"   Precision: {final_metrics['precision']:.3f}")
    print(f"   Recall:    {final_metrics['recall']:.3f}")
    print(f"   F1 Score:  {final_metrics['f1']:.3f}")
    if 'roc_auc' in final_metrics:
        print(f"   ROC-AUC:   {final_metrics['roc_auc']:.3f}")
    
    # ================== Save Model ==================
    print(f"\n💾 Saving model to {output_dir}/...")
    
    # Model is already saved by fit() to output_dir
    print(f"   ✅ Fine-tuned model saved")
    
    # Save optimal threshold
    threshold_path = os.path.join(output_dir, 'optimal_threshold.json')
    with open(threshold_path, 'w') as f:
        json.dump({'threshold': best_threshold}, f, indent=2)
    print(f"   ✅ Optimal threshold saved: {threshold_path}")
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'base_model': base_model_name,
        'total_pairs': len(train_examples) + len(test_examples),
        'train_pairs': len(train_examples),
        'test_pairs': len(test_examples),
        'optimal_threshold': best_threshold,
        'metrics': {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                   for k, v in final_metrics.items()}
    }
    
    metadata_path = os.path.join(output_dir, 'training_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Metadata saved: {metadata_path}")
    
    # ================== Summary ==================
    print("\n" + "=" * 60)
    print("✨ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"📁 Model saved to: {output_dir}/")
    print(f"🎯 Test F1 Score: {final_metrics['f1']:.3f}")
    print(f"📊 Optimal threshold: {best_threshold}")
    print("=" * 60)
    
    return model, best_threshold, metadata


if __name__ == "__main__":
    # Train models
    train_similarity_models()
