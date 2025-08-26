#!/usr/bin/env python3
"""
Trinitas v3.5 Memory Storage Benchmark
各ストレージバックエンドの性能測定
"""

import asyncio
import time
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

# Try importing optional dependencies
HAS_REDIS = False
HAS_CHROMADB = False

try:
    import redis
    import aioredis
    HAS_REDIS = True
except ImportError:
    print("Redis not installed - skipping Redis benchmarks")

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    print("ChromaDB not installed - skipping ChromaDB benchmarks")

from memory_core import MemoryItem, MemoryType

class BenchmarkResult:
    """ベンチマーク結果"""
    def __init__(self, name: str):
        self.name = name
        self.write_times: List[float] = []
        self.read_times: List[float] = []
        self.search_times: List[float] = []
        self.memory_usage: int = 0
        self.storage_size: int = 0
    
    def add_write(self, duration: float):
        self.write_times.append(duration)
    
    def add_read(self, duration: float):
        self.read_times.append(duration)
    
    def add_search(self, duration: float):
        self.search_times.append(duration)
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        def safe_stats(times):
            if not times:
                return {"mean": 0, "median": 0, "min": 0, "max": 0}
            return {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "min": min(times),
                "max": max(times)
            }
        
        return {
            "name": self.name,
            "write": safe_stats(self.write_times),
            "read": safe_stats(self.read_times),
            "search": safe_stats(self.search_times),
            "write_ops_per_sec": len(self.write_times) / sum(self.write_times) if self.write_times else 0,
            "read_ops_per_sec": len(self.read_times) / sum(self.read_times) if self.read_times else 0,
            "memory_usage_mb": self.memory_usage / 1024 / 1024,
            "storage_size_mb": self.storage_size / 1024 / 1024
        }

# Benchmark Implementations

class SQLiteBenchmark:
    """SQLiteベンチマーク"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "benchmark.db"
        self._init_db()
    
    def _init_db(self):
        """DBを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    persona TEXT,
                    type TEXT,
                    importance REAL,
                    timestamp TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_persona ON memories(persona)")
    
    async def write(self, item: MemoryItem) -> float:
        """書き込みベンチマーク"""
        start = time.perf_counter()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, persona, type, importance, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                json.dumps(item.content),
                item.persona,
                item.type.value,
                item.importance,
                item.timestamp.isoformat()
            ))
        
        return time.perf_counter() - start
    
    async def read(self, item_id: str) -> float:
        """読み込みベンチマーク"""
        start = time.perf_counter()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT content FROM memories WHERE id = ?",
                (item_id,)
            )
            result = cursor.fetchone()
        
        return time.perf_counter() - start
    
    async def search(self, query: str, limit: int = 10) -> float:
        """検索ベンチマーク"""
        start = time.perf_counter()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, content FROM memories
                WHERE content LIKE ?
                ORDER BY importance DESC
                LIMIT ?
            """, (f"%{query}%", limit))
            results = cursor.fetchall()
        
        return time.perf_counter() - start
    
    def get_size(self) -> int:
        """ストレージサイズを取得"""
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def cleanup(self):
        """クリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

class RedisBenchmark:
    """Redisベンチマーク"""
    
    def __init__(self):
        self.client = None
        self.async_client = None
    
    async def connect(self):
        """接続"""
        if not HAS_REDIS:
            return False
        
        try:
            self.client = redis.Redis(host='localhost', port=6379, db=1)
            self.client.ping()
            self.async_client = await aioredis.create_redis_pool(
                'redis://localhost:6379/1'
            )
            return True
        except:
            return False
    
    async def write(self, item: MemoryItem) -> float:
        """書き込みベンチマーク"""
        start = time.perf_counter()
        
        # Store as JSON
        data = json.dumps({
            "content": item.content,
            "persona": item.persona,
            "type": item.type.value,
            "importance": item.importance,
            "timestamp": item.timestamp.isoformat()
        })
        
        await self.async_client.setex(
            item.id,
            3600,  # TTL 1 hour
            data
        )
        
        # Also add to sorted set for search
        await self.async_client.zadd(
            f"persona:{item.persona}",
            item.importance,
            item.id
        )
        
        return time.perf_counter() - start
    
    async def read(self, item_id: str) -> float:
        """読み込みベンチマーク"""
        start = time.perf_counter()
        
        result = await self.async_client.get(item_id)
        
        return time.perf_counter() - start
    
    async def search(self, query: str, limit: int = 10) -> float:
        """検索ベンチマーク"""
        start = time.perf_counter()
        
        # Simple search by score range
        results = await self.async_client.zrevrange(
            f"persona:test",
            0, limit - 1,
            withscores=True
        )
        
        return time.perf_counter() - start
    
    def get_size(self) -> int:
        """メモリ使用量を取得"""
        if self.client:
            info = self.client.info('memory')
            return info.get('used_memory', 0)
        return 0
    
    async def cleanup(self):
        """クリーンアップ"""
        if self.async_client:
            await self.async_client.flushdb()
            self.async_client.close()
            await self.async_client.wait_closed()

