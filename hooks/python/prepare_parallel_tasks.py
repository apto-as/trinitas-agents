#!/usr/bin/env python3
"""
Trinitas Prepare Parallel Tasks Hook
Springfield: "戦略的にタスクを分割し、各エージェントの強みを最大限に活用します"
Krukai: "効率的なタスク配分で、並列処理のパフォーマンスを最大化するわ"
Vector: "……タスクの依存関係を分析し、安全な並列実行を保証する……"
"""

import json
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# =====================================================
# Agent Capabilities Definition
# =====================================================

AGENT_CAPABILITIES = {
    "trinitas-coordinator": {
        "strengths": ["comprehensive analysis", "multi-perspective", "integration"],
        "keywords": ["analyze", "review", "evaluate", "assess", "coordinate"],
        "max_parallel": 1,  # Usually run solo for final integration
    },
    "springfield-strategist": {
        "strengths": ["planning", "architecture", "strategy", "user experience"],
        "keywords": ["plan", "design", "strategy", "roadmap", "architecture"],
        "max_parallel": 2,
    },
    "krukai-optimizer": {
        "strengths": ["optimization", "performance", "code quality", "efficiency"],
        "keywords": ["optimize", "performance", "refactor", "improve", "efficiency"],
        "max_parallel": 3,
    },
    "vector-auditor": {
        "strengths": ["security", "risk", "vulnerability", "compliance"],
        "keywords": ["security", "audit", "risk", "vulnerability", "compliance"],
        "max_parallel": 2,
    },
    "trinitas-quality": {
        "strengths": ["testing", "quality assurance", "validation"],
        "keywords": ["test", "qa", "quality", "validate", "verify"],
        "max_parallel": 3,
    },
    "trinitas-workflow": {
        "strengths": ["workflow", "automation", "pipeline", "process"],
        "keywords": ["workflow", "automate", "pipeline", "process", "ci/cd"],
        "max_parallel": 2,
    },
}

# =====================================================
# Task Analysis and Splitting
# =====================================================


