#!/usr/bin/env python3
"""
Trinitas v3.5 - Real Delegation Test with Local LLM
Tests actual delegation decisions and execution
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    CognitiveComplexity
)
from delegation.delegation_engine import (
    CognitiveDelegationEngine,
    ExecutorType
)


async def test_real_delegation():
    """Test actual delegation with real Local LLM"""
    print("🧪 Testing Real Delegation with Local LLM")
    print("=" * 50)
    
    # Initialize delegation engine
    engine = CognitiveDelegationEngine()
    await engine.initialize()
    
    # Test various task types
    test_tasks = [
        # Simple mechanical task - should go to Local
        TaskRequest(
            id="real-001",
            type="file_search",
            description="List all Python files in the current directory",
            estimated_tokens=1000,
            required_tools=["file_operations"],
            complexity=None  # Let engine determine
        ),
        
        # Heavy analytical task - should go to Local
        TaskRequest(
            id="real-002",
            type="pattern_search",
            description="Find all usage patterns of async functions in 100K lines of code",
            estimated_tokens=50000,
            required_tools=["file_operations", "mcp_server"],
            complexity=None
        ),
        
        # Creative task - should go to Claude
        TaskRequest(
            id="real-003",
            type="algorithm_design",
            description="Design a novel caching algorithm for distributed systems",
            estimated_tokens=10000,
            required_tools=[],
            complexity=None
        ),
        
        # Strategic task - should go to Claude
        TaskRequest(
            id="real-004",
            type="architecture_design",
            description="Design microservices architecture for e-commerce platform",
            estimated_tokens=20000,
            required_tools=["mcp_server"],
            complexity=None
        ),
        
        # Heavy + Complex task - should go to Hybrid
        TaskRequest(
            id="real-005",
            type="system_design",
            description="Analyze 500K lines of legacy code and design complete refactoring strategy",
            estimated_tokens=200000,
            required_tools=["file_operations", "mcp_server"],
            complexity=None
        )
    ]
    
    print("\n📊 Testing Delegation Decisions:\n")
    
    for task in test_tasks:
        # Get delegation decision
        decision = await engine.decide_delegation(task)
        
        print(f"Task: {task.id} ({task.type})")
        print(f"  Description: {task.description[:50]}...")
        print(f"  Tokens: {task.estimated_tokens:,}")
        print(f"  Complexity: {task.complexity.name if task.complexity else 'Unknown'}")
        print(f"  ➡️  Decision: {decision.executor.value}")
        print(f"  Reason: {decision.reason}")
        print(f"  Confidence: {decision.confidence:.0%}")
        
        # If it's a Local task, try to execute it
        if decision.executor == ExecutorType.LOCAL:
            print(f"  🚀 Executing on Local LLM...")
            try:
                response = await engine.execute_task(task, decision)
                if response.errors:
                    print(f"  ❌ Execution errors: {response.errors}")
                else:
                    print(f"  ✅ Executed successfully")
                    print(f"     Tokens used: {response.tokens_used}")
                    print(f"     Duration: {response.duration:.2f}s")
            except Exception as e:
                print(f"  ⚠️  Execution failed: {e}")
        
        print()
    
    # Show delegation statistics
    stats = engine.get_delegation_stats()
    print("📈 Delegation Statistics:")
    print(f"  Total tasks analyzed: {stats['total_tasks']}")
    print(f"  Delegated to Local: {stats['by_executor']['local']}")
    print(f"  Delegated to Claude: {stats['by_executor']['claude']}")
    print(f"  Delegated to Hybrid: {stats['by_executor']['hybrid']}")
    print(f"  Local context used: {stats['context_usage']['local']:,} tokens")


async def test_context_pressure():
    """Test how context pressure affects delegation"""
    print("\n🔄 Testing Context Pressure Effects")
    print("=" * 50)
    
    engine = CognitiveDelegationEngine()
    await engine.initialize()
    
    # Test reasoning task with different context pressures
    reasoning_task = TaskRequest(
        id="pressure-001",
        type="debug_analysis",
        description="Debug complex memory leak in production system",
        estimated_tokens=15000,
        required_tools=["file_operations", "bash"]
    )
    
    # Test with low context pressure
    engine.context_state.claude_usage = 10000  # 5% usage
    decision_low = await engine.decide_delegation(reasoning_task)
    print(f"\nWith LOW Claude pressure (5%):")
    print(f"  Decision: {decision_low.executor.value}")
    print(f"  Reason: {decision_low.reason}")
    
    # Test with high context pressure
    engine.context_state.claude_usage = 150000  # 75% usage
    decision_high = await engine.decide_delegation(reasoning_task)
    print(f"\nWith HIGH Claude pressure (75%):")
    print(f"  Decision: {decision_high.executor.value}")
    print(f"  Reason: {decision_high.reason}")
    
    # Reset for next test
    engine.context_state.claude_usage = 0


async def test_real_execution():
    """Test actual execution on Local LLM"""
    print("\n💻 Testing Real Execution on Local LLM")
    print("=" * 50)
    
    connector = LocalLLMConnector()
    await connector.initialize()
    
    # Create a real task
    task = TaskRequest(
        id="exec-001",
        type="analysis",
        description="""Analyze this Python function and explain what it does:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

Provide a brief explanation and identify any performance issues.""",
        estimated_tokens=500,
        required_tools=[],
        complexity=CognitiveComplexity.ANALYTICAL
    )
    
    print(f"\n📝 Task: {task.description[:100]}...")
    print(f"\n🚀 Executing on Local LLM...")
    
    response = await connector.execute(task)
    
    if response.errors:
        print(f"❌ Errors: {response.errors}")
    else:
        print(f"✅ Success!")
        print(f"\n📊 Metrics:")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Duration: {response.duration:.2f}s")
        print(f"  Confidence: {response.confidence:.0%}")
        print(f"\n📤 Response:")
        print(f"  {response.result.get('content', 'No content')[:500]}...")
    
    await connector.cleanup()


async def main():
    """Run all real delegation tests"""
    print("🚀 Trinitas v3.5 - Real Delegation Tests")
    print("=" * 50)
    
    # Check server availability first
    connector = LocalLLMConnector()
    await connector.initialize()
    
    if not await connector.check_health():
        print("❌ Local LLM server is not available")
        print(f"   Endpoint: {connector.endpoint}")
        return
    
    print(f"✅ Connected to Local LLM at {connector.endpoint}")
    await connector.cleanup()
    
    # Run tests
    await test_real_delegation()
    await test_context_pressure()
    await test_real_execution()
    
    print("\n" + "=" * 50)
    print("✅ All real delegation tests completed!")


if __name__ == "__main__":
    asyncio.run(main())