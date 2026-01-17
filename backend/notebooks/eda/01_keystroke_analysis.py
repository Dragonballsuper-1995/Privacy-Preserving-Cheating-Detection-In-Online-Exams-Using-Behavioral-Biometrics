import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Add src to python path to import loaders
# Assuming script is in backend/notebooks/eda/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(os.path.join(project_root, "backend", "src"))

from data_loader.keystroke_loader import KeystrokeLoader

def analyze_cmu():
    print("Loading CMU Dataset...")
    loader = KeystrokeLoader()
    df = loader.load_cmu_dataset()
    
    # 1. Feature Distribution (Hold Times)
    hold_cols = [c for c in df.columns if c.startswith('H.')]
    if hold_cols:
        plt.figure(figsize=(10, 6))
        # Plot first 3 keys hold times
        for col in hold_cols[:3]:
            sns.kdeplot(df[col], label=col, fill=True)
        plt.title('Distribution of Hold Times (First 3 Keys)')
        plt.xlabel('Hold Time (ms?)') # CMU is likely seconds, need verification
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(current_dir, "plots/cmu_hold_dist.png"))
        print("Saved cmu_hold_dist.png")
        plt.close()

    # 2. Subject Keying Speed
    # Average of all hold times per subject
    df['avg_hold'] = df[hold_cols].mean(axis=1)
    
    plt.figure(figsize=(12, 6))
    # Top 20 subjects
    top_subjects = df['subject'].value_counts().index[:20]
    sns.boxplot(data=df[df['subject'].isin(top_subjects)], x='subject', y='avg_hold')
    plt.xticks(rotation=45)
    plt.title('Average Hold Time by Subject (Top 20)')
    plt.tight_layout()
    plt.savefig(os.path.join(current_dir, "plots/cmu_subject_speed.png"))
    print("Saved cmu_subject_speed.png")
    plt.close()

if __name__ == "__main__":
    os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)
    analyze_cmu()