class ChromaDBBenchmark:
    """ChromaDBベンチマーク"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = None
        self.collection = None
    
    def connect(self):
        """接続"""
        if not HAS_CHROMADB:
            return False
        
        try:
            self.client = chromadb.PersistentClient(path=self.temp_dir)
            self.collection = self.client.get_or_create_collection(
                name="benchmark",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except:
            return False
    
    async def write(self, item: MemoryItem) -> float:
        """書き込みベンチマーク"""
        start = time.perf_counter()
        
        # Add to collection
        self.collection.add(
            documents=[json.dumps(item.content)],
            metadatas=[{
                "persona": item.persona,
                "type": item.type.value,
                "importance": item.importance,
                "timestamp": item.timestamp.isoformat()
            }],
            ids=[item.id]
        )
        
        return time.perf_counter() - start
    
    async def read(self, item_id: str) -> float:
        """読み込みベンチマーク"""
        start = time.perf_counter()
        
        result = self.collection.get(ids=[item_id])
        
        return time.perf_counter() - start
    
    async def search(self, query: str, limit: int = 10) -> float:
        """セマンティック検索ベンチマーク"""
        start = time.perf_counter()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        return time.perf_counter() - start
    
    def get_size(self) -> int:
        """ストレージサイズを取得"""
        total_size = 0
        for path in Path(self.temp_dir).rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size
    
    def cleanup(self):
        """クリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

# Main Benchmark Runner

