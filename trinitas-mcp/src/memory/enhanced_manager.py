#!/usr/bin/env python3
"""
Trinitas v3.5 Enhanced Memory Manager
ハイブリッドバックエンド統合版メモリマネージャー
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

from .memory_core import (
    MemoryItem, MemoryType, Query, Context
)
from .hybrid_backend import (
    HybridMemoryBackend, HybridConfig, create_hybrid_backend
)
from .memory_manager import (
    PERSONA_MEMORY_CONFIG,
    MemoryConsolidator,
    ForgettingCurve
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EnhancedMemoryManager:
    """ハイブリッドバックエンド対応メモリマネージャー"""
    
    def __init__(self, persona: str = 'shared', config: Optional[Dict[str, Any]] = None):
        """初期化（ペルソナ対応）"""
        # Store persona
        self.persona = persona.lower()
        
        # Load configuration from environment or use provided config
        self.config = self._load_config(config)
        
        # Initialize hybrid backend with persona
        self.backend = create_hybrid_backend(self.config, persona=self.persona)
        
        # Persona configurations
        self.persona_configs = PERSONA_MEMORY_CONFIG
        
        # Memory consolidators and forgetting curves
        self.consolidators = {}
        self.forgetting_curves = {}
        
        # Statistics
        self.stats = {
            "total_stores": 0,
            "total_recalls": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Background tasks
        self.consolidation_task = None
        self.pruning_task = None
        self.health_check_task = None
        
        logger.info(f"Enhanced Memory Manager initialized with hybrid backend for persona {self.persona}")
    
    def _load_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """環境変数から設定を読み込み"""
        env_config = {
            # Redis
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", 6379)),
            "redis_db": int(os.getenv("REDIS_DB", 0)),
            "redis_ttl_working": int(os.getenv("REDIS_TTL_WORKING", 3600)),
            "redis_ttl_episodic": int(os.getenv("REDIS_TTL_EPISODIC", 86400)),
            "redis_ttl_cache": int(os.getenv("REDIS_TTL_CACHE", 300)),
            
            # ChromaDB
            "chromadb_enabled": os.getenv("CHROMADB_ENABLED", "true").lower() == "true",
            "chromadb_path": os.getenv("CHROMADB_PATH", "/tmp/trinitas_chromadb"),
            "chromadb_embedding_model": os.getenv("CHROMADB_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            
            # SQLite
            "sqlite_path": os.getenv("SQLITE_PATH", "/tmp/trinitas_sqlite"),
            "sqlite_archive_days": int(os.getenv("SQLITE_ARCHIVE_DAYS", 7)),
            
            # Hybrid routing
            "use_redis_for_working": os.getenv("USE_REDIS_FOR_WORKING", "true").lower() == "true",
            "use_redis_for_episodic": os.getenv("USE_REDIS_FOR_EPISODIC", "true").lower() == "true",
            "use_chromadb_for_semantic": os.getenv("USE_CHROMADB_FOR_SEMANTIC", "true").lower() == "true",
            "use_chromadb_for_procedural": os.getenv("USE_CHROMADB_FOR_PROCEDURAL", "true").lower() == "true",
            
            # Performance
            "batch_size": int(os.getenv("BATCH_SIZE", 100)),
            "cache_results": os.getenv("CACHE_RESULTS", "true").lower() == "true",
            "async_writes": os.getenv("ASYNC_WRITES", "true").lower() == "true",
        }
        
        # Override with provided config
        if config:
            env_config.update(config)
        
        return env_config
    
    async def initialize(self) -> bool:
        """バックエンドを初期化"""
        success = await self.backend.initialize()
        
        if success:
            # Start background tasks
            await self.start_background_tasks()
            logger.info("Enhanced Memory Manager fully initialized")
        else:
            logger.error("Failed to initialize memory backend")
        
        return success
    
    async def remember(self, 
                       persona: str,
                       content: Any,
                       memory_type: Optional[MemoryType] = None,
                       importance: float = 0.5,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        """記憶を保存"""
        # Auto-determine memory type if not specified
        if memory_type is None:
            memory_type = self._infer_memory_type(content)
        
        # Create memory item
        item = MemoryItem(
            id="",  # Will be auto-generated
            persona=persona,
            content=content,
            type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store via hybrid backend
        success = await self.backend.store(item)
        
        if success:
            self.stats["total_stores"] += 1
            logger.debug(f"Stored {memory_type.value} memory for {persona}: {item.id}")
        else:
            logger.error(f"Failed to store memory for {persona}")
        
        return item if success else None
    
    async def recall(self,
                    persona: str,
                    query_text: str,
                    context: Optional[Context] = None,
                    limit: int = 5,
                    use_semantic: bool = True) -> List[MemoryItem]:
        """記憶を想起"""
        # Create query
        query = Query(
            text=query_text,
            context=context,
            limit=limit,
            needs_experience=True,
            needs_knowledge=use_semantic,
            needs_procedure=use_semantic
        )
        
        # Search via hybrid backend
        results = await self.backend.search(query, persona)
        
        self.stats["total_recalls"] += 1
        
        if results:
            logger.debug(f"Retrieved {len(results)} memories for {persona}")
        
        return results
    
    async def semantic_search(self,
                             query_text: str,
                             personas: Optional[List[str]] = None,
                             limit: int = 10,
                             min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """セマンティック検索（ChromaDB活用）"""
        if not personas:
            personas = list(self.persona_configs.keys())
        
        all_results = []
        
        for persona in personas:
            query = Query(
                text=query_text,
                limit=limit,
                threshold=min_similarity,
                needs_knowledge=True,
                needs_procedure=True
            )
            
            results = await self.backend.search(query, persona)
            
            for result in results:
                all_results.append({
                    "persona": persona,
                    "content": result.content,
                    "type": result.type.value,
                    "importance": result.importance,
                    "timestamp": result.timestamp.isoformat(),
                    "tags": result.tags
                })
        
        # Sort by importance/relevance
        all_results.sort(key=lambda x: x["importance"], reverse=True)
        
        return all_results[:limit]
    
    async def cross_persona_share(self,
                                 from_persona: str,
                                 to_persona: str,
                                 query_text: str,
                                 limit: int = 5) -> int:
        """ペルソナ間で記憶を共有"""
        # Find memories to share
        memories = await self.recall(
            persona=from_persona,
            query_text=query_text,
            limit=limit
        )
        
        shared_count = 0
        for memory in memories:
            # Copy to target persona
            memory.persona = to_persona
            memory.metadata["shared_from"] = from_persona
            memory.metadata["shared_at"] = datetime.now().isoformat()
            
            if await self.backend.store(memory):
                shared_count += 1
        
        logger.info(f"Shared {shared_count} memories from {from_persona} to {to_persona}")
        
        return shared_count
    
    async def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        backend_stats = await self.backend.get_stats()
        
        return {
            "manager": self.stats,
            "backend": backend_stats,
            "cache_hit_rate": self.stats["cache_hits"] / max(self.stats["cache_hits"] + self.stats["cache_misses"], 1)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "backends": {}
        }
        
        # Check Redis
        if self.backend.redis_available:
            try:
                await self.backend.redis.client.ping()
                health["backends"]["redis"] = "healthy"
            except:
                health["backends"]["redis"] = "unhealthy"
                health["status"] = "degraded"
        
        # Check ChromaDB
        if self.backend.chromadb_available:
            try:
                # Simple test query
                await self.backend.chromadb.search(
                    Query(text="test", limit=1),
                    persona="test"
                )
                health["backends"]["chromadb"] = "healthy"
            except:
                health["backends"]["chromadb"] = "unhealthy"
                health["status"] = "degraded"
        
        # SQLite is always available
        health["backends"]["sqlite"] = "healthy"
        
        return health
    
    def _infer_memory_type(self, content: Any) -> MemoryType:
        """コンテンツから記憶タイプを推論"""
        content_str = str(content).lower()
        
        # Check for patterns
        if any(word in content_str for word in ["method", "algorithm", "process", "steps", "procedure"]):
            return MemoryType.PROCEDURAL
        elif any(word in content_str for word in ["concept", "definition", "theory", "architecture", "design"]):
            return MemoryType.SEMANTIC
        elif any(word in content_str for word in ["event", "happened", "occurred", "did", "was"]):
            return MemoryType.EPISODIC
        else:
            return MemoryType.WORKING
    
    async def start_background_tasks(self):
        """バックグラウンドタスクを開始"""
        if not self.health_check_task:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Background tasks started")
    
    async def stop_background_tasks(self):
        """バックグラウンドタスクを停止"""
        if self.health_check_task:
            self.health_check_task.cancel()
        
        logger.info("Background tasks stopped")
    
    async def _health_check_loop(self):
        """定期的なヘルスチェック"""
        interval = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
        
        while True:
            try:
                await asyncio.sleep(interval)
                health = await self.health_check()
                
                if health["status"] != "healthy":
                    logger.warning(f"Health check degraded: {health}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def cleanup(self):
        """クリーンアップ"""
        await self.stop_background_tasks()
        await self.backend.cleanup()
        logger.info("Enhanced Memory Manager cleaned up")

# Global instance
enhanced_memory_manager = None

async def get_enhanced_memory_manager(persona: str = 'shared') -> EnhancedMemoryManager:
    """シングルトンインスタンスを取得（ペルソナ対応）"""
    global enhanced_memory_manager
    
    if not enhanced_memory_manager:
        enhanced_memory_manager = EnhancedMemoryManager(persona=persona)
        await enhanced_memory_manager.initialize()
    
    return enhanced_memory_manager

# Convenience functions
async def remember(persona: str, content: Any, **kwargs) -> MemoryItem:
    """簡易記憶保存"""
    manager = await get_enhanced_memory_manager()
    return await manager.remember(persona, content, **kwargs)

async def recall(persona: str, query: str, **kwargs) -> List[MemoryItem]:
    """簡易記憶想起"""
    manager = await get_enhanced_memory_manager()
    return await manager.recall(persona, query, **kwargs)

async def semantic_search(query: str, **kwargs) -> List[Dict[str, Any]]:
    """簡易セマンティック検索"""
    manager = await get_enhanced_memory_manager()
    return await manager.semantic_search(query, **kwargs)