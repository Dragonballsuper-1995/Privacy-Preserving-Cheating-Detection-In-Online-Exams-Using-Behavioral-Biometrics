import pandas as pd
import os
import glob
from typing import List, Dict, Any

class ExamLoader:
    def __init__(self, base_path: str = "../../data/datasets/exam_behavior"):
        """
        Initialize the ExamLoader.
        
        Args:
            base_path (str): Path to the exam behavior datasets root.
        """
        if not os.path.isabs(base_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
            base_path = os.path.join(project_root, "backend", "data", "datasets", "exam_behavior")
            
        self.base_path = base_path

    def get_cheating_scenarios(self) -> List[str]:
        """
        List all scenario folder names.
        
        Returns:
            List[str]: List of folder names (e.g., ['Scenario 1', 'Scenario 2', ...])
        """
        scenarios_path = os.path.join(self.base_path, "cheating_scenarios")
        if not os.path.exists(scenarios_path):
            return []
            
        # List directories only
        scenarios = [d for d in os.listdir(scenarios_path) 
                     if os.path.isdir(os.path.join(scenarios_path, d))]
        # Sort numerically if possible
        try:
            scenarios.sort(key=lambda x: int(x.split(' ')[-1]) if ' ' in x else x)
        except:
            scenarios.sort()
            
        return scenarios

    def load_scenario_metadata(self, scenario_name: str) -> pd.DataFrame:
        """
        Load the annotations (txt files) for a specific scenario.
        Assumes txt files contain some structured data (likely gaze/pose).
        
        Args:
            scenario_name (str): Name of the scenario folder (e.g., "Scenario 1")
            
        Returns:
            pd.DataFrame: DataFrame containing parsed data from all txt files in the scenario.
        """
        base_dir = os.path.join(self.base_path, "cheating_scenarios", scenario_name)
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"Scenario {scenario_name} not found")
            
        txt_files = glob.glob(os.path.join(base_dir, "*.txt"))
        
        # This part depends heavily on the format of the TXT files. 
        # Based on previous analysis, they are frame-level annotations.
        # We'll just list them for now or try to read one if format is simple.
        # For now, let's return a simple dataframe listing the files and their content if small.
        # Or better, just return the list of files to iterate over.
        
        data = []
        for tf in txt_files:
            try:
                # Reading first line to see format
                with open(tf, 'r') as f:
                    content = f.read().strip()
                data.append({"filename": os.path.basename(tf), "content": content})
            except Exception:
                pass
                
        return pd.DataFrame(data)

    def load_suspicion_logs(self) -> pd.DataFrame:
        """
        Load the 'Students suspicious behaviors detection' dataset.
        
        Returns:
            pd.DataFrame: The loaded dataset.
        """
        folder = os.path.join(self.base_path, "student_suspicion")
        pattern = os.path.join(folder, "*.csv")
        files = glob.glob(pattern)
        
        if not files:
            raise FileNotFoundError(f"No CSV found in {folder}")
            
        # Assuming the first one is the main dataset V1
        return pd.read_csv(files[0])

if __name__ == "__main__":
    loader = ExamLoader()
    print(f"Base path: {loader.base_path}")
    
    scenarios = loader.get_cheating_scenarios()
    print(f"Found {len(scenarios)} scenarios: {scenarios[:5]}...")
    
    try:
        suspicion = loader.load_suspicion_logs()
        print(f"Suspicion Logs loaded: {suspicion.shape}")
    except Exception as e:
        print(f"Suspicion Load failed: {e}")
