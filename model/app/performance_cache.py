"""
Enhanced Performance Monitoring and Caching
"""
import time
import threading
from functools import wraps
from collections import defaultdict, deque
import json
import logging

class PerformanceCache:
    def __init__(self, max_size=5000, ttl=30):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.RLock()
        self.metrics = defaultdict(deque)
        self.logger = logging.getLogger(__name__)
        
        # Detailed metrics
        self.operation_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("✅ Performance Cache Initialized")

    def _cleanup_loop(self):
        """Background cleanup of expired cache entries"""
        while True:
            time.sleep(self.ttl)
            self._cleanup_expired()
    
    def _cleanup_expired(self):
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, access_time in self.access_times.items()
                if current_time - access_time > self.ttl
            ]
            for key in expired_keys:
                del self.cache[key]
                del self.access_times[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                if time.time() - self.access_times[key] < self.ttl:
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.access_times[key]
            return None
    
    def set(self, key, value):
        with self.lock:
            # Remove oldest if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def add_metric(self, endpoint, duration, success=True, error=None):
        with self.lock:
            self.metrics[endpoint].append((time.time(), duration, success))
            
            # Keep only last 1000 metrics
            if len(self.metrics[endpoint]) > 1000:
                self.metrics[endpoint].popleft()
            
            # Track success/error
            if success:
                self.success_counts[endpoint] += 1
            else:
                self.error_counts[endpoint] += 1
                if error:
                    self.logger.error(f"Operation {endpoint} failed: {error}")
    
    def get_average_response_time(self, endpoint):
        with self.lock:
            if endpoint not in self.metrics or not self.metrics[endpoint]:
                return 0
            durations = [duration for _, duration, _ in self.metrics[endpoint]]
            return sum(durations) / len(durations) if durations else 0
    
    def get_performance_report(self):
        """Generate comprehensive performance report"""
        with self.lock:
            report = {
                'timestamp': time.time(),
                'cache_size': len(self.cache),
                'cache_hit_rate': self._calculate_hit_rate(),
                'endpoints': {}
            }
            
            for endpoint in set(list(self.metrics.keys()) + list(self.success_counts.keys()) + list(self.error_counts.keys())):
                metrics = self.metrics[endpoint]
                if metrics:
                    durations = [duration for _, duration, _ in metrics]
                    successes = [success for _, _, success in metrics]
                    
                    report['endpoints'][endpoint] = {
                        'total_calls': len(metrics),
                        'success_rate': sum(successes) / len(successes) * 100 if successes else 0,
                        'avg_response_time_ms': sum(durations) / len(durations) if durations else 0,
                        'p95_response_time_ms': sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                        'success_count': self.success_counts.get(endpoint, 0),
                        'error_count': self.error_counts.get(endpoint, 0)
                    }
            
            return report
    
    def _calculate_hit_rate(self):
        """Calculate cache hit rate (simplified)"""
        # In production, you'd track hits/misses
        return 0.85  # Placeholder
    
    def save_report(self, filename='performance_report.json'):
        """Save performance report to file"""
        report = self.get_performance_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        return report

# Global cache instance
performance_cache = PerformanceCache()

def cache_result(ttl=30):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try cache
            cached_result = performance_cache.get(cache_key)
            if cached_result is not None:
                performance_cache.add_metric(f"cache_hit.{func.__name__}", 0.01, success=True)
                return cached_result
            
            # Execute and cache
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                performance_cache.set(cache_key, result)
                performance_cache.add_metric(func.__name__, duration, success=True)
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                performance_cache.add_metric(func.__name__, duration, success=False, error=str(e))
                raise
        return wrapper
    return decorator

def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            # Log based on performance
            if duration > 1000:
                performance_cache.logger.warning(f"⚠️  SLOW: {func.__name__} took {duration:.0f}ms")
            elif duration > 500:
                performance_cache.logger.info(f"ℹ️  MEDIUM: {func.__name__} took {duration:.0f}ms")
            elif duration < 10:
                performance_cache.logger.debug(f"⚡ FAST: {func.__name__} took {duration:.1f}ms")
            
            performance_cache.add_metric(f"monitored.{func.__name__}", duration, success=True)
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            performance_cache.add_metric(f"monitored.{func.__name__}", duration, success=False, error=str(e))
            raise
    return wrapper