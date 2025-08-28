#!/usr/bin/env python3
"""
FastMCP-based MCP Server for v35-mcp-tools
Properly implements MCP protocol using FastMCP framework
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name="Trinitas v3.5 MCP Tools"
)

# Import Trinitas components
try:
    from core.trinitas_mcp_tools import TrinitasMCPTools
    from core.engine_client import engine_client
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.core.trinitas_mcp_tools import TrinitasMCPTools
    from src.core.engine_client import engine_client

# Initialize Trinitas tools
trinitas_tools = TrinitasMCPTools()

@mcp.tool
async def trinitas_execute(
    persona: str,
    task: str,
    context: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Execute a task with a specified Trinitas persona.
    
    Args:
        persona: The persona to use (athena, artemis, hestia, bellona, seshat)
        task: The task description
        context: Optional context for the task
        ctx: MCP context for logging
    
    Returns:
        Execution results from the specified persona
    """
    try:
        if ctx:
            await ctx.info(f"Executing task with {persona}: {task[:100]}...")
        
        result = await trinitas_tools.persona_execute(
            persona=persona,
            task=task,
            context=context or {}
        )
        
        # Convert result to dict if it's an object
        if hasattr(result, '__dict__'):
            return result.__dict__
        return result
        
    except Exception as e:
        logger.error(f"Error executing persona task: {e}")
        if ctx:
            await ctx.error(f"Failed to execute task: {str(e)}")
        return {
            "error": str(e),
            "persona": persona,
            "status": "failed"
        }

