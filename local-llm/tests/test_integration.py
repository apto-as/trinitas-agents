#!/usr/bin/env python3
"""
Trinitas v3.5 - Integration Tests
Verifies all components work together correctly
"""

import asyncio
import json
import time
import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch

# Import all v3.5 components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    TaskResponse,
    CognitiveComplexity,
    ExecutorType
)
from delegation.delegation_engine import (
    CognitiveDelegationEngine,
    DelegationDecision,
    ContextState
)
from sparring.sparring_partner import (
    SparringPartnerSystem,
    SparringMode,
    SparringSession
)
from testing.test_automation import (
    TestAutomationPipeline,
    TestType,
    TestSuite,
    TestReport
)


class TestIntegration:
    """Integration tests for v3.5 Hybrid Intelligence"""
    
    @pytest.fixture
    async def setup_components(self):
        """Set up all components for testing"""
        # Initialize components
        connector = LocalLLMConnector()
        delegation_engine = CognitiveDelegationEngine()
        sparring_system = SparringPartnerSystem()
        test_pipeline = TestAutomationPipeline()
        
        # Mock the actual API calls
        connector.session = AsyncMock()
        
        # Initialize
        await delegation_engine.initialize()
        await sparring_system.initialize()
        await test_pipeline.initialize()
        
        return {
            "connector": connector,
            "delegation": delegation_engine,
            "sparring": sparring_system,
            "testing": test_pipeline
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_task_delegation(self, setup_components):
        """Test complete task delegation flow"""
        components = await setup_components
        delegation_engine = components["delegation"]
        
        # Test 1: Simple mechanical task -> Local
        simple_task = TaskRequest(
            id="test-simple",
            type="file_search",
            description="Find all Python files in project",
            estimated_tokens=50000,
            required_tools=["file_operations"]
        )
        
        decision = await delegation_engine.decide_delegation(simple_task)
        assert decision.executor == ExecutorType.LOCAL
        assert "Heavy but simple" in decision.reason or "Mechanical" in decision.reason
        assert decision.confidence >= 0.85
        
        # Test 2: Complex creative task -> Claude
        complex_task = TaskRequest(
            id="test-complex",
            type="algorithm_design",
            description="Design a new distributed consensus algorithm",
            estimated_tokens=10000,
            required_tools=[]
        )
        
        decision = await delegation_engine.decide_delegation(complex_task)
        assert decision.executor == ExecutorType.CLAUDE
        assert "cognitive complexity" in decision.reason.lower()
        assert decision.confidence >= 0.90
        
        # Test 3: Heavy + Complex task -> Hybrid
        hybrid_task = TaskRequest(
            id="test-hybrid",
            type="system_design",
            description="Analyze 500K lines of code and design refactoring strategy",
            estimated_tokens=200000,
            required_tools=["mcp_server", "file_operations"]
        )
        
        decision = await delegation_engine.decide_delegation(hybrid_task)
        assert decision.executor == ExecutorType.HYBRID
        assert decision.decomposition is not None
        assert len(decision.decomposition.local_tasks) > 0
        assert len(decision.decomposition.claude_tasks) > 0
    
    @pytest.mark.asyncio
    async def test_sparring_session_flow(self, setup_components):
        """Test complete sparring session"""
        components = await setup_components
        sparring = components["sparring"]
        
        # Mock the connector's execute method
        sparring.local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="sparring-test",
                executor="local",
                result={"content": "Challenge: Your solution lacks error handling"},
                tokens_used=1000,
                duration=0.5,
                confidence=0.85
            )
        )
        
        # Conduct sparring session
        problem = "Design a caching system for 1M requests/second"
        solution = "Use simple LRU cache with 5 minute TTL"
        
        session = await sparring.conduct_sparring(
            problem=problem,
            current_solution=solution,
            mode=SparringMode.AUTO
        )
        
        # Verify session results
        assert session.id.startswith("sparring_")
        assert session.mode != SparringMode.AUTO  # Should have been determined
        assert len(session.challenges) > 0
        assert session.synthesis is not None
        assert session.duration > 0
        
        # Check synthesis quality
        assert "recommendations" in session.synthesis
        assert "action_items" in session.synthesis
    
    @pytest.mark.asyncio
    async def test_test_automation_delegation(self, setup_components):
        """Test that test automation correctly delegates based on complexity"""
        components = await setup_components
        test_pipeline = components["testing"]
        
        # Mock the connector
        test_pipeline.local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="test-gen",
                executor="local",
                result={"content": "Generated test cases"},
                tokens_used=500,
                duration=0.3,
                confidence=0.9
            )
        )
        
        code = """
        def calculate_price(amount, discount):
            return amount * (1 - discount/100)
        """
        
        # Generate tests with different types
        suite = await test_pipeline.generate_tests(
            code=code,
            language="python",
            test_types=[
                TestType.UNIT,          # Mechanical -> Local
                TestType.INTEGRATION,   # Analytical -> Local
                TestType.SECURITY      # Strategic -> Claude
            ]
        )
        
        # Verify suite structure
        assert suite.id.startswith("suite_")
        assert len(suite.test_cases) > 0
        assert suite.language == "python"
        assert suite.framework == "pytest"
        
        # Verify delegation occurred correctly
        unit_tests = [t for t in suite.test_cases if t.type == TestType.UNIT]
        security_tests = [t for t in suite.test_cases if t.type == TestType.SECURITY]
        
        assert len(unit_tests) > 0  # Generated by Local
        assert len(security_tests) > 0  # Would be generated by Claude
    
    @pytest.mark.asyncio
    async def test_cognitive_complexity_routing(self, setup_components):
        """Test cognitive complexity determines correct routing"""
        components = await setup_components
        delegation_engine = components["delegation"]
        
        test_cases = [
            # (task_type, description, expected_complexity, expected_executor)
            ("file_search", "Search for files", CognitiveComplexity.MECHANICAL, ExecutorType.LOCAL),
            ("pattern_search", "Find usage patterns", CognitiveComplexity.ANALYTICAL, ExecutorType.LOCAL),
            ("debug_analysis", "Debug why feature fails", CognitiveComplexity.REASONING, ExecutorType.CLAUDE),
            ("algorithm_design", "Create new sorting algorithm", CognitiveComplexity.CREATIVE, ExecutorType.CLAUDE),
            ("architecture_design", "Design microservices", CognitiveComplexity.STRATEGIC, ExecutorType.CLAUDE)
        ]
        
        for task_type, description, expected_complexity, expected_executor in test_cases:
            task = TaskRequest(
                id=f"complexity-test-{task_type}",
                type=task_type,
                description=description,
                estimated_tokens=5000,
                required_tools=[]
            )
            
            decision = await delegation_engine.decide_delegation(task)
            
            # Check complexity determination
            assert task.complexity == expected_complexity, \
                f"Task {task_type} should have complexity {expected_complexity.name}"
            
            # Check executor selection (may vary based on context pressure)
            if expected_complexity.value >= 4:  # Creative/Strategic
                assert decision.executor in [ExecutorType.CLAUDE, ExecutorType.HYBRID]
            elif expected_complexity.value <= 2:  # Mechanical/Analytical
                assert decision.executor in [ExecutorType.LOCAL, ExecutorType.HYBRID]
    
    @pytest.mark.asyncio
    async def test_context_pressure_handling(self, setup_components):
        """Test that context pressure affects delegation decisions"""
        components = await setup_components
        delegation_engine = components["delegation"]
        
        # Set high Claude context pressure
        delegation_engine.context_state.claude_usage = 150000  # 75% used
        
        # Reasoning task should now prefer hybrid
        reasoning_task = TaskRequest(
            id="context-pressure-test",
            type="debug_analysis",
            description="Debug complex issue",
            estimated_tokens=10000,
            required_tools=["file_operations"]
        )
        
        decision = await delegation_engine.decide_delegation(reasoning_task)
        
        # With high context pressure, should use hybrid for reasoning
        assert decision.executor == ExecutorType.HYBRID
        assert "context pressure" in decision.reason.lower()
        
        # Reset context
        delegation_engine.context_state.claude_usage = 10000  # Low usage
        
        # Same task should now go to Claude
        decision2 = await delegation_engine.decide_delegation(reasoning_task)
        assert decision2.executor == ExecutorType.CLAUDE
    
    @pytest.mark.asyncio
    async def test_hybrid_execution_synthesis(self, setup_components):
        """Test hybrid execution properly synthesizes results"""
        components = await setup_components
        delegation_engine = components["delegation"]
        
        # Mock execution methods
        delegation_engine._execute_local = AsyncMock(
            return_value=TaskResponse(
                id="local-part",
                executor="local",
                result={"data": "Collected 100K lines of code"},
                tokens_used=50000,
                duration=2.0,
                confidence=0.9
            )
        )
        
        delegation_engine._execute_claude = AsyncMock(
            return_value=TaskResponse(
                id="claude-part",
                executor="claude",
                result={"analysis": "Found 5 architectural issues"},
                tokens_used=10000,
                duration=1.0,
                confidence=0.95
            )
        )
        
        # Create a heavy + complex task
        task = TaskRequest(
            id="hybrid-test",
            type="system_design",
            description="Analyze codebase and design improvements",
            estimated_tokens=150000,
            required_tools=["mcp_server"]
        )
        
        # Force hybrid execution
        decision = DelegationDecision(
            executor=ExecutorType.HYBRID,
            reason="Test hybrid",
            confidence=0.9,
            decomposition=await delegation_engine._decompose_heavy_complex(task)
        )
        
        # Execute
        result = await delegation_engine.execute_task(task, decision)
        
        # Verify synthesis
        assert result.executor == "hybrid"
        assert result.result["execution_mode"] == "hybrid"
        assert len(result.result["local_contributions"]) > 0
        assert len(result.result["claude_contributions"]) > 0
        assert result.result["final_result"] is not None
        assert result.tokens_used == 60000  # Sum of both
    
    @pytest.mark.asyncio
    async def test_test_failure_analysis_routing(self, setup_components):
        """Test that test failures are analyzed based on complexity"""
        components = await setup_components
        test_pipeline = components["testing"]
        
        # Create mock test results
        from testing.test_automation import TestResult, TestReport
        
        # Simple failure (assertion)
        simple_failure = TestResult(
            test_id="test_001",
            status="failed",
            duration=0.1,
            output="Test failed",
            error_message="Assertion failed: expected 5, got 4"
        )
        
        # Complex failure
        complex_failure = TestResult(
            test_id="test_002",
            status="failed",
            duration=0.5,
            output="Test failed",
            error_message="Complex system integration failure with race condition"
        )
        
        # Test simple failure analysis (should use Local)
        is_simple = test_pipeline._is_simple_failure(simple_failure)
        assert is_simple is True
        
        # Test complex failure analysis (should use Claude)
        is_complex = test_pipeline._is_simple_failure(complex_failure)
        assert is_complex is False
    
    @pytest.mark.asyncio
    async def test_sparring_mode_selection(self, setup_components):
        """Test automatic sparring mode selection"""
        components = await setup_components
        sparring = components["sparring"]
        
        test_cases = [
            ("Optimize algorithm performance", SparringMode.ALTERNATIVE_FINDER),
            ("Review security implementation", SparringMode.EDGE_CASE_HUNTER),
            ("Design system architecture", SparringMode.PERSPECTIVE_SHIFT),
            ("General code review", SparringMode.DEVIL_ADVOCATE)
        ]
        
        for problem, expected_mode in test_cases:
            mode = sparring._determine_mode(problem)
            assert mode == expected_mode, f"Problem '{problem}' should select {expected_mode.value}"
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, setup_components):
        """Test a complete workflow using all components"""
        components = await setup_components
        
        # Step 1: Delegate a complex task
        task = TaskRequest(
            id="workflow-test",
            type="code_generation",
            description="Create a REST API with authentication",
            estimated_tokens=30000,
            required_tools=["mcp_server"]
        )
        
        decision = await components["delegation"].decide_delegation(task)
        assert decision.executor == ExecutorType.CLAUDE  # Creative task
        
        # Step 2: Generate tests for the code
        test_code = """
        @app.route('/api/login', methods=['POST'])
        def login():
            username = request.json.get('username')
            password = request.json.get('password')
            # Authentication logic here
            return jsonify({'token': 'jwt-token'})
        """
        
        # Mock test generation
        components["testing"].local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="test-gen",
                executor="local",
                result={"content": "Test cases generated"},
                tokens_used=1000,
                duration=0.5,
                confidence=0.9
            )
        )
        
        suite = await components["testing"].generate_tests(
            code=test_code,
            language="python",
            test_types=[TestType.UNIT, TestType.SECURITY]
        )
        assert len(suite.test_cases) > 0
        
        # Step 3: Sparring session for improvements
        components["sparring"].local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="sparring",
                executor="local",
                result={"content": "Consider rate limiting"},
                tokens_used=2000,
                duration=1.0,
                confidence=0.85
            )
        )
        
        session = await components["sparring"].conduct_sparring(
            problem="REST API with authentication",
            current_solution=test_code,
            mode=SparringMode.EDGE_CASE_HUNTER
        )
        
        assert len(session.challenges) > 0
        assert session.synthesis is not None
        
        # Verify all components worked together
        stats = components["delegation"].get_delegation_stats()
        assert stats["total_tasks"] > 0


