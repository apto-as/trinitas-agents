#!/usr/bin/env python3
"""
Trinitas v3.5 Enhanced MCP Server with Context Management and Workflow Support
"""

from typing import Dict, Any, Optional, List
import json
import asyncio
from datetime import datetime
from mcp import Server, Tool
from mcp.types import TextContent, ToolResult, ToolError
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trinitas_mcp_tools import TrinitasMCPTools
from context_manager import AdvancedContextManager
from workflow_templates import WorkflowTemplatesEngine

# Initialize MCP server
mcp = Server("trinitas-v35-enhanced")

# Initialize Trinitas components
trinitas_tools = TrinitasMCPTools()
context_manager = AdvancedContextManager()
workflow_engine = WorkflowTemplatesEngine()

# Current session tracking
current_session_id = None

@mcp.tool()
async def persona_execute(
    persona: str,
    task: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Execute a task using a specific Trinitas persona with session context
    
    Args:
        persona: Name of the persona (springfield, krukai, vector, groza, littara)
        task: Task description for the persona to execute
        context: Optional context dictionary
        session_id: Optional session ID for context persistence
    
    Returns:
        ToolResult with execution outcome
    """
    global current_session_id
    
    # Use provided session ID or current session
    session_id = session_id or current_session_id
    
    # Get session context if available
    if session_id:
        session_context = await context_manager.get_session_context(session_id)
        if context:
            context.update(session_context)
        else:
            context = session_context
    
    # Execute persona task
    result = await trinitas_tools.persona_execute(persona, task, context)
    
    # Update session context with result
    if session_id and result.success:
        await context_manager.update_session_context(
            session_id,
            {"last_persona": persona, "last_result": result.data}
        )
    
    return result

@mcp.tool()
async def collaborate_personas(
    personas: List[str],
    task: str,
    mode: str = "sequential",
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Collaborate multiple personas on a task with context synchronization
    
    Args:
        personas: List of persona names to collaborate
        task: Task for collaboration
        mode: Collaboration mode (sequential, parallel, hierarchical, consensus)
        context: Optional context
        session_id: Optional session ID for context persistence
    
    Returns:
        ToolResult with collaboration outcome
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    # Get session context
    if session_id:
        session_context = await context_manager.get_session_context(session_id)
        if context:
            context.update(session_context)
        else:
            context = session_context
    
    # Execute collaboration
    result = await trinitas_tools.collaborate_personas(personas, task, mode, context)
    
    # Sync context between personas if in session
    if session_id and result.success:
        for i, persona in enumerate(personas[:-1]):
            next_persona = personas[i + 1]
            await context_manager.sync_context_between_personas(
                session_id, persona, next_persona
            )
    
    return result

@mcp.tool()
async def execute_workflow(
    template_name: str,
    project_context: Dict[str, Any],
    session_id: Optional[str] = None,
    parallel: bool = False
) -> ToolResult:
    """
    Execute a predefined workflow template
    
    Args:
        template_name: Name of the workflow template
        project_context: Project context for the workflow
        session_id: Optional session ID for tracking
        parallel: Whether to execute steps in parallel when possible
    
    Returns:
        ToolResult with workflow execution results
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    try:
        # Create or get session
        if not session_id:
            session_id = context_manager.create_session()
            current_session_id = session_id
        
        # Execute workflow
        result = await workflow_engine.execute_workflow(
            template_name,
            project_context,
            parallel=parallel
        )
        
        # Track workflow in session
        await context_manager.track_workflow(
            session_id,
            template_name,
            project_context,
            result
        )
        
        return ToolResult(
            success=True,
            data={
                "workflow": template_name,
                "result": result,
                "session_id": session_id
            },
            message=f"Workflow '{template_name}' executed successfully"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
            message=f"Workflow execution failed: {str(e)}"
        )

@mcp.tool()
async def create_session(
    session_name: Optional[str] = None,
    initial_context: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Create a new Trinitas session for context persistence
    
    Args:
        session_name: Optional name for the session
        initial_context: Optional initial context for the session
    
    Returns:
        ToolResult with session ID
    """
    global current_session_id
    
    session_id = context_manager.create_session(session_name)
    current_session_id = session_id
    
    if initial_context:
        await context_manager.update_session_context(session_id, initial_context)
    
    return ToolResult(
        success=True,
        data={"session_id": session_id, "name": session_name},
        message=f"Session created: {session_id}"
    )

@mcp.tool()
async def switch_session(session_id: str) -> ToolResult:
    """
    Switch to a different Trinitas session
    
    Args:
        session_id: ID of the session to switch to
    
    Returns:
        ToolResult with session status
    """
    global current_session_id
    
    if session_id in context_manager.sessions:
        current_session_id = session_id
        session_info = await context_manager.get_session_info(session_id)
        return ToolResult(
            success=True,
            data=session_info,
            message=f"Switched to session: {session_id}"
        )
    else:
        return ToolResult(
            success=False,
            error="Session not found",
            message=f"Session {session_id} does not exist"
        )

@mcp.tool()
async def get_session_context(
    key: Optional[str] = None,
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Get context from the current or specified session
    
    Args:
        key: Optional specific key to retrieve
        session_id: Optional session ID (uses current if not specified)
    
    Returns:
        ToolResult with context data
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    if not session_id:
        return ToolResult(
            success=False,
            error="No active session",
            message="No session is currently active"
        )
    
    if key:
        value = await context_manager.get_context(key, "session", session_id)
        return ToolResult(
            success=True,
            data={key: value},
            message=f"Retrieved context key: {key}"
        )
    else:
        context = await context_manager.get_session_context(session_id)
        return ToolResult(
            success=True,
            data=context,
            message="Retrieved full session context"
        )

@mcp.tool()
async def set_session_context(
    key: str,
    value: Any,
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Set context in the current or specified session
    
    Args:
        key: Context key to set
        value: Value to store
        session_id: Optional session ID (uses current if not specified)
    
    Returns:
        ToolResult with operation status
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    if not session_id:
        return ToolResult(
            success=False,
            error="No active session",
            message="No session is currently active"
        )
    
    await context_manager.set_context(key, value, "session", session_id)
    return ToolResult(
        success=True,
        data={"key": key, "value": value, "session_id": session_id},
        message=f"Context set: {key}"
    )

@mcp.tool()
async def list_sessions() -> ToolResult:
    """
    List all available Trinitas sessions
    
    Returns:
        ToolResult with list of sessions
    """
    sessions_info = []
    for session_id, session in context_manager.sessions.items():
        info = {
            "id": session_id,
            "created_at": session["created_at"].isoformat(),
            "updated_at": session["updated_at"].isoformat(),
            "context_keys": list(session["context"].keys())
        }
        sessions_info.append(info)
    
    return ToolResult(
        success=True,
        data={
            "sessions": sessions_info,
            "current_session": current_session_id
        },
        message=f"Found {len(sessions_info)} sessions"
    )

@mcp.tool()
async def get_workflow_templates() -> ToolResult:
    """
    Get list of available workflow templates
    
    Returns:
        ToolResult with template information
    """
    templates = workflow_engine.get_available_templates()
    
    return ToolResult(
        success=True,
        data={"templates": templates},
        message=f"Found {len(templates)} workflow templates"
    )

@mcp.tool()
async def get_workflow_details(template_name: str) -> ToolResult:
    """
    Get detailed information about a workflow template
    
    Args:
        template_name: Name of the workflow template
    
    Returns:
        ToolResult with template details
    """
    try:
        details = workflow_engine.get_template_details(template_name)
        return ToolResult(
            success=True,
            data=details,
            message=f"Retrieved details for workflow: {template_name}"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
            message=f"Failed to get workflow details: {str(e)}"
        )

@mcp.tool()
async def suggest_workflow(
    project_type: str,
    requirements: List[str],
    constraints: Optional[List[str]] = None
) -> ToolResult:
    """
    Suggest appropriate workflow based on project requirements
    
    Args:
        project_type: Type of project
        requirements: List of project requirements
        constraints: Optional list of constraints
    
    Returns:
        ToolResult with workflow suggestions
    """
    try:
        # Analyze requirements
        suggestions = []
        templates = workflow_engine.get_available_templates()
        
        for template_name in templates:
            details = workflow_engine.get_template_details(template_name)
            score = 0
            
            # Score based on matching requirements
            for req in requirements:
                req_lower = req.lower()
                if req_lower in details.get("description", "").lower():
                    score += 2
                for step in details.get("steps", []):
                    if req_lower in step.get("description", "").lower():
                        score += 1
            
            # Consider project type
            if project_type.lower() in template_name.lower():
                score += 3
            
            if score > 0:
                suggestions.append({
                    "template": template_name,
                    "score": score,
                    "description": details.get("description", "")
                })
        
        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return ToolResult(
            success=True,
            data={
                "suggestions": suggestions[:3],  # Top 3 suggestions
                "best_match": suggestions[0] if suggestions else None
            },
            message=f"Found {len(suggestions)} matching workflows"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
            message=f"Failed to suggest workflow: {str(e)}"
        )

@mcp.tool()
async def quality_check(
    code: str,
    level: str = "comprehensive",
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Perform quality check on code with session tracking
    
    Args:
        code: Code to check
        level: Check level (basic, standard, comprehensive)
        session_id: Optional session ID for tracking
    
    Returns:
        ToolResult with quality check results
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    result = await trinitas_tools.quality_check(code, level)
    
    # Track quality check in session
    if session_id and result.success:
        await context_manager.update_session_context(
            session_id,
            {
                "last_quality_check": {
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    "result": result.data
                }
            }
        )
    
    return result

@mcp.tool()
async def get_performance_stats(
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Get performance statistics for current or specified session
    
    Args:
        session_id: Optional session ID (uses current if not specified)
    
    Returns:
        ToolResult with performance statistics
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    if not session_id:
        return ToolResult(
            success=False,
            error="No active session",
            message="No session is currently active"
        )
    
    stats = await context_manager.get_performance_stats(session_id)
    
    return ToolResult(
        success=True,
        data=stats,
        message="Retrieved performance statistics"
    )

@mcp.tool()
async def natural_request(
    request: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> ToolResult:
    """
    Process natural language request and execute appropriate Trinitas actions
    
    Args:
        request: Natural language request
        context: Optional context
        session_id: Optional session ID
    
    Returns:
        ToolResult with execution outcome
    """
    global current_session_id
    session_id = session_id or current_session_id
    
    # Get session context
    if session_id:
        session_context = await context_manager.get_session_context(session_id)
        if context:
            context.update(session_context)
        else:
            context = session_context
    
    # Process natural request
    result = await trinitas_tools.natural_request(request, context)
    
    # Update session with result
    if session_id and result.success:
        await context_manager.update_session_context(
            session_id,
            {"last_natural_request": request, "last_result": result.data}
        )
    
    return result

@mcp.tool()
async def get_trinitas_status() -> ToolResult:
    """
    Get current Trinitas system status including sessions and performance
    
    Returns:
        ToolResult with comprehensive status information
    """
    global current_session_id
    
    # Get basic status
    basic_status = await trinitas_tools.get_trinitas_status()
    
    # Add session information
    session_count = len(context_manager.sessions)
    workflow_count = len(workflow_engine.get_available_templates())
    
    enhanced_status = {
        **basic_status.data,
        "sessions": {
            "total": session_count,
            "current": current_session_id,
            "active": [sid for sid in context_manager.sessions.keys()]
        },
        "workflows": {
            "available": workflow_count,
            "templates": workflow_engine.get_available_templates()
        },
        "enhanced_features": {
            "context_management": True,
            "workflow_templates": True,
            "session_persistence": True,
            "cross_persona_sync": True
        }
    }
    
    return ToolResult(
        success=True,
        data=enhanced_status,
        message="Trinitas v3.5 Enhanced - All systems operational"
    )

# Main execution
if __name__ == "__main__":
    print("🌸 Trinitas v3.5 Enhanced MCP Server")
    print("=" * 60)
    print("Initializing with advanced context management and workflow support...")
    print(f"Available personas: {', '.join(trinitas_tools.personas.keys())}")
    print(f"Workflow templates: {len(workflow_engine.get_available_templates())}")
    print(f"Server ready for Claude Code integration")
    print("-" * 60)
    
    # Run the MCP server
    mcp.run()