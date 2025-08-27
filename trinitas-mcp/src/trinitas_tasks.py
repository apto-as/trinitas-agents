#!/usr/bin/env python3
"""
Trinitas Task Processing Tools
並列実行、連鎖実行などのタスク処理をMCP toolsとして実装
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

class TrinitasTaskProcessor:
    """Trinitas task processing via MCP tools"""
    
    def __init__(self):
        self.claude_home = Path.home() / ".claude"
        self.agents_dir = self.claude_home / "agents"
        self.load_persona_definitions()
        
    def load_persona_definitions(self):
        """Load persona definitions from YAML"""
        try:
            definitions_path = self.claude_home / "trinitas" / "TRINITAS_PERSONA_DEFINITIONS.yaml"
            if definitions_path.exists():
                with open(definitions_path, 'r', encoding='utf-8') as f:
                    self.personas = yaml.safe_load(f).get('personas', {})
                logger.info(f"Loaded {len(self.personas)} persona definitions")
            else:
                # デフォルト定義
                self.personas = {
                    'athena': {'display_name': 'Athena', 'role': 'Strategic Architect'},
                    'artemis': {'display_name': 'Artemis', 'role': 'Technical Perfectionist'},
                    'hestia': {'display_name': 'Hestia', 'role': 'Security Guardian'}
                }
                logger.warning("Using default persona definitions")
        except Exception as e:
            logger.error(f"Error loading personas: {e}")
            self.personas = {}
    
    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        複数のペルソナを並列実行
        
        Args:
            tasks: List of task definitions
                [
                    {"persona": "athena", "task": "Design the architecture"},
                    {"persona": "artemis", "task": "Optimize performance"},
                    {"persona": "hestia", "task": "Check security"}
                ]
        
        Returns:
            Combined results from all personas
        """
        logger.info(f"Executing {len(tasks)} tasks in parallel")
        
        async def execute_single(task_def):
            persona = task_def.get('persona')
            task = task_def.get('task')
            
            # エージェントファイル読み込み
            agent_file = self.agents_dir / f"{persona}-*.md"
            agent_files = list(self.agents_dir.glob(f"{persona}-*.md"))
            
            if not agent_files:
                return {
                    'persona': persona,
                    'error': f"Agent file not found for {persona}",
                    'task': task
                }
            
            # シミュレート応答（実際にはLLMを呼ぶ）
            return {
                'persona': persona,
                'task': task,
                'response': f"{self.personas.get(persona, {}).get('display_name', persona)} analyzed: {task}",
                'status': 'completed'
            }
        
        # 並列実行
        results = await asyncio.gather(*[execute_single(task) for task in tasks])
        
        return {
            'execution_mode': 'parallel',
            'task_count': len(tasks),
            'results': results,
            'status': 'completed'
        }
    
    async def execute_chain(self, chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ペルソナを連鎖的に実行（前の結果を次に渡す）
        
        Args:
            chain: Chain of persona executions
                [
                    {"persona": "athena", "task": "Initial analysis"},
                    {"persona": "artemis", "task": "Technical refinement"},
                    {"persona": "hestia", "task": "Final security check"}
                ]
        
        Returns:
            Chain execution results
        """
        logger.info(f"Executing chain of {len(chain)} tasks")
        
        results = []
        previous_output = None
        
        for step in chain:
            persona = step.get('persona')
            task = step.get('task')
            
            # 前の結果を含めてタスクを構築
            if previous_output:
                task = f"{task}\n\nPrevious analysis:\n{previous_output}"
            
            # シミュレート応答
            response = f"{self.personas.get(persona, {}).get('display_name', persona)} processed: {task}"
            
            results.append({
                'persona': persona,
                'task': step.get('task'),  # 元のタスク
                'response': response,
                'step': len(results) + 1
            })
            
            previous_output = response
        
        return {
            'execution_mode': 'chain',
            'step_count': len(chain),
            'results': results,
            'final_output': previous_output,
            'status': 'completed'
        }
    
    async def execute_consensus(self, task: str) -> Dict[str, Any]:
        """
        三位一体の合意形成実行
        
        Args:
            task: Task for consensus building
        
        Returns:
            Consensus results from all three personas
        """
        logger.info(f"Building consensus for: {task}")
        
        # 全ペルソナで並列実行
        parallel_tasks = [
            {"persona": "athena", "task": task},
            {"persona": "artemis", "task": task},
            {"persona": "hestia", "task": task}
        ]
        
        parallel_results = await self.execute_parallel(parallel_tasks)
        
        # 合意形成シミュレート
        consensus = {
            'execution_mode': 'consensus',
            'task': task,
            'individual_views': parallel_results['results'],
            'consensus': 'All three personas agree on the approach with minor adjustments',
            'unified_recommendation': 'Proceed with implementation considering all perspectives',
            'status': 'completed'
        }
        
        return consensus
    
    async def execute_specialized(self, task: str, required_expertise: List[str]) -> Dict[str, Any]:
        """
        特定の専門性を持つペルソナのみ実行
        
        Args:
            task: Task description
            required_expertise: List of required expertise areas
        
        Returns:
            Specialized execution results
        """
        expertise_map = {
            'strategy': 'athena',
            'architecture': 'athena',
            'optimization': 'artemis',
            'performance': 'artemis',
            'security': 'hestia',
            'risk': 'hestia'
        }
        
        # 必要なペルソナを特定
        selected_personas = set()
        for expertise in required_expertise:
            if expertise.lower() in expertise_map:
                selected_personas.add(expertise_map[expertise.lower()])
        
        if not selected_personas:
            # デフォルトで全員
            selected_personas = {'athena', 'artemis', 'hestia'}
        
        # 選ばれたペルソナで実行
        tasks = [{"persona": p, "task": task} for p in selected_personas]
        
        results = await self.execute_parallel(tasks)
        results['selected_for_expertise'] = list(selected_personas)
        results['required_expertise'] = required_expertise
        
        return results


# MCP Server Integration
async def register_mcp_tools(server):
    """Register Trinitas task tools with MCP server"""
    
    processor = TrinitasTaskProcessor()
    
    @server.call_tool()
    async def trinitas_parallel(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple personas in parallel"""
        return await processor.execute_parallel(tasks)
    
    @server.call_tool()
    async def trinitas_chain(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute personas in sequence, passing results forward"""
        return await processor.execute_chain(chain)
    
    @server.call_tool()
    async def trinitas_consensus(task: str) -> Dict[str, Any]:
        """Build consensus from all three personas"""
        return await processor.execute_consensus(task)
    
    @server.call_tool()
    async def trinitas_specialized(task: str, expertise: List[str]) -> Dict[str, Any]:
        """Execute with specialized expertise selection"""
        return await processor.execute_specialized(task, expertise)
    
    logger.info("Trinitas task processing tools registered")


if __name__ == "__main__":
    # テスト実行
    async def test():
        processor = TrinitasTaskProcessor()
        
        print("\n=== Parallel Execution Test ===")
        result = await processor.execute_parallel([
            {"persona": "athena", "task": "Design system architecture"},
            {"persona": "artemis", "task": "Optimize algorithms"},
            {"persona": "hestia", "task": "Audit security"}
        ])
        print(f"Results: {result['results']}")
        
        print("\n=== Chain Execution Test ===")
        result = await processor.execute_chain([
            {"persona": "athena", "task": "Initial design"},
            {"persona": "artemis", "task": "Technical refinement"},
            {"persona": "hestia", "task": "Security validation"}
        ])
        print(f"Final output: {result['final_output']}")
        
        print("\n=== Consensus Test ===")
        result = await processor.execute_consensus("Should we use microservices?")
        print(f"Consensus: {result['consensus']}")
    
    asyncio.run(test())