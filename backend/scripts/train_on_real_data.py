import os
import sys

# Add src to path
# Script is in backend/scripts/
current_dir = os.path.dirname(os.path.abspath(__file__))
# backend/scripts/.. -> backend
project_root = os.path.abspath(os.path.join(current_dir, "../"))
# We expect source code in backend/src
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)
sys.path.append(project_root) # Add backend/ root to allow 'import app...'

print(f"DEBUG: Appended {src_path} and {project_root} to sys.path")
print(f"DEBUG: Contents of src: {os.listdir(src_path) if os.path.exists(src_path) else 'NOT FOUND'}")

from data_ingestion.cmu_adapter import CMUAdapter
from data_ingestion.manifest_generator import ManifestGenerator

def main():
    print("🚀 Starting Real Data Training Pipeline...")
    
    # Paths
    base_data = os.path.join(project_root, "data")
    cmu_path = os.path.join(base_data, "datasets/keystroke/cmu/DSL-StrongPasswordData.csv")
    event_logs_dir = os.path.join(base_data, "event_logs")
    manifest_path = os.path.join(base_data, "training_manifest.json")
    
    # 1. Run CMU Adapter
    print("\n[1/3] Converting CMU Data...")
    adapter = CMUAdapter(cmu_path, event_logs_dir)
    # Using a subset of 200 sessions to avoid overfitting or long training for this demo
    sessions_meta = adapter.convert(limit=200) 
    
    # 2. Generate Manifest
    print("\n[2/3] Generating Manifest...")
    gen = ManifestGenerator(manifest_path)
    gen.create_manifest(sessions_meta)
    
    # 3. Trigger Training (via API or direct import)
    # Since we are in the backend scope, we can import the training logic directly
    # BUT, the training logic in `app.api.simulation` is coupled to FastAPI.
    # The actual logic is in `train_models` endpoint but likely we want to run it directly.
    # We'll invoke the endpoint logic manually or import the core components.
    
    print("\n[3/3] Training Models...")
    # NOTE: In a real scenario we'd use requests.post('http://localhost:8000/api/simulation/train-models')
    # But checking if we can run it inline for simplicity.
    # app.api.simulation.train_models relies on `settings`.
    
    try:
        # We need to set pythonpath to backend/app for imports to work inside app
        sys.path.append(os.path.join(project_root, "../")) # Add 'backend' parent? No, 'app' is inside 'backend'.
        # Actually existing sys.path has project_root/src.
        # But 'app' is a sibling of 'src' or inside 'backend'?
        # Directory structure: backend/app, backend/src
        
        # We need 'backend' in path to do 'from app.ml...'?
        sys.path.append(project_root) # adds 'backend/' to path ? 
        # No, project_root is '.../backend'.
        
        from app.ml.anomaly import BehaviorAnomalyDetector
        from app.ml.fusion import RiskFusionModel
        from app.features.pipeline import extract_all_features
        import json
        
        # Re-implementing the core training loop here to avoid FastAPI dependencies
        feature_vectors = []
        fusion_training_data = [] # Not really usable yet as we only have honesty labels (0) from CMU
        
        print(f"  - Extracting features from {len(sessions_meta)} sessions...")
        for session_info in sessions_meta:
            log_file = os.path.join(event_logs_dir, session_info['events_file'])
            if not os.path.exists(log_file): continue
            
            events = []
            with open(log_file, 'r') as f:
                for line in f:
                    events.append(json.loads(line))
            
            if not events: continue
            
            features = extract_all_features(events, session_info['session_id'])
            feature_vectors.append(features.to_dict())
        
        print(f"  - Training Anomaly Detector on {len(feature_vectors)} vectors...")
        detector = BehaviorAnomalyDetector()
        detector.fit(feature_vectors)
        print(f"  - Model saved to {detector.model_path}")
        
        print("\n✅ Training Complete!")
        
    except ImportError as e:
        print(f"⚠️ Could not import app modules: {e}")
        print("Please run the server and hit /api/simulation/train-models instead.")
    except Exception as e:
        print(f"❌ Training Failed: {e}")

if __name__ == "__main__":
    main()