@mcp.tool
async def trinitas_collaborate(
    task: str,
    personas: List[str],
    mode: str = "parallel",
    context: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Execute a task collaboratively with multiple personas.
    
    Args:
        task: The task description
        personas: List of personas to collaborate
        mode: Execution mode - "parallel" or "sequential"
        context: Optional context for the task
        ctx: MCP context for logging
    
    Returns:
        Collaborative execution results
    """
    try:
        if ctx:
            await ctx.info(f"Starting {mode} collaboration with {', '.join(personas)}")
        
        # Use engine client for collaborative execution
        result = await engine_client.execute_collaborative(
            task=task,
            personas=personas,
            context=context or {},
            mode=mode
        )
        
        if ctx:
            await ctx.info("Collaboration completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in collaborative execution: {e}")
        if ctx:
            await ctx.error(f"Collaboration failed: {str(e)}")
        return {
            "error": str(e),
            "task": task,
            "personas": personas,
            "mode": mode,
            "status": "failed"
        }

@mcp.tool
async def trinitas_status(ctx: Context = None) -> Dict[str, Any]:
    """
    Get Trinitas system status and configuration.
    
    Args:
        ctx: MCP context for logging
    
    Returns:
        System status information
    """
    try:
        # Get engine status
        engine_status = await engine_client.get_engine_status()
        
        # Get current mode
        mode = trinitas_tools.mode_manager.current_mode.value if hasattr(trinitas_tools, 'mode_manager') else "unknown"
        
        # Build status response
        status = {
            "system": "Trinitas v3.5",
            "mode": mode,
            "personas": ["athena", "artemis", "hestia", "bellona", "seshat"],
            "engine": engine_status if engine_status else {"status": "offline"},
            "memory_backend": os.getenv("MEMORY_BACKEND", "hybrid"),
            "mcp_tools": "active",
            "version": "3.5.0"
        }
        
        if ctx:
            await ctx.info(f"System status: {status['engine'].get('status', 'unknown')}")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        if ctx:
            await ctx.error(f"Failed to get status: {str(e)}")
        return {
            "error": str(e),
            "system": "Trinitas v3.5",
            "status": "error"
        }

@mcp.tool
async def trinitas_remember(
    persona: str,
    memory_type: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Store information in a persona's memory.
    
    Args:
        persona: The persona to store memory for
        memory_type: Type of memory (working, episodic, semantic, procedural)
        content: The content to remember
        metadata: Optional metadata for the memory
        ctx: MCP context for logging
    
    Returns:
        Memory storage confirmation
    """
    try:
        if ctx:
            await ctx.info(f"Storing {memory_type} memory for {persona}")
        
        # Import memory system
        from memory.enhanced_manager import EnhancedMemoryManager
        from memory.memory_core import MemoryType
        
        # Create manager for persona
        manager = EnhancedMemoryManager(persona=persona.lower())
        await manager.initialize()
        
        # Map string type to MemoryType enum
        type_map = {
            "working": MemoryType.WORKING,
            "episodic": MemoryType.EPISODIC,
            "semantic": MemoryType.SEMANTIC,
            "procedural": MemoryType.PROCEDURAL
        }
        
        memory_type_enum = type_map.get(memory_type.lower(), MemoryType.SEMANTIC)
        
        # Extract importance from metadata if provided
        importance = 0.5
        tags = []
        if metadata:
            importance = metadata.get("importance", 0.5)
            tags = metadata.get("tags", [])
        
        # Store memory
        memory_id = await manager.remember(
            content=content,
            memory_type=memory_type_enum,
            importance=importance,
            tags=tags
        )
        
        if memory_id:
            return {
                "status": "stored",
                "persona": persona,
                "memory_type": memory_type,
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "failed",
                "persona": persona,
                "error": "Failed to store memory"
            }
        
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        if ctx:
            await ctx.error(f"Failed to store memory: {str(e)}")
        return {"error": str(e), "status": "failed"}

@mcp.tool
async def trinitas_recall(
    persona: str,
    query: str,
    memory_type: Optional[str] = None,
    limit: int = 10,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Retrieve information from a persona's memory.
    
    Args:
        persona: The persona to recall memory from
        query: Search query for memory retrieval
        memory_type: Optional specific memory type to search
        limit: Maximum number of memories to return
        ctx: MCP context for logging
    
    Returns:
        Retrieved memories
    """
    try:
        if ctx:
            await ctx.info(f"Recalling memories for {persona}: {query[:50]}...")
        
        # Import memory system
        from memory.enhanced_manager import EnhancedMemoryManager
        from memory.memory_core import MemoryType
        
        # Create manager for persona
        manager = EnhancedMemoryManager(persona=persona.lower())
        await manager.initialize()
        
        # Map string type to MemoryType enum if provided
        memory_type_enum = None
        if memory_type:
            type_map = {
                "working": MemoryType.WORKING,
                "episodic": MemoryType.EPISODIC,
                "semantic": MemoryType.SEMANTIC,
                "procedural": MemoryType.PROCEDURAL
            }
            memory_type_enum = type_map.get(memory_type.lower())
        
        # Search memories
        results = await manager.search(
            query=query,
            limit=limit,
            memory_type=memory_type_enum
        )
        
        # Format results
        memories = []
        if results:
            for item in results:
                memory_dict = {
                    "id": item.id,
                    "content": item.content,
                    "type": item.type.value,
                    "importance": item.importance,
                    "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                    "tags": item.tags if hasattr(item, 'tags') else []
                }
                memories.append(memory_dict)
        
        return {
            "status": "success",
            "persona": persona,
            "memories": memories,
            "count": len(memories),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error recalling memory: {e}")
        if ctx:
            await ctx.error(f"Failed to recall memory: {str(e)}")
        return {"error": str(e), "status": "failed"}

# Add initialization hook
async def initialize():
    """Initialize Trinitas components on server startup"""
    try:
        await engine_client.initialize()
        logger.info("Trinitas MCP Tools initialized successfully")
    except Exception as e:
        logger.warning(f"Engine client initialization failed (non-critical): {e}")

# Set server lifecycle (if supported by FastMCP version)
# mcp.set_startup_handler(initialize)  # Commented out - not supported in current FastMCP

def main():
    """Main entry point for the Trinitas MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()