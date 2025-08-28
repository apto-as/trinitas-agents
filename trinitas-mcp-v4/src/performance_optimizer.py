"""
Performance Optimizer for Trinitas v4.0
メモリアクセスとシステムパフォーマンスの最適化
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
import hashlib
import pickle

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """キャッシュエントリ"""
    key: str
    value: Any
    size: int
    access_count: int
    last_access: datetime
    ttl: timedelta
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time_ms: float = 0
    total_requests: int = 0
    memory_usage_mb: float = 0
    optimization_score: float = 0

class LRUCache:
    """
    LRU (Least Recently Used) Cache
    高速メモリアクセスのためのキャッシュ
    """
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.total_memory_bytes = 0
        self.metrics = PerformanceMetrics()
        
    def get(self, key: str) -> Optional[Any]:
        """キャッシュから取得"""
        if key in self.cache:
            # Move to end (most recently used)
            entry = self.cache.pop(key)
            
            # Check TTL
            if datetime.now() - entry.last_access > entry.ttl:
                # Expired
                self.total_memory_bytes -= entry.size
                self.metrics.cache_misses += 1
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_access = datetime.now()
            self.cache[key] = entry
            
            self.metrics.cache_hits += 1
            return entry.value
        
        self.metrics.cache_misses += 1
        return None
    
    def put(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """キャッシュに保存"""
        try:
            # Calculate size
            size = len(pickle.dumps(value))
            
            # Check if we need to evict
            while (self.total_memory_bytes + size > self.max_memory_bytes or 
                   len(self.cache) >= self.max_size):
                if not self.cache:
                    break
                # Evict least recently used
                evicted_key, evicted_entry = self.cache.popitem(last=False)
                self.total_memory_bytes -= evicted_entry.size
                logger.debug(f"Evicted cache entry: {evicted_key}")
            
            # Add new entry
            entry = CacheEntry(
                key=key,
                value=value,
                size=size,
                access_count=1,
                last_access=datetime.now(),
                ttl=timedelta(seconds=ttl_seconds)
            )
            
            self.cache[key] = entry
            self.total_memory_bytes += size
            
            return True
            
        except Exception as e:
            logger.error(f"Cache put error: {e}")
            return False
    
    def invalidate(self, pattern: Optional[str] = None):
        """キャッシュを無効化"""
        if pattern:
            # Pattern-based invalidation
            keys_to_remove = [k for k in self.cache if pattern in k]
            for key in keys_to_remove:
                entry = self.cache.pop(key)
                self.total_memory_bytes -= entry.size
        else:
            # Clear all
            self.cache.clear()
            self.total_memory_bytes = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        hit_rate = (self.metrics.cache_hits / 
                   max(1, self.metrics.cache_hits + self.metrics.cache_misses))
        
        return {
            "size": len(self.cache),
            "memory_mb": self.total_memory_bytes / (1024 * 1024),
            "hit_rate": hit_rate,
            "hits": self.metrics.cache_hits,
            "misses": self.metrics.cache_misses,
            "total_requests": self.metrics.cache_hits + self.metrics.cache_misses
        }

class QueryOptimizer:
    """
    クエリ最適化
    メモリクエリを最適化して高速化
    """
    
    def __init__(self):
        self.query_cache = {}
        self.query_patterns = defaultdict(list)
        self.optimization_rules = self._initialize_rules()
        
    def _initialize_rules(self) -> List[Dict]:
        """最適化ルールを初期化"""
        return [
            {
                "name": "index_hint",
                "condition": lambda q: "persona" in q and "section" in q,
                "optimization": lambda q: {**q, "use_index": ["persona", "section"]}
            },
            {
                "name": "limit_optimization",
                "condition": lambda q: q.get("limit", 0) > 100,
                "optimization": lambda q: {**q, "limit": 100, "paginate": True}
            },
            {
                "name": "semantic_batch",
                "condition": lambda q: q.get("semantic") and q.get("limit", 0) > 10,
                "optimization": lambda q: {**q, "batch_size": 5}
            }
        ]
    
    def optimize_query(self, query: Dict) -> Dict:
        """クエリを最適化"""
        optimized = query.copy()
        
        # Apply optimization rules
        for rule in self.optimization_rules:
            if rule["condition"](query):
                optimized = rule["optimization"](optimized)
                logger.debug(f"Applied optimization: {rule['name']}")
        
        # Don't add query_hash to actual params, keep it separate
        return optimized
    
    def analyze_query_pattern(self, query: Dict, response_time_ms: float):
        """クエリパターンを分析"""
        query_type = self._classify_query(query)
        self.query_patterns[query_type].append({
            "query": query,
            "response_time_ms": response_time_ms,
            "timestamp": datetime.now()
        })
        
        # Identify slow queries
        if response_time_ms > 100:
            logger.warning(f"Slow query detected ({response_time_ms}ms): {query}")
    
    def _classify_query(self, query: Dict) -> str:
        """クエリを分類"""
        if query.get("semantic"):
            return "semantic_search"
        elif query.get("filters", {}).get("persona"):
            return "persona_filtered"
        elif query.get("limit", 0) == 1:
            return "single_fetch"
        else:
            return "general"
    
    def get_optimization_suggestions(self) -> List[str]:
        """最適化提案を取得"""
        suggestions = []
        
        # Analyze patterns
        for query_type, patterns in self.query_patterns.items():
            if patterns:
                avg_time = sum(p["response_time_ms"] for p in patterns) / len(patterns)
                if avg_time > 50:
                    suggestions.append(f"Consider indexing for {query_type} queries (avg: {avg_time:.0f}ms)")
        
        return suggestions

class ConnectionPool:
    """
    コネクションプール
    データベース接続を効率的に管理
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = None  # Will be initialized when needed
        self.active_connections = 0
        self.total_requests = 0
        self.connection_wait_times = []
        
    async def acquire(self) -> Any:
        """コネクションを取得"""
        start_time = time.time()
        
        # Initialize queue on first use
        if self.connections is None:
            self.connections = asyncio.Queue(maxsize=self.max_connections)
        
        try:
            # Try to get existing connection
            connection = await asyncio.wait_for(
                self.connections.get(),
                timeout=0.1
            )
        except asyncio.TimeoutError:
            # Create new connection if under limit
            if self.active_connections < self.max_connections:
                connection = await self._create_connection()
                self.active_connections += 1
            else:
                # Wait for available connection
                connection = await self.connections.get()
        
        wait_time = (time.time() - start_time) * 1000
        self.connection_wait_times.append(wait_time)
        self.total_requests += 1
        
        return connection
    
    async def release(self, connection: Any):
        """コネクションを解放"""
        if self.connections is None:
            self.connections = asyncio.Queue(maxsize=self.max_connections)
        await self.connections.put(connection)
    
    async def _create_connection(self) -> Any:
        """新規コネクションを作成"""
        # Placeholder - would create actual DB connection
        return {"id": self.active_connections, "created": datetime.now()}
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        avg_wait = (sum(self.connection_wait_times) / len(self.connection_wait_times) 
                   if self.connection_wait_times else 0)
        
        return {
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "total_requests": self.total_requests,
            "avg_wait_time_ms": avg_wait,
            "pool_utilization": self.active_connections / self.max_connections
        }

