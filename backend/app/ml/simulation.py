"""
Simulation Mode for Test Data Generation

Generates synthetic behavioral data for testing and model training.
Creates both "honest" and "cheating" session simulations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
import json
import os
import uuid
from datetime import datetime

from app.core.config import settings


@dataclass
class SimulationConfig:
    """Configuration for session simulation."""
    session_id: str
    is_cheater: bool
    question_count: int = 6
    avg_typing_speed: float = 40.0  # WPM
    paste_probability: float = 0.0
    tab_switch_probability: float = 0.0
    long_pause_probability: float = 0.1
    

def generate_keystroke_events(
    config: SimulationConfig,
    question_id: str,
    text_length: int = 100,
    start_time: float = 0
) -> List[Dict[str, Any]]:
    """Generate simulated keystroke events."""
    events = []
    current_time = start_time
    
    if config.is_cheater:
        # Cheaters type faster (might have pre-written answers)
        base_delay = 60000 / (config.avg_typing_speed * 1.5) / 5
        delay_variance = 50  # More consistent (suspicious)
    else:
        # Normal typing pattern
        base_delay = 60000 / config.avg_typing_speed / 5
        delay_variance = 150  # Natural variation
    
    characters = 0
    while characters < text_length:
        # Keydown event
        inter_key_delay = base_delay + random.gauss(0, delay_variance)
        inter_key_delay = max(30, inter_key_delay)  # Minimum 30ms
        
        current_time += inter_key_delay
        
        events.append({
            "event_type": "key",
            "timestamp": current_time,
            "question_id": question_id,
            "data": {
                "type": "keydown",
                "key": chr(random.randint(97, 122)),  # random letter
                "code": f"Key{chr(random.randint(65, 90))}",
            }
        })
        
        # Keyup event (after hold time)
        hold_time = random.gauss(100, 30)
        hold_time = max(30, min(300, hold_time))
        current_time += hold_time
        
        events.append({
            "event_type": "key",
            "timestamp": current_time,
            "question_id": question_id,
            "data": {
                "type": "keyup",
                "key": events[-1]["data"]["key"],
                "code": events[-1]["data"]["code"],
            }
        })
        
        characters += 1
        
        # Random long pause (thinking)
        if random.random() < config.long_pause_probability:
            pause_duration = random.uniform(3000, 15000)
            if config.is_cheater:
                pause_duration = random.uniform(5000, 30000)  # Longer pauses (looking up answers)
            current_time += pause_duration
    
    return events, current_time


def generate_paste_events(
    config: SimulationConfig,
    question_id: str,
    current_time: float
) -> List[Dict[str, Any]]:
    """Generate simulated paste events."""
    events = []
    
    if random.random() < config.paste_probability:
        # Paste event
        paste_length = random.randint(50, 500)
        current_time += random.uniform(100, 500)
        
        events.append({
            "event_type": "paste",
            "timestamp": current_time,
            "question_id": question_id,
            "data": {
                "content_length": paste_length,
            }
        })
    
    return events, current_time


def generate_focus_events(
    config: SimulationConfig,
    question_id: str,
    start_time: float,
    duration: float
) -> List[Dict[str, Any]]:
    """Generate simulated focus/blur events."""
    events = []
    current_time = start_time
    
    # Number of tab switches based on probability
    num_switches = 0
    if config.is_cheater and random.random() < config.tab_switch_probability:
        num_switches = random.randint(2, 8)
    elif random.random() < config.tab_switch_probability * 0.3:
        num_switches = random.randint(0, 2)
    
    for _ in range(num_switches):
        # Random time for blur
        blur_time = start_time + random.uniform(0, duration)
        
        # Duration of unfocused time
        if config.is_cheater:
            unfocused_duration = random.uniform(5000, 45000)  # 5-45 seconds
        else:
            unfocused_duration = random.uniform(1000, 5000)  # 1-5 seconds (accidental)
        
        events.append({
            "event_type": "focus",
            "timestamp": blur_time,
            "question_id": question_id,
            "data": {"type": "blur"}
        })
        
        events.append({
            "event_type": "focus",
            "timestamp": blur_time + unfocused_duration,
            "question_id": question_id,
            "data": {"type": "focus"}
        })
    
    return sorted(events, key=lambda x: x["timestamp"])


def simulate_session(
    is_cheater: bool = False,
    question_count: int = 6,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a complete simulated exam session.
    
    Args:
        is_cheater: Whether to simulate cheating behavior
        question_count: Number of questions
        session_id: Optional session ID (generated if not provided)
        
    Returns:
        Dictionary with session info and events
    """
    session_id = session_id or str(uuid.uuid4())
    
    # Configure simulation based on behavior type
    if is_cheater:
        config = SimulationConfig(
            session_id=session_id,
            is_cheater=True,
            question_count=question_count,
            avg_typing_speed=60,  # Faster
            paste_probability=0.7,  # High paste chance
            tab_switch_probability=0.8,  # High tab switching
            long_pause_probability=0.3,  # More long pauses
        )
    else:
        config = SimulationConfig(
            session_id=session_id,
            is_cheater=False,
            question_count=question_count,
            avg_typing_speed=35,  # Normal speed
            paste_probability=0.05,  # Rare paste
            tab_switch_probability=0.1,  # Rare tab switch
            long_pause_probability=0.1,  # Some thinking pauses
        )
    
    all_events = []
    current_time = 0
    
    for q_idx in range(question_count):
        question_id = f"q{q_idx + 1}"
        question_start = current_time
        
        # Text length varies by question
        text_length = random.randint(50, 200)
        
        # Generate keystrokes
        key_events, current_time = generate_keystroke_events(
            config, question_id, text_length, current_time
        )
        all_events.extend(key_events)
        
        # Generate paste events
        paste_events, current_time = generate_paste_events(
            config, question_id, current_time
        )
        all_events.extend(paste_events)
        
        # Generate focus events
        question_duration = current_time - question_start
        focus_events = generate_focus_events(
            config, question_id, question_start, question_duration
        )
        all_events.extend(focus_events)
        
        # Transition time between questions
        current_time += random.uniform(2000, 5000)
    
    # Sort all events by timestamp
    all_events.sort(key=lambda x: x["timestamp"])
    
    return {
        "session_id": session_id,
        "is_cheater": is_cheater,
        "question_count": question_count,
        "total_events": len(all_events),
        "duration_ms": current_time,
        "events": all_events,
    }


