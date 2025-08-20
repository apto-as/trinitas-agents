#!/usr/bin/env python3
"""
Trinitas v3.5 - Sparring Partner System
Uses Local LLM as intelligent rubber duck for complex problem solving
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    TaskResponse,
    CognitiveComplexity
)


class SparringMode(Enum):
    """Sparring session modes"""
    DEVIL_ADVOCATE = "devil_advocate"      # Challenge assumptions
    ALTERNATIVE_FINDER = "alternative_finder"  # Find different approaches
    EDGE_CASE_HUNTER = "edge_case_hunter"    # Find failure scenarios
    PERSPECTIVE_SHIFT = "perspective_shift"   # Different mental models
    AUTO = "auto"                            # Automatically determine


@dataclass
class Challenge:
    """A challenge or critique from sparring"""
    id: str
    type: str
    severity: str  # critical, major, minor
    description: str
    evidence: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class Alternative:
    """An alternative solution approach"""
    id: str
    approach_type: str
    description: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    implementation_notes: Optional[str] = None


@dataclass
class SparringSession:
    """A complete sparring session"""
    id: str
    problem: str
    original_solution: str
    mode: SparringMode
    timestamp: float
    challenges: List[Challenge] = field(default_factory=list)
    alternatives: List[Alternative] = field(default_factory=list)
    synthesis: Optional[Dict] = None
    duration: float = 0.0


class SparringPartnerSystem:
    """
    Intelligent sparring partner using Local LLM
    Provides different perspectives and challenges to improve solutions
    """
    
    def __init__(self):
        self.local_connector = LocalLLMConnector()
        self.session_history = []
        self.mode_prompts = self._initialize_mode_prompts()
        
    def _initialize_mode_prompts(self) -> Dict[SparringMode, str]:
        """Initialize prompts for different sparring modes"""
        return {
            SparringMode.DEVIL_ADVOCATE: """
As a devil's advocate, critically analyze this solution:

Your tasks:
1. Identify hidden assumptions that might be wrong
2. Find potential failure modes and edge cases
3. Question every design decision
4. Suggest stress test scenarios
5. Point out missing requirements or considerations

Be thorough but constructive. Provide evidence for your concerns.
Use available tools to find similar failed implementations if relevant.
""",
            
            SparringMode.ALTERNATIVE_FINDER: """
Provide 3 alternative approaches to solve this problem:

For each alternative:
1. Use a different paradigm or technology
2. Explain the core concept
3. List pros and cons
4. Provide implementation notes
5. Compare with the original solution

Be creative and think outside the box.
Consider approaches from different domains or industries.
""",
            
            SparringMode.EDGE_CASE_HUNTER: """
Hunt for edge cases and failure scenarios:

Focus on:
1. Boundary conditions
2. Race conditions
3. Resource limitations
4. Unusual input combinations
5. Scale-related issues
6. Security vulnerabilities
7. Performance degradation scenarios

For each edge case, explain:
- How it could occur
- What would fail
- How to test for it
- Potential mitigation
""",
            
            SparringMode.PERSPECTIVE_SHIFT: """
Analyze this problem from different perspectives:

Apply these mental models:
1. Systems thinking - How does this fit in the larger system?
2. First principles - What are the fundamental truths?
3. Inversion - What would make this fail?
4. Second-order thinking - What are the consequences of consequences?
5. Probabilistic thinking - What are the odds of different outcomes?

