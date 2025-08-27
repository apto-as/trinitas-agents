# Trinitas v3.5 Memory System - Phase 2 Implementation Plan
## ハイブリッドバックエンド統合実装計画

### Executive Summary

フェーズ2では、SQLiteベースの記憶システムをRedis + ChromaDB + SQLiteのハイブリッドアーキテクチャへ移行します。これにより、高速アクセス、セマンティック検索、信頼性のある永続化を実現します。

## 1. Architecture Decision

### 1.1 選択したアーキテクチャ: **Hybrid Approach**

```
理由:
✅ 最高のパフォーマンス (Redis: 100k ops/sec)
✅ 優れたセマンティック検索 (ChromaDB)
✅ 信頼性のあるフォールバック (SQLite)
✅ 段階的移行が可能
✅ Claude Code環境に適応可能
```

### 1.2 メモリタイプ別ストレージ割り当て

| Memory Type | Primary Storage | Cache Layer | Archive |
|-------------|----------------|-------------|---------|
| Working | Redis (1h TTL) | - | SQLite |
| Episodic | Redis (24h TTL) | - | SQLite (7d+) |
| Semantic | ChromaDB | Redis (5m TTL) | SQLite |
| Procedural | ChromaDB | Redis (5m TTL) | SQLite |

## 2. Implementation Roadmap

### Week 1: Backend Infrastructure (今週)

#### Day 1-2: Environment Setup
```bash
# Docker Compose設定
cat > docker-compose.yml << EOF
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # ChromaDB runs embedded, no container needed

volumes:
  redis_data:
EOF

# Dependencies installation
pip install redis aioredis chromadb sentence-transformers
```

#### Day 3-4: Backend Implementation
- [x] RedisBackend class implementation
- [x] ChromaDBBackend class implementation  
- [x] HybridMemoryBackend orchestrator
- [x] Connection pooling & health checks

#### Day 5: Testing & Benchmarking
- [x] Unit tests for each backend
- [x] Integration tests for hybrid operations
- [x] Performance benchmarking
- [ ] Load testing (10K+ items)

### Week 2: Data Migration & Integration

#### Day 6-7: Migration Tools
```python
# Migration script from SQLite to Hybrid
async def migrate_to_hybrid():
    # 1. Read all SQLite data
    sqlite_manager = TrinitasMemoryManager("/tmp/trinitas_memory")
    
    # 2. Initialize hybrid backend
    hybrid = create_hybrid_backend({
        "redis_enabled": True,
        "chromadb_enabled": True
    })
    await hybrid.initialize()
    
    # 3. Migrate persona by persona
    for persona in ["athena", "artemis", "hestia", "bellona", "seshat"]:
        memories = await sqlite_manager.recall(persona, "", limit=10000)
        
        for memory in memories:
            await hybrid.store(memory)
    
    print(f"Migrated {len(memories)} memories")
```

#### Day 8-9: Memory Manager Integration
```python
# Update MemoryManager to use hybrid backend
class EnhancedMemoryManager(TrinitasMemoryManager):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__()
        
        # Use hybrid backend instead of SQLite
        self.backend = create_hybrid_backend(config)
        
    async def store(self, item: MemoryItem):
        # Delegate to hybrid backend
        return await self.backend.store(item)
    
    async def retrieve(self, query: Query):
        # Use intelligent routing
        return await self.backend.search(query, self.current_persona)
```

#### Day 10: Fallback Mechanisms
- [ ] Auto-fallback from Redis to SQLite
- [ ] ChromaDB failure handling
- [ ] Graceful degradation testing

### Week 3: MCP Tools Enhancement

#### Day 11-12: Enhanced MCP Tools
```python
# New MCP tools for advanced memory operations
@Tool(
    name="trinitas_semantic_search",
    description="Semantic search across all memories"
)
async def semantic_search_tool(
    query: str,
    personas: Optional[List[str]] = None,
    min_similarity: float = 0.7
) -> List[Dict]:
    """ChromaDBを活用したセマンティック検索"""
    backend = get_hybrid_backend()
    
    # Use ChromaDB for semantic search
    results = await backend.chromadb.search(
        Query(text=query, threshold=min_similarity),
        personas=personas
    )
    
    return format_results(results)

@Tool(
    name="trinitas_memory_analytics",
    description="Analyze memory patterns and usage"
)
async def memory_analytics_tool() -> Dict:
    """記憶パターンの分析"""
    backend = get_hybrid_backend()
    stats = await backend.get_stats()
    
    # Add analytics
    stats["patterns"] = await analyze_memory_patterns()
    stats["recommendations"] = await get_optimization_recommendations()
    
    return stats
```

#### Day 13-14: Testing & Documentation
- [ ] Update all MCP tool tests
- [ ] API documentation update
- [ ] Usage examples

### Week 4: Optimization & Deployment

#### Day 15-16: Performance Optimization
```yaml
optimization_targets:
  redis:
    - Connection pooling (min: 5, max: 20)
    - Pipeline batching (batch_size: 100)
    - Compression for large items
    
  chromadb:
    - Async embedding generation
    - Index optimization (HNSW parameters)
    - Collection sharding by persona
    
  cache:
    - LRU eviction policy
    - Preemptive cache warming
    - Query result caching
```

#### Day 17-18: Production Readiness
```python
# Health check endpoint
async def health_check():
    status = {
        "redis": await check_redis(),
        "chromadb": await check_chromadb(),
        "sqlite": await check_sqlite(),
        "memory_usage": get_memory_usage(),
        "performance": await benchmark_latency()
    }
    
    return {
        "healthy": all(status.values()),
        "details": status
    }

# Monitoring metrics
async def collect_metrics():
    return {
        "ops_per_second": calculate_ops(),
        "cache_hit_rate": get_cache_stats(),
        "memory_distribution": get_memory_distribution(),
        "search_latency_p99": get_latency_percentile(99)
    }
```

