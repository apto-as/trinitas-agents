#!/usr/bin/env python3
"""
Trinitas v3.5 - Cognitive-Aware Delegation Engine
Intelligently routes tasks based on cognitive complexity and computational load
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

from ..connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    TaskResponse,
    CognitiveComplexity,
    ExecutorType
)


@dataclass
class ContextState:
    """Current context usage state"""
    claude_usage: int = 0
    local_usage: int = 0
    claude_remaining: int = 200000
    local_remaining: int = 120000
    
    @property
    def claude_pressure(self) -> float:
        """Calculate Claude context pressure (0.0 to 1.0)"""
        return self.claude_usage / 200000
    
    @property
    def local_pressure(self) -> float:
        """Calculate Local context pressure (0.0 to 1.0)"""
        return self.local_usage / 120000


@dataclass
class TaskDecomposition:
    """Decomposed task for hybrid execution"""
    local_tasks: List[TaskRequest] = field(default_factory=list)
    claude_tasks: List[TaskRequest] = field(default_factory=list)
    synthesis_required: bool = False
    claude_priority: bool = False  # Claude leads if True


@dataclass
class DelegationDecision:
    """Decision on how to execute a task"""
    executor: ExecutorType
    reason: str
    confidence: float
    decomposition: Optional[TaskDecomposition] = None


class CognitiveDelegationEngine:
    """
    Intelligently routes tasks based on:
    1. Cognitive complexity (thinking depth)
    2. Computational load (data size)
    3. Context pressure (remaining tokens)
    """
    
    # Cognitive Complexity Thresholds
    COMPLEXITY_ROUTING = {
        CognitiveComplexity.MECHANICAL: ExecutorType.LOCAL,
        CognitiveComplexity.ANALYTICAL: ExecutorType.LOCAL,
        CognitiveComplexity.REASONING: ExecutorType.CLAUDE,
        CognitiveComplexity.CREATIVE: ExecutorType.CLAUDE,
        CognitiveComplexity.STRATEGIC: ExecutorType.CLAUDE,
    }
    
    # Task type to complexity mapping
    TASK_COMPLEXITY_MAP = {
        # Mechanical tasks (Level 1)
        "file_search": CognitiveComplexity.MECHANICAL,
        "copy_files": CognitiveComplexity.MECHANICAL,
        "run_command": CognitiveComplexity.MECHANICAL,
        "list_files": CognitiveComplexity.MECHANICAL,
        
        # Analytical tasks (Level 2)
        "pattern_search": CognitiveComplexity.ANALYTICAL,
        "test_generation": CognitiveComplexity.ANALYTICAL,
        "documentation": CognitiveComplexity.ANALYTICAL,
        "metric_collection": CognitiveComplexity.ANALYTICAL,
        "log_analysis": CognitiveComplexity.ANALYTICAL,
        
        # Reasoning tasks (Level 3)
        "debug_analysis": CognitiveComplexity.REASONING,
        "error_investigation": CognitiveComplexity.REASONING,
        "code_review": CognitiveComplexity.REASONING,
        "performance_analysis": CognitiveComplexity.REASONING,
        
        # Creative tasks (Level 4)
        "algorithm_design": CognitiveComplexity.CREATIVE,
        "api_design": CognitiveComplexity.CREATIVE,
        "code_generation": CognitiveComplexity.CREATIVE,
        "refactoring": CognitiveComplexity.CREATIVE,
        
        # Strategic tasks (Level 5)
        "architecture_design": CognitiveComplexity.STRATEGIC,
        "roadmap_planning": CognitiveComplexity.STRATEGIC,
        "system_design": CognitiveComplexity.STRATEGIC,
        "security_audit": CognitiveComplexity.STRATEGIC,
    }
    
    def __init__(self):
        self.context_state = ContextState()
        self.delegation_history = []
        self.local_connector = LocalLLMConnector()
        
    async def initialize(self):
        """Initialize delegation engine"""
        await self.local_connector.initialize()
    
    async def decide_delegation(
        self,
        task: TaskRequest,
        force_executor: Optional[ExecutorType] = None
    ) -> DelegationDecision:
        """
        Decide how to execute a task based on cognitive complexity
        and computational load
        """
        
        # Allow forced execution for testing
        if force_executor:
            return DelegationDecision(
                executor=force_executor,
                reason="Forced by user",
                confidence=1.0
            )
        
        # Step 1: Determine cognitive complexity
        complexity = self._determine_complexity(task)
        task.complexity = complexity
        
        # Step 2: Check if task is too complex for local
        if complexity.value >= 4:  # Creative or Strategic
            if task.estimated_tokens > 100000:
                # Too heavy even for Claude - needs decomposition
                decomposition = await self._decompose_heavy_complex(task)
                return DelegationDecision(
                    executor=ExecutorType.HYBRID,
                    reason=f"Heavy + Complex task (complexity={complexity.value})",
                    confidence=0.9,
                    decomposition=decomposition
                )
            else:
                # Complex but manageable - Claude handles it
                return DelegationDecision(
                    executor=ExecutorType.CLAUDE,
                    reason=f"High cognitive complexity ({complexity.name})",
                    confidence=0.95
                )
        
        # Step 3: Check if task requires reasoning
        if complexity == CognitiveComplexity.REASONING:
            if self.context_state.claude_pressure > 0.5:
                # Context pressure - try hybrid
                decomposition = await self._decompose_reasoning_task(task)
                return DelegationDecision(
                    executor=ExecutorType.HYBRID,
                    reason="Reasoning task with context pressure",
                    confidence=0.8,
                    decomposition=decomposition
                )
            else:
                # Claude has space for reasoning
                return DelegationDecision(
                    executor=ExecutorType.CLAUDE,
                    reason="Reasoning required",
                    confidence=0.85
                )
        
        # Step 4: Low complexity tasks - check computational load
        if complexity.value <= 2:  # Mechanical or Analytical
            if task.estimated_tokens > 20000:
                # Heavy but simple - perfect for local
                return DelegationDecision(
                    executor=ExecutorType.LOCAL,
                    reason=f"Heavy but simple (tokens={task.estimated_tokens})",
                    confidence=0.95
                )
            
            if len(task.required_tools) > 3:
                # Tool-heavy but simple - local is better
                return DelegationDecision(
                    executor=ExecutorType.LOCAL,
                    reason=f"Tool-intensive task ({len(task.required_tools)} tools)",
                    confidence=0.9
                )
            
            if self.context_state.claude_pressure > 0.5:
                # Save Claude's context for important work
                return DelegationDecision(
                    executor=ExecutorType.LOCAL,
                    reason="Preserving Claude context",
                    confidence=0.85
                )
        
        # Step 5: Default decision based on complexity
        default_executor = self.COMPLEXITY_ROUTING.get(
            complexity,
            ExecutorType.CLAUDE
        )
        
        return DelegationDecision(
            executor=default_executor,
            reason=f"Default routing for {complexity.name}",
            confidence=0.7
        )
    
    def _determine_complexity(self, task: TaskRequest) -> CognitiveComplexity:
        """Determine cognitive complexity of a task"""
        
        # Check explicit task type mapping
        if task.type in self.TASK_COMPLEXITY_MAP:
            return self.TASK_COMPLEXITY_MAP[task.type]
        
        # Analyze task description for complexity indicators
        description_lower = task.description.lower()
        
        # Strategic indicators
        strategic_keywords = [
            "architecture", "design system", "roadmap", "long-term",
            "strategy", "planning", "scalability", "future-proof"
        ]
        if any(keyword in description_lower for keyword in strategic_keywords):
            return CognitiveComplexity.STRATEGIC
        
        # Creative indicators
        creative_keywords = [
            "create", "design", "invent", "novel", "innovative",
            "new approach", "from scratch", "original"
        ]
        if any(keyword in description_lower for keyword in creative_keywords):
            return CognitiveComplexity.CREATIVE
        
        # Reasoning indicators
        reasoning_keywords = [
            "why", "debug", "analyze", "understand", "explain",
            "investigate", "diagnose", "root cause", "figure out"
        ]
        if any(keyword in description_lower for keyword in reasoning_keywords):
            return CognitiveComplexity.REASONING
        
        # Analytical indicators
        analytical_keywords = [
            "find", "search", "compare", "measure", "count",
            "pattern", "trend", "statistics", "metrics"
        ]
        if any(keyword in description_lower for keyword in analytical_keywords):
            return CognitiveComplexity.ANALYTICAL
        
        # Default to mechanical for simple tasks
        return CognitiveComplexity.MECHANICAL
    
    async def _decompose_heavy_complex(
        self,
        task: TaskRequest
    ) -> TaskDecomposition:
        """
        Decompose a task that is both heavy and complex
        Local handles data gathering, Claude handles thinking
        """
        
        # Local LLM tasks - mechanical work
        local_tasks = [
            TaskRequest(
                id=f"{task.id}_local_1",
                type="data_gathering",
                description=f"Gather all relevant data for: {task.description}",
                estimated_tokens=task.estimated_tokens // 2,
                required_tools=["file_operations", "bash"],
                complexity=CognitiveComplexity.MECHANICAL
            ),
            TaskRequest(
                id=f"{task.id}_local_2",
                type="initial_analysis",
                description="Process and organize collected data",
                estimated_tokens=20000,
                required_tools=["mcp_server"],
                complexity=CognitiveComplexity.ANALYTICAL
            )
        ]
        
        # Claude tasks - deep thinking
        claude_tasks = [
            TaskRequest(
                id=f"{task.id}_claude_1",
                type="deep_analysis",
                description=f"Analyze and understand: {task.description}",
                estimated_tokens=30000,
                required_tools=[],
                complexity=task.complexity
            ),
            TaskRequest(
                id=f"{task.id}_claude_2",
                type="solution_design",
                description="Design optimal solution based on analysis",
                estimated_tokens=20000,
                required_tools=[],
                complexity=CognitiveComplexity.CREATIVE
            )
        ]
        
        return TaskDecomposition(
            local_tasks=local_tasks,
            claude_tasks=claude_tasks,
            synthesis_required=True,
            claude_priority=True  # Claude leads this work
        )
    
    async def _decompose_reasoning_task(
        self,
        task: TaskRequest
    ) -> TaskDecomposition:
        """
        Decompose a reasoning task to preserve Claude context
        """
        
        # Local handles fact gathering
        local_tasks = [
            TaskRequest(
                id=f"{task.id}_facts",
                type="fact_gathering",
                description=f"Collect facts and evidence for: {task.description}",
                estimated_tokens=task.estimated_tokens * 0.6,
                required_tools=task.required_tools,
                complexity=CognitiveComplexity.ANALYTICAL
            )
        ]
        
        # Claude performs reasoning on gathered facts
        claude_tasks = [
            TaskRequest(
                id=f"{task.id}_reasoning",
                type="reasoning",
                description=f"Reason about: {task.description} (based on gathered facts)",
                estimated_tokens=task.estimated_tokens * 0.4,
                required_tools=[],
                complexity=CognitiveComplexity.REASONING
            )
        ]
        
        return TaskDecomposition(
            local_tasks=local_tasks,
            claude_tasks=claude_tasks,
            synthesis_required=True,
            claude_priority=False  # Local gathers first
        )
    
    async def execute_task(
        self,
        task: TaskRequest,
        decision: Optional[DelegationDecision] = None
    ) -> TaskResponse:
        """Execute task according to delegation decision"""
        
        # Get decision if not provided
        if decision is None:
            decision = await self.decide_delegation(task)
        
        # Record decision
        self.delegation_history.append({
            "task_id": task.id,
            "decision": decision,
            "timestamp": time.time()
        })
        
        # Execute based on decision
        if decision.executor == ExecutorType.LOCAL:
            return await self._execute_local(task)
        
        elif decision.executor == ExecutorType.CLAUDE:
            return await self._execute_claude(task)
        
        elif decision.executor == ExecutorType.HYBRID:
            return await self._execute_hybrid(task, decision.decomposition)
        
        else:
            raise ValueError(f"Unknown executor: {decision.executor}")
    
    async def _execute_local(self, task: TaskRequest) -> TaskResponse:
        """Execute task on Local LLM"""
        response = await self.local_connector.execute(task)
        
        # Update context tracking
        self.context_state.local_usage += response.tokens_used
        
        return response
    
    async def _execute_claude(self, task: TaskRequest) -> TaskResponse:
        """Execute task on Claude (placeholder for actual implementation)"""
        # This would connect to actual Claude API
        # For now, return a mock response
        return TaskResponse(
            id=task.id,
            executor="claude",
            result={"message": "Claude execution placeholder"},
            tokens_used=task.estimated_tokens,
            duration=1.0,
            confidence=0.95
        )
    
    async def _execute_hybrid(
        self,
        task: TaskRequest,
        decomposition: TaskDecomposition
    ) -> TaskResponse:
        """Execute task using hybrid approach"""
        
        start_time = time.time()
        local_results = []
        claude_results = []
        
        # Execute local tasks
        for local_task in decomposition.local_tasks:
            result = await self._execute_local(local_task)
            local_results.append(result)
        
        # Execute Claude tasks
        for claude_task in decomposition.claude_tasks:
            # Add context from local results if needed
            if local_results:
                claude_task.context = {
                    "local_results": [r.result for r in local_results]
                }
            result = await self._execute_claude(claude_task)
            claude_results.append(result)
        
        # Synthesize results
        synthesis = self._synthesize_results(
            task,
            local_results,
            claude_results,
            decomposition
        )
        
        total_tokens = sum(r.tokens_used for r in local_results + claude_results)
        
        return TaskResponse(
            id=task.id,
            executor="hybrid",
            result=synthesis,
            tokens_used=total_tokens,
            duration=time.time() - start_time,
            confidence=0.85
        )
    
    def _synthesize_results(
        self,
        original_task: TaskRequest,
        local_results: List[TaskResponse],
        claude_results: List[TaskResponse],
        decomposition: TaskDecomposition
    ) -> Dict:
        """Synthesize results from hybrid execution"""
        
        synthesis = {
            "task_id": original_task.id,
            "task_type": original_task.type,
            "execution_mode": "hybrid",
            "local_contributions": [],
            "claude_contributions": [],
            "final_result": None
        }
        
        # Collect local contributions
        for result in local_results:
            if result.result:
                synthesis["local_contributions"].append({
                    "task_id": result.id,
                    "result": result.result,
                    "confidence": result.confidence
                })
        
        # Collect Claude contributions
        for result in claude_results:
            if result.result:
                synthesis["claude_contributions"].append({
                    "task_id": result.id,
                    "result": result.result,
                    "confidence": result.confidence
                })
        
        # Determine final result based on priority
        if decomposition.claude_priority:
            # Claude's results are primary
            synthesis["final_result"] = claude_results[-1].result if claude_results else None
        else:
            # Combine both results
            synthesis["final_result"] = {
                "data": local_results[-1].result if local_results else None,
                "analysis": claude_results[-1].result if claude_results else None
            }
        
        return synthesis
    
    def get_delegation_stats(self) -> Dict:
        """Get statistics about delegation decisions"""
        stats = {
            "total_tasks": len(self.delegation_history),
            "by_executor": {
                "claude": 0,
                "local": 0,
                "hybrid": 0
            },
            "by_complexity": {
                "MECHANICAL": 0,
                "ANALYTICAL": 0,
                "REASONING": 0,
                "CREATIVE": 0,
                "STRATEGIC": 0
            },
            "context_usage": {
                "claude": self.context_state.claude_usage,
                "local": self.context_state.local_usage
            }
        }
        
        for entry in self.delegation_history:
            decision = entry["decision"]
            stats["by_executor"][decision.executor.value] += 1
            
            # Note: Would need task complexity tracking for full stats
        
        return stats


# Example usage
async def main():
    """Example of using the Delegation Engine"""
    engine = CognitiveDelegationEngine()
    await engine.initialize()
    
    # Test different task types
    tasks = [
        TaskRequest(
            id="task-001",
            type="file_search",
            description="Search for all Python files in the project",
            estimated_tokens=50000,  # Heavy but simple
            required_tools=["file_operations"]
        ),
        TaskRequest(
            id="task-002",
            type="algorithm_design",
            description="Design a new caching algorithm for our system",
            estimated_tokens=10000,  # Light but complex
            required_tools=[]
        ),
        TaskRequest(
            id="task-003",
            type="system_design",
            description="Design microservices architecture for e-commerce platform",
            estimated_tokens=150000,  # Heavy and complex
            required_tools=["mcp_server"]
        )
    ]
    
    for task in tasks:
        decision = await engine.decide_delegation(task)
        print(f"\nTask: {task.id} ({task.type})")
        print(f"Complexity: {task.complexity.name if task.complexity else 'Unknown'}")
        print(f"Tokens: {task.estimated_tokens}")
        print(f"Decision: {decision.executor.value}")
        print(f"Reason: {decision.reason}")
        print(f"Confidence: {decision.confidence:.2%}")
        
        if decision.decomposition:
            print(f"Decomposed into {len(decision.decomposition.local_tasks)} local tasks")
            print(f"and {len(decision.decomposition.claude_tasks)} Claude tasks")
    
    # Show stats
    print("\n=== Delegation Statistics ===")
    stats = engine.get_delegation_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(main())