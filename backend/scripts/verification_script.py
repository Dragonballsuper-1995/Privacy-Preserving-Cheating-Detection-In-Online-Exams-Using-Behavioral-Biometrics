
import sys
import os
import logging

# Ensure backend is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.ml.ieee_loaders import (
    load_student_suspicion_data,
    load_authcode_data,
    load_ensemble_keystroke_data,
    load_tchad100_data,
    load_ikdd_data,
    load_liveness_detection_data,
    load_balabit_mouse_data,
    load_pan11_plagiarism_data
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_loaders():
    print("=== Testing IEEE Loaders ===")
    
    # 1. Student Suspicion
    try:
        data = load_student_suspicion_data(max_rows=10)
        print(f"Student Suspicion: Loaded {len(data)} samples - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"Student Suspicion: ERROR - {e}")

    # 2. Authcode
    try:
        data = load_authcode_data(dataset_num=1, max_rows=10)
        print(f"Authcode: Loaded {len(data)} samples - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"Authcode: ERROR - {e}")

    # 3. Ensemble Keystroke (Impostor) - Was failing
    try:
        data = load_ensemble_keystroke_data(label_type="impostor", max_rows=10)
        print(f"Ensemble (Impostor): Loaded {len(data)} samples - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"Ensemble (Impostor): ERROR - {e}")

    # 4. Liveness Detection - Was failing
    try:
        data = load_liveness_detection_data()
        # It loads from many files, might be 0 if only small subset checked?
        # But we expect >0
        print(f"Liveness Detection: Loaded {len(data)} samples - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"Liveness Detection: ERROR - {e}")

    # 5. Balabit Mouse - Was 0
    try:
        data = load_balabit_mouse_data(max_users=2)
        print(f"Balabit Mouse: Loaded {len(data)} sessions - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"Balabit Mouse: ERROR - {e}")

    # 6. PAN-11 - Was failing
    try:
        data = load_pan11_plagiarism_data()
        print(f"PAN-11: Loaded {len(data)} documents - {'OK' if len(data)>0 else 'FAIL'}")
    except Exception as e:
        print(f"PAN-11: ERROR - {e}")

if __name__ == "__main__":
    test_loaders()
