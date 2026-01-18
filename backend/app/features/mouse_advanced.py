"""
Advanced Mouse Movement Analysis

Detects suspicious mouse behavior patterns:
- Unnatural linear movements (indicating copy-paste from external source)
- Trajectory entropy (randomness in mouse paths)
- Click patterns and timing
- Mouse idle periods
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import math
import statistics


@dataclass
class MouseFeatures:
    """Advanced mouse movement features."""
    # Movement characteristics
    total_movements: int = 0
    total_distance: float = 0.0
    avg_velocity: float = 0.0
    max_velocity: float = 0.0
    velocity_variance: float = 0.0
    
    # Acceleration
    avg_acceleration: float = 0.0
    sudden_direction_changes: int = 0
    
    # Trajectory analysis
    trajectory_entropy: float = 0.0
    linear_movement_ratio: float = 0.0
    
    # Click patterns
    total_clicks: int = 0
    left_clicks: int = 0
    right_clicks: int = 0
    double_clicks: int = 0
    avg_click_duration: float = 0.0
    
    # Idle periods
    idle_periods: int = 0
    total_idle_time: float = 0.0
    max_idle_duration: float = 0.0
    
    # Context switches (mouse leaving exam area)
    context_switches: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_movements": self.total_movements,
            "total_distance": self.total_distance,
            "avg_velocity": self.avg_velocity,
            "max_velocity": self.max_velocity,
            "velocity_variance": self.velocity_variance,
            "avg_acceleration": self.avg_acceleration,
            "sudden_direction_changes": self.sudden_direction_changes,
            "trajectory_entropy": self.trajectory_entropy,
            "linear_movement_ratio": self.linear_movement_ratio,
            "total_clicks": self.total_clicks,
            "left_clicks": self.left_clicks,
            "right_clicks": self.right_clicks,
            "double_clicks": self.double_clicks,
            "avg_click_duration": self.avg_click_duration,
            "idle_periods": self.idle_periods,
            "total_idle_time": self.total_idle_time,
            "max_idle_duration": self.max_idle_duration,
            "context_switches": self.context_switches,
        }


def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def calculate_velocity(distance: float, time_delta_ms: float) -> float:
    """Calculate velocity in pixels per second."""
    if time_delta_ms <= 0:
        return 0.0
    return (distance / time_delta_ms) * 1000  # Convert to px/second


def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
    """Calculate angle between three points (in degrees)."""
    # Vector 1: p1 -> p2
    v1_x, v1_y = p2[0] - p1[0], p2[1] - p1[1]
    # Vector 2: p2 -> p3
    v2_x, v2_y = p3[0] - p2[0], p3[1] - p2[1]
    
    # Dot product and magnitudes
    dot_product = v1_x * v2_x + v1_y * v2_y
    mag1 = math.sqrt(v1_x**2 + v1_y**2)
    mag2 = math.sqrt(v2_x**2 + v2_y**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Angle in radians, then convert to degrees
    cos_angle = dot_product / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp for numerical stability
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)


def calculate_trajectory_entropy(points: List[Tuple[float, float]]) -> float:
    """
    Calculate entropy of mouse trajectory.
    
    Higher entropy = more random, natural movements.
    Lower entropy = more linear, potentially suspicious movements.
    """
    if len(points) < 3:
        return 0.0
    
    # Divide trajectory into grid cells and calculate entropy
    # Based on distribution of points across cells
    
    # Find bounding box
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Avoid division by zero
    if max_x == min_x or max_y == min_y:
        return 0.0
    
    # Create 10x10 grid
    grid_size = 10
    cell_width = (max_x - min_x) / grid_size
    cell_height = (max_y - min_y) / grid_size
    
    # Count points in each cell
    cell_counts = {}
    for x, y in points:
        cell_x = min(int((x - min_x) / cell_width), grid_size - 1)
        cell_y = min(int((y - min_y) / cell_height), grid_size - 1)
        cell_key = (cell_x, cell_y)
        cell_counts[cell_key] = cell_counts.get(cell_key, 0) + 1
    
    # Calculate entropy
    total_points = len(points)
    entropy = 0.0
    
    for count in cell_counts.values():
        if count > 0:
            probability = count / total_points
            entropy -= probability * math.log2(probability)
    
    return entropy


def extract_mouse_features(events: List[Dict[str, Any]], idle_threshold_ms: float = 3000) -> MouseFeatures:
    """
    Extract advanced mouse movement features from events.
    
    Args:
        events: List of event dictionaries
        idle_threshold_ms: Minimum time without movement to count as idle
        
    Returns:
        MouseFeatures dataclass with extracted features
    """
    features = MouseFeatures()
    
    # Filter mouse events
    mouse_events = [e for e in events if e.get("event_type") in ["mouse", "click"]]
    
    if not mouse_events:
        return features
    
    # Extract mouse movements
    movements = []
    clicks = []
    
    for event in mouse_events:
        event_type = event.get("event_type")
        data = event.get("data", {})
        timestamp = event.get("timestamp", 0)
        
        if event_type == "mouse":
            x = data.get("x", 0)
            y = data.get("y", 0)
            movements.append({"x": x, "y": y, "timestamp": timestamp})
        
        elif event_type == "click":
            button = data.get("button", "left")
            duration = data.get("duration", 0)
            clicks.append({
                "button": button,
                "duration": duration,
                "timestamp": timestamp
            })
    
    # Analyze movements
    if len(movements) >= 2:
        features.total_movements = len(movements)
        
        # Calculate distances, velocities, and accelerations
        distances = []
        velocities = []
        points = [(m["x"], m["y"]) for m in movements]
        
        for i in range(1, len(movements)):
            # Distance
            dist = calculate_distance(
                (movements[i-1]["x"], movements[i-1]["y"]),
                (movements[i]["x"], movements[i]["y"])
            )
            distances.append(dist)
            
            # Velocity
            time_delta = movements[i]["timestamp"] - movements[i-1]["timestamp"]
            velocity = calculate_velocity(dist, time_delta)
            velocities.append(velocity)
        
        if distances:
            features.total_distance = sum(distances)
        
        if velocities:
            features.avg_velocity = statistics.mean(velocities)
            features.max_velocity = max(velocities)
            features.velocity_variance = statistics.variance(velocities) if len(velocities) > 1 else 0.0
        
        # Calculate accelerations (change in velocity)
        if len(velocities) >= 2:
            accelerations = []
            for i in range(1, len(velocities)):
                time_delta = movements[i+1]["timestamp"] - movements[i]["timestamp"]
                if time_delta > 0:
                    accel = (velocities[i] - velocities[i-1]) / (time_delta / 1000)
                    accelerations.append(accel)
            
            if accelerations:
                features.avg_acceleration = statistics.mean([abs(a) for a in accelerations])
        
        # Detect sudden direction changes (sharp angles)
        if len(movements) >= 3:
            sharp_turns = 0
            for i in range(1, len(movements) - 1):
                angle = calculate_angle(
                    (movements[i-1]["x"], movements[i-1]["y"]),
                    (movements[i]["x"], movements[i]["y"]),
                    (movements[i+1]["x"], movements[i+1]["y"])
                )
                # Angle > 120 degrees is a sharp turn
                if angle > 120:
                    sharp_turns += 1
            
            features.sudden_direction_changes = sharp_turns
        
        # Calculate trajectory entropy
        features.trajectory_entropy = calculate_trajectory_entropy(points)
        
        # Calculate linear movement ratio
        # Ratio of straight-line distance to actual path distance
        if features.total_distance > 0:
            straight_line_dist = calculate_distance(points[0], points[-1])
            features.linear_movement_ratio = straight_line_dist / features.total_distance
    
    # Analyze clicks
    if clicks:
        features.total_clicks = len(clicks)
        features.left_clicks = sum(1 for c in clicks if c["button"] == "left")
        features.right_clicks = sum(1 for c in clicks if c["button"] == "right")
        
        # Detect double clicks (clicks within 500ms)
        double_click_threshold = 500
        for i in range(1, len(clicks)):
            time_diff = clicks[i]["timestamp"] - clicks[i-1]["timestamp"]
            if time_diff < double_click_threshold:
                features.double_clicks += 1
        
        # Average click duration
        durations = [c["duration"] for c in clicks if c["duration"] > 0]
        if durations:
            features.avg_click_duration = statistics.mean(durations)
    
    # Detect idle periods
    if len(movements) >= 2:
        idle_count = 0
        idle_durations = []
        
        for i in range(1, len(movements)):
            time_gap = movements[i]["timestamp"] - movements[i-1]["timestamp"]
            if time_gap > idle_threshold_ms:
                idle_count += 1
                idle_durations.append(time_gap)
        
        features.idle_periods = idle_count
        if idle_durations:
            features.total_idle_time = sum(idle_durations)
            features.max_idle_duration = max(idle_durations)
    
    return features


def calculate_mouse_anomaly_score(features: MouseFeatures) -> float:
    """
    Calculate anomaly score based on mouse features.
    
    Higher scores indicate more suspicious patterns.
    
    Args:
        features: MouseFeatures dataclass
        
    Returns:
        Anomaly score between 0 and 1
    """
    score = 0.0
    
    # Very high velocity suggests automated movement or copy-paste
    if features.avg_velocity > 1000:  # > 1000 px/s
        score += 0.25
    elif features.avg_velocity > 500:
        score += 0.1
    
    # Very linear movements (low entropy) suggest copy-paste
    if features.trajectory_entropy < 2.0 and features.total_movements > 10:
        score += 0.2
    
    # High linear movement ratio (straight lines) is suspicious
    if features.linear_movement_ratio > 0.9 and features.total_distance > 100:
        score += 0.15
    
    # Extended idle periods might indicate looking up answers
    if features.max_idle_duration > 30000:  # > 30 seconds
        score += 0.2
    elif features.max_idle_duration > 15000:
        score += 0.1
    
    # Very few mouse movements despite activity might indicate keyboard-only cheating
    if features.total_movements < 10:
        score += 0.1
    
    return min(score, 1.0)
