import pandas as pd
import os
import glob
from typing import Optional, Dict, List

class KeystrokeLoader:
    def __init__(self, base_path: str = "../../data/datasets/keystroke"):
        """
        Initialize the KeystrokeLoader.
        
        Args:
            base_path (str): Path to the keystroke datasets root directory. 
                             Defaults to relative path from src/data_loader/
        """
        # Resolve absolute path if relative is given
        if not os.path.isabs(base_path):
             # Assuming this script is in backend/src/data_loader/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Adjust backtracking based on depth. 
            # src/data_loader -> src -> backend -> data -> datasets -> keystroke
            # That is ../../../data/datasets/keystroke
            project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
            base_path = os.path.join(project_root, "backend", "data", "datasets", "keystroke")
            
        self.base_path = base_path

    def load_cmu_dataset(self) -> pd.DataFrame:
        """
        Load the CMU Keystroke Dynamics Benchmark dataset.
        
        Returns:
            pd.DataFrame: The loaded dataset.
        """
        file_path = os.path.join(self.base_path, "cmu", "DSL-StrongPasswordData.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CMU dataset not found at {file_path}")
            
        df = pd.read_csv(file_path)
        return df

    def load_keyrecs_dataset(self, file_type: str = "fixed") -> pd.DataFrame:
        """
        Load the KeyRecs dataset.
        
        Args:
            file_type (str): 'fixed', 'free', or 'demographics'
            
        Returns:
            pd.DataFrame: The loaded dataset.
        """
        folder_path = os.path.join(self.base_path, "keyrecs")
        
        files = {
            "fixed": "fixed-text.csv",
            "free": "free-text.csv",
            "demographics": "demographics.csv"
        }
        
        if file_type not in files:
            raise ValueError(f"Invalid file_type. Choose from {list(files.keys())}")
            
        file_path = os.path.join(folder_path, files[file_type])
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"KeyRecs file not found at {file_path}")
            
        # KeyRecs CSVs sometimes have specific encoding or separator issues, 
        # but usually standard read_csv works.
        df = pd.read_csv(file_path)
        return df

    def load_raw_user_session(self, user_limit: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """
        Load raw user keystroke logs.
        
        Args:
            user_limit (int, optional): Limit the number of user files to load.
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping filename to dataframe.
        """
        folder_path = os.path.join(self.base_path, "raw_users", "files")
        # Handle case where files might be directly in raw_users or in a 'files' subdir
        # Based on previous analysis: "Content: files/ containing thousands of _keystrokes.txt files"
        
        if not os.path.exists(folder_path):
             # Fallback to direct check
             folder_path = os.path.join(self.base_path, "raw_users")

        pattern = os.path.join(folder_path, "*_keystrokes.txt")
        files = glob.glob(pattern)
        
        if not files:
            print(f"No files found in {folder_path} with pattern *_keystrokes.txt")
            return {}
            
        if user_limit:
            files = files[:user_limit]
            
        loaded_data = {}
        for f in files:
            filename = os.path.basename(f)
            try:
                # These are likely raw text files, format needs verification.
                # Assuming simple CSV or specific delimiter. 
                # If it fails, we might need a custom parser.
                # Inspecting one file would be ideal.
                df = pd.read_csv(f) 
                loaded_data[filename] = df
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                
        return loaded_data

if __name__ == "__main__":
    # Simple test
    loader = KeystrokeLoader()
    print(f"Base path: {loader.base_path}")
    
    try:
        cmu = loader.load_cmu_dataset()
        print(f"CMU Dataset loaded: {cmu.shape}")
    except Exception as e:
        print(f"CMU Load Failed: {e}")

    try:
        keyrecs = loader.load_keyrecs_dataset()
        print(f"KeyRecs (fixed) loaded: {keyrecs.shape}")
    except Exception as e:
        print(f"KeyRecs Load Failed: {e}")
