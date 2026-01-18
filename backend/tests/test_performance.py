"""
Performance Testing Suite

Benchmarks feature extraction latency, ML inference speed, and system throughput.
Targets: Feature extraction <100ms, ML inference <500ms.
"""

import sys
import os
import time
import pytest
from pathlib import Path
import statistics

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.features.pipeline import extract_all_features
from app.ml.anomaly import BehaviorAnomalyDetector
from app.ml.fusion import RiskFusionModel


def generate_test_events(count=100):
    """Generate realistic test events."""
    events = []
    timestamp = 1000
    
    for i in range(count):
        # Mix of different event types
        if i % 10 == 0:
            events.append({"event_type": "paste", "timestamp": timestamp, "data": {"length": 50}})
        elif i % 15 == 0:
            events.append({"event_type": "blur", "timestamp": timestamp, "data": {}})
        elif i % 16 == 0:
            events.append({"event_type": "focus", "timestamp": timestamp, "data": {}})
        else:
            events.append({
                "event_type": "keydown",
                "timestamp": timestamp,
                "data": {"key": chr(97 + (i % 26)), "hold_time": 80 + (i % 20)}
            })
        
        timestamp += 100 + (i % 50)
    
    return events


class TestPerformanceBenchmarks:
    """Performance benchmarks for critical operations."""
    
    def test_feature_extraction_latency(self):
        """Benchmark feature extraction speed (target: <100ms)."""
        events = generate_test_events(500)  # 500 events is realistic for one answer
        
        # Warm-up
        extract_all_features(events, session_id="warmup")
        
        # Benchmark multiple runs
        times = []
        for _ in range(10):
            start = time.perf_counter()
            features = extract_all_features(events, session_id=f"test_{_}")
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"\nFeature Extraction Performance:")
        print(f"  Events: {len(events)}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        
        # Target: <100ms for p95
        assert p95_time < 100, f"Feature extraction too slow: {p95_time:.2f}ms (target: <100ms)"
    
    def test_ml_inference_latency(self):
        """Benchmark ML prediction speed (target: <500ms)."""
        # Generate features
        events = generate_test_events(200)
        features = extract_all_features(events, session_id="test")
        feature_dict = features.to_dict()
        
        # Create detector
        detector = BehaviorAnomalyDetector()
        
        # Warm-up
        detector.detect(feature_dict, "test")
        
        # Benchmark multiple runs
        times = []
        for i in range(20):
            start = time.perf_counter()
            result = detector.detect(feature_dict, f"test_{i}")
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"\nML Inference Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        
        # Target: <500ms for p95
        assert p95_time < 500, f"ML inference too slow: {p95_time:.2f}ms (target: <500ms)"
    
    def test_end_to_end_pipeline_latency(self):
        """Benchmark complete pipeline from events to prediction."""
        events = generate_test_events(300)
        detector = BehaviorAnomalyDetector()
        
        times = []
        for i in range(10):
            start = time.perf_counter()
            
            # Complete pipeline
            features = extract_all_features(events, session_id=f"session_{i}")
            feature_dict = features.to_dict()
            result = detector.detect(feature_dict, f"session_{i}")
            
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"\nEnd-to-End Pipeline Performance:")
        print(f"  Events: {len(events)}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        
        # Combined target: <600ms for complete pipeline
        assert p95_time < 600, f"Pipeline too slow: {p95_time:.2f}ms (target: <600ms)"
    
    def test_concurrent_feature_extraction(self):
        """Test feature extraction under concurrent load."""
        import concurrent.futures
        
        events_list = [generate_test_events(200) for _ in range(10)]
        
        start = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(extract_all_features, events, f"session_{i}") for i, events in enumerate(events_list)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end = time.perf_counter()
        total_time = (end - start) * 1000
        
        print(f"\nConcurrent Processing Performance:")
        print(f"  Sessions: 10")
        print(f"  Workers: 5")
        print(f"  Total time: {total_time:.2f}ms")
        print(f"  Avg per session: {total_time/10:.2f}ms")
        
        assert len(results) == 10, "All concurrent tasks should complete"
   
    def test_memory_usage(self):
        """Monitor memory usage during processing."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Measure baseline
            baseline_mb = process.memory_info().rss / 1024 / 1024
            
            # Process many events
            large_events = generate_test_events(10000)
            
            for i in range(10):
                features = extract_all_features(large_events, session_id=f"test_{i}")
                feature_dict = features.to_dict()
            
            # Measure after processing
            peak_mb = process.memory_info().rss / 1024 / 1024
            increase_mb = peak_mb - baseline_mb
            
            print(f"\nMemory Usage:")
            print(f"  Baseline: {baseline_mb:.2f} MB")
            print(f"  Peak: {peak_mb:.2f} MB")
            print(f"  Increase: {increase_mb:.2f} MB")
            
            # Should not increase memory by more than 100MB
            assert increase_mb < 100, f"Memory increase too high: {increase_mb:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not installed, skipping memory test")
    
    def test_scalability_with_event_count(self):
        """Test how performance scales with number of events."""
        event_counts = [100, 500, 1000, 2000, 5000]
        results = []
        
        print(f"\nScalability Test:")
        print(f"{'Events':>8} | {'Time (ms)':>10} | {'Events/ms':>10}")
        print("-" * 35)
        
        for count in event_counts:
            events = generate_test_events(count)
            
            start = time.perf_counter()
            features = extract_all_features(events, session_id=f"test_{count}")
            end = time.perf_counter()
            
            time_ms = (end - start) * 1000
            throughput = count / time_ms if time_ms > 0 else 0
            
            print(f"{count:>8} | {time_ms:>10.2f} | {throughput:>10.2f}")
            results.append((count, time_ms))
        
        # Performance should be roughly linear (not exponential)
        # Check that doubling events doesn't quadruple time
        time_100 = results[0][1]
        time_2000 = results[3][1]
        
        ratio = time_2000 / time_100
        expected_ratio = 2000 / 100  # Linear would be 20x
        
        # Allow some overhead, but should be less than 2x the expected linear ratio
        assert ratio < expected_ratio * 2, f"Performance degradation too severe"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print output
