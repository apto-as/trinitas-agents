#!/usr/bin/env python3
"""
Trinitas v3.5 Advanced Cache Manager
Multi-level caching with intelligent invalidation
"""

import asyncio
import hashlib
import json
import pickle
import redis
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import aiofiles
import threading
from collections import OrderedDict
import time

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache levels"""
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"

class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    level: CacheLevel
    timestamp: datetime
    ttl: Optional[int] = None
    access_count: int = 0
    last_access: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    persona: Optional[str] = None
    workflow: Optional[str] = None

class AdvancedCacheManager:
    """Multi-level cache manager with intelligent features"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Memory cache (L1)
        self.memory_cache = OrderedDict()
        self.memory_size = 0
        self.memory_limit = self.config["memory_limit_mb"] * 1024 * 1024
        
        # Disk cache (L2)
        self.disk_cache_dir = Path(self.config["disk_cache_dir"])
        self.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        self.disk_index = {}
        
        # Distributed cache (L3) - Redis
        self.redis_client = None
        if self.config.get("redis_enabled"):
            try:
                self.redis_client = redis.Redis(
                    host=self.config.get("redis_host", "localhost"),
                    port=self.config.get("redis_port", 6379),
                    db=self.config.get("redis_db", 0),
                    decode_responses=False
                )
                self.redis_client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self.redis_client = None
        
        # Cache statistics
        self.stats = {
            "hits": {"memory": 0, "disk": 0, "distributed": 0},
            "misses": 0,
            "evictions": {"memory": 0, "disk": 0, "distributed": 0},
            "writes": {"memory": 0, "disk": 0, "distributed": 0}
        }
        
        # Invalidation rules
        self.invalidation_rules = {}
        
        # Cache warming
        self.warm_cache_items = []
        
        logger.info("Advanced Cache Manager initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "memory_limit_mb": 256,
            "disk_cache_dir": "/tmp/trinitas_cache",
            "disk_limit_mb": 1024,
            "redis_enabled": False,
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0,
            "default_ttl": 3600,
            "strategy": CacheStrategy.LRU,
            "warm_cache_on_start": True
        }
    
    # Cache Key Generation
    
    def generate_key(self, 
                    namespace: str,
                    identifier: Any,
                    context: Optional[Dict[str, Any]] = None,
                    persona: Optional[str] = None,
                    workflow: Optional[str] = None) -> str:
        """Generate context-aware cache key"""
        key_data = {
            "namespace": namespace,
            "id": identifier,
            "context": context or {},
            "persona": persona,
            "workflow": workflow
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    # Multi-level Cache Operations
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache, checking all levels"""
        # Check L1 - Memory
        value = self._get_from_memory(key)
        if value is not None:
            self.stats["hits"]["memory"] += 1
            return value
        
        # Check L2 - Disk
        value = await self._get_from_disk(key)
        if value is not None:
            self.stats["hits"]["disk"] += 1
            # Promote to memory
            await self._promote_to_memory(key, value)
            return value
        
        # Check L3 - Distributed
        if self.redis_client:
            value = await self._get_from_redis(key)
            if value is not None:
                self.stats["hits"]["distributed"] += 1
                # Promote to memory and disk
                await self._promote_to_memory(key, value)
                await self._promote_to_disk(key, value)
                return value
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, 
                 key: str,
                 value: Any,
                 ttl: Optional[int] = None,
                 tags: Optional[List[str]] = None,
                 persona: Optional[str] = None,
                 workflow: Optional[str] = None,
                 levels: Optional[List[CacheLevel]] = None) -> bool:
        """Set in cache at specified levels"""
        ttl = ttl or self.config["default_ttl"]
        tags = tags or []
        levels = levels or [CacheLevel.MEMORY, CacheLevel.DISK]
        
        # Calculate size
        size_bytes = len(pickle.dumps(value))
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            level=CacheLevel.MEMORY,
            timestamp=datetime.now(),
            ttl=ttl,
            size_bytes=size_bytes,
            tags=tags,
            persona=persona,
            workflow=workflow
        )
        
        success = True
        
        # Write to specified levels
        if CacheLevel.MEMORY in levels:
            success &= await self._set_to_memory(entry)
        
        if CacheLevel.DISK in levels:
            success &= await self._set_to_disk(entry)
        
        if CacheLevel.DISTRIBUTED in levels and self.redis_client:
            success &= await self._set_to_redis(entry)
        
        return success
    
    async def invalidate(self, 
                        key: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        persona: Optional[str] = None,
                        workflow: Optional[str] = None):
        """Invalidate cache entries"""
        keys_to_invalidate = set()
        
        if key:
            keys_to_invalidate.add(key)
        
        # Find keys by criteria
        if tags or persona or workflow:
            for cache_key, entry in self.memory_cache.items():
                if tags and any(tag in entry.tags for tag in tags):
                    keys_to_invalidate.add(cache_key)
                if persona and entry.persona == persona:
                    keys_to_invalidate.add(cache_key)
                if workflow and entry.workflow == workflow:
                    keys_to_invalidate.add(cache_key)
        
        # Invalidate from all levels
        for key in keys_to_invalidate:
            await self._invalidate_key(key)
    
    # Memory Cache (L1)
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get from memory cache"""
        if key not in self.memory_cache:
            return None
        
        entry = self.memory_cache[key]
        
        # Check TTL
        if entry.ttl and (datetime.now() - entry.timestamp).seconds > entry.ttl:
            del self.memory_cache[key]
            self.memory_size -= entry.size_bytes
            return None
        
        # Update access info
        entry.access_count += 1
        entry.last_access = datetime.now()
        
        # Move to end for LRU
        if self.config["strategy"] == CacheStrategy.LRU:
            self.memory_cache.move_to_end(key)
        
        return entry.value
    
    async def _set_to_memory(self, entry: CacheEntry) -> bool:
        """Set in memory cache"""
        # Check memory limit
        while self.memory_size + entry.size_bytes > self.memory_limit:
            await self._evict_from_memory()
        
        self.memory_cache[entry.key] = entry
        self.memory_size += entry.size_bytes
        self.stats["writes"]["memory"] += 1
        
        return True
    
    async def _evict_from_memory(self):
        """Evict from memory based on strategy"""
        if not self.memory_cache:
            return
        
        strategy = self.config["strategy"]
        
        if strategy == CacheStrategy.LRU:
            # Remove least recently used
            key, entry = self.memory_cache.popitem(last=False)
        elif strategy == CacheStrategy.LFU:
            # Remove least frequently used
            key = min(self.memory_cache, key=lambda k: self.memory_cache[k].access_count)
            entry = self.memory_cache.pop(key)
        elif strategy == CacheStrategy.FIFO:
            # Remove oldest
            key, entry = self.memory_cache.popitem(last=False)
        else:  # TTL
            # Remove expired or oldest
            now = datetime.now()
            for key, entry in self.memory_cache.items():
                if entry.ttl and (now - entry.timestamp).seconds > entry.ttl:
                    del self.memory_cache[key]
                    self.memory_size -= entry.size_bytes
                    self.stats["evictions"]["memory"] += 1
                    return
            # If no expired, remove oldest
            key, entry = self.memory_cache.popitem(last=False)
        
        self.memory_size -= entry.size_bytes
        self.stats["evictions"]["memory"] += 1
    
    # Disk Cache (L2)
    
    async def _get_from_disk(self, key: str) -> Optional[Any]:
        """Get from disk cache"""
        file_path = self.disk_cache_dir / f"{key}.cache"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                data = await f.read()
                entry = pickle.loads(data)
                
                # Check TTL
                if entry.ttl and (datetime.now() - entry.timestamp).seconds > entry.ttl:
                    file_path.unlink()
                    return None
                
                return entry.value
        except Exception as e:
            logger.error(f"Error reading disk cache: {e}")
            return None
    
    async def _set_to_disk(self, entry: CacheEntry) -> bool:
        """Set in disk cache"""
        file_path = self.disk_cache_dir / f"{entry.key}.cache"
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(pickle.dumps(entry))
            
            self.disk_index[entry.key] = {
                "path": str(file_path),
                "size": entry.size_bytes,
                "timestamp": entry.timestamp
            }
            
            self.stats["writes"]["disk"] += 1
            return True
        except Exception as e:
            logger.error(f"Error writing disk cache: {e}")
            return False
    
    # Redis Cache (L3)
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get from Redis cache"""
        try:
            data = self.redis_client.get(key)
            if data:
                entry = pickle.loads(data)
                return entry.value
        except Exception as e:
            logger.error(f"Error reading Redis cache: {e}")
        
        return None
    
    async def _set_to_redis(self, entry: CacheEntry) -> bool:
        """Set in Redis cache"""
        try:
            data = pickle.dumps(entry)
            self.redis_client.setex(
                entry.key,
                entry.ttl or self.config["default_ttl"],
                data
            )
            self.stats["writes"]["distributed"] += 1
            return True
        except Exception as e:
            logger.error(f"Error writing Redis cache: {e}")
            return False
    
    # Cache Promotion
    
    async def _promote_to_memory(self, key: str, value: Any):
        """Promote entry to memory cache"""
        entry = CacheEntry(
            key=key,
            value=value,
            level=CacheLevel.MEMORY,
            timestamp=datetime.now(),
            size_bytes=len(pickle.dumps(value))
        )
        await self._set_to_memory(entry)
    
    async def _promote_to_disk(self, key: str, value: Any):
        """Promote entry to disk cache"""
        entry = CacheEntry(
            key=key,
            value=value,
            level=CacheLevel.DISK,
            timestamp=datetime.now(),
            size_bytes=len(pickle.dumps(value))
        )
        await self._set_to_disk(entry)
    
    # Cache Invalidation
    
    async def _invalidate_key(self, key: str):
        """Invalidate key from all levels"""
        # Remove from memory
        if key in self.memory_cache:
            entry = self.memory_cache.pop(key)
            self.memory_size -= entry.size_bytes
        
        # Remove from disk
        file_path = self.disk_cache_dir / f"{key}.cache"
        if file_path.exists():
            file_path.unlink()
        
        # Remove from Redis
        if self.redis_client:
            self.redis_client.delete(key)
    
    # Cache Warming
    
    async def warm_cache(self, items: List[Tuple[str, Any, Optional[int]]]):
        """Pre-populate cache with frequently used items"""
        logger.info(f"Warming cache with {len(items)} items")
        
        for key, value, ttl in items:
            await self.set(key, value, ttl)
        
        self.warm_cache_items = items
    
    async def refresh_warm_cache(self):
        """Refresh warm cache items"""
        for key, value, ttl in self.warm_cache_items:
            await self.set(key, value, ttl)
    
    # Persona and Workflow Specific Caching
    
    async def get_persona_cache(self, persona: str) -> Dict[str, Any]:
        """Get all cache entries for a persona"""
        results = {}
        
        for key, entry in self.memory_cache.items():
            if entry.persona == persona:
                results[key] = entry.value
        
        return results
    
    async def get_workflow_cache(self, workflow: str) -> Dict[str, Any]:
        """Get all cache entries for a workflow"""
        results = {}
        
        for key, entry in self.memory_cache.items():
            if entry.workflow == workflow:
                results[key] = entry.value
        
        return results
    
    # Statistics and Monitoring
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_hits = sum(self.stats["hits"].values())
        total_requests = total_hits + self.stats["misses"]
        hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "stats": self.stats,
            "memory": {
                "size_mb": self.memory_size / 1024 / 1024,
                "limit_mb": self.memory_limit / 1024 / 1024,
                "entries": len(self.memory_cache)
            },
            "disk": {
                "entries": len(self.disk_index)
            },
            "redis": {
                "connected": self.redis_client is not None
            }
        }
    
    async def cleanup(self):
        """Clean up expired entries"""
        now = datetime.now()
        
        # Clean memory cache
        keys_to_remove = []
        for key, entry in self.memory_cache.items():
            if entry.ttl and (now - entry.timestamp).seconds > entry.ttl:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            await self._invalidate_key(key)
        
        logger.info(f"Cleaned up {len(keys_to_remove)} expired entries")

# Global cache manager instance
cache_manager = AdvancedCacheManager()

if __name__ == "__main__":
    # Test cache manager
    async def test():
        print("Testing Advanced Cache Manager")
        print("=" * 60)
        
        # Test multi-level caching
        key = cache_manager.generate_key("test", "item1", persona="springfield")
        
        # Set value
        await cache_manager.set(key, {"data": "test value"}, ttl=60)
        
        # Get value (should hit memory)
        value = await cache_manager.get(key)
        print(f"Retrieved: {value}")
        
        # Clear memory cache
        cache_manager.memory_cache.clear()
        cache_manager.memory_size = 0
        
        # Get again (should hit disk)
        value = await cache_manager.get(key)
        print(f"Retrieved from disk: {value}")
        
        # Test invalidation
        await cache_manager.invalidate(persona="springfield")
        value = await cache_manager.get(key)
        print(f"After invalidation: {value}")
        
        # Show stats
        stats = cache_manager.get_stats()
        print(f"\nCache Statistics:")
        print(json.dumps(stats, indent=2))
    
    asyncio.run(test())