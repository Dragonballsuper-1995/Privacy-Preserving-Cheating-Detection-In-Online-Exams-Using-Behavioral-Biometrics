import pandas as pd
import os
from typing import Optional

class MouseLoader:
    def __init__(self, base_path: str = "../../data/datasets/mouse_dynamics"):
        """
        Initialize the MouseLoader.
        
        Args:
            base_path (str): Path to the mouse dynamics datasets root.
        """
        if not os.path.isabs(base_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
            base_path = os.path.join(project_root, "backend", "data", "datasets", "mouse_dynamics")
            
        self.base_path = base_path

    def load_auth_challenge(self, split: str = "train") -> pd.DataFrame:
        """
        Load Mouse Dynamics for User Authentication dataset.
        
        Args:
            split (str): 'train' or 'test'
            
        Returns:
            pd.DataFrame: Loaded dataset.
        """
        folder = os.path.join(self.base_path, "auth_challenge")
        filename = "Train_Mouse.csv" if split.lower() == "train" else "Test_Mouse.csv"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Auth challenge file not found: {file_path}")
            
        return pd.read_csv(file_path)

    def load_log_data(self) -> pd.DataFrame:
        """
        Load the large Mouse Tracking Log Data (from 'Identifying potential cheaters...' dataset).
        
        Returns:
            pd.DataFrame: Loaded dataset.
        """
        folder = os.path.join(self.base_path, "log_data")
        # The filename might vary if it was renamed or if I recall correctly from analysis
        # Analysis said: "mouse_tracking_logdata.csv"
        file_path = os.path.join(folder, "mouse_tracking_logdata.csv")
        
        if not os.path.exists(file_path):
            # Try finding any CSV in that folder
            import glob
            csvs = glob.glob(os.path.join(folder, "*.csv"))
            if csvs:
                file_path = csvs[0]
            else:
                raise FileNotFoundError(f"Log data CSV not found in {folder}")
                
        return pd.read_csv(file_path)

    def load_challenge_public_labels(self) -> pd.DataFrame:
        """
        Load the public labels for the Mouse Dynamics Challenge.
        """
        file_path = os.path.join(self.base_path, "challenge", "public_labels.csv")
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"Challenge labels not found: {file_path}")
        return pd.read_csv(file_path)

if __name__ == "__main__":
    loader = MouseLoader()
    print(f"Base path: {loader.base_path}")
    
    try:
        auth_train = loader.load_auth_challenge("train")
        print(f"Auth Train loaded: {auth_train.shape}")
    except Exception as e:
        print(f"Auth Train failed: {e}")
        
    try:
        log_data = loader.load_log_data()
        print(f"Log Data loaded: {log_data.shape}")
    except Exception as e:
        print(f"Log Data failed: {e}")
