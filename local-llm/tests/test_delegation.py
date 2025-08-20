#!/usr/bin/env python3
"""
Trinitas v3.5 - Delegation Engine Unit Tests
Tests for Cognitive-Aware Delegation Engine
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delegation.delegation_engine import (
    CognitiveDelegationEngine,
    DelegationDecision,
    ContextState,
    TaskDecomposition,
    ExecutorType
)
from connector.llm_connector import (
    TaskRequest,
    TaskResponse,
    CognitiveComplexity
)


class TestCognitiveDelegationEngine:
    """Unit tests for Cognitive Delegation Engine"""
    
    @pytest.fixture
    def engine(self):
        """Create delegation engine instance"""
        engine = CognitiveDelegationEngine()
        engine.local_connector = AsyncMock()
        return engine
    
    def test_context_state_pressure(self):
        """Test context pressure calculations"""
        state = ContextState()
        
        # Test initial state
        assert state.claude_pressure == 0.0
        assert state.local_pressure == 0.0
        
        # Test with usage
        state.claude_usage = 100000  # 50% of 200K
        state.local_usage = 60000    # 50% of 120K
        
        assert state.claude_pressure == 0.5
        assert state.local_pressure == 0.5
        
        # Test high pressure
        state.claude_usage = 180000  # 90% of 200K
        assert state.claude_pressure == 0.9
    
    def test_determine_complexity(self, engine):
        """Test cognitive complexity determination"""
        
        # Test explicit type mapping
        task1 = TaskRequest(
            id="test-1",
            type="file_search",
            description="Search files",
            estimated_tokens=1000,
            required_tools=[]
        )
        complexity1 = engine._determine_complexity(task1)
        assert complexity1 == CognitiveComplexity.MECHANICAL
        
        # Test description-based detection - Strategic
        task2 = TaskRequest(
            id="test-2",
            type="custom",
            description="Design system architecture for scalability",
            estimated_tokens=5000,
            required_tools=[]
        )
        complexity2 = engine._determine_complexity(task2)
        assert complexity2 == CognitiveComplexity.STRATEGIC
        
        # Test description-based detection - Creative
        task3 = TaskRequest(
            id="test-3",
            type="custom",
            description="Create a novel algorithm from scratch",
            estimated_tokens=3000,
            required_tools=[]
        )
        complexity3 = engine._determine_complexity(task3)
        assert complexity3 == CognitiveComplexity.CREATIVE
        
        # Test description-based detection - Reasoning
        task4 = TaskRequest(
            id="test-4",
            type="custom",
            description="Debug and understand why the system fails",
            estimated_tokens=2000,
            required_tools=[]
        )
        complexity4 = engine._determine_complexity(task4)
        assert complexity4 == CognitiveComplexity.REASONING
        
        # Test description-based detection - Analytical
        task5 = TaskRequest(
            id="test-5",
            type="custom",
            description="Find patterns in the log files",
            estimated_tokens=1500,
            required_tools=[]
        )
        complexity5 = engine._determine_complexity(task5)
        assert complexity5 == CognitiveComplexity.ANALYTICAL
    
    @pytest.mark.asyncio
    async def test_decide_delegation_simple(self, engine):
        """Test delegation decision for simple tasks"""
        await engine.initialize()
        
        # Heavy but simple task -> Local
        task = TaskRequest(
            id="simple-heavy",
            type="file_search",
            description="Search through 100K files",
            estimated_tokens=50000,
            required_tools=["file_operations"]
        )
        
        decision = await engine.decide_delegation(task)
        assert decision.executor == ExecutorType.LOCAL
        assert "Heavy but simple" in decision.reason
        assert decision.confidence >= 0.85
        
        # Light and simple task -> Local (with low context pressure)
        engine.context_state.claude_pressure = 0.1
        task2 = TaskRequest(
            id="simple-light",
            type="copy_files",
            description="Copy configuration files",
            estimated_tokens=500,
            required_tools=[]
        )
        
        decision2 = await engine.decide_delegation(task2)
        assert decision2.executor == ExecutorType.LOCAL
    
    @pytest.mark.asyncio
    async def test_decide_delegation_complex(self, engine):
        """Test delegation decision for complex tasks"""
        await engine.initialize()
        
        # Complex creative task -> Claude
        task = TaskRequest(
            id="complex-creative",
            type="algorithm_design",
            description="Design a new distributed consensus algorithm",
            estimated_tokens=10000,
            required_tools=[]
        )
        
        decision = await engine.decide_delegation(task)
        assert decision.executor == ExecutorType.CLAUDE
        assert "cognitive complexity" in decision.reason.lower()
        assert decision.confidence >= 0.90
        
        # Complex strategic task -> Claude
        task2 = TaskRequest(
            id="complex-strategic",
            type="architecture_design",
            description="Design microservices architecture",
            estimated_tokens=20000,
            required_tools=[]
        )
        
        decision2 = await engine.decide_delegation(task2)
        assert decision2.executor == ExecutorType.CLAUDE
        assert task2.complexity == CognitiveComplexity.STRATEGIC
    
    @pytest.mark.asyncio
    async def test_decide_delegation_hybrid(self, engine):
        """Test delegation decision for hybrid tasks"""
        await engine.initialize()
        
        # Heavy + Complex task -> Hybrid
        task = TaskRequest(
            id="heavy-complex",
            type="system_design",
            description="Analyze 500K lines of code and design refactoring strategy",
            estimated_tokens=200000,
            required_tools=["mcp_server", "file_operations"]
        )
        
        decision = await engine.decide_delegation(task)
        assert decision.executor == ExecutorType.HYBRID
        assert "Heavy + Complex" in decision.reason
        assert decision.decomposition is not None
        assert len(decision.decomposition.local_tasks) > 0
        assert len(decision.decomposition.claude_tasks) > 0
        assert decision.decomposition.synthesis_required is True
    
    @pytest.mark.asyncio
    async def test_context_pressure_effects(self, engine):
        """Test how context pressure affects delegation"""
        await engine.initialize()
        
        # Test with high Claude context pressure
        engine.context_state.claude_usage = 150000  # 75% used
        
        # Reasoning task should prefer hybrid with high pressure
        task = TaskRequest(
            id="reasoning-pressure",
            type="debug_analysis",
            description="Debug complex system issue",
            estimated_tokens=10000,
            required_tools=["file_operations"]
        )
        
        decision = await engine.decide_delegation(task)
        assert decision.executor == ExecutorType.HYBRID
        assert "context pressure" in decision.reason.lower()
        
        # Reset context and test again
        engine.context_state.claude_usage = 10000  # Low usage
        
        decision2 = await engine.decide_delegation(task)
        assert decision2.executor == ExecutorType.CLAUDE
        assert "Reasoning required" in decision2.reason
    
    @pytest.mark.asyncio
    async def test_decompose_heavy_complex(self, engine):
        """Test decomposition of heavy + complex tasks"""
        task = TaskRequest(
            id="test-decompose",
            type="system_design",
            description="Analyze and redesign entire system",
            estimated_tokens=300000,
            required_tools=["mcp_server", "file_operations"],
            complexity=CognitiveComplexity.STRATEGIC
        )
        
        decomposition = await engine._decompose_heavy_complex(task)
        
        # Check local tasks
        assert len(decomposition.local_tasks) == 2
        assert decomposition.local_tasks[0].type == "data_gathering"
        assert decomposition.local_tasks[0].complexity == CognitiveComplexity.MECHANICAL
        assert decomposition.local_tasks[1].type == "initial_analysis"
        assert decomposition.local_tasks[1].complexity == CognitiveComplexity.ANALYTICAL
        
        # Check Claude tasks
        assert len(decomposition.claude_tasks) == 2
        assert decomposition.claude_tasks[0].type == "deep_analysis"
        assert decomposition.claude_tasks[0].complexity == CognitiveComplexity.STRATEGIC
        assert decomposition.claude_tasks[1].type == "solution_design"
        assert decomposition.claude_tasks[1].complexity == CognitiveComplexity.CREATIVE
        
        # Check flags
        assert decomposition.synthesis_required is True
        assert decomposition.claude_priority is True  # Claude leads
    
    @pytest.mark.asyncio
    async def test_decompose_reasoning_task(self, engine):
        """Test decomposition of reasoning tasks"""
        task = TaskRequest(
            id="test-reasoning",
            type="debug_analysis",
            description="Debug complex failure",
            estimated_tokens=50000,
            required_tools=["file_operations", "bash"]
        )
        
        decomposition = await engine._decompose_reasoning_task(task)
        
        # Check task distribution
        assert len(decomposition.local_tasks) == 1
        assert decomposition.local_tasks[0].type == "fact_gathering"
        assert decomposition.local_tasks[0].complexity == CognitiveComplexity.ANALYTICAL
        assert decomposition.local_tasks[0].estimated_tokens == 30000  # 60% of 50K
        
        assert len(decomposition.claude_tasks) == 1
        assert decomposition.claude_tasks[0].type == "reasoning"
        assert decomposition.claude_tasks[0].complexity == CognitiveComplexity.REASONING
        assert decomposition.claude_tasks[0].estimated_tokens == 20000  # 40% of 50K
        
        assert decomposition.claude_priority is False  # Local gathers first
    
    @pytest.mark.asyncio
    async def test_execute_task_local(self, engine):
        """Test local task execution"""
        await engine.initialize()
        
        # Mock local execution
        engine.local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="local-result",
                executor="local",
                result={"data": "collected"},
                tokens_used=5000,
                duration=1.0,
                confidence=0.9
            )
        )
        
        task = TaskRequest(
            id="test-local",
            type="file_search",
            description="Search files",
            estimated_tokens=5000,
            required_tools=["file_operations"]
        )
        
        decision = DelegationDecision(
            executor=ExecutorType.LOCAL,
            reason="Test",
            confidence=0.95
        )
        
        response = await engine.execute_task(task, decision)
        
        assert response.executor == "local"
        assert response.result["data"] == "collected"
        assert response.tokens_used == 5000
        assert engine.context_state.local_usage == 5000
    
    @pytest.mark.asyncio
    async def test_execute_task_hybrid(self, engine):
        """Test hybrid task execution"""
        await engine.initialize()
        
        # Mock execution methods
        engine._execute_local = AsyncMock(
            return_value=TaskResponse(
                id="local-part",
                executor="local",
                result={"data": "Local data"},
                tokens_used=30000,
                duration=2.0,
                confidence=0.85
            )
        )
        
        engine._execute_claude = AsyncMock(
            return_value=TaskResponse(
                id="claude-part",
                executor="claude",
                result={"analysis": "Claude analysis"},
                tokens_used=10000,
                duration=1.0,
                confidence=0.95
            )
        )
        
        task = TaskRequest(
            id="test-hybrid",
            type="system_design",
            description="Complex task",
            estimated_tokens=100000,
            required_tools=["mcp_server"]
        )
        
        decomposition = TaskDecomposition(
            local_tasks=[TaskRequest(
                id="local-1",
                type="gather",
                description="Gather data",
                estimated_tokens=30000,
                required_tools=[]
            )],
            claude_tasks=[TaskRequest(
                id="claude-1",
                type="analyze",
                description="Analyze",
                estimated_tokens=10000,
                required_tools=[]
            )],
            synthesis_required=True,
            claude_priority=True
        )
        
        decision = DelegationDecision(
            executor=ExecutorType.HYBRID,
            reason="Test hybrid",
            confidence=0.9,
            decomposition=decomposition
        )
        
        response = await engine.execute_task(task, decision)
        
        assert response.executor == "hybrid"
        assert response.result["execution_mode"] == "hybrid"
        assert len(response.result["local_contributions"]) > 0
        assert len(response.result["claude_contributions"]) > 0
        assert response.result["final_result"] is not None
        assert response.tokens_used == 40000  # Sum of both
    
    def test_synthesize_results(self, engine):
        """Test result synthesis"""
        original_task = TaskRequest(
            id="original",
            type="complex",
            description="Complex task",
            estimated_tokens=100000,
            required_tools=[]
        )
        
        local_results = [
            TaskResponse(
                id="local-1",
                executor="local",
                result={"data": "Local data 1"},
                tokens_used=10000,
                duration=1.0,
                confidence=0.85
            )
        ]
        
        claude_results = [
            TaskResponse(
                id="claude-1",
                executor="claude",
                result={"analysis": "Claude analysis"},
                tokens_used=5000,
                duration=0.5,
                confidence=0.95
            )
        ]
        
        decomposition = TaskDecomposition(
            local_tasks=[],
            claude_tasks=[],
            synthesis_required=True,
            claude_priority=True
        )
        
        synthesis = engine._synthesize_results(
            original_task,
            local_results,
            claude_results,
            decomposition
        )
        
        assert synthesis["task_id"] == "original"
        assert synthesis["execution_mode"] == "hybrid"
        assert len(synthesis["local_contributions"]) == 1
        assert len(synthesis["claude_contributions"]) == 1
        assert synthesis["final_result"] == {"analysis": "Claude analysis"}  # Claude priority
    
    def test_get_delegation_stats(self, engine):
        """Test delegation statistics"""
        # Add some history
        engine.delegation_history = [
            {
                "task_id": "task-1",
                "decision": DelegationDecision(
                    executor=ExecutorType.LOCAL,
                    reason="Simple",
                    confidence=0.9
                ),
                "timestamp": 1000
            },
            {
                "task_id": "task-2",
                "decision": DelegationDecision(
                    executor=ExecutorType.CLAUDE,
                    reason="Complex",
                    confidence=0.95
                ),
                "timestamp": 2000
            },
            {
                "task_id": "task-3",
                "decision": DelegationDecision(
                    executor=ExecutorType.HYBRID,
                    reason="Heavy+Complex",
                    confidence=0.85
                ),
                "timestamp": 3000
            }
        ]
        
        engine.context_state.claude_usage = 50000
        engine.context_state.local_usage = 80000
        
        stats = engine.get_delegation_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["by_executor"]["local"] == 1
        assert stats["by_executor"]["claude"] == 1
        assert stats["by_executor"]["hybrid"] == 1
        assert stats["context_usage"]["claude"] == 50000
        assert stats["context_usage"]["local"] == 80000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])