# Performance benchmarks
class TestPerformance:
    """Performance tests for v3.5 components"""
    
    @pytest.mark.asyncio
    async def test_delegation_speed(self, setup_components):
        """Test delegation decision speed"""
        components = await setup_components
        delegation_engine = components["delegation"]
        
        tasks = [
            TaskRequest(
                id=f"perf-{i}",
                type="file_search",
                description=f"Task {i}",
                estimated_tokens=10000,
                required_tools=["file_operations"]
            )
            for i in range(100)
        ]
        
        start = time.time()
        decisions = []
        for task in tasks:
            decision = await delegation_engine.decide_delegation(task)
            decisions.append(decision)
        duration = time.time() - start
        
        # Should decide quickly
        assert duration < 1.0  # 100 decisions in < 1 second
        assert len(decisions) == 100
        
        # Check decision distribution
        local_count = sum(1 for d in decisions if d.executor == ExecutorType.LOCAL)
        assert local_count > 90  # Most simple tasks should go to local
    
    @pytest.mark.asyncio
    async def test_parallel_sparring_sessions(self, setup_components):
        """Test running multiple sparring sessions in parallel"""
        components = await setup_components
        sparring = components["sparring"]
        
        # Mock connector
        sparring.local_connector.execute = AsyncMock(
            return_value=TaskResponse(
                id="sparring",
                executor="local",
                result={"content": "Challenge"},
                tokens_used=500,
                duration=0.1,
                confidence=0.85
            )
        )
        
        # Create multiple sparring tasks
        sparring_tasks = [
            sparring.conduct_sparring(
                problem=f"Problem {i}",
                current_solution=f"Solution {i}",
                mode=SparringMode.DEVIL_ADVOCATE
            )
            for i in range(5)
        ]
        
        # Run in parallel
        start = time.time()
        sessions = await asyncio.gather(*sparring_tasks)
        duration = time.time() - start
        
        # Should complete quickly in parallel
        assert duration < 2.0  # 5 sessions in < 2 seconds
        assert len(sessions) == 5
        assert all(s.id.startswith("sparring_") for s in sessions)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])