class PerformanceOptimizer:
    """
    統合パフォーマンス最適化
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = LRUCache(
            max_size=config.get("cache", {}).get("max_size", 1000),
            max_memory_mb=config.get("cache", {}).get("max_memory_mb", 100)
        )
        self.query_optimizer = QueryOptimizer()
        self.connection_pool = ConnectionPool(
            max_connections=config.get("db", {}).get("max_connections", 10)
        )
        
        # Performance tracking
        self.request_times = []
        self.optimization_enabled = True
        
    async def optimized_recall(self, memory_manager, query: str, **kwargs) -> Tuple[List[Dict], float]:
        """最適化されたメモリ取得"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"recall_{query}_{str(kwargs)}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            response_time = (time.time() - start_time) * 1000
            self.request_times.append(response_time)
            return cached_result, response_time
        
        # Optimize query
        optimized_params = self.query_optimizer.optimize_query(kwargs)
        
        # Execute with connection pool
        connection = await self.connection_pool.acquire()
        try:
            result = await memory_manager.recall(query, **optimized_params)
        finally:
            await self.connection_pool.release(connection)
        
        # Cache result
        self.cache.put(cache_key, result, ttl_seconds=300)  # 5 minutes TTL
        
        response_time = (time.time() - start_time) * 1000
        self.request_times.append(response_time)
        
        # Analyze for future optimization
        self.query_optimizer.analyze_query_pattern(kwargs, response_time)
        
        return result, response_time
    
    async def optimized_store(self, memory_manager, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """最適化されたメモリ保存"""
        start_time = time.time()
        
        # Invalidate related cache entries
        self.cache.invalidate(pattern=key.split("_")[0])
        
        # Store with connection pool
        connection = await self.connection_pool.acquire()
        try:
            result = await memory_manager.store(key, value, metadata)
        finally:
            await self.connection_pool.release(connection)
        
        response_time = (time.time() - start_time) * 1000
        self.request_times.append(response_time)
        
        return result
    
    def apply_batch_optimization(self, operations: List[Dict]) -> List[Dict]:
        """バッチ操作を最適化"""
        # Group operations by type
        grouped = defaultdict(list)
        for op in operations:
            grouped[op["type"]].append(op)
        
        # Optimize each group
        optimized = []
        for op_type, ops in grouped.items():
            if op_type == "store":
                # Batch stores can be combined
                optimized.append({
                    "type": "batch_store",
                    "operations": ops
                })
            elif op_type == "recall":
                # Similar queries can be combined
                similar_groups = self._group_similar_queries(ops)
                for group in similar_groups:
                    if len(group) > 1:
                        optimized.append({
                            "type": "batch_recall",
                            "operations": group
                        })
                    else:
                        optimized.extend(group)
            else:
                optimized.extend(ops)
        
        return optimized
    
    def _group_similar_queries(self, queries: List[Dict]) -> List[List[Dict]]:
        """類似クエリをグループ化"""
        groups = []
        used = set()
        
        for i, q1 in enumerate(queries):
            if i in used:
                continue
            
            group = [q1]
            used.add(i)
            
            for j, q2 in enumerate(queries[i+1:], i+1):
                if j in used:
                    continue
                
                # Check similarity
                if self._queries_similar(q1, q2):
                    group.append(q2)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _queries_similar(self, q1: Dict, q2: Dict) -> bool:
        """クエリの類似性をチェック"""
        # Simple similarity check
        return (q1.get("filters", {}).get("persona") == q2.get("filters", {}).get("persona") and
                q1.get("semantic") == q2.get("semantic"))
    
    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        avg_response_time = (sum(self.request_times) / len(self.request_times) 
                           if self.request_times else 0)
        
        return {
            "cache_stats": self.cache.get_stats(),
            "connection_pool_stats": self.connection_pool.get_stats(),
            "average_response_time_ms": avg_response_time,
            "total_requests": len(self.request_times),
            "optimization_suggestions": self.query_optimizer.get_optimization_suggestions(),
            "optimization_enabled": self.optimization_enabled
        }
    
    async def auto_tune(self):
        """自動チューニング"""
        report = self.get_performance_report()
        
        # Auto-adjust cache size based on hit rate
        cache_stats = report["cache_stats"]
        if cache_stats["hit_rate"] < 0.5 and cache_stats["memory_mb"] < 50:
            # Increase cache size
            self.cache.max_size = min(self.cache.max_size * 1.5, 5000)
            logger.info(f"Auto-tuned: Increased cache size to {self.cache.max_size}")
        
        # Auto-adjust connection pool
        pool_stats = report["connection_pool_stats"]
        if pool_stats["avg_wait_time_ms"] > 10 and pool_stats["pool_utilization"] > 0.8:
            # Increase pool size
            self.connection_pool.max_connections = min(
                self.connection_pool.max_connections + 2, 20
            )
            logger.info(f"Auto-tuned: Increased connection pool to {self.connection_pool.max_connections}")
    
    def enable_optimization(self, enabled: bool = True):
        """最適化の有効/無効を設定"""
        self.optimization_enabled = enabled
        logger.info(f"Performance optimization {'enabled' if enabled else 'disabled'}")