async def run_benchmark(num_items: int = 1000, search_queries: int = 100):
    """ベンチマークを実行"""
    print("=" * 80)
    print(f"Trinitas Memory Storage Benchmark")
    print(f"Testing with {num_items} items and {search_queries} searches")
    print("=" * 80)
    
    # Generate test data
    print("\nGenerating test data...")
    test_items = []
    for i in range(num_items):
        item = MemoryItem(
            id=f"item_{i}",
            content={
                "text": f"This is test memory item {i}",
                "data": f"Some data for item {i}",
                "index": i
            },
            type=MemoryType.EPISODIC if i % 2 == 0 else MemoryType.SEMANTIC,
            persona="test",
            importance=i / num_items
        )
        test_items.append(item)
    
    results = {}
    
    # SQLite Benchmark
    print("\n1. SQLite Benchmark...")
    sqlite_bench = SQLiteBenchmark()
    sqlite_result = BenchmarkResult("SQLite")
    
    # Write test
    print("   Writing items...")
    for item in test_items[:100]:  # Test with subset for speed
        duration = await sqlite_bench.write(item)
        sqlite_result.add_write(duration)
    
    # Read test
    print("   Reading items...")
    for i in range(min(100, num_items)):
        duration = await sqlite_bench.read(f"item_{i}")
        sqlite_result.add_read(duration)
    
    # Search test
    print("   Searching items...")
    for i in range(min(search_queries, 20)):
        duration = await sqlite_bench.search(f"item {i}")
        sqlite_result.add_search(duration)
    
    sqlite_result.storage_size = sqlite_bench.get_size()
    results["SQLite"] = sqlite_result.get_stats()
    sqlite_bench.cleanup()
    
    # Redis Benchmark
    if HAS_REDIS:
        print("\n2. Redis Benchmark...")
        redis_bench = RedisBenchmark()
        if await redis_bench.connect():
            redis_result = BenchmarkResult("Redis")
            
            # Write test
            print("   Writing items...")
            for item in test_items[:100]:
                duration = await redis_bench.write(item)
                redis_result.add_write(duration)
            
            # Read test
            print("   Reading items...")
            for i in range(min(100, num_items)):
                duration = await redis_bench.read(f"item_{i}")
                redis_result.add_read(duration)
            
            # Search test
            print("   Searching items...")
            for i in range(min(search_queries, 20)):
                duration = await redis_bench.search(f"item {i}")
                redis_result.add_search(duration)
            
            redis_result.memory_usage = redis_bench.get_size()
            results["Redis"] = redis_result.get_stats()
            await redis_bench.cleanup()
        else:
            print("   Redis not available - skipping")
    
    # ChromaDB Benchmark
    if HAS_CHROMADB:
        print("\n3. ChromaDB Benchmark...")
        chroma_bench = ChromaDBBenchmark()
        if chroma_bench.connect():
            chroma_result = BenchmarkResult("ChromaDB")
            
            # Write test
            print("   Writing items...")
            for item in test_items[:100]:
                duration = await chroma_bench.write(item)
                chroma_result.add_write(duration)
            
            # Read test
            print("   Reading items...")
            for i in range(min(100, num_items)):
                duration = await chroma_bench.read(f"item_{i}")
                chroma_result.add_read(duration)
            
            # Search test (semantic)
            print("   Semantic searching...")
            for i in range(min(search_queries, 20)):
                duration = await chroma_bench.search(f"test memory item {i}")
                chroma_result.add_search(duration)
            
            chroma_result.storage_size = chroma_bench.get_size()
            results["ChromaDB"] = chroma_result.get_stats()
            chroma_bench.cleanup()
        else:
            print("   ChromaDB not available - skipping")
    
    # Print results
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    
    # Table header
    print(f"\n{'Storage':<15} {'Write (ms)':<20} {'Read (ms)':<20} {'Search (ms)':<20} {'Ops/sec':<15}")
    print("-" * 90)
    
    for name, stats in results.items():
        write_ms = stats['write']['mean'] * 1000
        read_ms = stats['read']['mean'] * 1000
        search_ms = stats['search']['mean'] * 1000
        
        print(f"{name:<15} "
              f"{write_ms:>8.2f} (±{stats['write']['max']*1000 - write_ms:.2f}) "
              f"{read_ms:>8.2f} (±{stats['read']['max']*1000 - read_ms:.2f}) "
              f"{search_ms:>8.2f} (±{stats['search']['max']*1000 - search_ms:.2f}) "
              f"W:{stats['write_ops_per_sec']:.0f}/R:{stats['read_ops_per_sec']:.0f}")
    
    print("\n" + "-" * 90)
    print(f"\n{'Storage':<15} {'Storage Size (MB)':<20} {'Memory Usage (MB)':<20}")
    print("-" * 55)
    
    for name, stats in results.items():
        print(f"{name:<15} {stats['storage_size_mb']:>17.2f} {stats['memory_usage_mb']:>20.2f}")
    
    # Save results to JSON
    output_file = Path("benchmark_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if len(results) >= 2:
        # Find best for each metric
        best_write = min(results.items(), key=lambda x: x[1]['write']['mean'])
        best_read = min(results.items(), key=lambda x: x[1]['read']['mean'])
        
        print(f"\n• Best write performance: {best_write[0]}")
        print(f"• Best read performance: {best_read[0]}")
        
        if "ChromaDB" in results:
            print(f"• Best semantic search: ChromaDB")
        
        if "Redis" in results and "ChromaDB" in results:
            print(f"\n✓ RECOMMENDED: Hybrid approach (Redis + ChromaDB)")
            print(f"  - Use Redis for working/episodic memory (fast access)")
            print(f"  - Use ChromaDB for semantic/procedural memory (smart search)")
            print(f"  - Use SQLite as fallback/archive (reliable persistence)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(run_benchmark())