def save_simulated_session(session_data: Dict[str, Any]) -> str:
    """
    Save a simulated session to JSONL file.
    
    Args:
        session_data: Session data from simulate_session()
        
    Returns:
        Path to saved file
    """
    session_id = session_data["session_id"]
    log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
    
    os.makedirs(settings.event_logs_dir, exist_ok=True)
    
    with open(log_file, 'w') as f:
        for event in session_data["events"]:
            f.write(json.dumps(event) + "\n")
    
    return log_file


def generate_training_dataset(
    honest_count: int = 50,
    cheater_count: int = 20
) -> List[Dict[str, Any]]:
    """
    Generate a training dataset with labeled sessions.
    
    Args:
        honest_count: Number of honest sessions
        cheater_count: Number of cheating sessions
        
    Returns:
        List of session data dictionaries with labels
    """
    dataset = []
    
    print(f"📊 Generating {honest_count} honest sessions...")
    for i in range(honest_count):
        session = simulate_session(is_cheater=False)
        save_simulated_session(session)
        dataset.append({
            "session_id": session["session_id"],
            "label": 0,  # Honest
            "events_file": f"session_{session['session_id']}.jsonl",
        })
    
    print(f"📊 Generating {cheater_count} cheating sessions...")
    for i in range(cheater_count):
        session = simulate_session(is_cheater=True)
        save_simulated_session(session)
        dataset.append({
            "session_id": session["session_id"],
            "label": 1,  # Cheating
            "events_file": f"session_{session['session_id']}.jsonl",
        })
    
    # Save dataset manifest
    manifest_path = os.path.join(settings.data_dir, "training_manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat(),
            "honest_count": honest_count,
            "cheater_count": cheater_count,
            "sessions": dataset,
        }, f, indent=2)
    
    print(f"✅ Dataset saved to {manifest_path}")
    return dataset
