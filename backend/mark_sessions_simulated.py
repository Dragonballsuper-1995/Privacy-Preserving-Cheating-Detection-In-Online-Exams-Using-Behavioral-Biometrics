"""
Mark all existing sessions as simulated.

This script creates .meta.json files for all existing session files,
marking them as simulated. Future sessions created manually will not
have these metadata files and will be treated as "Real" sessions.
"""

import os
import json
from datetime import datetime

# Configuration
EVENT_LOGS_DIR = "data/event_logs"

def mark_sessions_as_simulated():
    """Add metadata files to all existing sessions."""
    
    if not os.path.exists(EVENT_LOGS_DIR):
        print(f"❌ Directory not found: {EVENT_LOGS_DIR}")
        return
    
    session_files = []
    for filename in os.listdir(EVENT_LOGS_DIR):
        if filename.startswith("session_") and filename.endswith(".jsonl"):
            session_files.append(filename)
    
    print(f"📊 Found {len(session_files)} session files")
    
    marked_count = 0
    skipped_count = 0
    
    for filename in session_files:
        session_id = filename.replace("session_", "").replace(".jsonl", "")
        filepath = os.path.join(EVENT_LOGS_DIR, filename)
        metadata_file = os.path.join(EVENT_LOGS_DIR, f"session_{session_id}.meta.json")
        
        # Skip if metadata already exists
        if os.path.exists(metadata_file):
            skipped_count += 1
            continue
        
        # Get file creation time
        try:
            file_mtime = os.path.getmtime(filepath)
            created_at = datetime.fromtimestamp(file_mtime).isoformat()
        except:
            created_at = datetime.utcnow().isoformat()
        
        # Count events in file
        event_count = 0
        try:
            with open(filepath, 'r') as f:
                event_count = sum(1 for line in f if line.strip())
        except:
            pass
        
        # Create metadata file
        metadata = {
            "session_id": session_id,
            "is_simulated": True,
            "is_cheater": False,  # Unknown, defaulting to False
            "created_at": created_at,
            "total_events": event_count,
            "marked_at": datetime.utcnow().isoformat(),
            "note": "Marked as simulated via bulk script"
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        marked_count += 1
        
        if marked_count % 50 == 0:
            print(f"  ✓ Processed {marked_count} sessions...")
    
    print(f"\n✅ Complete!")
    print(f"  • Marked as simulated: {marked_count}")
    print(f"  • Already had metadata: {skipped_count}")
    print(f"  • Total sessions: {len(session_files)}")
    print(f"\n📝 From now on:")
    print(f"  • Simulated filter: Shows these {len(session_files)} sessions")
    print(f"  • Real filter: Shows only NEW sessions you create manually")

if __name__ == "__main__":
    print("🏷️  Marking Existing Sessions as Simulated\n")
    print("=" * 60)
    mark_sessions_as_simulated()
    print("=" * 60)
