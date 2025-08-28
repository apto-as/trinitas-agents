#!/usr/bin/env python3
"""
Trinitas v3.5 Hybrid Memory Backend
Redis + ChromaDB + SQLite の統合実装
"""

import asyncio
import json
import logging
import os
import sqlite3
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .memory_core import (
    MemoryItem, MemoryType, Query, Context,
    WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory
)
from .security.persona_isolation import PersonaIsolationManager, get_isolation_manager
from .security.access_control import AccessControlManager, get_access_control_manager, MemoryOperation

logger = logging.getLogger(__name__)

# Configuration
@dataclass
class HybridConfig:
    """ハイブリッドバックエンド設定"""
    # Redis config
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl_working: int = 3600  # 1 hour
    redis_ttl_episodic: int = 86400  # 24 hours
    redis_ttl_cache: int = 300  # 5 minutes
    
    # ChromaDB config
    chromadb_enabled: bool = False
    chromadb_path: str = "/tmp/trinitas_chromadb"
    chromadb_embedding_model: str = "all-MiniLM-L6-v2"
    
    # SQLite config (always enabled as fallback)
    sqlite_path: str = "/tmp/trinitas_sqlite.db"
    sqlite_archive_days: int = 7
    
    # Hybrid behavior
    use_redis_for_working: bool = True
    use_redis_for_episodic: bool = True
    use_chromadb_for_semantic: bool = True
    use_chromadb_for_procedural: bool = True
    
    # Performance
    batch_size: int = 100
    cache_results: bool = True
    async_writes: bool = True

# Base Backend Interface
class MemoryBackend(ABC):
    """記憶バックエンドの基底クラス"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初期化"""
        pass
    
    @abstractmethod
    async def store(self, item: MemoryItem) -> bool:
        """記憶を保存"""
        pass
    
    @abstractmethod
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """記憶を取得"""
        pass
    
    @abstractmethod
    async def search(self, query: Query, persona: str) -> List[MemoryItem]:
        """記憶を検索"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """記憶を削除"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        pass

