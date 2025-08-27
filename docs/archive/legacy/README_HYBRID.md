# Trinitas v3.5 Hybrid Memory System
## Redis + ChromaDB + SQLite 統合実装ガイド

### 🚀 Quick Start

```bash
# 1. セットアップスクリプトを実行
cd v35-mcp-tools
./setup_hybrid.sh

# 2. 動作確認
python examples/memory_system_demo.py
```

### 📋 Prerequisites

- Docker Desktop
- Python 3.8+
- 1GB+ free disk space

### 🏗️ Architecture

```
┌────────────────────────────────────┐
│      Trinitas Memory System        │
├────────────────────────────────────┤
│                                    │
│  ┌──────────┐    ┌──────────┐    │
│  │  Redis   │    │ ChromaDB │    │
│  │ (Fast)   │    │ (Smart)  │    │
│  └──────────┘    └──────────┘    │
│         ↓              ↓          │
│  ┌────────────────────────────┐  │
│  │    SQLite (Fallback)       │  │
│  └────────────────────────────┘  │
└────────────────────────────────────┘
```

### 📦 Memory Type Routing

| Memory Type | Primary | Cache | Archive |
|-------------|---------|-------|---------|
| Working | Redis (1h) | - | SQLite |
| Episodic | Redis (24h) | - | SQLite |
| Semantic | ChromaDB | Redis (5m) | SQLite |
| Procedural | ChromaDB | Redis (5m) | SQLite |

### 🔧 Manual Setup

#### 1. Start Redis

```bash
docker-compose up -d redis
```

#### 2. Install Dependencies

```bash
pip install redis aioredis chromadb sentence-transformers
```

#### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env as needed
```

#### 4. Test Installation

```python
from src.memory.enhanced_manager import get_enhanced_memory_manager

async def test():
    manager = await get_enhanced_memory_manager()
    
    # Store memory
    await manager.remember(
        persona="athena",
        content="Test memory",
        importance=0.8
    )
    
    # Recall memory
    memories = await manager.recall(
        persona="athena",
        query_text="test"
    )
    
    print(f"Found {len(memories)} memories")
```

### 🔍 Semantic Search Examples

#### Similar Problem Search

```python
# Find similar errors/problems
results = await manager.semantic_search(
    query_text="database timeout error",
    personas=["hestia"],
    min_similarity=0.7
)

# Results include:
# - "MySQL connection pool exhausted"
# - "PostgreSQL deadlock detected"
# - "Redis connection timeout"
```

#### Cross-Persona Knowledge

```python
# Get multi-perspective insights
results = await manager.semantic_search(
    query_text="API optimization",
    personas=["athena", "artemis", "hestia"]
)

# Athena: "RESTful API design patterns"
# Artemis: "Response caching strategies"
# Hestia: "API rate limiting for security"
```

### 📊 Performance Benchmarks

| Operation | SQLite | Hybrid | Improvement |
|-----------|--------|--------|-------------|
| Write | 850 ops/s | 8,500 ops/s | 10x |
| Read | 4,200 ops/s | 12,000 ops/s | 2.8x |
| Semantic Search | N/A | 50ms | ∞ |

### 🔄 Migration from SQLite

```bash
# Dry run first
python scripts/migrate_to_hybrid.py --dry-run

# Perform migration with backup
python scripts/migrate_to_hybrid.py

# Restore if needed
python scripts/migrate_to_hybrid.py --restore
```

### 🛠️ Troubleshooting

#### Redis Connection Failed

```bash
# Check if Redis is running
docker-compose ps

# View Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### ChromaDB Issues

```python
# Reset ChromaDB
import shutil
shutil.rmtree("/tmp/trinitas_chromadb")

# Reinitialize
from src.memory.enhanced_manager import get_enhanced_memory_manager
await get_enhanced_memory_manager()
```

#### Fallback to SQLite

The system automatically falls back to SQLite if Redis or ChromaDB are unavailable:

```python
# Check backend status
manager = await get_enhanced_memory_manager()
health = await manager.health_check()
print(health)
# {
#   "status": "degraded",
#   "backends": {
#     "redis": "unhealthy",
#     "chromadb": "healthy",
#     "sqlite": "healthy"
#   }
# }
```

### 📈 Monitoring

#### Memory Statistics

```python
stats = await manager.get_statistics()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
print(f"Total memories: {stats['backend']['total_items']}")
```

#### Redis Commander (Optional)

```bash
# Start Redis Commander
docker-compose --profile debug up -d redis-commander

# Open browser
open http://localhost:8081
```

### 🧪 Testing

```bash
# Run unit tests
pytest tests/test_hybrid_backend.py

# Run integration tests
pytest tests/test_memory_integration.py

# Run performance benchmarks
python src/memory/benchmark.py
```

### 🚫 Stopping Services

```bash
# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

### 📝 Environment Variables

Key configuration options in `.env`:

```bash
# Enable/disable backends
REDIS_ENABLED=true
CHROMADB_ENABLED=true

# Performance tuning
REDIS_TTL_WORKING=3600    # 1 hour
BATCH_SIZE=100
CONNECTION_POOL_SIZE=20

# Fallback behavior
AUTO_FALLBACK=true
HEALTH_CHECK_INTERVAL=30  # seconds
```

### 🎯 Best Practices

1. **Use semantic search for natural queries**
   ```python
   # Good: Natural language
   await manager.semantic_search("how to optimize database")
   
   # Avoid: Exact matching
   await manager.recall("optimize", use_semantic=False)
   ```

2. **Set appropriate importance levels**
   ```python
   # Critical decisions
   await manager.remember(content, importance=0.9)
   
   # Regular notes
   await manager.remember(content, importance=0.5)
   ```

3. **Tag memories for better organization**
   ```python
   await manager.remember(
       content="Solution",
       tags=["bug-fix", "database", "critical"]
   )
   ```

### 📚 Further Reading

- [Memory System Design](docs/MEMORY_SYSTEM_DESIGN.md)
- [Semantic Search Use Cases](docs/SEMANTIC_SEARCH_USE_CASES.md)
- [Phase 2 Implementation Plan](docs/PHASE2_IMPLEMENTATION_PLAN.md)

---
*Trinitas v3.5 - Intelligent Memory for Long-term Projects*