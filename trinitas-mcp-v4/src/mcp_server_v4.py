#!/usr/bin/env python3
"""
Trinitas v4.0 MCP Server
Memory and Learning Focused Implementation with FastMCP
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import v4.0 components
from bellona_distributor import BellonaTaskDistributor, TaskDistribution
from seshat_monitor import SeshatMemoryMonitor
from memory_manager_v4 import EnhancedMemoryManager
from learning_system import LearningSystem

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name="Trinitas v4.0 Memory System",
    version="4.0.0"
)

class TrinitasV4Core:
    """
    Core v4.0 functionality - Memory and Learning focused
    五位一体の統合知能をメモリと学習に特化
    """
    
    def __init__(self):
        """Initialize Trinitas v4.0 Core"""
        logger.info("Initializing Trinitas v4.0 Core...")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.memory_manager = EnhancedMemoryManager(self.config)
        self.learning_system = LearningSystem(self.config)
        self.bellona_distributor = BellonaTaskDistributor(self.config)
        self.seshat_monitor = SeshatMemoryMonitor(self.config)
        
        # Check Local LLM status
        self.local_llm_enabled = os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true"
        
        logger.info(f"Trinitas v4.0 Core initialized - LLM: {'Enabled' if self.local_llm_enabled else 'Disabled'}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment"""
        return {
            "mode": os.getenv("TRINITAS_MODE", "memory_focused"),
            "memory": {
                "backend": os.getenv("MEMORY_BACKEND", "hybrid"),
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                "chromadb_path": os.getenv("CHROMADB_PATH", "./chromadb_data"),
                "sqlite_path": os.getenv("SQLITE_PATH", "./sqlite_data.db"),
                "auto_optimize": os.getenv("SESHAT_AUTO_OPTIMIZE", "true").lower() == "true"
            },
            "learning": {
                "enabled": os.getenv("LEARNING_ENABLED", "true").lower() == "true",
                "storage": os.getenv("LEARNING_STORAGE", "./learning_data"),
                "auto_learn": os.getenv("AUTO_LEARN", "true").lower() == "true",
                "pattern_recognition": os.getenv("PATTERN_RECOGNITION", "true").lower() == "true"
            },
            "local_llm": {
                "enabled": os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true",
                "endpoint": os.getenv("LOCAL_LLM_ENDPOINT", "http://192.168.99.102:1234/v1/"),
                "model": os.getenv("LOCAL_LLM_MODEL", "auto"),
                "distribution": {
                    "max_parallel_tasks": int(os.getenv("LLM_MAX_PARALLEL_TASKS", "3")),
                    "priority_threshold": float(os.getenv("LLM_PRIORITY_THRESHOLD", "0.3")),
                    "task_types": os.getenv("LLM_TASK_TYPES", "").split(",")
                }
            },
            "personas": {
                "seshat": {
                    "reporting_interval": int(os.getenv("SESHAT_REPORTING_INTERVAL", "300"))
                }
            }
        }
    
    async def process_with_memory(self, persona: str, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Process task with memory context
        メモリコンテキストを使用してタスクを処理
        """
        start_time = datetime.now()
        
        try:
            # Seshat monitors memory usage
            usage_pattern = await self.seshat_monitor.analyze_usage_pattern(persona, task, context)
            logger.info(f"Seshat analysis: {usage_pattern['optimization_suggestions']}")
            
            # Retrieve relevant memories
            memory_context = await self.memory_manager.get_context(persona, task)
            
            # Bellona's task distribution decision
            distribution = await self.bellona_distributor.evaluate_task(task, context)
            
            if distribution.send_to_llm and self.local_llm_enabled:
                logger.info(f"Bellona decision: Sending to Local LLM - {distribution.reason}")
                result = await self._process_with_local_llm(task, distribution, memory_context)
            else:
                if not self.local_llm_enabled:
                    # When LLM is OFF, Bellona manages memory with Seshat
                    await self.bellona_distributor.optimize_memory_with_seshat(
                        self.memory_manager, 
                        self.seshat_monitor
                    )
                
                # Process with main system
                result = await self._execute_persona_task(persona, task, memory_context)
            
            # Learn from execution
            if self.config["learning"]["auto_learn"]:
                await self.learning_system.learn_from_execution(persona, task, result)
            
            # Store result in memory
            await self.memory_manager.store_result(persona, task, result)
            
            # Release LLM task slot if used
            if distribution.send_to_llm:
                await self.bellona_distributor.release_task(distribution.task_id)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "persona": persona,
                "result": result,
                "distribution": {
                    "processor": distribution.assigned_processor,
                    "priority": distribution.priority
                },
                "memory_usage": usage_pattern,
                "execution_time_seconds": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in process_with_memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "persona": persona,
                "task": task[:100]  # Truncate for safety
            }
    
    async def _process_with_local_llm(self, task: str, distribution: TaskDistribution, context: Dict) -> Dict:
        """Process task with Local LLM"""
        # TODO: Implement actual Local LLM integration
        logger.info(f"Processing with Local LLM: {distribution.task_id}")
        
        # Placeholder implementation
        return {
            "type": "llm_result",
            "task_id": distribution.task_id,
            "content": f"LLM processed: {task[:50]}...",
            "processor": "local_llm",
            "tokens_used": distribution.estimated_tokens
        }
    
    async def _execute_persona_task(self, persona: str, task: str, context: Dict) -> Dict:
        """Execute task with specified persona"""
        logger.info(f"Executing with {persona}: {task[:100]}")
        
        # Persona-specific processing
        persona_responses = {
            "athena": f"戦略的分析完了: {task}",
            "artemis": f"技術的最適化完了: {task}",
            "hestia": f"セキュリティ検証完了: {task}",
            "bellona": f"戦術的調整完了: {task}",
            "seshat": f"文書化完了: {task}"
        }
        
        return {
            "persona": persona,
            "response": persona_responses.get(persona, f"処理完了: {task}"),
            "context_used": bool(context),
            "memory_sections": list(context.keys()) if context else []
        }

# Initialize Trinitas Core
trinitas_core = TrinitasV4Core()

# ===== MCP Tool Definitions =====

@mcp.tool
async def memory_store(
    key: str,
    value: Any,
    persona: Optional[str] = None,
    importance: float = 0.5,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Store information in memory system
    メモリシステムに情報を保存
    
    Args:
        key: Memory key
        value: Value to store
        persona: Associated persona (optional)
        importance: Importance level (0.0-1.0)
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Storing memory: {key} (importance: {importance})")
        
        result = await trinitas_core.memory_manager.store(
            key=key,
            value=value,
            metadata={
                "persona": persona,
                "importance": importance,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "key": key,
            "stored": True,
            "importance": importance,
            "persona": persona
        }
    except Exception as e:
        logger.error(f"Memory store error: {e}")
        if ctx:
            await ctx.error(f"Failed to store memory: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def memory_recall(
    query: str,
    semantic: bool = False,
    persona: Optional[str] = None,
    limit: int = 10,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Recall information from memory system
    メモリシステムから情報を取得
    
    Args:
        query: Search query
        semantic: Use semantic search
        persona: Filter by persona
        limit: Maximum results
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Recalling memory: {query} (semantic: {semantic})")
        
        results = await trinitas_core.memory_manager.recall(
            query=query,
            semantic=semantic,
            filters={"persona": persona} if persona else None,
            limit=limit
        )
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "semantic": semantic
        }
    except Exception as e:
        logger.error(f"Memory recall error: {e}")
        if ctx:
            await ctx.error(f"Failed to recall memory: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def execute_with_memory(
    persona: str,
    task: str,
    use_llm: Optional[bool] = None,
    context: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Execute task with memory-focused processing
    メモリフォーカス処理でタスクを実行
    
    Args:
        persona: Persona to use
        task: Task to execute
        use_llm: Force LLM usage (override Bellona's decision)
        context: Additional context
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Executing with {persona}: {task[:100]}")
        
        # Override LLM decision if specified
        if use_llm is not None and context is None:
            context = {}
        if use_llm is not None:
            context["force_llm"] = use_llm
        
        result = await trinitas_core.process_with_memory(persona, task, context)
        
        return result
    except Exception as e:
        logger.error(f"Execution error: {e}")
        if ctx:
            await ctx.error(f"Failed to execute: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def learning_apply(
    pattern: str,
    task: str,
    context: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Apply learned patterns to task
    学習パターンをタスクに適用
    
    Args:
        pattern: Pattern to apply
        task: Task to apply pattern to
        context: Additional context
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Applying pattern: {pattern}")
        
        result = await trinitas_core.learning_system.apply_pattern(
            pattern=pattern,
            task=task,
            context=context or {}
        )
        
        return {
            "success": True,
            "pattern": pattern,
            "applied": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Learning apply error: {e}")
        if ctx:
            await ctx.error(f"Failed to apply pattern: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def get_status(
    component: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get system status
    システムステータスを取得
    
    Args:
        component: Specific component (bellona, seshat, memory, learning, all)
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Getting status: {component or 'all'}")
        
        status = {
            "mode": trinitas_core.config["mode"],
            "local_llm_enabled": trinitas_core.local_llm_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
        if component in [None, "all", "bellona"]:
            status["bellona"] = trinitas_core.bellona_distributor.get_status()
        
        if component in [None, "all", "seshat"]:
            status["seshat"] = trinitas_core.seshat_monitor.get_status()
        
        if component in [None, "all", "memory"]:
            status["memory"] = await trinitas_core.memory_manager.get_status()
        
        if component in [None, "all", "learning"]:
            status["learning"] = await trinitas_core.learning_system.get_status()
        
        return status
    except Exception as e:
        logger.error(f"Status error: {e}")
        if ctx:
            await ctx.error(f"Failed to get status: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def generate_report(
    report_type: str = "usage",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Generate system report
    システムレポートを生成
    
    Args:
        report_type: Type of report (usage, optimization, learning)
        ctx: MCP context
    """
    try:
        if ctx:
            await ctx.info(f"Generating {report_type} report")
        
        if report_type == "usage":
            report = await trinitas_core.seshat_monitor.get_usage_report()
        elif report_type == "optimization":
            report = {
                "bellona_status": trinitas_core.bellona_distributor.get_status(),
                "seshat_recommendations": (await trinitas_core.seshat_monitor.get_usage_report())["recommendations"]
            }
        elif report_type == "learning":
            report = await trinitas_core.learning_system.get_learning_report()
        else:
            report = {"error": f"Unknown report type: {report_type}"}
        
        return {
            "success": True,
            "report_type": report_type,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        if ctx:
            await ctx.error(f"Failed to generate report: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main entry point for v4.0 MCP server"""
    logger.info("Starting Trinitas v4.0 MCP Server...")
    logger.info(f"Mode: {trinitas_core.config['mode']}")
    logger.info(f"Local LLM: {'Enabled' if trinitas_core.local_llm_enabled else 'Disabled (Default)'}")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()