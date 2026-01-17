import pandas as pd
import json
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime

# Adjust import based on where this script is called from or setup PYTHONPATH
# For simplicity in this standalone-ish adapter, we won't strictly depend on app.core.config 
# for paths unless necessary, but we will output to the standard location.

class CMUAdapter:
    def __init__(self, cmu_csv_path: str, output_dir: str):
        """
        Args:
            cmu_csv_path: Absolute path to DSL-StrongPasswordData.csv
            output_dir: Absolute path to where session JSONL files should be saved (backend/data/event_logs)
        """
        self.cmu_csv_path = cmu_csv_path
        self.output_dir = output_dir
        
    def convert(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Convert CMU rows to session logs.
        
        Args:
            limit: Max number of sessions (rows) to convert.
            
        Returns:
            List of session metadata dicts (session_id, is_cheater=False, etc.)
        """
        if not os.path.exists(self.cmu_csv_path):
             raise FileNotFoundError(f"CMU CSV not found at {self.cmu_csv_path}")
             
        df = pd.read_csv(self.cmu_csv_path)
        
        # Take a subset
        if limit and limit < len(df):
            df = df.head(limit)
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        converted_sessions = []
        
        print(f"Converting {len(df)} CMU sessions...")
        
        for idx, row in df.iterrows():
            session_id = str(uuid.uuid4())
            subject = row['subject']
            
            events = self._row_to_events(row, session_id)
            
            # Save JSONL
            filename = f"session_{session_id}.jsonl"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            
            converted_sessions.append({
                "session_id": session_id,
                "label": 0, # Considering all CMU benchmark data as "Honest" / "Normal" for now 
                            # (or at least consistent baseline behavior)
                "original_subject": subject,
                "events_file": filename,
                "source": "cmu_real_data"
            })
            
        return converted_sessions

    def _row_to_events(self, row, session_id: str) -> List[Dict[str, Any]]:
        """
        Reconstruct timing from CMU features.
        CMU Columns: 
        - H.period: Hold time for '.'
        - DD.period.t: Down-Down time from '.' to 't'
        - UD.period.t: Up-Down time from '.' to 't'
        ... and so on for password ".tie5Roanl"
        
        Password sequence: . t i e 5 R o a n l
        """
        password = ['.', 't', 'i', 'e', '5', 'R', 'o', 'a', 'n', 'l']
        column_map = self._get_column_map()
        
        events = []
        current_time_ms = 1000.0 # Start at 1 second
        
        for i, char in enumerate(password):
            # 1. Key Down
            # If not first char, add DD latency from previous
            if i > 0:
                prev_char = password[i-1]
                # Column name format example: DD.period.t
                dd_col = self._get_col_name('DD', prev_char, char)
                
                # CMU data is typically in seconds? Or ms?
                # "DSL-StrongPasswordData.csv" usually has seconds (e.g., 0.1234)
                # Need to verify. Based on EDA plot labels or typical datasets.
                # Assuming seconds, converting to ms.
                latency_s = row.get(dd_col, 0.1) 
                current_time_ms += (latency_s * 1000)
            
            key_down_ts = current_time_ms
            
            events.append({
                "event_type": "key",
                "timestamp": key_down_ts,
                "question_id": "cmu_task",
                "data": {
                    "type": "keydown",
                    "key": char,
                    "code": self._char_to_code(char)
                }
            })
            
            # 2. Key Up
            # Add Hold Time
            h_col = self._get_col_name('H', char)
            hold_s = row.get(h_col, 0.1)
            key_up_ts = key_down_ts + (hold_s * 1000)
            
            events.append({
                "event_type": "key",
                "timestamp": key_up_ts,
                "question_id": "cmu_task",
                "data": {
                    "type": "keyup",
                    "key": char,
                    "code": self._char_to_code(char)
                }
            })
            
        return events

    def _get_col_name(self, feature_type, char1, char2=None):
        """Helper to construct CMU column names"""
        # Mapping special chars to column names usually found in this dataset
        map_char = {
            '.': 'period',
            't': 't', 'i': 'i', 'e': 'e', '5': 'five',
            'R': 'Shift.r', 'o': 'o', 'a': 'a', 'n': 'n', 'l': 'l', 'Enter': 'Return' 
        }
        
        c1 = map_char.get(char1, char1)
        
        if feature_type == 'H':
            return f"H.{c1}"
        else:
            c2 = map_char.get(char2, char2)
            return f"{feature_type}.{c1}.{c2}"

    def _char_to_code(self, char):
        if char == '.': return "Period"
        if char.isdigit(): return f"Digit{char}"
        if char.isalpha(): return f"Key{char.upper()}"
        return "Unknown"
        
    def _get_column_map(self):
        # Could pre-compute column names, but dynamic lookup in _get_col_name is fine
        pass

if __name__ == "__main__":
    # Test run
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    cmu_path = os.path.join(base, "backend/data/datasets/keystroke/cmu/DSL-StrongPasswordData.csv")
    out_dir = os.path.join(base, "backend/data/event_logs_cmu_test")
    
    print(f"Reading from: {cmu_path}")
    adapter = CMUAdapter(cmu_path, out_dir)
    try:
        sessions = adapter.convert(limit=5)
        print(f"Successfully converted {len(sessions)} sessions.")
        print(f"First session ID: {sessions[0]['session_id']}")
    except Exception as e:
        print(f"Conversion failed: {e}")