class ParallelTaskPreparer:
    """Prepares tasks for parallel agent execution"""

    def __init__(self, user_prompt: str, context: Dict[str, Any]):
        self.user_prompt = user_prompt
        self.context = context
        self.session_id = (
            datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        )
        self.tasks = []

    def analyze_prompt(self) -> Dict[str, Any]:
        """Analyze the user prompt to determine parallelization strategy"""
        analysis = {
            "complexity": self._assess_complexity(),
            "suitable_agents": self._identify_suitable_agents(),
            "parallelizable": False,
            "recommended_strategy": "single",
            "estimated_speedup": 1.0,
        }

        # Determine if parallel execution would be beneficial
        if analysis["complexity"] >= 3 and len(analysis["suitable_agents"]) >= 2:
            analysis["parallelizable"] = True
            analysis["recommended_strategy"] = "parallel"
            analysis["estimated_speedup"] = min(
                len(analysis["suitable_agents"]) * 0.7, 2.5
            )

        return analysis

    def _assess_complexity(self) -> int:
        """Assess task complexity on a scale of 1-5"""
        complexity = 1

        # Length-based complexity
        word_count = len(self.user_prompt.split())
        if word_count > 50:
            complexity += 1
        if word_count > 100:
            complexity += 1

        # Multi-aspect indicators
        multi_aspect_keywords = ["and", "also", "additionally", "furthermore", "plus"]
        if any(
            keyword in self.user_prompt.lower() for keyword in multi_aspect_keywords
        ):
            complexity += 1

        # Technical depth indicators
        technical_keywords = [
            "optimize",
            "analyze",
            "security",
            "architecture",
            "performance",
        ]
        if (
            sum(
                1
                for keyword in technical_keywords
                if keyword in self.user_prompt.lower()
            )
            >= 2
        ):
            complexity += 1

        return min(complexity, 5)

    def _identify_suitable_agents(self) -> List[str]:
        """Identify which agents would be suitable for this task"""
        suitable_agents = []
        prompt_lower = self.user_prompt.lower()

        for agent, config in AGENT_CAPABILITIES.items():
            # Check keyword matches
            keyword_matches = sum(
                1 for keyword in config["keywords"] if keyword in prompt_lower
            )

            # Check strength relevance
            strength_matches = sum(
                1
                for strength in config["strengths"]
                for word in strength.split()
                if word in prompt_lower
            )

            if keyword_matches >= 1 or strength_matches >= 2:
                suitable_agents.append(agent)

        # Always consider coordinator for complex tasks
        if len(suitable_agents) >= 2 and "trinitas-coordinator" not in suitable_agents:
            suitable_agents.append("trinitas-coordinator")

        return suitable_agents

    def prepare_parallel_tasks(self) -> List[Dict[str, Any]]:
        """Prepare tasks for parallel execution"""
        analysis = self.analyze_prompt()

        if not analysis["parallelizable"]:
            return []  # No parallel execution needed

        # Create specialized prompts for each agent
        for agent in analysis["suitable_agents"]:
            if agent == "trinitas-coordinator":
                # Coordinator runs last to integrate results
                continue

            task = self._create_agent_task(agent)
            if task:
                self.tasks.append(task)

        # Add coordinator task if multiple agents are involved
        if len(self.tasks) >= 2:
            coordinator_task = self._create_coordinator_task()
            self.tasks.append(coordinator_task)

        # Set parallel execution metadata
        for task in self.tasks:
            task["metadata"]["session_id"] = self.session_id
            task["metadata"]["total_tasks"] = len(self.tasks)

        return self.tasks

    def _create_agent_task(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Create a specialized task for a specific agent"""
        AGENT_CAPABILITIES[agent_type]

        # Create agent-specific prompt
        agent_prompt = self._specialize_prompt_for_agent(agent_type)

        if not agent_prompt:
            return None

        task = {
            "agent_type": agent_type,
            "prompt": agent_prompt,
            "priority": self._calculate_priority(agent_type),
            "metadata": {
                "original_prompt": self.user_prompt,
                "task_id": f"{agent_type}_{uuid.uuid4().hex[:8]}",
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
        }

        return task

    def _specialize_prompt_for_agent(self, agent_type: str) -> str:
        """Create an agent-specific version of the prompt"""
        base_prompt = self.user_prompt

        specializations = {
            "springfield-strategist": (
                f"From a strategic planning and architecture perspective:\n{base_prompt}\n\n"
                "Focus on: long-term vision, team coordination, user experience, and project roadmap."
            ),
            "krukai-optimizer": (
                f"From a technical optimization perspective:\n{base_prompt}\n\n"
                "Focus on: performance optimization, code quality, efficiency improvements, and technical excellence."
            ),
            "vector-auditor": (
                f"From a security and risk perspective:\n{base_prompt}\n\n"
                "Focus on: security vulnerabilities, risk assessment, compliance issues, and defensive measures."
            ),
            "trinitas-quality": (
                f"From a quality assurance perspective:\n{base_prompt}\n\n"
                "Focus on: test coverage, validation strategies, quality metrics, and verification methods."
            ),
            "trinitas-workflow": (
                f"From a workflow automation perspective:\n{base_prompt}\n\n"
                "Focus on: process optimization, automation opportunities, pipeline design, and workflow efficiency."
            ),
        }

        return specializations.get(agent_type, base_prompt)

    def _create_coordinator_task(self) -> Dict[str, Any]:
        """Create a task for the coordinator to integrate results"""
        task = {
            "agent_type": "trinitas-coordinator",
            "prompt": (
                f"Integrate and synthesize the parallel analysis results for:\n{self.user_prompt}\n\n"
                "Combine insights from all agents into a cohesive response that:\n"
                "1. Highlights consensus and divergent viewpoints\n"
                "2. Provides actionable recommendations\n"
                "3. Identifies critical risks and opportunities\n"
                "4. Presents a unified strategic direction"
            ),
            "priority": 0,  # Highest priority (runs last)
            "metadata": {
                "original_prompt": self.user_prompt,
                "task_id": f"coordinator_{uuid.uuid4().hex[:8]}",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "depends_on": [t["metadata"]["task_id"] for t in self.tasks],
            },
        }

        return task

    def _calculate_priority(self, agent_type: str) -> int:
        """Calculate execution priority (lower number = higher priority)"""
        # Default priorities
        priorities = {
            "vector-auditor": 1,  # Security first
            "krukai-optimizer": 2,
            "springfield-strategist": 3,
            "trinitas-quality": 4,
            "trinitas-workflow": 5,
            "trinitas-coordinator": 0,  # Always last
        }

        return priorities.get(agent_type, 10)


# =====================================================
# Hook Output Generation
# =====================================================


def generate_hook_output(
    tasks: List[Dict[str, Any]], session_id: str
) -> Dict[str, Any]:
    """Generate the hook output with parallel task information"""
    if not tasks:
        return {}

    # Set environment variables for downstream hooks
    os.environ["TRINITAS_SESSION_ID"] = session_id
    os.environ["TRINITAS_PARALLEL_COUNT"] = str(len(tasks))

    # Generate hook response
    hook_output = {
        "systemMessage": (
            f"🔄 Trinitas: 並列実行を準備しました\n"
            f"Session: {session_id}\n"
            f"Agents: {', '.join(t['agent_type'] for t in tasks)}\n"
            f"推定高速化: {len(tasks) * 0.7:.1f}x"
        ),
        "hookSpecificOutput": {
            "parallel_tasks": tasks,
            "session_id": session_id,
            "execution_strategy": "parallel",
        },
    }

    return hook_output


# =====================================================
# Main Execution
# =====================================================


def main():
    """Main entry point for the hook"""
    # Get environment variables
    user_prompt = os.environ.get("CLAUDE_USER_PROMPT", "")
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")

    # Only process for Task tool
    if tool_name != "Task":
        print("{}")
        return 0

    # Check if parallel execution is enabled
    if os.environ.get("TRINITAS_PARALLEL_ENABLED", "true").lower() != "true":
        print("{}")
        return 0

    # Create task preparer
    preparer = ParallelTaskPreparer(
        user_prompt,
        {
            "project_dir": os.environ.get("CLAUDE_PROJECT_DIR", ""),
            "request_id": os.environ.get("CLAUDE_REQUEST_ID", ""),
        },
    )

    # Analyze and prepare tasks
    tasks = preparer.prepare_parallel_tasks()

    if tasks:
        # Generate and output hook response
        output = generate_hook_output(tasks, preparer.session_id)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # No parallel execution needed
        print("{}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
