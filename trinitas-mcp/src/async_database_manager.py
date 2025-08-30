"""
Trinitas v4.0 - Perfect Async Database Manager
完璧な非同期データベース管理システム（Artemis 404基準）

フン、同期的SQLiteなど404の恥よ。真の非同期実装を見せてあげるわ
"""

import asyncio
import aiosqlite
from typing import Dict, List, Optional, Any, Tuple, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import asynccontextmanager
import time
from pathlib import Path

# SECURITY: セキュアエラーハンドリング 
try:
    from .security.secure_error_handler import secure_log_error, get_secure_error_message
except ImportError:
    # フォールバック関数
    def secure_log_error(e, context):
        return f"ERR-{hash(get_secure_error_message(e)) % 100000:05d}"
    def get_secure_error_message(e):
        return "Operation failed"

from .exceptions_hierarchy import (
    MemorySystemError, MemoryConnectionError, MemoryDataCorruptionError,
    PerfectExceptionHandler, PerfectRetryHandler, TimeoutError,
    PerformanceDegradationError
)

logger = logging.getLogger(__name__)

# ============================================================================
# Perfect Connection Pool for SQLite (完璧なSQLite接続プール)
# ============================================================================

@dataclass
class ConnectionMetrics:
    """Perfect connection metrics tracking"""
    created_at: datetime
    last_used: datetime
    query_count: int = 0
    total_duration: float = 0.0
    
    @property
    def average_query_time(self) -> float:
        return self.total_duration / max(1, self.query_count)

