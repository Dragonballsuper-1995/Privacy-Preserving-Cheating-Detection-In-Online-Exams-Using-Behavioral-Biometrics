"""
Load Testing with Locust

Simulates realistic exam scenarios with multiple concurrent users.
Tests API response times under load.
"""

from locust import HttpUser, task, between, events
import random
import json


class ExamStudent(HttpUser):
    """Simulates a student taking an exam."""
    
    wait_time = between(0.5, 2)  # Wait 0.5-2 seconds between actions
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Create a session
        response = self.client.post("/api/sessions/create", json={
            "exam_id": "load-test-exam",
            "student_id": f"student_{random.randint(1, 1000)}"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data.get("session_id")
        else:
            self.session_id = f"test_session_{random.randint(1, 10000)}"
    
    @task(10)
    def log_keystroke_events(self):
        """Simulate typing behavior (most common action)."""
        events = []
        
        # Generate multiple keystrokes
        for i in range(random.randint(5, 20)):
            events.append({
                "event_type": "keydown",
                "timestamp": int(random.random() * 10000),
                "data": {
                    "key": chr(random.randint(97, 122)),  # a-z
                    "hold_time": random.randint(60, 120)
                }
            })
        
        self.client.post("/api/events/log", json={
            "session_id": self.session_id,
            "events": events
        })
    
    @task(2)
    def log_paste_event(self):
        """Simulate paste event (less common)."""
        self.client.post("/api/events/log", json={
            "session_id": self.session_id,
            "events": [{
                "event_type": "paste",
                "timestamp": int(random.random() * 10000),
                "data": {"length": random.randint(10, 500)}
            }]
        })
    
    @task(3)
    def log_focus_events(self):
        """Simulate focus/blur events."""
        events = [
            {
                "event_type": "blur",
                "timestamp": int(random.random() * 10000),
                "data": {}
            },
            {
                "event_type": "focus",
                "timestamp": int(random.random() * 10000) + 1000,
                "data": {}
            }
        ]
        
        self.client.post("/api/events/log", json={
            "session_id": self.session_id,
            "events": events
        })
    
    @task(1)
    def check_session_status(self):
        """Check session status (admin-like query)."""
        self.client.get(f"/api/sessions/{self.session_id}")
    
    def on_stop(self):
        """Called when a simulated user stops."""
        # Submit the session
        if hasattr(self, 'session_id'):
            self.client.post(f"/api/sessions/{self.session_id}/submit", json={
                "answers": {}
            })


class AdminUser(HttpUser):
    """Simulates an administrator monitoring exams."""
    
    wait_time = between(2, 5)  # Check less frequently
    
    @task
    def get_dashboard_summary(self):
        """Get dashboard statistics."""
        self.client.get("/api/analysis/dashboard/summary")
    
    @task
    def analyze_random_session(self):
        """Analyze a random session."""
        session_id = f"test_session_{random.randint(1, 100)}"
        self.client.post("/api/analysis/analyze", json={
            "session_id": session_id
        })


# Event handlers for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom metrics."""
    if exception:
        print(f"Request failed: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("🚀 Starting load test...")
    print(f"   Target: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    stats = environment.stats
    print("\n📊 Load Test Results:")
    print(f"   Total requests: {stats.total.num_requests}")
    print(f"   Failures: {stats.total.num_failures}")
    print(f"   Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"   P95 response time: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"   P99 response time: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"   Requests/sec: {stats.total.total_rps:.2f}")


# To run this file:
# locust -f test_load.py --host=http://localhost:8000
#
# Then open http://localhost:8089 to configure:
# - Number of users (e.g., 100)
# - Spawn rate (e.g., 10 users per second)
# - Run time (e.g., 5 minutes)
#
# Targets to verify:
# - Handle 100+ concurrent users
# - P95 response time < 500ms under load
# - No failed requests under normal load
