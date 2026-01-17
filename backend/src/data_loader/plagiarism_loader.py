import pandas as pd
import os
import glob
from typing import List, Dict, Tuple

class PlagiarismLoader:
    def __init__(self, base_path: str = "../../data/datasets/plagiarism"):
        """
        Initialize the PlagiarismLoader.
        
        Args:
            base_path (str): Path to the plagiarism datasets root.
        """
        if not os.path.isabs(base_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
            base_path = os.path.join(project_root, "backend", "data", "datasets", "plagiarism")
            
        self.base_path = base_path

    def load_student_code_sim(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load Student Code Similarity & Plagiarism dataset.
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (Main labels/data CSV, Features CSV if available)
        """
        folder = os.path.join(self.base_path, "student_code")
        
        # Based on analysis: cheating_dataset.csv, cheating_features_dataset.csv
        main_path = os.path.join(folder, "cheating_dataset.csv")
        feats_path = os.path.join(folder, "cheating_features_dataset.csv")
        
        df_main = pd.DataFrame()
        df_feats = pd.DataFrame()
        
        if os.path.exists(main_path):
            df_main = pd.read_csv(main_path)
            
        if os.path.exists(feats_path):
            try:
                df_feats = pd.read_csv(feats_path)
            except:
                pass # Optional
                
        return df_main, df_feats

    def list_pan09_structure(self) -> Dict[str, List[str]]:
        """
        List subdirectories in PAN-09 to understand structure.
        
        Returns:
            Dict: Structure summary.
        """
        folder = os.path.join(self.base_path, "pan_09")
        if not os.path.exists(folder):
            return {}
            
        structure = {}
        for root, dirs, files in os.walk(folder):
            rel_path = os.path.relpath(root, folder)
            if rel_path == ".":
                structure["roots"] = dirs
            else:
                if len(files) > 0:
                     structure[rel_path] = f"{len(files)} files"
        return structure

if __name__ == "__main__":
    loader = PlagiarismLoader()
    print(f"Base path: {loader.base_path}")
    
    try:
        main, feats = loader.load_student_code_sim()
        print(f"Student Code Main: {main.shape}")
        if not feats.empty:
            print(f"Student Code Features: {feats.shape}")
    except Exception as e:
        print(f"Student Code Load failed: {e}")
    
    pan09 = loader.list_pan09_structure()
    print(f"PAN 09 Structure keys: {list(pan09.keys())[:5]}")