# Redis Backend
class RedisBackend(MemoryBackend):
    """Redis記憶バックエンド"""
    
    def __init__(self, config: HybridConfig, persona: str = 'shared'):
        self.config = config
        self.persona = persona.lower()
        self.client = None
        self.async_client = None
        self.pipeline = None
        self.isolation_manager = None
        self.access_control = None
        
    async def initialize(self) -> bool:
        """Redis接続を初期化（ペルソナ分離対応）"""
        if not self.config.redis_enabled:
            return False
        
        try:
            # Initialize security managers
            self.isolation_manager = await get_isolation_manager(
                self.config.redis_host,
                self.config.redis_port
            )
            self.access_control = get_access_control_manager()
            
            # Get persona-specific connection
            self.client = self.isolation_manager.get_connection(self.persona)
            
            if not self.client:
                logger.warning(f"Failed to get connection for persona {self.persona}")
                return False
            
            # Test connection
            await self.client.ping()
            
            # For async operations, we'll use the same connection
            self.async_client = self.client
            
            logger.info(f"Redis backend initialized for persona {self.persona}")
            return True
            
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            return False
    
    async def store(self, item: MemoryItem) -> bool:
        """Redisに記憶を保存"""
        if not self.async_client:
            return False
        
        try:
            # Serialize item
            data = pickle.dumps(item)
            
            # Determine TTL based on memory type
            ttl = self.config.redis_ttl_working
            if item.type == MemoryType.EPISODIC:
                ttl = self.config.redis_ttl_episodic
            elif item.type in [MemoryType.SEMANTIC, MemoryType.PROCEDURAL]:
                ttl = self.config.redis_ttl_cache
            
            # Store with TTL
            await self.async_client.setex(
                f"memory:{item.id}",
                ttl,
                data
            )
            
            # Add to persona index (fixed zadd format)
            await self.async_client.zadd(
                f"persona:{item.persona}:{item.type.value}",
                {item.id: item.importance}  # Dictionary format for zadd
            )
            
            # Add to type index
            await self.async_client.sadd(
                f"type:{item.type.value}",
                item.id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Redis store failed: {e}")
            return False
    
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Redisから記憶を取得"""
        if not self.async_client:
            return None
        
        try:
            data = await self.async_client.get(f"memory:{item_id}")
            if data:
                return pickle.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Redis retrieve failed: {e}")
            return None
    
    async def search(self, query: Query, persona: str) -> List[MemoryItem]:
        """Redisで記憶を検索"""
        if not self.async_client:
            return []
        
        results = []
        
        try:
            # Search in persona's memories by importance
            memory_ids = await self.async_client.zrevrange(
                f"persona:{persona}:*",
                0, query.limit - 1
            )
            
            # Retrieve actual memories
            for memory_id in memory_ids:
                item = await self.retrieve(memory_id)
                if item:
                    results.append(item)
            
            return results[:query.limit]
            
        except Exception as e:
            logger.error(f"Redis search failed: {e}")
            return []
    
    async def delete(self, item_id: str) -> bool:
        """Redisから記憶を削除"""
        if not self.async_client:
            return False
        
        try:
            # Get item first to remove from indices
            item = await self.retrieve(item_id)
            if item:
                # Remove from indices
                await self.async_client.zrem(
                    f"persona:{item.persona}:{item.type.value}",
                    item.id
                )
                await self.async_client.srem(
                    f"type:{item.type.value}",
                    item.id
                )
            
            # Delete the item
            await self.async_client.delete(f"memory:{item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Redis統計を取得"""
        if not self.client:
            return {}
        
        try:
            info = self.client.info('memory')
            dbsize = self.client.dbsize()
            
            return {
                "backend": "redis",
                "connected": True,
                "memory_used_mb": info.get('used_memory', 0) / 1024 / 1024,
                "total_keys": dbsize
            }
        except:
            return {"backend": "redis", "connected": False}
    
    async def cleanup(self):
        """接続をクリーンアップ"""
        if self.async_client:
            await self.async_client.aclose()  # Use aclose for modern Redis
        if self.client:
            await self.client.aclose()

# ChromaDB Backend
class ChromaDBBackend(MemoryBackend):
    """ChromaDBベクトル検索バックエンド"""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.client = None
        self.collections = {}
        
    async def initialize(self) -> bool:
        """ChromaDBを初期化"""
        if not self.config.chromadb_enabled:
            return False
        
        try:
            import chromadb
            
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.config.chromadb_path
            )
            
            # Create collections for each memory type
            for mem_type in MemoryType:
                collection_name = f"memory_{mem_type.value}"
                self.collections[mem_type] = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            
            logger.info("ChromaDB backend initialized")
            return True
            
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}")
            return False
    
    async def store(self, item: MemoryItem) -> bool:
        """ChromaDBに記憶を保存"""
        if not self.client:
            return False
        
        try:
            collection = self.collections.get(item.type)
            if not collection:
                return False
            
            # Prepare document
            document = json.dumps(item.content) if not isinstance(item.content, str) else item.content
            
            # Prepare metadata
            metadata = {
                "persona": item.persona,
                "importance": item.importance,
                "timestamp": item.timestamp.isoformat(),
                "type": item.type.value
            }
            
            # Add tags if present
            if item.tags:
                metadata["tags"] = ",".join(item.tags)
            
            # Store in collection
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[item.id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB store failed: {e}")
            return False
    
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """ChromaDBから記憶を取得"""
        if not self.client:
            return None
        
        try:
            # Search all collections
            for mem_type, collection in self.collections.items():
                result = collection.get(ids=[item_id])
                
                if result and result['documents']:
                    # Reconstruct MemoryItem
                    metadata = result['metadatas'][0] if result['metadatas'] else {}
                    content = json.loads(result['documents'][0]) if result['documents'] else {}
                    
                    return MemoryItem(
                        id=item_id,
                        content=content,
                        type=mem_type,
                        persona=metadata.get('persona', ''),
                        timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                        importance=metadata.get('importance', 0.5),
                        tags=metadata.get('tags', '').split(',') if metadata.get('tags') else []
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"ChromaDB retrieve failed: {e}")
            return None
    
    async def search(self, query: Query, persona: str) -> List[MemoryItem]:
        """ChromaDBでセマンティック検索"""
        if not self.client:
            return []
        
        results = []
        
        try:
            # Search across relevant collections
            for mem_type, collection in self.collections.items():
                # Filter by persona
                where = {"persona": persona} if persona else None
                
                # Perform semantic search
                search_results = collection.query(
                    query_texts=[query.text],
                    n_results=query.limit,
                    where=where
                )
                
                # Convert to MemoryItems
                if search_results['documents']:
                    for i, doc in enumerate(search_results['documents'][0]):
                        metadata = search_results['metadatas'][0][i] if search_results['metadatas'] else {}
                        
                        item = MemoryItem(
                            id=search_results['ids'][0][i],
                            content=json.loads(doc) if doc.startswith('{') else doc,
                            type=mem_type,
                            persona=metadata.get('persona', persona),
                            timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                            importance=metadata.get('importance', 0.5),
                            tags=metadata.get('tags', '').split(',') if metadata.get('tags') else []
                        )
                        results.append(item)
            
            # Sort by relevance/importance and limit
            results.sort(key=lambda x: x.importance, reverse=True)
            return results[:query.limit]
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    async def delete(self, item_id: str) -> bool:
        """ChromaDBから記憶を削除"""
        if not self.client:
            return False
        
        try:
            # Delete from all collections
            for collection in self.collections.values():
                collection.delete(ids=[item_id])
            
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB delete failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """ChromaDB統計を取得"""
        if not self.client:
            return {}
        
        try:
            total_items = 0
            for collection in self.collections.values():
                total_items += collection.count()
            
            # Calculate storage size
            storage_path = Path(self.config.chromadb_path)
            storage_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())
            
            return {
                "backend": "chromadb",
                "connected": True,
                "total_items": total_items,
                "storage_size_mb": storage_size / 1024 / 1024,
                "collections": len(self.collections)
            }
        except:
            return {"backend": "chromadb", "connected": False}