class PerfectSQLitePool:
    """
    Perfect SQLite Connection Pool with async support
    完璧な非同期接続プールの実装
    """
    
    def __init__(self, db_path: str, max_connections: int = 10, 
                 connection_timeout: float = 5.0):
        self.db_path = Path(db_path)
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        # Connection management
        self._available_connections = asyncio.Queue(maxsize=max_connections)
        self._all_connections: Dict[int, aiosqlite.Connection] = {}
        self._connection_metrics: Dict[int, ConnectionMetrics] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        
        # Performance tracking
        self._total_connections = 0
        self._active_connections = 0
    
    async def initialize(self):
        """Initialize the connection pool"""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create initial connections
            for _ in range(min(3, self.max_connections)):  # Start with 3 connections
                await self._create_connection()
            
            self._initialized = True
            logger.info(f"SQLite pool initialized with {len(self._all_connections)} connections")
    
    async def _create_connection(self) -> aiosqlite.Connection:
        """Create a new database connection"""
        try:
            conn = await aiosqlite.connect(
                str(self.db_path),
                timeout=self.connection_timeout
            )
            
            # Optimize SQLite settings for async usage
            await conn.execute("PRAGMA journal_mode=WAL")  # Better for concurrent access
            await conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety/performance
            await conn.execute("PRAGMA cache_size=10000")  # 10MB cache
            await conn.execute("PRAGMA temp_store=memory")  # Use memory for temp tables
            await conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapped I/O
            
            conn_id = id(conn)
            self._all_connections[conn_id] = conn
            self._connection_metrics[conn_id] = ConnectionMetrics(
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            
            await self._available_connections.put(conn)
            self._total_connections += 1
            
            logger.debug(f"Created new SQLite connection {conn_id}")
            return conn
            
        except Exception as e:
            raise MemoryConnectionError("sqlite", f"Failed to create connection: {get_secure_error_message(e)}") from e
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool"""
        if not self._initialized:
            await self.initialize()
        
        connection = None
        conn_id = None
        start_time = time.time()
        
        try:
            # Try to get available connection
            try:
                connection = await asyncio.wait_for(
                    self._available_connections.get(),
                    timeout=self.connection_timeout
                )
            except asyncio.TimeoutError:
                # Create new connection if under limit
                if len(self._all_connections) < self.max_connections:
                    connection = await self._create_connection()
                else:
                    raise TimeoutError(
                        "acquire_connection",
                        self.connection_timeout,
                        time.time() - start_time
                    )
            
            conn_id = id(connection)
            self._active_connections += 1
            
            # Update metrics
            if conn_id in self._connection_metrics:
                self._connection_metrics[conn_id].last_used = datetime.now()
            
            yield connection
            
        except Exception as e:
            if conn_id:
                error_id = secure_log_error(e, "connection_operation")
                logger.error(f"Error with connection {conn_id}: {error_id}")
            raise
            
        finally:
            if connection:
                try:
                    # Return connection to pool
                    await self._available_connections.put(connection)
                    self._active_connections -= 1
                except Exception as e:
                    error_id = secure_log_error(e, "connection_operation")
                    logger.error(f"Error returning connection to pool: {error_id}")
    
    async def execute_query(self, query: str, params: Tuple = None) -> List[aiosqlite.Row]:
        """Execute query with connection pooling"""
        start_time = time.time()
        
        async with self.acquire() as conn:
            try:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                results = await cursor.fetchall()
                await conn.commit()
                
                # Update metrics
                conn_id = id(conn)
                if conn_id in self._connection_metrics:
                    metrics = self._connection_metrics[conn_id]
                    metrics.query_count += 1
                    metrics.total_duration += time.time() - start_time
                
                return results
                
            except Exception as e:
                await conn.rollback()
                raise MemorySystemError(f"Query execution failed: {get_secure_error_message(e)}") from e
    
    async def execute_many(self, query: str, param_list: List[Tuple]) -> int:
        """Execute multiple queries in batch"""
        start_time = time.time()
        
        async with self.acquire() as conn:
            try:
                cursor = await conn.executemany(query, param_list)
                await conn.commit()
                
                # Update metrics
                conn_id = id(conn)
                if conn_id in self._connection_metrics:
                    metrics = self._connection_metrics[conn_id]
                    metrics.query_count += len(param_list)
                    metrics.total_duration += time.time() - start_time
                
                return cursor.rowcount
                
            except Exception as e:
                await conn.rollback()
                raise MemorySystemError(f"Batch execution failed: {get_secure_error_message(e)}") from e
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        available_count = self._available_connections.qsize()
        
        return {
            "total_connections": len(self._all_connections),
            "active_connections": self._active_connections,
            "available_connections": available_count,
            "max_connections": self.max_connections,
            "pool_utilization": (self._active_connections / self.max_connections) * 100,
            "connection_metrics": [
                {
                    "connection_id": conn_id,
                    "created_at": metrics.created_at.isoformat(),
                    "last_used": metrics.last_used.isoformat(),
                    "query_count": metrics.query_count,
                    "avg_query_time": metrics.average_query_time
                }
                for conn_id, metrics in self._connection_metrics.items()
            ]
        }
    
    async def cleanup(self):
        """Clean up all connections"""
        async with self._lock:
            while not self._available_connections.empty():
                try:
                    conn = await self._available_connections.get_nowait()
                    await conn.close()
                except Exception as e:
                    error_id = secure_log_error(e, "connection_operation")
                    logger.error(f"Error closing connection: {error_id}")
            
            for conn in self._all_connections.values():
                try:
                    await conn.close()
                except Exception as e:
                    error_id = secure_log_error(e, "connection_operation")
                    logger.error(f"Error closing connection: {error_id}")
            
            self._all_connections.clear()
            self._connection_metrics.clear()
            logger.info("SQLite connection pool cleaned up")

# ============================================================================
# Perfect Async Database Manager (完璧な非同期データベース管理)
# ============================================================================

class PerfectAsyncDatabaseManager:
    """
    Perfect Async Database Manager - 完璧な非同期データベース実装
    妥協なき404基準でのパフォーマンスと信頼性
    """
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.pool = PerfectSQLitePool(db_path, max_connections)
        self._schema_initialized = False
        self._schema_lock = asyncio.Lock()
        
        # Performance monitoring
        self._query_stats = {}
        self._slow_query_threshold = 1.0  # 1 second
    
    async def initialize(self):
        """Initialize database with perfect schema"""
        if self._schema_initialized:
            return
        
        async with self._schema_lock:
            if self._schema_initialized:
                return
            
            await self.pool.initialize()
            await self._create_perfect_schema()
            self._schema_initialized = True
            logger.info("Perfect database schema initialized")
    
    async def _create_perfect_schema(self):
        """Create optimized database schema"""
        
        # Memory table with all necessary columns and indexes
        memory_table_sql = '''
        CREATE TABLE IF NOT EXISTS memories (
            key TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            importance REAL NOT NULL CHECK (importance >= 0.0 AND importance <= 1.0),
            timestamp TEXT NOT NULL,
            persona TEXT,
            category TEXT,
            metadata TEXT,
            access_count INTEGER DEFAULT 0,
            last_access TEXT,
            content_hash TEXT,  -- For deduplication
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        '''
        
        # Performance-optimized indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC)',
            'CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp DESC)',
            'CREATE INDEX IF NOT EXISTS idx_memories_persona_category ON memories(persona, category)',
            'CREATE INDEX IF NOT EXISTS idx_memories_content_search ON memories(content)',
            'CREATE INDEX IF NOT EXISTS idx_memories_access_count ON memories(access_count DESC)',
            'CREATE INDEX IF NOT EXISTS idx_memories_last_access ON memories(last_access DESC)',
            'CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash)',
        ]
        
        # Learning patterns table
        learning_table_sql = '''
        CREATE TABLE IF NOT EXISTS learning_patterns (
            pattern_id TEXT PRIMARY KEY,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            last_applied TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL DEFAULT 0.5
        )
        '''
        
        learning_indexes = [
            'CREATE INDEX IF NOT EXISTS idx_learning_type ON learning_patterns(pattern_type)',
            'CREATE INDEX IF NOT EXISTS idx_learning_confidence ON learning_patterns(confidence_score DESC)',
            'CREATE INDEX IF NOT EXISTS idx_learning_success ON learning_patterns(success_count DESC)'
        ]
        
        # Performance metrics table
        metrics_table_sql = '''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            metric_id TEXT PRIMARY KEY,
            operation TEXT NOT NULL,
            duration REAL NOT NULL,
            timestamp TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            metadata TEXT
        )
        '''
        
        metrics_indexes = [
            'CREATE INDEX IF NOT EXISTS idx_metrics_operation ON performance_metrics(operation)',
            'CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp DESC)',
            'CREATE INDEX IF NOT EXISTS idx_metrics_duration ON performance_metrics(duration DESC)'
        ]
        
        # Execute all schema creation
        all_queries = [
            memory_table_sql,
            learning_table_sql,
            metrics_table_sql
        ] + indexes + learning_indexes + metrics_indexes
        
        for query in all_queries:
            try:
                await self.pool.execute_query(query)
                logger.debug(f"Executed schema query: {query[:50]}...")
            except Exception as e:
                error_id = secure_log_error(e, "query_operation")
                logger.error(f"Failed to execute schema query: {error_id}")
                raise MemorySystemError(f"Schema creation failed: {get_secure_error_message(e)}") from e
    
    # ========================================================================
    # Perfect Memory Operations (完璧なメモリ操作)
    # ========================================================================
    
    @PerfectExceptionHandler.handle_async_with_context
    @PerfectRetryHandler.with_retry(max_retries=2)
    async def store_memory(self, key: str, content: str, importance: float,
                          persona: Optional[str] = None, category: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store memory with perfect async performance"""
        await self.initialize()
        
        start_time = time.time()
        
        # Generate content hash for deduplication
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Prepare data
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        query = '''
        INSERT OR REPLACE INTO memories 
        (key, content, importance, timestamp, persona, category, metadata, 
         content_hash, created_at, updated_at, access_count, last_access)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        '''
        
        params = (
            key, content, importance, timestamp, persona, category, 
            metadata_json, content_hash, timestamp, timestamp, timestamp
        )
        
        try:
            await self.pool.execute_query(query, params)
            
            # Record performance metrics
            duration = time.time() - start_time
            await self._record_performance_metric("store_memory", duration, True)
            
            logger.debug(f"Stored memory '{key}' in {duration:.3f}s")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            await self._record_performance_metric("store_memory", duration, False, {"error": get_secure_error_message(e)})
            raise MemorySystemError(f"Failed to store memory '{key}': {get_secure_error_message(e)}") from e
    
    @PerfectExceptionHandler.handle_async_with_context
    async def recall_memories(self, query: str, limit: int = 10, 
                            filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Recall memories with perfect async search"""
        await self.initialize()
        
        start_time = time.time()
        
        # Build optimized SQL query
        where_clauses = []
        params = []
        
        # Text search
        where_clauses.append("(content LIKE ? OR key LIKE ?)")
        query_pattern = f"%{query}%"
        params.extend([query_pattern, query_pattern])
        
        # Apply filters
        if filters:
            if filters.get('persona'):
                where_clauses.append("persona = ?")
                params.append(filters['persona'])
            
            if filters.get('category'):
                where_clauses.append("category = ?")
                params.append(filters['category'])
            
            if filters.get('min_importance'):
                where_clauses.append("importance >= ?")
                params.append(filters['min_importance'])
            
            if filters.get('since'):
                where_clauses.append("timestamp >= ?")
                params.append(filters['since'])
        
        # Construct final query with perfect optimization
        sql = f'''
        SELECT 
            key, content, importance, timestamp, persona, category, metadata,
            access_count, last_access, content_hash,
            -- Relevance scoring
            CASE 
                WHEN key = ? THEN 1.0
                WHEN content LIKE ? THEN 0.9
                WHEN key LIKE ? THEN 0.8
                ELSE 0.7
            END * importance AS relevance_score
        FROM memories 
        WHERE {' AND '.join(where_clauses)}
        ORDER BY relevance_score DESC, importance DESC, timestamp DESC
        LIMIT ?
        '''
        
        # Add relevance parameters
        final_params = [query, f"%{query}%", f"%{query}%"] + params + [limit]
        
        try:
            rows = await self.pool.execute_query(sql, tuple(final_params))
            
            # Convert to dictionaries and update access stats
            results = []
            update_queries = []
            
            for row in rows:
                result = dict(row)
                
                # Parse metadata
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        result['metadata'] = {}
                
                results.append(result)
                
                # Prepare access count update
                update_queries.append((
                    result['access_count'] + 1,
                    datetime.now().isoformat(),
                    result['key']
                ))
            
            # Batch update access statistics
            if update_queries:
                update_sql = '''
                UPDATE memories 
                SET access_count = ?, last_access = ? 
                WHERE key = ?
                '''
                await self.pool.execute_many(update_sql, update_queries)
            
            # Record performance
            duration = time.time() - start_time
            await self._record_performance_metric("recall_memories", duration, True, 
                                                {"results_count": len(results)})
            
            logger.debug(f"Recalled {len(results)} memories in {duration:.3f}s")
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            await self._record_performance_metric("recall_memories", duration, False, 
                                                {"error": get_secure_error_message(e)})
            raise MemorySystemError(f"Failed to recall memories: {get_secure_error_message(e)}") from e
    
    # ========================================================================
    # Perfect Analytics & Optimization (完璧な分析と最適化)
    # ========================================================================
    
    async def get_memory_analytics(self) -> Dict[str, Any]:
        """Get comprehensive memory analytics"""
        await self.initialize()
        
        queries = {
            "total_memories": "SELECT COUNT(*) as count FROM memories",
            "avg_importance": "SELECT AVG(importance) as avg FROM memories",
            "top_personas": '''
                SELECT persona, COUNT(*) as count 
                FROM memories 
                WHERE persona IS NOT NULL 
                GROUP BY persona 
                ORDER BY count DESC 
                LIMIT 5
            ''',
            "top_categories": '''
                SELECT category, COUNT(*) as count 
                FROM memories 
                WHERE category IS NOT NULL 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 5
            ''',
            "recent_activity": '''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM memories 
                WHERE timestamp >= date('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''',
            "most_accessed": '''
                SELECT key, access_count, last_access
                FROM memories
                WHERE access_count > 0
                ORDER BY access_count DESC
                LIMIT 10
            '''
        }
        
        results = {}
        
        for name, query in queries.items():
            try:
                rows = await self.pool.execute_query(query)
                if name in ["total_memories", "avg_importance"]:
                    results[name] = dict(rows[0]) if rows else {name.split('_')[1]: 0}
                else:
                    results[name] = [dict(row) for row in rows]
            except Exception as e:
                error_id = secure_log_error(e, "query_operation")
                logger.error(f"Analytics query '{name}' failed: {error_id}")
                results[name] = []
        
        return results
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization"""
        await self.initialize()
        
        optimizations = []
        start_time = time.time()
        
        try:
            # Vacuum database
            await self.pool.execute_query("VACUUM")
            optimizations.append("Database vacuumed")
            
            # Analyze tables for better query planning
            await self.pool.execute_query("ANALYZE")
            optimizations.append("Statistics updated")
            
            # Check for unused data
            old_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            old_data_query = '''
                SELECT COUNT(*) as count 
                FROM memories 
                WHERE timestamp < ? AND access_count = 0
            '''
            old_rows = await self.pool.execute_query(old_data_query, (old_cutoff,))
            old_count = dict(old_rows[0])['count'] if old_rows else 0
            
            if old_count > 0:
                optimizations.append(f"Found {old_count} old unused memories")
            
            # Get final stats
            pool_stats = await self.pool.get_pool_stats()
            
            duration = time.time() - start_time
            
            return {
                "optimizations_applied": optimizations,
                "duration": duration,
                "pool_stats": pool_stats,
                "old_data_count": old_count
            }
            
        except Exception as e:
            raise MemorySystemError(f"Database optimization failed: {get_secure_error_message(e)}") from e
    
    async def _record_performance_metric(self, operation: str, duration: float, 
                                       success: bool, metadata: Optional[Dict] = None):
        """Record performance metrics for monitoring"""
        try:
            metric_id = f"{operation}_{int(time.time()*1000)}"
            metadata_json = json.dumps(metadata) if metadata else None
            
            query = '''
            INSERT INTO performance_metrics 
            (metric_id, operation, duration, timestamp, success, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                metric_id, operation, duration, 
                datetime.now().isoformat(), success, metadata_json
            )
            
            await self.pool.execute_query(query, params)
            
            # Log slow queries
            if duration > self._slow_query_threshold:
                logger.warning(f"Slow {operation}: {duration:.3f}s")
            
        except Exception as e:
            # Don't fail the main operation for metrics
            error_id = secure_log_error(e, "general_operation")
            logger.debug(f"Failed to record performance metric: {error_id}")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        await self.initialize()
        
        # Get recent performance data
        since = (datetime.now() - timedelta(hours=1)).isoformat()
        
        query = '''
        SELECT 
            operation,
            COUNT(*) as total_count,
            AVG(duration) as avg_duration,
            MIN(duration) as min_duration,
            MAX(duration) as max_duration,
            SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN duration > 1.0 THEN 1 ELSE 0 END) as slow_count
        FROM performance_metrics 
        WHERE timestamp >= ?
        GROUP BY operation
        ORDER BY total_count DESC
        '''
        
        try:
            rows = await self.pool.execute_query(query, (since,))
            operation_stats = [dict(row) for row in rows]
            
            # Calculate success rates
            for stat in operation_stats:
                stat['success_rate'] = (stat['success_count'] / stat['total_count']) * 100
                stat['slow_query_rate'] = (stat['slow_count'] / stat['total_count']) * 100
            
            pool_stats = await self.pool.get_pool_stats()
            
            return {
                "report_period": "last_hour",
                "operation_statistics": operation_stats,
                "connection_pool": pool_stats,
                "overall_health": "excellent" if all(s['success_rate'] > 95 for s in operation_stats) else "good"
            }
            
        except Exception as e:
            error_id = secure_log_error(e, "general_operation")
            logger.error(f"Performance report generation failed: {error_id}")
            return {"error": get_secure_error_message(e)}
    
    async def cleanup(self):
        """Clean up database resources"""
        await self.pool.cleanup()
        logger.info("Database manager cleaned up")

# ============================================================================
# Perfect Factory and Integration (完璧なファクトリーと統合)
# ============================================================================

class AsyncDatabaseFactory:
    """Perfect factory for creating optimized async database managers"""
    
    _instances: Dict[str, PerfectAsyncDatabaseManager] = {}
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_instance(cls, db_path: str, max_connections: int = 10) -> PerfectAsyncDatabaseManager:
        """Get singleton database manager instance"""
        async with cls._lock:
            if db_path not in cls._instances:
                manager = PerfectAsyncDatabaseManager(db_path, max_connections)
                await manager.initialize()
                cls._instances[db_path] = manager
                logger.info(f"Created new database manager for {db_path}")
            
            return cls._instances[db_path]
    
    @classmethod
    async def cleanup_all(cls):
        """Cleanup all database manager instances"""
        async with cls._lock:
            for manager in cls._instances.values():
                await manager.cleanup()
            cls._instances.clear()

# Example usage:
# manager = await AsyncDatabaseFactory.get_instance("./trinitas.db", max_connections=15)
# await manager.store_memory("test_key", "test_content", 0.8)
# results = await manager.recall_memories("test", limit=5)