#### Day 19-20: Deployment Guide
- [ ] Docker deployment instructions
- [ ] Configuration management
- [ ] Backup & restore procedures
- [ ] Monitoring setup

## 3. Configuration Management

### 3.1 Environment Variables
```bash
# .env.example
MEMORY_BACKEND=hybrid

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_TTL_WORKING=3600
REDIS_TTL_EPISODIC=86400

# ChromaDB Configuration
CHROMADB_PATH=/var/lib/trinitas/chromadb
CHROMADB_MODEL=all-MiniLM-L6-v2

# SQLite Configuration
SQLITE_PATH=/var/lib/trinitas/sqlite
SQLITE_ARCHIVE_DAYS=7

# Performance
CACHE_SIZE_MB=100
BATCH_SIZE=100
ASYNC_WRITES=true
```

### 3.2 Dynamic Configuration
```yaml
# config/memory.yaml
memory:
  backend: hybrid
  
  routing:
    working: [redis, sqlite]
    episodic: [redis, sqlite]
    semantic: [chromadb, sqlite]
    procedural: [chromadb, sqlite]
  
  performance:
    cache_ttl: 300
    batch_size: 100
    connection_pool_size: 20
    
  fallback:
    redis_failure: sqlite
    chromadb_failure: sqlite
    auto_retry: true
    retry_delay: 1000  # ms
```

## 4. Testing Strategy

### 4.1 Unit Tests
```python
# test_hybrid_backend.py
async def test_redis_fallback():
    """Redisが利用不可の場合のフォールバックテスト"""
    config = HybridConfig(redis_enabled=False)
    backend = HybridMemoryBackend(config)
    
    # Should fallback to SQLite
    item = create_test_memory()
    assert await backend.store(item)
    
    retrieved = await backend.retrieve(item.id)
    assert retrieved == item

async def test_semantic_search():
    """セマンティック検索のテスト"""
    backend = create_hybrid_backend()
    
    # Store semantically related items
    await backend.store(create_memory("Python programming"))
    await backend.store(create_memory("Python development"))
    await backend.store(create_memory("Java programming"))
    
    # Search should find Python-related items
    results = await backend.search(
        Query(text="Python coding", limit=2),
        persona="athena"
    )
    
    assert len(results) == 2
    assert all("Python" in r.content for r in results)
```

### 4.2 Load Tests
```python
# test_load.py
async def test_high_load():
    """高負荷テスト (10,000 items)"""
    backend = create_hybrid_backend()
    
    # Concurrent writes
    start = time.time()
    tasks = [
        backend.store(create_random_memory(i))
        for i in range(10000)
    ]
    await asyncio.gather(*tasks)
    write_time = time.time() - start
    
    print(f"Write throughput: {10000/write_time:.0f} ops/sec")
    
    # Concurrent reads
    start = time.time()
    tasks = [
        backend.search(Query(text=f"query {i}", limit=5), "test")
        for i in range(1000)
    ]
    await asyncio.gather(*tasks)
    read_time = time.time() - start
    
    print(f"Read throughput: {1000/read_time:.0f} ops/sec")
```

## 5. Migration Checklist

### Pre-Migration
- [ ] Backup existing SQLite databases
- [ ] Document current memory statistics
- [ ] Test hybrid backend in staging
- [ ] Prepare rollback plan

### Migration Steps
1. [ ] Deploy Redis container
2. [ ] Initialize ChromaDB
3. [ ] Run migration script
4. [ ] Verify data integrity
5. [ ] Switch to hybrid backend
6. [ ] Monitor for 24 hours

### Post-Migration
- [ ] Performance benchmarking
- [ ] Update documentation
- [ ] Train team on new features
- [ ] Collect user feedback

## 6. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Redis connection failure | Medium | High | Auto-fallback to SQLite, connection retry |
| ChromaDB slow indexing | Low | Medium | Async indexing, batch operations |
| Data migration errors | Low | High | Incremental migration, validation checks |
| Memory overflow | Medium | Medium | TTL policies, automatic pruning |
| Performance degradation | Low | High | Caching, query optimization |

## 7. Success Metrics

### Performance KPIs
- Write latency: < 10ms (p99)
- Read latency: < 5ms (p99)
- Semantic search: < 50ms (p99)
- Cache hit rate: > 80%
- Memory usage: < 1GB for 100K items

### Functional KPIs
- Zero data loss during migration
- 100% backward compatibility
- Semantic search accuracy: > 90%
- Cross-persona sharing: < 100ms

## 8. Next Steps (Phase 3 Preview)

### Advanced Features
1. **Vector Embeddings Optimization**
   - Custom embedding models per persona
   - Incremental index updates
   - Dimensionality reduction

2. **Distributed Memory**
   - Multi-instance synchronization
   - Consensus protocols
   - Partition tolerance

3. **AI-Powered Memory Management**
   - Automatic importance scoring
   - Predictive caching
   - Anomaly detection

4. **Memory Visualization**
   - Knowledge graph rendering
   - Memory timeline view
   - Persona interaction mapping

## Conclusion

Phase 2 implementation will transform Trinitas memory system from a simple SQLite-based storage to a sophisticated hybrid architecture combining:

- **Speed**: Redis for microsecond access
- **Intelligence**: ChromaDB for semantic understanding  
- **Reliability**: SQLite for guaranteed persistence

This architecture ensures Trinitas can handle long-term projects with millions of memories while maintaining sub-second response times and intelligent recall capabilities.

---
*Implementation Plan by Trinitas-Core v3.5 - Memory Architecture Team*