# SQLite Backend (inherited from existing implementation)
class SQLiteBackend(MemoryBackend):
    """SQLite記憶バックエンド（フォールバック）"""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.episodic = None
        self.semantic = None
        self.procedural = None
        
    async def initialize(self) -> bool:
        """SQLiteを初期化"""
        try:
            # Use existing implementations
            db_dir = Path(self.config.sqlite_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            self.episodic = EpisodicMemory(str(db_dir / "episodic.db"))
            self.semantic = SemanticMemory(str(db_dir / "semantic"))
            self.procedural = ProceduralMemory(str(db_dir / "procedural.db"))
            
            logger.info("SQLite backend initialized")
            return True
            
        except Exception as e:
            logger.error(f"SQLite initialization failed: {e}")
            return False
    
    async def store(self, item: MemoryItem) -> bool:
        """SQLiteに記憶を保存"""
        try:
            if item.type == MemoryType.EPISODIC:
                await self.episodic.store(item)
            elif item.type == MemoryType.SEMANTIC:
                await self.semantic.store(item)
            elif item.type == MemoryType.PROCEDURAL:
                await self.procedural.store(item)
            return True
        except Exception as e:
            logger.error(f"SQLite store failed: {e}")
            return False
    
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """SQLiteから記憶を取得"""
        # This would need to search all databases
        # For simplicity, returning None for now
        return None
    
    async def search(self, query: Query, persona: str) -> List[MemoryItem]:
        """SQLiteで記憶を検索"""
        results = []
        
        if query.needs_experience:
            results.extend(await self.episodic.retrieve(query))
        if query.needs_knowledge:
            results.extend(await self.semantic.retrieve(query))
        if query.needs_procedure:
            results.extend(await self.procedural.retrieve(query))
        
        # Filter by persona
        results = [r for r in results if r.persona == persona]
        
        return results[:query.limit]
    
    async def delete(self, item_id: str) -> bool:
        """SQLiteから記憶を削除"""
        try:
            await self.episodic.forget(item_id)
            await self.semantic.forget(item_id)
            await self.procedural.forget(item_id)
            return True
        except:
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """SQLite統計を取得"""
        db_path = Path(self.config.sqlite_path)
        size = sum(f.stat().st_size for f in db_path.parent.rglob('*.db')) if db_path.parent.exists() else 0
        
        return {
            "backend": "sqlite",
            "connected": True,
            "storage_size_mb": size / 1024 / 1024
        }

# Hybrid Backend Implementation
class HybridMemoryBackend(MemoryBackend):
    """ハイブリッド記憶バックエンド"""
    
    def __init__(self, config: Optional[HybridConfig] = None, persona: str = 'shared'):
        self.config = config or HybridConfig()
        self.persona = persona.lower()
        
        # Initialize backends with persona support
        self.redis = RedisBackend(self.config, persona=self.persona)
        self.chromadb = ChromaDBBackend(self.config)
        self.sqlite = SQLiteBackend(self.config)
        
        # Track availability
        self.redis_available = False
        self.chromadb_available = False
        self.sqlite_available = False
        
        # Cache for performance
        self.cache = {}
        self.cache_ttl = {}
        
        # Access control
        self.access_control = None
        self.auth_token = None
        
    async def initialize(self) -> bool:
        """全バックエンドを初期化"""
        # Initialize access control
        self.access_control = get_access_control_manager()
        
        # Authenticate persona and get token
        self.auth_token = await self.access_control.authenticate(self.persona)
        if not self.auth_token:
            logger.warning(f"Failed to authenticate persona {self.persona}")
            # Continue without authentication for backward compatibility
        
        # Always initialize SQLite as fallback
        self.sqlite_available = await self.sqlite.initialize()
        
        # Try to initialize Redis
        if self.config.redis_enabled:
            self.redis_available = await self.redis.initialize()
        
        # Try to initialize ChromaDB
        if self.config.chromadb_enabled:
            self.chromadb_available = await self.chromadb.initialize()
        
        logger.info(f"Hybrid backend initialized for persona {self.persona} - "
                   f"Redis: {self.redis_available}, "
                   f"ChromaDB: {self.chromadb_available}, "
                   f"SQLite: {self.sqlite_available}")
        
        return self.sqlite_available  # At minimum, SQLite must work  # At minimum, SQLite must work
    
    async def store(self, item: MemoryItem) -> bool:
        """インテリジェントストレージルーティング（アクセス制御付き）"""
        # Check access control if authentication is enabled
        if self.auth_token:
            token_id = self.auth_token.token_id  # Use the hashed token_id
            authorized, error = await self.access_control.authorize(
                token_id,
                MemoryOperation.STORE,
                target_persona=self.persona,
                memory_type=item.type.value
            )
            if not authorized:
                logger.warning(f"Access denied for store operation: {error}")
                return False
        
        success = False
        
        # Route based on memory type and backend availability
        if item.type == MemoryType.WORKING:
            # Working memory -> Redis (fast) or SQLite
            if self.redis_available and self.config.use_redis_for_working:
                success = await self.redis.store(item)
            else:
                success = await self.sqlite.store(item)
        
        elif item.type == MemoryType.EPISODIC:
            # Episodic -> Redis (recent) + SQLite (archive)
            if self.redis_available and self.config.use_redis_for_episodic:
                success = await self.redis.store(item)
            
            # Always archive important episodic memories
            if item.importance > 0.5:
                await self.sqlite.store(item)
            
            if not success:
                success = await self.sqlite.store(item)
        
        elif item.type == MemoryType.SEMANTIC:
            # Semantic -> ChromaDB (semantic search) + Redis cache
            if self.chromadb_available and self.config.use_chromadb_for_semantic:
                success = await self.chromadb.store(item)
                
                # Cache in Redis for fast access
                if self.redis_available:
                    await self.redis.store(item)
            else:
                success = await self.sqlite.store(item)
        
        elif item.type == MemoryType.PROCEDURAL:
            # Procedural -> ChromaDB + SQLite
            if self.chromadb_available and self.config.use_chromadb_for_procedural:
                success = await self.chromadb.store(item)
            
            # Always store procedures in SQLite for reliability
            await self.sqlite.store(item)
            
            if not success:
                success = await self.sqlite.store(item)
        
        # Update cache
        if success and self.config.cache_results:
            self._cache_item(item)
        
        return success
    
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """多層取得戦略（アクセス制御付き）"""
        # Check access control if authentication is enabled
        if self.auth_token:
            token_id = self.auth_token.token_id  # Use the hashed token_id
            authorized, error = await self.access_control.authorize(
                token_id,
                MemoryOperation.RETRIEVE,
                target_persona=self.persona
            )
            if not authorized:
                logger.warning(f"Access denied for retrieve operation: {error}")
                return None
        
        # Check cache first
        if item_id in self.cache:
            if self._is_cache_valid(item_id):
                return self.cache[item_id]
        
        # Try Redis (fastest)
        if self.redis_available:
            item = await self.redis.retrieve(item_id)
            if item:
                self._cache_item(item)
                return item
        
        # Try ChromaDB
        if self.chromadb_available:
            item = await self.chromadb.retrieve(item_id)
            if item:
                self._cache_item(item)
                # Also cache in Redis for next time
                if self.redis_available:
                    await self.redis.store(item)
                return item
        
        # Fallback to SQLite
        item = await self.sqlite.retrieve(item_id)
        if item:
            self._cache_item(item)
        
        return item
    
    async def search(self, query: Query, persona: str) -> List[MemoryItem]:
        """ハイブリッド検索戦略"""
        results = []
        
        # For semantic queries, use ChromaDB first
        if query.needs_knowledge or query.needs_procedure:
            if self.chromadb_available:
                chroma_results = await self.chromadb.search(query, persona)
                results.extend(chroma_results)
        
        # For recent/working queries, use Redis
        if query.needs_experience:
            if self.redis_available:
                redis_results = await self.redis.search(query, persona)
                results.extend(redis_results)
        
        # If not enough results, search SQLite
        if len(results) < query.limit:
            sqlite_results = await self.sqlite.search(query, persona)
            results.extend(sqlite_results)
        
        # Remove duplicates and limit
        seen_ids = set()
        unique_results = []
        for item in results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)
        
        return unique_results[:query.limit]
    
    async def delete(self, item_id: str) -> bool:
        """全バックエンドから削除"""
        success = True
        
        if self.redis_available:
            success &= await self.redis.delete(item_id)
        
        if self.chromadb_available:
            success &= await self.chromadb.delete(item_id)
        
        success &= await self.sqlite.delete(item_id)
        
        # Remove from cache
        if item_id in self.cache:
            del self.cache[item_id]
            del self.cache_ttl[item_id]
        
        return success
    
    async def get_stats(self) -> Dict[str, Any]:
        """統合統計を取得"""
        stats = {
            "backend": "hybrid",
            "backends": {}
        }
        
        if self.redis_available:
            stats["backends"]["redis"] = await self.redis.get_stats()
        
        if self.chromadb_available:
            stats["backends"]["chromadb"] = await self.chromadb.get_stats()
        
        stats["backends"]["sqlite"] = await self.sqlite.get_stats()
        
        stats["cache_size"] = len(self.cache)
        
        return stats
    
    def _cache_item(self, item: MemoryItem):
        """アイテムをキャッシュ"""
        self.cache[item.id] = item
        self.cache_ttl[item.id] = datetime.now() + timedelta(seconds=self.config.redis_ttl_cache)
    
    def _is_cache_valid(self, item_id: str) -> bool:
        """キャッシュが有効か確認"""
        if item_id not in self.cache_ttl:
            return False
        return datetime.now() < self.cache_ttl[item_id]
    
    async def cleanup(self):
        """全バックエンドをクリーンアップ"""
        if self.redis_available:
            await self.redis.cleanup()

# Factory function
def create_hybrid_backend(
    config: Optional[Union[Dict[str, Any], HybridConfig]] = None,
    persona: str = 'shared'
) -> HybridMemoryBackend:
    """ハイブリッドバックエンドを作成（ペルソナ対応）"""
    if config:
        # Handle both dict and HybridConfig
        if isinstance(config, HybridConfig):
            hybrid_config = config
        else:
            hybrid_config = HybridConfig(**config)
    else:
        # Auto-detect available backends
        hybrid_config = HybridConfig()
        
        # Try to import and enable backends
        try:
            import redis
            hybrid_config.redis_enabled = True
        except ImportError:
            logger.info("Redis not available - using SQLite for working memory")
        
        try:
            import chromadb
            hybrid_config.chromadb_enabled = True
        except ImportError:
            logger.info("ChromaDB not available - using SQLite for semantic search")
    
    return HybridMemoryBackend(hybrid_config, persona=persona)