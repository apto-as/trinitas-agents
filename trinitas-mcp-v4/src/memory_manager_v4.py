"""
Enhanced Memory Manager for Trinitas v4.0
メモリ管理システム - ハイブリッドバックエンド対応
"""

import asyncio
import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

# Import performance optimizer if available
try:
    from performance_optimizer import PerformanceOptimizer
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False
    logger.info("Performance optimizer not available, using standard operations")

class EnhancedMemoryManager:
    """
    強化メモリマネージャー
    Redis, ChromaDB, SQLiteのハイブリッドバックエンドをサポート
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend = config["memory"]["backend"]
        
        # Initialize backends based on configuration
        self.redis_client = None
        self.chromadb_client = None
        self.sqlite_conn = None
        
        self._initialize_backends()
        
        # Memory sections
        self.memory_sections = {
            "working_memory": {},      # Short-term, fast access
            "episodic_memory": {},      # Event-based memories
            "semantic_memory": {},      # Knowledge and facts
            "procedural_memory": {},    # How-to knowledge
            "cache": {},               # Temporary cache
            "learning_data": {},       # Learning system data
            "pattern_storage": {},     # Identified patterns
            "performance_metrics": {}, # Performance data
        }
        
        # Initialize performance optimizer
        self.optimizer = None
        if OPTIMIZER_AVAILABLE:
            optimizer_config = {
                "cache": {
                    "max_size": 1000,
                    "max_memory_mb": 100
                },
                "db": {
                    "max_connections": 10
                }
            }
            self.optimizer = PerformanceOptimizer(optimizer_config)
            logger.info("Performance optimizer initialized")
        
        logger.info(f"Memory Manager initialized with backend: {self.backend}")
    
    def _initialize_backends(self):
        """Initialize memory backends"""
        backend_type = self.backend.lower()
        
        if backend_type in ["hybrid", "sqlite"]:
            # Initialize SQLite (always available)
            self._init_sqlite()
        
        if backend_type in ["hybrid", "redis"]:
            # Try to initialize Redis
            try:
                import redis
                self.redis_client = redis.from_url(
                    self.config["memory"]["redis_url"],
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Redis backend initialized")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                if backend_type == "redis":
                    logger.error("Redis-only mode but Redis unavailable!")
        
        if backend_type in ["hybrid", "chromadb"]:
            # Try to initialize ChromaDB
            try:
                import chromadb
                from chromadb.config import Settings
                
                self.chromadb_client = chromadb.PersistentClient(
                    path=self.config["memory"]["chromadb_path"],
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info("ChromaDB backend initialized")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}")
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        db_path = Path(self.config["memory"]["sqlite_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.sqlite_conn = sqlite3.connect(str(db_path))
        cursor = self.sqlite_conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                section TEXT,
                persona TEXT,
                importance REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_key ON memory_store(key);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_persona ON memory_store(persona);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance ON memory_store(importance);
        """)
        
        self.sqlite_conn.commit()
        logger.info("SQLite backend initialized")
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Store value in memory
        
        Args:
            key: Memory key
            value: Value to store
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Determine memory section
            section = self._determine_section(key, metadata)
            
            # Prepare data
            data = {
                "value": value,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "section": section
            }
            
            # Store in appropriate backend
            if self.redis_client and section in ["working_memory", "cache"]:
                # Fast access sections go to Redis
                self.redis_client.setex(
                    key,
                    timedelta(hours=24),
                    json.dumps(data)
                )
            
            if self.chromadb_client and section in ["semantic_memory", "learning_data"]:
                # Semantic sections go to ChromaDB for vector search
                collection = self._get_or_create_collection(section)
                collection.upsert(
                    ids=[key],
                    documents=[json.dumps(value) if not isinstance(value, str) else value],
                    metadatas=[metadata or {}]
                )
            
            # Always store in SQLite as backup
            if self.sqlite_conn:
                cursor = self.sqlite_conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO memory_store 
                    (key, value, metadata, section, persona, importance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    json.dumps(value),
                    json.dumps(metadata or {}),
                    section,
                    metadata.get("persona") if metadata else None,
                    metadata.get("importance", 0.5) if metadata else 0.5
                ))
                self.sqlite_conn.commit()
            
            # Update in-memory cache
            self.memory_sections[section][key] = data
            
            logger.debug(f"Stored {key} in {section}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
    
    async def recall(self, query: str, semantic: bool = False, 
                    filters: Optional[Dict] = None, limit: int = 10) -> List[Dict]:
        """
        Recall memories based on query
        
        Args:
            query: Search query
            semantic: Use semantic search
            filters: Additional filters
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        # Use optimizer if available
        if self.optimizer and self.optimizer.optimization_enabled:
            results, response_time = await self.optimizer.optimized_recall(
                self, query, semantic=semantic, filters=filters, limit=limit
            )
            logger.debug(f"Optimized recall completed in {response_time:.2f}ms")
            return results
        
        results = []
        
        try:
            if semantic and self.chromadb_client:
                # Semantic search using ChromaDB
                for section in ["semantic_memory", "learning_data"]:
                    collection = self._get_or_create_collection(section)
                    query_results = collection.query(
                        query_texts=[query],
                        n_results=min(limit, 10),
                        where=filters
                    )
                    
                    if query_results["ids"][0]:
                        for i, id in enumerate(query_results["ids"][0]):
                            results.append({
                                "key": id,
                                "value": query_results["documents"][0][i],
                                "metadata": query_results["metadatas"][0][i],
                                "section": section,
                                "distance": query_results["distances"][0][i] if "distances" in query_results else None
                            })
            else:
                # Regular search
                if self.redis_client:
                    # Search in Redis for fast sections
                    pattern = f"*{query}*"
                    keys = self.redis_client.keys(pattern)[:limit]
                    for key in keys:
                        try:
                            data = json.loads(self.redis_client.get(key))
                            if self._match_filters(data, filters):
                                results.append({
                                    "key": key,
                                    "value": data["value"],
                                    "metadata": data["metadata"],
                                    "section": data["section"]
                                })
                        except:
                            pass
                
                # Search in SQLite
                if self.sqlite_conn:
                    cursor = self.sqlite_conn.cursor()
                    
                    where_clauses = ["key LIKE ?"]
                    params = [f"%{query}%"]
                    
                    if filters:
                        if "persona" in filters:
                            where_clauses.append("persona = ?")
                            params.append(filters["persona"])
                        if "section" in filters:
                            where_clauses.append("section = ?")
                            params.append(filters["section"])
                    
                    cursor.execute(f"""
                        SELECT key, value, metadata, section, importance
                        FROM memory_store
                        WHERE {" AND ".join(where_clauses)}
                        ORDER BY importance DESC, accessed_at DESC
                        LIMIT ?
                    """, params + [limit])
                    
                    for row in cursor.fetchall():
                        results.append({
                            "key": row[0],
                            "value": json.loads(row[1]),
                            "metadata": json.loads(row[2]),
                            "section": row[3],
                            "importance": row[4]
                        })
                    
                    # Update access time
                    for result in results:
                        cursor.execute("""
                            UPDATE memory_store 
                            SET accessed_at = CURRENT_TIMESTAMP, 
                                access_count = access_count + 1
                            WHERE key = ?
                        """, (result["key"],))
                    self.sqlite_conn.commit()
            
        except Exception as e:
            logger.error(f"Error recalling memory: {e}")
        
        return results[:limit]
    
    async def get_context(self, persona: str, task: str) -> Dict:
        """
        Get relevant context for persona and task
        
        Args:
            persona: Active persona
            task: Current task
            
        Returns:
            Relevant memory context
        """
        context = {}
        
        try:
            # Get working memory
            working_memories = await self.recall(
                query=task[:50],  # Use first 50 chars as query
                filters={"persona": persona, "section": "working_memory"},
                limit=5
            )
            if working_memories:
                context["working_memory"] = working_memories
            
            # Get relevant semantic memory
            semantic_memories = await self.recall(
                query=task,
                semantic=True,
                filters={"persona": persona},
                limit=3
            )
            if semantic_memories:
                context["semantic_memory"] = semantic_memories
            
            # Get recent episodic memory
            if self.sqlite_conn:
                cursor = self.sqlite_conn.cursor()
                cursor.execute("""
                    SELECT key, value, metadata
                    FROM memory_store
                    WHERE persona = ? AND section = 'episodic_memory'
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (persona,))
                
                episodic = []
                for row in cursor.fetchall():
                    episodic.append({
                        "key": row[0],
                        "value": json.loads(row[1]),
                        "metadata": json.loads(row[2])
                    })
                
                if episodic:
                    context["episodic_memory"] = episodic
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
        
        return context
    
    async def store_result(self, persona: str, task: str, result: Dict):
        """
        Store execution result in memory
        
        Args:
            persona: Persona that executed
            task: Task that was executed
            result: Execution result
        """
        try:
            # Store in episodic memory
            await self.store(
                key=f"episode_{persona}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                value={
                    "task": task,
                    "result": result,
                    "persona": persona
                },
                metadata={
                    "persona": persona,
                    "type": "execution_result",
                    "importance": 0.6
                }
            )
            
            # Update working memory
            await self.store(
                key=f"working_{persona}_latest",
                value=result,
                metadata={
                    "persona": persona,
                    "type": "latest_result",
                    "importance": 0.7
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing result: {e}")
    
    async def apply_optimizations(self, optimization_plan: Dict):
        """
        Apply memory optimizations from Bellona/Seshat
        
        Args:
            optimization_plan: Optimization plan
        """
        try:
            for action in optimization_plan.get("actions", []):
                if action["type"] == "cleanup":
                    await self._cleanup_old_memories(action.get("threshold_days", 30))
                elif action["type"] == "cache_expansion":
                    await self._expand_cache()
                elif action["type"] == "index_optimization":
                    await self._optimize_indices(action.get("targets", []))
            
            logger.info(f"Applied optimizations: {optimization_plan['summary']}")
            
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
    
    async def _cleanup_old_memories(self, threshold_days: int):
        """Clean up old memories"""
        if self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                DELETE FROM memory_store
                WHERE accessed_at < datetime('now', '-' || ? || ' days')
                AND importance < 0.5
            """, (threshold_days,))
            deleted = cursor.rowcount
            self.sqlite_conn.commit()
            logger.info(f"Cleaned up {deleted} old memories")
    
    async def _expand_cache(self):
        """Expand cache capacity"""
        # This would involve Redis configuration in production
        logger.info("Cache expansion requested (placeholder)")
    
    async def _optimize_indices(self, targets: List[str]):
        """Optimize database indices"""
        if self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("ANALYZE")
            self.sqlite_conn.commit()
            logger.info("Database indices optimized")
    
    def _determine_section(self, key: str, metadata: Optional[Dict]) -> str:
        """Determine which memory section to use"""
        if metadata:
            if metadata.get("section"):
                return metadata["section"]
            
            type = metadata.get("type", "")
            if "working" in type or "temp" in type:
                return "working_memory"
            elif "episode" in type or "event" in type:
                return "episodic_memory"
            elif "knowledge" in type or "fact" in type:
                return "semantic_memory"
            elif "learn" in type:
                return "learning_data"
            elif "pattern" in type:
                return "pattern_storage"
        
        # Default based on key prefix
        if key.startswith("working_"):
            return "working_memory"
        elif key.startswith("episode_"):
            return "episodic_memory"
        elif key.startswith("knowledge_"):
            return "semantic_memory"
        elif key.startswith("cache_"):
            return "cache"
        
        return "working_memory"  # Default
    
    def _get_or_create_collection(self, name: str):
        """Get or create ChromaDB collection"""
        if self.chromadb_client:
            try:
                return self.chromadb_client.get_or_create_collection(name)
            except:
                pass
        return None
    
    def _match_filters(self, data: Dict, filters: Optional[Dict]) -> bool:
        """Check if data matches filters"""
        if not filters:
            return True
        
        metadata = data.get("metadata", {})
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        
        return True
    
    async def get_status(self) -> Dict:
        """Get memory system status"""
        status = {
            "backend": self.backend,
            "backends_active": [],
            "memory_sections": list(self.memory_sections.keys()),
            "total_memories": 0
        }
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                status["backends_active"].append("redis")
            except:
                pass
        
        if self.chromadb_client:
            status["backends_active"].append("chromadb")
        
        if self.sqlite_conn:
            status["backends_active"].append("sqlite")
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_store")
            status["total_memories"] = cursor.fetchone()[0]
        
        # Count memories in each section
        status["section_counts"] = {}
        for section, memories in self.memory_sections.items():
            status["section_counts"][section] = len(memories)
        
        return status