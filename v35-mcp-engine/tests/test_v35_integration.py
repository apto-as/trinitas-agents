#!/usr/bin/env python3
"""
Trinitas v3.5 TRUE - Comprehensive Integration Tests
Tests for the complete hybrid MCP intelligence platform
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import asyncio
import pytest
from typing import Dict, List, Any
from datetime import datetime

# Import all components
from persona_registry import PersonaType, ExecutorType, TaskType, registry
from routing_engine import routing_engine, RoutingStrategy
from context_synchronizer import context_sync, ContextType
from collaboration_protocol import collaboration_protocol, CollaborationMode
from hybrid_executor import hybrid_executor
from quality_gates import quality_gates
from performance_optimizer import performance_optimizer, OptimizationTarget

class TestPersonaRegistry:
    """Test persona registry functionality"""
    
    def test_all_personas_registered(self):
        """Test that all 5 personas are registered"""
        assert len(registry.personas) == 5
        
        # Check Claude personas
        assert PersonaType.SPRINGFIELD in registry.personas
        assert PersonaType.KRUKAI in registry.personas
        assert PersonaType.VECTOR in registry.personas
        
        # Check Local LLM personas
        assert PersonaType.GROZA in registry.personas
        assert PersonaType.LITTARA in registry.personas
    
    def test_persona_languages(self):
        """Test persona language settings"""
        # Claude personas use Japanese
        assert registry.get_persona(PersonaType.SPRINGFIELD).language == "japanese"
        assert registry.get_persona(PersonaType.KRUKAI).language == "japanese"
        assert registry.get_persona(PersonaType.VECTOR).language == "japanese"
        
        # Local personas use English
        assert registry.get_persona(PersonaType.GROZA).language == "english"
        assert registry.get_persona(PersonaType.LITTARA).language == "english"
    
    def test_persona_executors(self):
        """Test persona executor assignments"""
        # Claude executor
        assert registry.get_persona(PersonaType.SPRINGFIELD).executor == ExecutorType.CLAUDE
        assert registry.get_persona(PersonaType.KRUKAI).executor == ExecutorType.CLAUDE
        assert registry.get_persona(PersonaType.VECTOR).executor == ExecutorType.CLAUDE
        
        # Local executor
        assert registry.get_persona(PersonaType.GROZA).executor == ExecutorType.LOCAL
        assert registry.get_persona(PersonaType.LITTARA).executor == ExecutorType.LOCAL
    
    def test_find_best_persona(self):
        """Test persona selection logic"""
        # Strategic task
        best = registry.find_best_persona("Design system architecture", TaskType.STRATEGIC)
        assert best in [PersonaType.SPRINGFIELD, PersonaType.GROZA]
        
        # Technical task
        best = registry.find_best_persona("Optimize database queries", TaskType.TECHNICAL)
        assert best in [PersonaType.KRUKAI, PersonaType.LITTARA]
        
        # Security task
        best = registry.find_best_persona("Security audit", TaskType.SECURITY)
        assert best == PersonaType.VECTOR

class TestRoutingEngine:
    """Test routing engine functionality"""
    
    @pytest.mark.asyncio
    async def test_capability_routing(self):
        """Test capability-based routing"""
        decision = await routing_engine.route_task(
            "Design microservice architecture",
            TaskType.STRATEGIC,
            strategy=RoutingStrategy.CAPABILITY
        )
        
        assert decision.primary_persona in [PersonaType.SPRINGFIELD, PersonaType.GROZA]
        assert decision.executor in [ExecutorType.CLAUDE, ExecutorType.LOCAL]
        assert decision.confidence > 0
    
    @pytest.mark.asyncio
    async def test_load_balancing(self):
        """Test load-based routing"""
        # Simulate load on Claude
        routing_engine.metrics[ExecutorType.CLAUDE].active_tasks = 10
        
        decision = await routing_engine.route_task(
            "Simple task",
            strategy=RoutingStrategy.LEAST_LOADED
        )
        
        # Should route to Local LLM due to load
        assert decision.executor == ExecutorType.LOCAL
        
        # Reset
        routing_engine.metrics[ExecutorType.CLAUDE].active_tasks = 0
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self):
        """Test cost-optimized routing"""
        decision = await routing_engine.route_task(
            "Process large dataset with 10000 records",
            strategy=RoutingStrategy.COST_OPTIMIZED
        )
        
        # Should prefer Local LLM for large tasks
        assert decision.executor == ExecutorType.LOCAL
        assert decision.estimated_cost < 0.01
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        # Simulate failures
        for _ in range(10):
            await routing_engine.update_metrics(
                ExecutorType.CLAUDE,
                success=False,
                response_time=5.0,
                tokens_used=100
            )
        
        # Circuit breaker should be triggered
        assert routing_engine.circuit_breakers[ExecutorType.CLAUDE] == True
        
        # Should route to fallback
        decision = await routing_engine.route_task(
            "Test task",
            strategy=RoutingStrategy.CAPABILITY
        )
        assert decision.executor == ExecutorType.LOCAL
        
        # Reset
        routing_engine.circuit_breakers[ExecutorType.CLAUDE] = False

class TestContextSynchronization:
    """Test context synchronization"""
    
    @pytest.mark.asyncio
    async def test_cross_persona_sync(self):
        """Test context sync between personas"""
        context_data = {
            "requirements": "Build API",
            "architecture": "REST",
            "constraints": ["performance", "security"]
        }
        
        sync_state = await context_sync.sync_context(
            PersonaType.SPRINGFIELD,
            PersonaType.KRUKAI,
            "test_session",
            context_data
        )
        
        assert sync_state.success
        assert len(sync_state.context_frames) == 2
        assert "strategic_to_technical" in sync_state.transformations[0]
    
    @pytest.mark.asyncio
    async def test_cross_llm_sync(self):
        """Test context sync across LLMs"""
        context_data = {
            "長期計画": "3 year plan",
            "チーム構成": "10 members"
        }
        
        sync_state = await context_sync.sync_context(
            PersonaType.SPRINGFIELD,
            PersonaType.GROZA,
            "test_session",
            context_data
        )
        
        assert sync_state.success
        assert "japanese_to_english" in str(sync_state.transformations)
    
    def test_context_retrieval(self):
        """Test context retrieval"""
        # Create and store frames
        frame = context_sync.create_context_frame(
            {"test": "data"},
            PersonaType.SPRINGFIELD,
            ContextType.TASK,
            "japanese"
        )
        context_sync.store_context("test_session", frame)
        
        # Retrieve
        frames = context_sync.get_session_context("test_session")
        assert len(frames) > 0
        assert frames[0].persona == PersonaType.SPRINGFIELD

class TestCollaborationProtocol:
    """Test collaboration protocol"""
    
    @pytest.mark.asyncio
    async def test_sequential_collaboration(self):
        """Test sequential execution"""
        plan = await collaboration_protocol.create_collaboration_plan(
            "Implement API",
            mode=CollaborationMode.SEQUENTIAL,
            personas=[PersonaType.SPRINGFIELD, PersonaType.KRUKAI, PersonaType.LITTARA]
        )
        
        assert len(plan.tasks) == 3
        assert plan.tasks[1].dependencies == [plan.tasks[0].id]
        assert plan.tasks[2].dependencies == [plan.tasks[1].id]
        
        result = await collaboration_protocol.execute_collaboration(
            plan,
            {"description": "REST API"}
        )
        
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_collaboration(self):
        """Test parallel execution"""
        plan = await collaboration_protocol.create_collaboration_plan(
            "Analyze codebase",
            mode=CollaborationMode.PARALLEL,
            personas=[PersonaType.GROZA, PersonaType.LITTARA]
        )
        
        assert len(plan.tasks) == 2
        # No dependencies in parallel mode
        assert plan.tasks[0].dependencies == []
        assert plan.tasks[1].dependencies == []
    
    @pytest.mark.asyncio
    async def test_consensus_collaboration(self):
        """Test Trinity consensus"""
        plan = await collaboration_protocol.create_collaboration_plan(
            "Security critical decision",
            mode=CollaborationMode.CONSENSUS
        )
        
        result = await collaboration_protocol.execute_collaboration(
            plan,
            {"description": "Deploy to production"}
        )
        
        assert "consensus" in result
        assert "confidence" in result
        assert "individual_assessments" in result

class TestHybridExecutor:
    """Test hybrid execution"""
    
    @pytest.mark.asyncio
    async def test_simple_execution(self):
        """Test simple single-phase execution"""
        await hybrid_executor.initialize()
        
        plan = await hybrid_executor.create_execution_plan(
            "List files",
            estimated_tokens=100
        )
        
        assert len(plan.phases) == 1
        assert plan.phases[0] == "processing"
        
        await hybrid_executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_complex_execution(self):
        """Test complex multi-phase execution"""
        await hybrid_executor.initialize()
        
        plan = await hybrid_executor.create_execution_plan(
            "Design and implement secure authentication system with full audit",
            estimated_tokens=100000
        )
        
        assert len(plan.phases) > 1
        assert "analysis" in [p.value for p in plan.phases]
        assert "validation" in [p.value for p in plan.phases]
        
        await hybrid_executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_hybrid_routing(self):
        """Test hybrid LLM routing"""
        await hybrid_executor.initialize()
        
        complexity, needs_hybrid = hybrid_executor.analyze_task(
            "Complex security audit of entire infrastructure",
            100000
        )
        
        assert complexity > 0.5
        assert needs_hybrid == True
        
        await hybrid_executor.cleanup()

class TestQualityGates:
    """Test quality validation system"""
    
    @pytest.mark.asyncio
    async def test_quality_checks(self):
        """Test quality check execution"""
        implementation = {
            "response_time": 150,
            "test_coverage": 0.92,
            "documentation_coverage": 0.95,
            "vulnerabilities": [],
            "complexity": 5
        }
        
        report = await quality_gates.run_quality_checks(
            "Implement secure API",
            implementation
        )
        
        assert report.overall_score > 0.8
        assert report.overall_status in ["approved", "conditional"]
        assert len(report.checks) > 0
    
    @pytest.mark.asyncio
    async def test_trinity_consensus(self):
        """Test Trinity consensus in quality gates"""
        implementation = {
            "response_time": 100,
            "test_coverage": 0.95,
            "vulnerabilities": []
        }
        
        report = await quality_gates.run_quality_checks(
            "Critical system component",
            implementation
        )
        
        # Check Trinity personas participated
        trinity_checks = [
            c for c in report.checks
            if c.checker in [PersonaType.SPRINGFIELD, PersonaType.KRUKAI, PersonaType.VECTOR]
        ]
        assert len(trinity_checks) >= 3
    
    def test_improvement_plan(self):
        """Test improvement plan generation"""
        # Create a report with issues
        from quality_gates import QualityReport, QualityCheck, QualityMetric, ApprovalStatus
        
        report = QualityReport(
            id="test",
            task_description="Test task",
            checks=[
                QualityCheck(
                    metric=QualityMetric.SECURITY,
                    checker=PersonaType.VECTOR,
                    score=0.3,
                    status=ApprovalStatus.REJECTED,
                    details="Critical vulnerabilities",
                    recommendations=["Fix SQL injection", "Update dependencies"]
                )
            ],
            overall_score=0.3,
            overall_status=ApprovalStatus.REJECTED,
            trinity_consensus=False
        )
        
        plan = quality_gates.generate_improvement_plan(report)
        
        assert len(plan["priority_fixes"]) > 0
        assert plan["priority_fixes"][0]["priority"] == "CRITICAL"

class TestPerformanceOptimizer:
    """Test performance optimization"""
    
    @pytest.mark.asyncio
    async def test_monitoring(self):
        """Test performance monitoring"""
        await performance_optimizer.start_monitoring()
        
        # Record metrics
        performance_optimizer.record_performance(
            "test_entity",
            "latency",
            100.0,
            "ms"
        )
        
        assert "test_entity" in performance_optimizer.profiles
        assert len(performance_optimizer.profiles["test_entity"].metrics_history) > 0
        
        await performance_optimizer.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_token_optimization(self):
        """Test token optimization"""
        long_text = "This is a test. " * 100
        
        optimized, reduction = await performance_optimizer.token_optimizer.optimize_tokens(
            long_text,
            target_reduction=0.3
        )
        
        assert len(optimized) < len(long_text)
        assert reduction > 0
    
    def test_cache_functionality(self):
        """Test response cache"""
        cache = performance_optimizer.cache
        
        # Test put and get
        cache.put("key1", {"data": "test"})
        result = cache.get("key1")
        assert result == {"data": "test"}
        
        # Test miss
        miss = cache.get("nonexistent")
        assert miss is None
        
        # Test hit rate
        assert cache.hit_rate > 0
    
    @pytest.mark.asyncio
    async def test_optimization_strategies(self):
        """Test optimization strategy application"""
        result = await performance_optimizer.optimize_execution_plan(
            "test_plan",
            OptimizationTarget.LATENCY
        )
        
        assert result.strategy in ["parallelize", "cache"]
        assert result.target == OptimizationTarget.LATENCY
        assert len(result.recommendations) > 0

class TestEndToEndScenarios:
    """Test complete end-to-end scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow from routing to quality validation"""
        
        # 1. Route task
        routing_decision = await routing_engine.route_task(
            "Implement secure authentication API",
            TaskType.TECHNICAL
        )
        
        assert routing_decision.primary_persona is not None
        
        # 2. Create collaboration plan
        plan = await collaboration_protocol.create_collaboration_plan(
            "Implement secure authentication API",
            mode=CollaborationMode.SEQUENTIAL,
            personas=[
                PersonaType.SPRINGFIELD,
                PersonaType.KRUKAI,
                PersonaType.VECTOR
            ]
        )
        
        assert len(plan.tasks) == 3
        
        # 3. Execute with context sync
        context_data = {"requirements": "OAuth2 + JWT"}
        
        for i in range(len(plan.tasks) - 1):
            await context_sync.sync_context(
                plan.tasks[i].assigned_persona,
                plan.tasks[i+1].assigned_persona,
                "workflow_session",
                context_data
            )
        
        # 4. Quality validation
        implementation = {
            "response_time": 120,
            "test_coverage": 0.88,
            "vulnerabilities": []
        }
        
        quality_report = await quality_gates.run_quality_checks(
            "Authentication API",
            implementation
        )
        
        assert quality_report.overall_score > 0.7
        
        # 5. Performance optimization
        optimization_result = await performance_optimizer.optimize_execution_plan(
            plan.id,
            OptimizationTarget.LATENCY
        )
        
        assert optimization_result.success

def run_all_tests():
    """Run all integration tests"""
    print("Running Trinitas v3.5 TRUE Integration Tests")
    print("=" * 60)
    
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

if __name__ == "__main__":
    # For quick testing without pytest
    import asyncio
    
    async def quick_test():
        print("Quick Integration Test")
        print("-" * 40)
        
        # Test persona registry
        print(f"✓ Registered personas: {len(registry.personas)}")
        
        # Test routing
        decision = await routing_engine.route_task(
            "Test task",
            strategy=RoutingStrategy.CAPABILITY
        )
        print(f"✓ Routing decision: {decision.primary_persona}")
        
        # Test collaboration
        plan = await collaboration_protocol.create_collaboration_plan(
            "Test collaboration",
            mode=CollaborationMode.SEQUENTIAL,
            personas=[PersonaType.SPRINGFIELD, PersonaType.KRUKAI]
        )
        print(f"✓ Collaboration plan: {len(plan.tasks)} tasks")
        
        # Test quality gates
        report = await quality_gates.run_quality_checks(
            "Test implementation",
            {"test_coverage": 0.9}
        )
        print(f"✓ Quality score: {report.overall_score:.0%}")
        
        print("\n✅ All quick tests passed!")
    
    asyncio.run(quick_test())