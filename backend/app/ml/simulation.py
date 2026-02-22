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
from datetime import datetime, timezone

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


# ─── Answer Text Pools ────────────────────────────────────────────────────────

# AI-like answers (formal, uniform, hedge phrases, transition words)
_AI_ANSWERS = [
    (
        "It is important to note that encryption plays a crucial role in modern cybersecurity. "
        "Furthermore, symmetric encryption algorithms such as AES utilize fixed-length keys to ensure data confidentiality. "
        "Additionally, asymmetric encryption leverages public-private key pairs to facilitate secure communication. "
        "Moreover, the implementation of robust encryption protocols is essential to protect sensitive information. "
        "In conclusion, a comprehensive understanding of encryption mechanisms is vital for maintaining data integrity."
    ),
    (
        "In today's digital age, data structures form the foundation of efficient software development. "
        "Furthermore, arrays and linked lists serve as fundamental building blocks for more complex structures. "
        "Additionally, hash tables provide constant-time lookups, which significantly enhances application performance. "
        "It is worth mentioning that balanced binary search trees maintain logarithmic time complexity for insertions and deletions. "
        "Consequently, selecting the appropriate data structure is crucial for optimizing algorithmic efficiency."
    ),
    (
        "The concept of object-oriented programming is essential to modern software engineering. "
        "Moreover, encapsulation facilitates the bundling of data with methods that operate on that data. "
        "Furthermore, inheritance enables the creation of hierarchical class structures that promote code reuse. "
        "It is crucial to understand that polymorphism allows objects to be treated as instances of their parent class. "
        "In summary, these comprehensive principles form the backbone of maintainable and scalable software systems."
    ),
    (
        "Database normalization plays a vital role in reducing data redundancy and improving data integrity. "
        "Additionally, the first normal form eliminates repeating groups and ensures atomic values in each column. "
        "Furthermore, the second normal form removes partial dependencies on composite primary keys. "
        "It is important to note that the third normal form addresses transitive dependencies between non-key attributes. "
        "Nevertheless, in certain scenarios, denormalization may be leveraged to optimize query performance."
    ),
    (
        "Machine learning algorithms can be broadly categorized into supervised and unsupervised learning paradigms. "
        "Furthermore, supervised learning utilizes labeled training data to facilitate model training and prediction. "
        "Additionally, unsupervised learning algorithms such as k-means clustering identify inherent patterns in unlabeled datasets. "
        "It is essential to consider that overfitting occurs when a model learns noise rather than the underlying data distribution. "
        "Consequently, techniques such as cross-validation and regularization are crucial for developing robust models."
    ),
    (
        "Network protocols are essential for facilitating communication between devices in a distributed system. "
        "Moreover, the TCP/IP model provides a comprehensive framework for data transmission across networks. "
        "Furthermore, HTTP and HTTPS protocols leverage the application layer to enable web-based communication. "
        "It is worth mentioning that the implementation of TLS encryption ensures secure data transfer between clients and servers. "
        "In conclusion, understanding network protocols is vital for designing and maintaining robust distributed systems."
    ),
]

# Human-like answers (casual, varied, some errors, natural rhythm)
_HUMAN_ANSWERS = [
    (
        "Encryption is basically scrambling data so nobody can read it without the right key. "
        "There's two main types - symmetric where both sides use the same key like AES, "
        "and asymmetric where you have a public key and private key. I think RSA is the most common one for that. "
        "The main point is keeping stuff secure when sending data over the internet."
    ),
    (
        "So data structures are how we organize data in programs. "
        "Arrays are pretty simple, just a list of items. Linked lists are similar but each item points to the next one. "
        "Hash maps are super fast for looking things up. "
        "Trees and graphs get more complicated but they're good for hierarchical data and networks."
    ),
    (
        "OOP is about organizing code into objects that have properties and methods. "
        "You can extend classes through inheritance which saves a lot of rewriting code. "
        "Polymorphism lets you use a parent class type to refer to child objects, pretty handy. "
        "I find encapsulation useful bc it keeps internals hidden from outside code."
    ),
    (
        "Normalization is about organizing database tables to avoid duplicate data. "
        "1NF means no repeating groups, every cell has one value. "
        "2NF builds on that - no partial deps on the primary key. "
        "3NF removes transitive dependencies. Sometimes you denormalize for speed tho."
    ),
    (
        "ML is split into supervised and unsupervised basically. "
        "Supervised means you have labeled data to train on, like classification or regression. "
        "Unsupervised is finding patterns without labels, clustering and stuff. "
        "You gotta watch out for overfitting, thats when the model memorizes the training data instead of learning patterns."
    ),
    (
        "Networking uses protocols to let computers talk to each other. "
        "TCP/IP is the main one, handles how data gets packaged and sent. "
        "HTTP is for web stuff, HTTPS adds encryption on top. "
        "DNS converts domain names to IP addresses. Routers and switches handle moving data between networks."
    ),
]


def _generate_answer_text(is_cheater: bool, question_idx: int) -> str:
    """
    Generate answer text for a simulated session.
    Cheaters get AI-like text; honest students get casual human text.
    """
    if is_cheater:
        return random.choice(_AI_ANSWERS)
    else:
        return random.choice(_HUMAN_ANSWERS)

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
        
        # Generate answer submission event
        current_time += random.uniform(500, 2000)
        answer_text = _generate_answer_text(is_cheater, q_idx)
        all_events.append({
            "event_type": "answer_submit",
            "timestamp": current_time,
            "question_id": question_id,
            "data": {"content": answer_text}
        })
        
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
    Save a simulated session to JSONL file with metadata.
    
    Args:
        session_data: Session data from simulate_session()
        
    Returns:
        Path to saved file
    """
    session_id = session_data["session_id"]
    log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
    metadata_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.meta.json")
    
    os.makedirs(settings.event_logs_dir, exist_ok=True)
    
    # Save events to JSONL
    with open(log_file, 'w') as f:
        for event in session_data["events"]:
            f.write(json.dumps(event) + "\n")
    
    # Save metadata marking this as simulated
    metadata = {
        "session_id": session_id,
        "is_simulated": True,
        "is_cheater": session_data.get("is_cheater", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question_count": session_data.get("question_count", 0),
        "total_events": len(session_data.get("events", [])),
    }
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
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
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "honest_count": honest_count,
            "cheater_count": cheater_count,
            "sessions": dataset,
        }, f, indent=2)
    
    print(f"✅ Dataset saved to {manifest_path}")
    return dataset
