#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Server
FastMCP-based server for Claude Code integration
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Warning: FastMCP not installed. Install with: pip install fastmcp")

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trinitas_mcp_tools import TrinitasMCPTools, ToolResult
from services.workflow_templates import workflow_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server if FastMCP is available
if FASTMCP_AVAILABLE:
    mcp = FastMCP(
        "Trinitas v3.5 MCP Server",
        version="3.5.0"
    )
else:
    mcp = None

# Initialize tools
trinitas_tools = TrinitasMCPTools()


# =============================================================================
# Core MCP Tools - Available to Claude Code
# =============================================================================

if FASTMCP_AVAILABLE:
    
    @mcp.tool()
    async def persona_execute(
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with a specific Trinitas persona.
        
        Available personas:
        - springfield: Strategic planning and architecture
        - krukai: Technical optimization and quality
        - vector: Security and risk analysis
        - groza: Tactical execution and leadership
        - littara: Implementation and documentation
        
        Args:
            persona: The persona to use (e.g., "springfield")
            task: Description of the task to execute
            context: Optional context information
            
        Returns:
            Execution result with persona's response
        """
        result = await trinitas_tools.persona_execute(persona, task, context)
        return result.to_dict()
    
    
    @mcp.tool()
    async def collaborate_personas(
        personas: List[str],
        task: str,
        mode: str = "sequential",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Have multiple personas collaborate on a task.
        
        Collaboration modes:
        - sequential: One after another, passing context
        - parallel: All at once, independent execution
        - hierarchical: Springfield leads, others follow
        - consensus: Trinity voting system
        
        Args:
            personas: List of personas to involve
            task: Task for collaboration
            mode: How to collaborate (default: sequential)
            context: Optional context
            
        Returns:
            Collaboration results from all personas
        """
        result = await trinitas_tools.collaborate_personas(
            personas, task, mode, context
        )
        return result.to_dict()
    
    
    @mcp.tool()
    async def quality_check(
        code: str,
        check_type: str = "comprehensive",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform Trinity quality validation on code.
        
        Check types:
        - basic: Quick checks
        - standard: Regular validation
        - comprehensive: Full Trinity review (default)
        - paranoid: Vector's maximum security mode
        
        Args:
            code: Code to check
            check_type: Level of checking
            context: Optional context
            
        Returns:
            Quality report with scores and recommendations
        """
        result = await trinitas_tools.quality_check(code, check_type, context)
        return result.to_dict()
    
    
    @mcp.tool()
    async def optimize_code(
        code: str,
        target: str = "performance",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize code using Krukai's expertise.
        
        Optimization targets:
        - performance: Speed and efficiency (default)
        - readability: Code clarity
        - memory: Memory usage
        - maintainability: Long-term maintenance
        
        Args:
            code: Code to optimize
            target: What to optimize for
            context: Optional context
            
        Returns:
            Optimized code with improvement metrics
        """
        result = await trinitas_tools.optimize_code(code, target, context)
        return result.to_dict()
    
    
    @mcp.tool()
    async def security_audit(
        code: str,
        level: str = "paranoid",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Security audit by Vector with paranoid analysis.
        
        Security levels:
        - basic: Quick security scan
        - standard: Regular security check
        - comprehensive: Deep security analysis
        - paranoid: Vector's maximum paranoia (default)
        
        Args:
            code: Code to audit
            level: Security check level
            context: Optional context
            
        Returns:
            Security report with vulnerabilities and recommendations
        """
        result = await trinitas_tools.security_audit(code, level, context)
        return result.to_dict()
    
    
    # =========================================================================
    # Utility Tools
    # =========================================================================
    
    @mcp.tool()
    async def suggest_persona(
        task_description: str
    ) -> Dict[str, Any]:
        """
        Get recommendation for which persona to use for a task.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Recommended persona(s) with reasoning
        """
        task_lower = task_description.lower()
        
        recommendations = []
        reasoning = []
        
        # Analyze task for persona fit
        if any(word in task_lower for word in ["strategy", "design", "architecture", "plan"]):
            recommendations.append("springfield")
            reasoning.append("Strategic planning detected")
        
        if any(word in task_lower for word in ["optimize", "performance", "quality", "refactor"]):
            recommendations.append("krukai")
            reasoning.append("Optimization or quality focus")
        
        if any(word in task_lower for word in ["security", "audit", "risk", "vulnerability"]):
            recommendations.append("vector")
            reasoning.append("Security concerns identified")
        
        if any(word in task_lower for word in ["execute", "deploy", "tactical", "coordinate"]):
            recommendations.append("groza")
            reasoning.append("Tactical execution needed")
        
        if any(word in task_lower for word in ["implement", "code", "document", "detail"]):
            recommendations.append("littara")
            reasoning.append("Implementation or documentation")
        
        # Default recommendation if no clear match
        if not recommendations:
            recommendations.append("springfield")
            reasoning.append("Default to strategic overview")
        
        return {
            "recommended_personas": recommendations,
            "reasoning": reasoning,
            "task_type": "complex" if len(recommendations) > 1 else "focused"
        }
    
    
    @mcp.tool()
    async def execute_workflow(
        workflow_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute predefined workflows for common patterns.
        
        Available workflows:
        - comprehensive_review: Full Trinity review (Springfield, Krukai, Vector)
        - rapid_implementation: Quick development (Groza, Littara)
        - secure_deployment: Security-focused deployment
        - full_analysis: All 5 personas analyze
        
        Args:
            workflow_type: Type of workflow to execute
            parameters: Workflow parameters (must include 'task')
            
        Returns:
            Workflow execution results
        """
        workflows = {
            "comprehensive_review": {
                "personas": ["springfield", "krukai", "vector"],
                "mode": "sequential",
                "description": "Full Trinity review"
            },
            "rapid_implementation": {
                "personas": ["groza", "littara"],
                "mode": "parallel",
                "description": "Fast implementation"
            },
            "secure_deployment": {
                "personas": ["vector", "krukai", "vector"],
                "mode": "sequential",
                "description": "Security-focused deployment"
            },
            "full_analysis": {
                "personas": ["springfield", "krukai", "vector", "groza", "littara"],
                "mode": "parallel",
                "description": "Complete team analysis"
            }
        }
        
        if workflow_type not in workflows:
            return {
                "success": False,
                "error": f"Unknown workflow: {workflow_type}",
                "available_workflows": list(workflows.keys())
            }
        
        workflow = workflows[workflow_type]
        task = parameters.get("task", "Execute workflow")
        
        # Execute workflow
        result = await trinitas_tools.collaborate_personas(
            workflow["personas"],
            task,
            workflow["mode"],
            parameters
        )
        
        return {
            "workflow": workflow_type,
            "description": workflow["description"],
            "result": result.to_dict()
        }
    
    
    @mcp.tool()
    async def get_trinitas_status() -> Dict[str, Any]:
        """
        Get current status of Trinitas system.
        
        Returns:
            System status including personas, stats, and health
        """
        stats = trinitas_tools.get_execution_stats()
        
        return {
            "status": "operational",
            "version": "3.5.0",
            "personas_available": [
                "springfield", "krukai", "vector", "groza", "littara"
            ],
            "v35_components": component_wrapper.v35_available,
            "execution_stats": stats,
            "server_uptime": datetime.now().isoformat(),
            "modes_supported": ["sequential", "parallel", "hierarchical", "consensus"],
            "workflows_available": [
                "comprehensive_review",
                "rapid_implementation",
                "secure_deployment",
                "full_analysis"
            ]
        }
    
    
    @mcp.tool()
    async def natural_request(
        request: str
    ) -> Dict[str, Any]:
        """
        Process natural language requests about Trinitas operations.
        
        Examples:
        - "Have Springfield review this architecture"
        - "Get Krukai to optimize this code"
        - "Run a security check with Vector"
        
        Args:
            request: Natural language request
            
        Returns:
            Interpreted action and execution result
        """
        request_lower = request.lower()
        
        # Parse intent
        action = None
        persona = None
        
        # Identify persona mentioned
        for p in ["springfield", "krukai", "vector", "groza", "littara"]:
            if p in request_lower:
                persona = p
                break
        
        # Identify action
        if any(word in request_lower for word in ["review", "check", "analyze"]):
            action = "review"
        elif any(word in request_lower for word in ["optimize", "improve", "enhance"]):
            action = "optimize"
        elif any(word in request_lower for word in ["security", "audit", "vulnerability"]):
            action = "security"
        elif any(word in request_lower for word in ["implement", "code", "build"]):
            action = "implement"
        
        # Default persona based on action
        if not persona:
            action_persona_map = {
                "review": "springfield",
                "optimize": "krukai",
                "security": "vector",
                "implement": "littara"
            }
            persona = action_persona_map.get(action, "groza")
        
        # Execute based on parsed intent
        if action and persona:
            result = await trinitas_tools.persona_execute(
                persona,
                f"{action}: {request}",
                {"original_request": request}
            )
            
            return {
                "interpreted_action": action,
                "assigned_persona": persona,
                "result": result.to_dict()
            }
        
        return {
            "success": False,
            "error": "Could not parse request",
            "suggestion": "Try being more specific about the task and persona"
        }
    
    
    # =========================================================================
    # Advanced MCP Tools - Context & Workflow Management
    # =========================================================================
    
    @mcp.tool()
    async def set_trinitas_context(
        key: str,
        value: Any,
        level: str = "session",
        persona: Optional[str] = None,
        priority: int = 2,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set context in Trinitas context management system.
        
        Context levels:
        - global: Available across all sessions
        - session: Current session only (default)
        - persona: Persona-specific context
        - temp: Temporary context (cleared frequently)
        
        Args:
            key: Context key
            value: Context value (any JSON-serializable data)
            level: Context level (global, session, persona, temp)
            persona: Persona name (required if level=persona)
            priority: Priority 1=low to 4=critical (default: 2)
            ttl: Time to live in seconds (optional)
            
        Returns:
            Success status and context info
        """
        success = await context_manager.set_context(
            key, value, level, persona, priority, ttl
        )
        
        return {
            "success": success,
            "key": key,
            "level": level,
            "persona": persona,
            "priority": priority,
            "ttl": ttl
        }
    
    
    @mcp.tool()
    async def get_trinitas_context(
        key: str,
        level: Optional[str] = None,
        persona: Optional[str] = None,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Get context from Trinitas context management system.
        
        Args:
            key: Context key
            level: Specific level to search (optional)
            persona: Persona context to search (optional)
            include_metadata: Include metadata about the context entry
            
        Returns:
            Context value and metadata if requested
        """
        value = await context_manager.get_context(key, level, persona, include_metadata)
        
        if value is None:
            return {
                "found": False,
                "key": key,
                "level": level,
                "persona": persona
            }
        
        return {
            "found": True,
            "key": key,
            "value": value,
            "level": level,
            "persona": persona
        }
    
    
    @mcp.tool()
    async def get_session_context() -> Dict[str, Any]:
        """
        Get all context for current session.
        
        Returns:
            All session context data and session info
        """
        session_context = await context_manager.get_session_context()
        session_info = context_manager.get_session_info()
        
        return {
            "session_context": session_context,
            "session_info": session_info
        }
    
    
    @mcp.tool()
    async def execute_trinitas_workflow(
        workflow_type: str,
        parameters: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a predefined Trinitas workflow.
        
        Available workflows:
        - full_development_cycle: Complete development from planning to deployment
        - rapid_prototyping: Fast prototype development and validation
        - security_hardening: Comprehensive security assessment
        - performance_optimization: System performance optimization
        - incident_response: Emergency response and recovery
        - comprehensive_qa: Full quality assurance process
        
        Args:
            workflow_type: Type of workflow to execute
            parameters: Workflow parameters (varies by type)
            workflow_id: Optional workflow ID for tracking
            
        Returns:
            Workflow execution result and status
        """
        result = await workflow_engine.execute_workflow(
            workflow_type, parameters, workflow_id
        )
        
        return {
            "workflow_id": result.workflow_id,
            "status": result.status,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "steps_completed": result.steps_completed,
            "steps_failed": result.steps_failed,
            "results": result.results,
            "error": result.error,
            "metadata": result.metadata
        }
    
    
    @mcp.tool()
    async def get_workflow_templates() -> Dict[str, Any]:
        """
        Get available workflow templates with descriptions.
        
        Returns:
            Dictionary of available workflow templates and their info
        """
        templates = workflow_engine.get_available_templates()
        
        return {
            "templates": templates,
            "total_templates": len(templates)
        }
    
    
    @mcp.tool()
    async def get_workflow_status(
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a running or completed workflow.
        
        Args:
            workflow_id: ID of workflow to check
            
        Returns:
            Workflow status and progress information
        """
        status = workflow_engine.get_workflow_status(workflow_id)
        
        if not status:
            return {
                "found": False,
                "workflow_id": workflow_id
            }
        
        return {
            "found": True,
            "workflow_id": status.workflow_id,
            "status": status.status,
            "start_time": status.start_time.isoformat(),
            "end_time": status.end_time.isoformat() if status.end_time else None,
            "steps_completed": status.steps_completed,
            "steps_failed": status.steps_failed,
            "progress": len(status.steps_completed) / max(
                len(status.steps_completed) + len(status.steps_failed), 1
            ),
            "error": status.error
        }
    
    
    @mcp.tool()
    async def create_session(
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Trinitas session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            New session information
        """
        new_session_id = context_manager.create_session(session_id)
        session_info = context_manager.get_session_info()
        
        return {
            "session_id": new_session_id,
            "session_info": session_info
        }
    
    
    @mcp.tool()
    async def switch_session(
        session_id: str
    ) -> Dict[str, Any]:
        """
        Switch to an existing Trinitas session.
        
        Args:
            session_id: ID of session to switch to
            
        Returns:
            Switch result and session info
        """
        success = context_manager.switch_session(session_id)
        
        if success:
            session_info = context_manager.get_session_info()
            return {
                "success": True,
                "session_id": session_id,
                "session_info": session_info
            }
        
        return {
            "success": False,
            "session_id": session_id,
            "error": "Session not found"
        }
    
    
    @mcp.tool()
    async def get_performance_stats() -> Dict[str, Any]:
        """
        Get Trinitas system performance statistics.
        
        Returns:
            Performance metrics for context management and execution
        """
        context_stats = context_manager.get_performance_stats()
        execution_stats = trinitas_tools.get_execution_stats()
        active_workflows = workflow_engine.list_active_workflows()
        
        return {
            "context_management": context_stats,
            "persona_execution": execution_stats,
            "active_workflows": len(active_workflows),
            "workflow_ids": active_workflows,
            "system_status": "operational"
        }


# =============================================================================
# Server Management
# =============================================================================

async def start_server():
    """Start the MCP server"""
    if not FASTMCP_AVAILABLE:
        print("FastMCP not available. Please install with: pip install fastmcp")
        return
    
    logger.info("Starting Trinitas v3.5 MCP Server...")
    logger.info("Available tools:")
    logger.info("  - persona_execute")
    logger.info("  - collaborate_personas")
    logger.info("  - quality_check")
    logger.info("  - optimize_code")
    logger.info("  - security_audit")
    logger.info("  - suggest_persona")
    logger.info("  - execute_workflow")
    logger.info("  - get_trinitas_status")
    logger.info("  - natural_request")
    logger.info("  - set_trinitas_context")
    logger.info("  - get_trinitas_context")
    logger.info("  - get_session_context")
    logger.info("  - execute_trinitas_workflow")
    logger.info("  - get_workflow_templates")
    logger.info("  - get_workflow_status")
    logger.info("  - create_session")
    logger.info("  - switch_session")
    logger.info("  - get_performance_stats")
    
    # Run the server
    await mcp.run()


if __name__ == "__main__":
    if FASTMCP_AVAILABLE:
        # Run the MCP server
        asyncio.run(start_server())
    else:
        print("=" * 60)
        print("Trinitas v3.5 MCP Server")
        print("=" * 60)
        print("\nFastMCP is not installed. To use this server:")
        print("1. Install FastMCP: pip install fastmcp")
        print("2. Run this script again: python mcp_server.py")
        print("\nOnce running, Claude Code can use these tools:")
        print("  - persona_execute: Execute with specific persona")
        print("  - collaborate_personas: Multi-persona collaboration")
        print("  - quality_check: Trinity quality validation")
        print("  - optimize_code: Krukai optimization")
        print("  - security_audit: Vector security analysis")
        print("  - And more utility tools...")
        print("=" * 60)