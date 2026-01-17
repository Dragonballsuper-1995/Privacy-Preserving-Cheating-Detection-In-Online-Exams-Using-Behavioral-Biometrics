import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Add src to python path to import loaders
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(os.path.join(project_root, "backend", "src"))

from data_loader.mouse_loader import MouseLoader

def analyze_mouse_logs():
    print("Loading Mouse Log Data...")
    loader = MouseLoader()
    try:
        df = loader.load_log_data()
        print(f"Loaded {len(df)} rows.")
        
        # Check columns
        # Assuming columns like x, y, user_id, session_id...
        print(f"Columns: {df.columns.tolist()}")
        
        # If dataset is too large, sample it
        if len(df) > 100000:
            df_sample = df.sample(10000)
        else:
            df_sample = df
            
        # Try to identify X and Y columns
        # Likely 'x', 'y' or similar
        x_col = next((c for c in df.columns if c.lower() == 'x'), None)
        y_col = next((c for c in df.columns if c.lower() == 'y'), None)
        
        if x_col and y_col:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_sample, x=x_col, y=y_col, alpha=0.1, s=10)
            plt.title(f'Mouse Trajectory (Sample {len(df_sample)})')
            plt.grid(True)
            plt.savefig(os.path.join(current_dir, "plots/mouse_trajectory.png"))
            print("Saved mouse_trajectory.png")
            plt.close()
        else:
            print("Could not identify X/Y columns for trajectory plot.")
            
    except Exception as e:
        print(f"Mouse Analysis Failed: {e}")

if __name__ == "__main__":
    os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)
    analyze_mouse_logs()
