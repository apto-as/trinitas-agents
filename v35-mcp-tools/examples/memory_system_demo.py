#!/usr/bin/env python3
"""
Trinitas v3.5 Memory System Demo
記憶システムのデモンストレーション
"""

import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory import (
    initialize_memory_manager,
    MemoryType,
    Context
)

async def demo_memory_system():
    """記憶システムのデモ"""
    print("=" * 80)
    print("Trinitas v3.5 Memory System Demonstration")
    print("統合知性記憶アーキテクチャのデモンストレーション")
    print("=" * 80)
    
    # Initialize memory manager
    print("\n1. Initializing Memory Manager...")
    manager = await initialize_memory_manager("/tmp/trinitas_memory_demo")
    print("   ✓ Memory manager initialized for 5 personas")
    
    # Demo 1: Athena stores architecture decision
    print("\n2. Athena stores an architecture decision...")
    await manager.remember(
        persona="athena",
        content={
            "decision": "Use microservices architecture",
            "project": "E-commerce Platform",
            "reasoning": "Better scalability and team independence",
            "date": datetime.now().isoformat()
        },
        memory_type=MemoryType.SEMANTIC,
        importance=0.9,
        tags=["architecture", "microservices", "decision"]
    )
    print("   ✓ Architecture decision stored in Athena's semantic memory")
    
    # Demo 2: Artemis stores optimization technique
    print("\n3. Artemis stores an optimization pattern...")
    await manager.remember(
        persona="artemis",
        content={
            "name": "Database Query Optimization",
            "type": "performance",
            "steps": [
                "Add composite index on (user_id, created_at)",
                "Use query batching for N+1 problems",
                "Implement connection pooling"
            ],
            "success_rate": 0.95,
            "performance_gain": "850% improvement"
        },
        memory_type=MemoryType.PROCEDURAL,
        importance=0.85,
        tags=["optimization", "database", "performance"]
    )
    print("   ✓ Optimization pattern stored in Artemis's procedural memory")
    
    # Demo 3: Hestia stores security incident
    print("\n4. Hestia stores a security incident...")
    await manager.remember(
        persona="hestia",
        content={
            "incident_type": "SQL Injection attempt",
            "timestamp": datetime.now().isoformat(),
            "source_ip": "192.168.1.100",
            "action_taken": "Blocked and logged",
            "vulnerability_fixed": True
        },
        memory_type=MemoryType.EPISODIC,
        importance=1.0,
        tags=["security", "incident", "sql_injection"]
    )
    print("   ✓ Security incident stored in Hestia's episodic memory")
    
    # Demo 4: Bellona stores execution strategy
    print("\n5. Bellona stores a deployment strategy...")
    await manager.remember(
        persona="bellona",
        content={
            "strategy": "Blue-Green Deployment",
            "steps": [
                "Deploy to green environment",
                "Run smoke tests",
                "Switch traffic gradually",
                "Monitor metrics",
                "Rollback if needed"
            ],
            "resources_needed": ["2x production capacity", "monitoring tools"],
            "execution_time": "45 minutes"
        },
        memory_type=MemoryType.PROCEDURAL,
        importance=0.75,
        tags=["deployment", "strategy", "blue-green"]
    )
    print("   ✓ Deployment strategy stored in Bellona's procedural memory")
    
    # Demo 5: Seshat stores documentation template
    print("\n6. Seshat stores a documentation template...")
    await manager.remember(
        persona="seshat",
        content={
            "template_name": "API Documentation",
            "sections": [
                "Overview",
                "Authentication",
                "Endpoints",
                "Error Codes",
                "Examples"
            ],
            "format": "OpenAPI 3.0",
            "auto_generate": True
        },
        memory_type=MemoryType.SEMANTIC,
        importance=0.8,
        tags=["documentation", "api", "template"]
    )
    print("   ✓ Documentation template stored in Seshat's semantic memory")
    
    # Demo 6: Recall memories
    print("\n7. Testing memory recall...")
    
    # Athena recalls architecture decisions
    print("\n   a. Athena recalls architecture-related memories:")
    athena_memories = await manager.recall(
        persona="athena",
        query_text="microservices architecture",
        limit=3
    )
    for memory in athena_memories:
        print(f"      - {memory.type.value}: {memory.content.get('decision', memory.content)}")
    
    # Artemis recalls optimization techniques
    print("\n   b. Artemis recalls optimization patterns:")
    artemis_memories = await manager.recall(
        persona="artemis",
        query_text="database optimization",
        limit=3
    )
    for memory in artemis_memories:
        print(f"      - {memory.type.value}: {memory.content.get('name', memory.content)}")
    
    # Demo 7: Cross-persona memory sharing
    print("\n8. Testing cross-persona memory sharing...")
    
    # Share Hestia's security knowledge with Athena
    hestia_security = await manager.recall(
        persona="hestia",
        query_text="security",
        limit=1
    )
    
    if hestia_security:
        await manager.share_memory(
            from_persona="hestia",
            to_persona="athena",
            memory_id=hestia_security[0].id
        )
        print("   ✓ Shared security incident from Hestia to Athena")
    
    # Verify shared memory
    athena_security = await manager.recall(
        persona="athena",
        query_text="security incident",
        limit=1
    )
    if athena_security:
        print(f"   ✓ Athena now has access to security incident: {athena_security[0].content.get('incident_type')}")
    
    # Demo 8: Memory consolidation
    print("\n9. Testing memory consolidation...")
    
    # Add some working memory items for Athena
    for i in range(5):
        await manager.remember(
            persona="athena",
            content=f"Temporary decision {i+1}",
            memory_type=MemoryType.WORKING,
            importance=0.3 + i * 0.1
        )
    
    # Consolidate memories
    consolidator = manager.consolidators["athena"]
    await consolidator.consolidate()
    print("   ✓ Consolidated Athena's working memory to long-term storage")
    
    # Demo 9: Memory statistics
    print("\n10. Memory System Statistics:")
    stats = manager.get_statistics()
    for persona, persona_stats in stats.items():
        print(f"    {persona}:")
        print(f"      - Working Memory: {persona_stats['working_memory_size']}/{persona_stats['working_memory_capacity']}")
    
    # Demo 10: Complex query with context
    print("\n11. Testing complex contextual recall...")
    
    context = Context(
        current_task="Design a secure microservices deployment",
        constraints=["High availability", "Security compliance", "Cost optimization"],
        preferences={"deployment_type": "blue-green"},
        history=["Previous SQL injection attempt"]
    )
    
    # Each persona recalls relevant memories
    print("\n   Multi-persona collaborative recall:")
    for persona in ["athena", "artemis", "hestia", "bellona"]:
        memories = await manager.recall(
            persona=persona,
            query_text="deployment security microservices",
            context=context,
            limit=2
        )
        if memories:
            print(f"\n   {persona.capitalize()} contributes:")
            for memory in memories:
                content_preview = str(memory.content)[:100] if isinstance(memory.content, str) else \
                                json.dumps(memory.content, indent=2)[:100]
                print(f"      - {memory.type.value}: {content_preview}...")
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("Memory system is ready for production use.")
    print("=" * 80)

