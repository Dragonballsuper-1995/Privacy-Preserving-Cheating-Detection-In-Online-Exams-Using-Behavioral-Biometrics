import json
import os
from typing import List, Dict, Any
from datetime import datetime

class ManifestGenerator:
    def __init__(self, output_path: str):
        """
        Args:
            output_path: Path to save training_manifest.json
        """
        self.output_path = output_path
        
    def create_manifest(self, sessions_metadata: List[Dict[str, Any]]):
        """
        Create and save the manifest file.
        
        Args:
            sessions_metadata: List of dicts, each containing 'session_id', 'label', etc.
        """
        # Count stats
        honest_count = sum(1 for s in sessions_metadata if s.get('label') == 0)
        cheater_count = sum(1 for s in sessions_metadata if s.get('label') == 1)
        
        manifest_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "honest_count": honest_count,
            "cheater_count": cheater_count,
            "total_count": len(sessions_metadata),
            "sessions": sessions_metadata
        }
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
            
        print(f"Manifest created at {self.output_path} with {len(sessions_metadata)} sessions.")

if __name__ == "__main__":
    # Test
    pass
