#!/usr/bin/env python3
"""
Trinitas v3.5 Performance Optimizer
Advanced optimization for production deployments
"""

import asyncio
import hashlib
import json
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable
import logging
from functools import wraps
import psutil
import threading

logger = logging.getLogger(__name__)

@dataclass
class CachedResponse:
    """Cached response with metadata"""
    key: str
    value: Any
    timestamp: datetime
    ttl: int
    hit_count: int = 0
    size_bytes: int = 0
    persona: Optional[str] = None

@dataclass
class BatchRequest:
    """Batched request for processing"""
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    timestamp: datetime
    priority: int = 0

class PerformanceOptimizer:
    """Advanced performance optimization system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Response caching
        self.response_cache = OrderedDict()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        
        # Request batching
        self.request_queue = deque()
        self.batch_processors = {}
        self.dedup_cache = {}
        
        # Token optimization
        self.token_usage = {
            "total": 0,
            "cached": 0,
            "optimized": 0
        }
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        
        # Parallel processing
        self.executor_pool = None
        self.max_workers = self.config.get("max_workers", 10)
        
        # Lazy loading registry
        self.lazy_resources = {}
        
        logger.info("Performance Optimizer initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "cache_max_size": 1000,
            "cache_ttl_default": 3600,
            "batch_size": 50,
            "batch_timeout": 0.1,
            "max_workers": 10,
            "memory_limit_mb": 512,
            "dedup_window": 60
        }
    
    # Response Caching
    
    def cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key"""
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def cached(self, ttl: Optional[int] = None, persona: Optional[str] = None):
        """Decorator for caching function responses"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key = self.cache_key(func.__name__, args, kwargs)
                
                # Check cache
                cached = self.get_cached_response(key)
                if cached:
                    self.cache_stats["hits"] += 1
                    cached.hit_count += 1
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached.value
                
                # Execute function
                self.cache_stats["misses"] += 1
                result = await func(*args, **kwargs)
                
                # Cache result
                self.cache_response(
                    key, 
                    result, 
                    ttl or self.config["cache_ttl_default"],
                    persona
                )
                
                return result
            return wrapper
        return decorator
    
    def get_cached_response(self, key: str) -> Optional[CachedResponse]:
        """Get cached response if valid"""
        if key not in self.response_cache:
            return None
        
        cached = self.response_cache[key]
        
        # Check TTL
        if datetime.now() - cached.timestamp > timedelta(seconds=cached.ttl):
            del self.response_cache[key]
            self.cache_stats["evictions"] += 1
            return None
        
        # Move to end (LRU)
        self.response_cache.move_to_end(key)
        return cached
    
    def cache_response(self, key: str, value: Any, ttl: int, persona: Optional[str] = None):
        """Cache a response"""
        # Check cache size
        if len(self.response_cache) >= self.config["cache_max_size"]:
            # Evict oldest
            self.response_cache.popitem(last=False)
            self.cache_stats["evictions"] += 1
        
        # Calculate size
        size_bytes = len(json.dumps(value, default=str))
        
        # Store cached response
        self.response_cache[key] = CachedResponse(
            key=key,
            value=value,
            timestamp=datetime.now(),
            ttl=ttl,
            size_bytes=size_bytes,
            persona=persona
        )
    
    def clear_cache(self, persona: Optional[str] = None):
        """Clear cache, optionally for specific persona"""
        if persona:
            keys_to_remove = [
                k for k, v in self.response_cache.items()
                if v.persona == persona
            ]
            for key in keys_to_remove:
                del self.response_cache[key]
        else:
            self.response_cache.clear()
        
        logger.info(f"Cache cleared for persona: {persona or 'all'}")
    
    # Request Batching
    
    async def batch_process(self, func: Callable, requests: List[BatchRequest]):
        """Process a batch of requests"""
        batch_id = f"batch_{datetime.now().timestamp()}"
        logger.info(f"Processing batch {batch_id} with {len(requests)} requests")
        
        # Deduplicate requests
        unique_requests = self._deduplicate_requests(requests)
        
        # Process in parallel if possible
        if self.executor_pool:
            tasks = [
                self._process_single_request(req)
                for req in unique_requests
            ]
            results = await asyncio.gather(*tasks)
        else:
            results = []
            for req in unique_requests:
                result = await self._process_single_request(req)
                results.append(result)
        
        return results
    
    def _deduplicate_requests(self, requests: List[BatchRequest]) -> List[BatchRequest]:
        """Remove duplicate requests within window"""
        unique = {}
        window = timedelta(seconds=self.config["dedup_window"])
        now = datetime.now()
        
        for req in requests:
            # Generate dedup key
            key = self.cache_key(req.func.__name__, req.args, req.kwargs)
            
            # Check if seen recently
            if key in self.dedup_cache:
                last_seen = self.dedup_cache[key]
                if now - last_seen < window:
                    logger.debug(f"Deduplicating request: {key}")
                    continue
            
            # Add to unique
            unique[key] = req
            self.dedup_cache[key] = now
        
        # Clean old dedup entries
        self._clean_dedup_cache()
        
        return list(unique.values())
    
    def _clean_dedup_cache(self):
        """Remove old deduplication entries"""
        window = timedelta(seconds=self.config["dedup_window"])
        now = datetime.now()
        
        keys_to_remove = [
            k for k, v in self.dedup_cache.items()
            if now - v > window
        ]
        
        for key in keys_to_remove:
            del self.dedup_cache[key]
    
    async def _process_single_request(self, request: BatchRequest) -> Any:
        """Process a single request"""
        try:
            if asyncio.iscoroutinefunction(request.func):
                return await request.func(*request.args, **request.kwargs)
            else:
                return request.func(*request.args, **request.kwargs)
        except Exception as e:
            logger.error(f"Error processing request {request.id}: {e}")
            return {"error": str(e)}
    
    # Token Optimization
    
    def optimize_tokens(self, text: str, max_tokens: int = 1000) -> str:
        """Optimize text to use fewer tokens"""
        # Simple optimization - can be enhanced with better tokenization
        if len(text) <= max_tokens:
            return text
        
        # Truncate intelligently
        truncated = text[:max_tokens-10] + "..."
        
        self.token_usage["optimized"] += len(text) - len(truncated)
        
        return truncated
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Simple estimation - ~4 chars per token
        return len(text) // 4
    
    # Parallel Processing
    
    async def parallel_execute(self, tasks: List[Callable], max_concurrent: Optional[int] = None) -> List[Any]:
        """Execute tasks in parallel with concurrency limit"""
        max_concurrent = max_concurrent or self.max_workers
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_task(task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task):
                    return await task()
                else:
                    return task()
        
        results = await asyncio.gather(*[bounded_task(task) for task in tasks])
        
        return results
    
    # Memory Management
    
    def optimize_memory(self):
        """Optimize memory usage"""
        # Clear old cache entries
        self._evict_old_cache()
        
        # Compact data structures
        self._compact_structures()
        
        # Force garbage collection if needed
        if self.resource_monitor.memory_usage_mb() > self.config["memory_limit_mb"]:
            import gc
            gc.collect()
            logger.info("Forced garbage collection due to memory limit")
    
    def _evict_old_cache(self):
        """Evict old cache entries"""
        now = datetime.now()
        keys_to_remove = []
        
        for key, cached in self.response_cache.items():
            if now - cached.timestamp > timedelta(seconds=cached.ttl):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.response_cache[key]
            self.cache_stats["evictions"] += 1
    
    def _compact_structures(self):
        """Compact internal data structures"""
        # Recreate ordered dict if too fragmented
        if len(self.response_cache) < self.config["cache_max_size"] * 0.5:
            self.response_cache = OrderedDict(self.response_cache)
    
    # Lazy Loading
    
    def lazy_load(self, resource_name: str, loader: Callable):
        """Register a resource for lazy loading"""
        self.lazy_resources[resource_name] = {
            "loader": loader,
            "loaded": False,
            "value": None
        }
    
    async def get_resource(self, resource_name: str) -> Any:
        """Get a lazily loaded resource"""
        if resource_name not in self.lazy_resources:
            raise ValueError(f"Unknown resource: {resource_name}")
        
        resource = self.lazy_resources[resource_name]
        
        if not resource["loaded"]:
            logger.info(f"Lazy loading resource: {resource_name}")
            if asyncio.iscoroutinefunction(resource["loader"]):
                resource["value"] = await resource["loader"]()
            else:
                resource["value"] = resource["loader"]()
            resource["loaded"] = True
        
        return resource["value"]
    
    # Performance Metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        cache_hit_rate = 0
        if self.cache_stats["hits"] + self.cache_stats["misses"] > 0:
            cache_hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])
        
        return {
            "cache": {
                "size": len(self.response_cache),
                "hit_rate": cache_hit_rate,
                "stats": self.cache_stats
            },
            "tokens": self.token_usage,
            "memory": {
                "usage_mb": self.resource_monitor.memory_usage_mb(),
                "limit_mb": self.config["memory_limit_mb"]
            },
            "batching": {
                "queue_size": len(self.request_queue),
                "dedup_cache_size": len(self.dedup_cache)
            }
        }

class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def cpu_percent(self) -> float:
        """Get CPU usage percentage"""
        return self.process.cpu_percent(interval=0.1)
    
    def io_counters(self) -> Dict[str, int]:
        """Get I/O counters"""
        counters = self.process.io_counters()
        return {
            "read_bytes": counters.read_bytes,
            "write_bytes": counters.write_bytes,
            "read_count": counters.read_count,
            "write_count": counters.write_count
        }

# Global optimizer instance
optimizer = PerformanceOptimizer()

if __name__ == "__main__":
    # Test performance optimizer
    async def test():
        print("Testing Performance Optimizer")
        print("=" * 60)
        
        # Test caching
        @optimizer.cached(ttl=60)
        async def expensive_operation(x):
            await asyncio.sleep(0.1)
            return x * 2
        
        # First call - miss
        start = time.time()
        result1 = await expensive_operation(5)
        time1 = time.time() - start
        
        # Second call - hit
        start = time.time()
        result2 = await expensive_operation(5)
        time2 = time.time() - start
        
        print(f"First call: {time1:.3f}s, Result: {result1}")
        print(f"Second call: {time2:.3f}s, Result: {result2}")
        print(f"Cache hit rate: {optimizer.get_metrics()['cache']['hit_rate']:.2%}")
        
        # Test parallel execution
        tasks = [lambda: i*2 for i in range(10)]
        results = await optimizer.parallel_execute(tasks, max_concurrent=3)
        print(f"Parallel results: {results}")
        
        # Show metrics
        print("\nPerformance Metrics:")
        metrics = optimizer.get_metrics()
        print(json.dumps(metrics, indent=2))
    
    asyncio.run(test())