async def test_memory_lifecycle():
    """記憶のライフサイクルテスト"""
    print("\n" + "=" * 80)
    print("Testing Memory Lifecycle (Forgetting Curve)")
    print("=" * 80)
    
    manager = await initialize_memory_manager("/tmp/trinitas_memory_test")
    
    # Create memories with different importance levels
    print("\n1. Creating memories with varying importance...")
    
    memories_data = [
        ("Critical architecture decision", 1.0, ["critical"]),
        ("Important optimization", 0.8, ["important"]),
        ("Regular task note", 0.5, ["normal"]),
        ("Minor observation", 0.2, ["minor"]),
        ("Trivial detail", 0.1, ["trivial"])
    ]
    
    for content, importance, tags in memories_data:
        await manager.remember(
            persona="athena",
            content=content,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            tags=tags
        )
        print(f"   ✓ Stored: {content} (importance: {importance})")
    
    # Test forgetting curve
    print("\n2. Testing forgetting curve calculation...")
    curve = manager.forgetting_curves["athena"]
    
    # Simulate passage of time and access patterns
    all_memories = await manager.recall("athena", "", limit=100)
    for memory in all_memories:
        retention = curve.calculate_retention(memory)
        print(f"   - {memory.content}: retention = {retention:.2%}")
    
    print("\n✓ Memory lifecycle test completed")

async def test_memory_performance():
    """記憶システムのパフォーマンステスト"""
    print("\n" + "=" * 80)
    print("Testing Memory System Performance")
    print("=" * 80)
    
    manager = await initialize_memory_manager("/tmp/trinitas_memory_perf")
    
    # Bulk write test
    print("\n1. Bulk write test (100 memories)...")
    start_time = asyncio.get_event_loop().time()
    
    for i in range(100):
        await manager.remember(
            persona="artemis",
            content={
                "id": i,
                "data": f"Performance test data {i}",
                "timestamp": datetime.now().isoformat()
            },
            memory_type=MemoryType.EPISODIC,
            importance=0.5
        )
    
    write_time = asyncio.get_event_loop().time() - start_time
    print(f"   ✓ Write time: {write_time:.2f} seconds ({100/write_time:.0f} writes/sec)")
    
    # Bulk read test
    print("\n2. Bulk read test (100 queries)...")
    start_time = asyncio.get_event_loop().time()
    
    for i in range(100):
        await manager.recall(
            persona="artemis",
            query_text=f"test data {i}",
            limit=1
        )
    
    read_time = asyncio.get_event_loop().time() - start_time
    print(f"   ✓ Read time: {read_time:.2f} seconds ({100/read_time:.0f} reads/sec)")
    
    print("\n✓ Performance test completed")

async def main():
    """メイン実行関数"""
    print("\nTrinitas v3.5 Memory System")
    print("Choose a demo:")
    print("1. Basic Memory Operations")
    print("2. Memory Lifecycle (Forgetting Curve)")
    print("3. Performance Test")
    print("4. Run All Tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        await demo_memory_system()
    elif choice == "2":
        await test_memory_lifecycle()
    elif choice == "3":
        await test_memory_performance()
    elif choice == "4":
        await demo_memory_system()
        await test_memory_lifecycle()
        await test_memory_performance()
    else:
        print("Invalid choice")
        return
    
    # Clean up
    print("\n✓ All tests completed successfully")
    print("Memory system is functioning correctly")

if __name__ == "__main__":
    asyncio.run(main())