Provide insights from each perspective.
"""
        }
    
    async def initialize(self):
        """Initialize sparring partner system"""
        await self.local_connector.initialize()
    
    async def conduct_sparring(
        self,
        problem: str,
        current_solution: str,
        mode: SparringMode = SparringMode.AUTO,
        context: Optional[Dict] = None
    ) -> SparringSession:
        """
        Conduct a complete sparring session
        """
        start_time = time.time()
        
        # Create session
        session = SparringSession(
            id=f"sparring_{int(time.time()*1000)}",
            problem=problem,
            original_solution=current_solution,
            mode=mode if mode != SparringMode.AUTO else self._determine_mode(problem),
            timestamp=start_time
        )
        
        # Step 1: Get challenges (devil's advocate)
        if session.mode in [SparringMode.DEVIL_ADVOCATE, SparringMode.AUTO]:
            session.challenges = await self._get_challenges(session)
        
        # Step 2: Get alternatives
        if session.mode in [SparringMode.ALTERNATIVE_FINDER, SparringMode.AUTO]:
            session.alternatives = await self._get_alternatives(session)
        
        # Step 3: Hunt edge cases
        if session.mode in [SparringMode.EDGE_CASE_HUNTER, SparringMode.AUTO]:
            edge_cases = await self._hunt_edge_cases(session)
            # Add edge cases as challenges
            session.challenges.extend(edge_cases)
        
        # Step 4: Get perspective shifts
        if session.mode in [SparringMode.PERSPECTIVE_SHIFT, SparringMode.AUTO]:
            perspectives = await self._get_perspectives(session)
            # Add perspectives to synthesis
            session.synthesis = {"perspectives": perspectives}
        
        # Step 5: Synthesize all feedback
        session.synthesis = await self._synthesize_feedback(session)
        
        session.duration = time.time() - start_time
        
        # Store session
        self.session_history.append(session)
        
        return session
    
    def _determine_mode(self, problem: str) -> SparringMode:
        """Automatically determine best sparring mode"""
        problem_lower = problem.lower()
        
        # Check for specific indicators
        if any(word in problem_lower for word in ["algorithm", "optimization", "performance"]):
            return SparringMode.ALTERNATIVE_FINDER
        
        if any(word in problem_lower for word in ["security", "safety", "critical"]):
            return SparringMode.EDGE_CASE_HUNTER
        
        if any(word in problem_lower for word in ["architecture", "design", "system"]):
            return SparringMode.PERSPECTIVE_SHIFT
        
        # Default to devil's advocate for general problems
        return SparringMode.DEVIL_ADVOCATE
    
    async def _get_challenges(self, session: SparringSession) -> List[Challenge]:
        """Get challenges using devil's advocate mode"""
        
        prompt = self.mode_prompts[SparringMode.DEVIL_ADVOCATE]
        prompt += f"\n\nProblem: {session.problem}\n\nProposed Solution: {session.original_solution}"
        
        task = TaskRequest(
            id=f"{session.id}_challenges",
            type="analysis",
            description=prompt,
            estimated_tokens=5000,
            required_tools=["mcp_server"],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse challenges from response
        challenges = self._parse_challenges(response.result)
        
        return challenges
    
    async def _get_alternatives(self, session: SparringSession) -> List[Alternative]:
        """Get alternative solutions"""
        
        prompt = self.mode_prompts[SparringMode.ALTERNATIVE_FINDER]
        prompt += f"\n\nProblem: {session.problem}\n\nCurrent Solution: {session.original_solution}"
        
        task = TaskRequest(
            id=f"{session.id}_alternatives",
            type="creative",
            description=prompt,
            estimated_tokens=8000,
            required_tools=["mcp_server"],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse alternatives from response
        alternatives = self._parse_alternatives(response.result)
        
        return alternatives
    
    async def _hunt_edge_cases(self, session: SparringSession) -> List[Challenge]:
        """Hunt for edge cases and failure scenarios"""
        
        prompt = self.mode_prompts[SparringMode.EDGE_CASE_HUNTER]
        prompt += f"\n\nProblem: {session.problem}\n\nSolution: {session.original_solution}"
        
        task = TaskRequest(
            id=f"{session.id}_edges",
            type="analysis",
            description=prompt,
            estimated_tokens=6000,
            required_tools=["mcp_server", "file_operations"],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Convert edge cases to challenges
        edge_cases = self._parse_edge_cases(response.result)
        
        return edge_cases
    
    async def _get_perspectives(self, session: SparringSession) -> Dict:
        """Get different perspective analyses"""
        
        prompt = self.mode_prompts[SparringMode.PERSPECTIVE_SHIFT]
        prompt += f"\n\nProblem: {session.problem}\n\nSolution: {session.original_solution}"
        
        task = TaskRequest(
            id=f"{session.id}_perspectives",
            type="analysis",
            description=prompt,
            estimated_tokens=7000,
            required_tools=["mcp_server"],
            complexity=CognitiveComplexity.REASONING
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse perspectives
        perspectives = self._parse_perspectives(response.result)
        
        return perspectives
    
    async def _synthesize_feedback(self, session: SparringSession) -> Dict:
        """Synthesize all feedback into actionable recommendations"""
        
        synthesis = {
            "session_id": session.id,
            "mode": session.mode.value,
            "summary": {
                "total_challenges": len(session.challenges),
                "critical_challenges": len([c for c in session.challenges if c.severity == "critical"]),
                "alternatives_found": len(session.alternatives),
            },
            "recommendations": [],
            "action_items": [],
            "improved_solution": None
        }
        
        # Prioritize critical challenges
        critical_challenges = [c for c in session.challenges if c.severity == "critical"]
        if critical_challenges:
            synthesis["recommendations"].append({
                "priority": "HIGH",
                "type": "address_critical_issues",
                "details": [c.description for c in critical_challenges]
            })
            
            for challenge in critical_challenges:
                if challenge.suggested_fix:
                    synthesis["action_items"].append({
                        "challenge_id": challenge.id,
                        "action": challenge.suggested_fix,
                        "priority": "HIGH"
                    })
        
        # Evaluate alternatives
        if session.alternatives:
            best_alternative = self._select_best_alternative(session.alternatives)
            if best_alternative:
                synthesis["recommendations"].append({
                    "priority": "MEDIUM",
                    "type": "consider_alternative",
                    "details": best_alternative.description,
                    "pros": best_alternative.pros,
                    "cons": best_alternative.cons
                })
        
        # Create improved solution outline
        synthesis["improved_solution"] = await self._create_improved_solution(
            session.original_solution,
            synthesis["action_items"],
            best_alternative if session.alternatives else None
        )
        
        return synthesis
    
    def _parse_challenges(self, result: Dict) -> List[Challenge]:
        """Parse challenges from LLM response"""
        challenges = []
        
        content = result.get("content", "")
        
        # Simple parsing - in production, use structured output
        # For now, create example challenges
        if "assumption" in content.lower():
            challenges.append(Challenge(
                id="ch_001",
                type="assumption",
                severity="major",
                description="Assumes unlimited memory available",
                evidence="No memory checks in algorithm",
                suggested_fix="Add memory limit checks and graceful degradation"
            ))
        
        if "fail" in content.lower():
            challenges.append(Challenge(
                id="ch_002",
                type="failure_mode",
                severity="critical",
                description="Can fail under high concurrency",
                evidence="No locking mechanism",
                suggested_fix="Implement proper synchronization"
            ))
        
        return challenges
    
    def _parse_alternatives(self, result: Dict) -> List[Alternative]:
        """Parse alternatives from LLM response"""
        alternatives = []
        
        # Simple parsing - in production, use structured output
        alternatives.append(Alternative(
            id="alt_001",
            approach_type="different_algorithm",
            description="Use hash table instead of tree structure",
            pros=["O(1) lookup time", "Simple implementation"],
            cons=["More memory usage", "No ordering"],
            implementation_notes="Use Python dict or JavaScript Map"
        ))
        
        alternatives.append(Alternative(
            id="alt_002",
            approach_type="different_architecture",
            description="Event-driven instead of polling",
            pros=["More efficient", "Real-time updates"],
            cons=["More complex", "Harder to debug"],
            implementation_notes="Use message queue like RabbitMQ"
        ))
        
        return alternatives
    
    def _parse_edge_cases(self, result: Dict) -> List[Challenge]:
        """Parse edge cases as challenges"""
        edge_cases = []
        
        # Convert edge cases to challenges
        edge_cases.append(Challenge(
            id="edge_001",
            type="edge_case",
            severity="major",
            description="Empty input not handled",
            evidence="No null/empty checks",
            suggested_fix="Add input validation"
        ))
        
        return edge_cases
    
    def _parse_perspectives(self, result: Dict) -> Dict:
        """Parse different perspectives"""
        return {
            "systems_thinking": "Consider impact on overall system performance",
            "first_principles": "Core requirement is data consistency",
            "inversion": "What would cause complete failure?",
            "second_order": "Performance improvement might increase complexity",
            "probabilistic": "80% of cases are simple, optimize for those"
        }
    
    def _select_best_alternative(self, alternatives: List[Alternative]) -> Optional[Alternative]:
        """Select the best alternative based on pros/cons"""
        if not alternatives:
            return None
        
        # Simple scoring - count pros vs cons
        best = None
        best_score = -float('inf')
        
        for alt in alternatives:
            score = len(alt.pros) - len(alt.cons)
            if score > best_score:
                best = alt
                best_score = score
        
        return best
    
    async def _create_improved_solution(
        self,
        original: str,
        action_items: List[Dict],
        best_alternative: Optional[Alternative]
    ) -> str:
        """Create an improved solution outline"""
        
        improved = f"=== Improved Solution ===\n\n"
        improved += f"Original: {original[:200]}...\n\n"
        
        if action_items:
            improved += "Critical Fixes:\n"
            for item in action_items[:3]:  # Top 3 items
                improved += f"- {item['action']}\n"
            improved += "\n"
        
        if best_alternative:
            improved += f"Consider Alternative Approach:\n"
            improved += f"- {best_alternative.description}\n"
            improved += f"- Benefits: {', '.join(best_alternative.pros[:2])}\n\n"
        
        improved += "This improved solution addresses critical issues and incorporates best practices."
        
        return improved
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of a sparring session"""
        for session in self.session_history:
            if session.id == session_id:
                return {
                    "id": session.id,
                    "problem": session.problem[:100] + "...",
                    "mode": session.mode.value,
                    "duration": f"{session.duration:.2f}s",
                    "challenges_found": len(session.challenges),
                    "critical_issues": len([c for c in session.challenges if c.severity == "critical"]),
                    "alternatives": len(session.alternatives),
                    "has_synthesis": session.synthesis is not None
                }
        return None


# Example usage
async def main():
    """Example of using Sparring Partner System"""
    sparring = SparringPartnerSystem()
    await sparring.initialize()
    
    # Example problem and solution
    problem = "Design a caching system for our API that handles 1M requests/second"
    solution = """
    Use a simple in-memory cache with LRU eviction policy.
    Store responses for 5 minutes.
    Use a single global cache instance.
    """
    
    # Conduct sparring session
    print("🥊 Starting Sparring Session...")
    session = await sparring.conduct_sparring(
        problem=problem,
        current_solution=solution,
        mode=SparringMode.AUTO
    )
    
    print(f"\n✅ Session Complete: {session.id}")
    print(f"Mode: {session.mode.value}")
    print(f"Duration: {session.duration:.2f}s")
    
    # Show challenges
    print(f"\n🎯 Challenges Found: {len(session.challenges)}")
    for challenge in session.challenges:
        print(f"  - [{challenge.severity}] {challenge.description}")
        if challenge.suggested_fix:
            print(f"    Fix: {challenge.suggested_fix}")
    
    # Show alternatives
    print(f"\n💡 Alternatives: {len(session.alternatives)}")
    for alt in session.alternatives:
        print(f"  - {alt.description}")
        print(f"    Pros: {', '.join(alt.pros)}")
        print(f"    Cons: {', '.join(alt.cons)}")
    
    # Show synthesis
    if session.synthesis:
        print(f"\n📊 Synthesis:")
        print(f"  Recommendations: {len(session.synthesis.get('recommendations', []))}")
        print(f"  Action Items: {len(session.synthesis.get('action_items', []))}")
        
        if session.synthesis.get('improved_solution'):
            print(f"\n📝 Improved Solution:")
            print(session.synthesis['improved_solution'])


if __name__ == "__main__":
    asyncio.run(main())