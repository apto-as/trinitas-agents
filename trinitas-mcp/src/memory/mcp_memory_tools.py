#!/usr/bin/env python3
"""
Trinitas v3.5 Memory MCP Tools
MCP統合用の記憶システムツール
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from fastmcp import Context, Tool
from pydantic import BaseModel, Field

from .enhanced_manager import get_enhanced_memory_manager, semantic_search as search_semantic
from .memory_core import MemoryType, Context as MemoryContext

logger = logging.getLogger(__name__)

# Pydantic models for MCP tools
class RememberRequest(BaseModel):
    """記憶保存リクエスト"""
    persona: str = Field(description="Persona name (athena, artemis, hestia, bellona, seshat)")
    content: str = Field(description="Content to remember")
    memory_type: Optional[str] = Field(default=None, description="Memory type (episodic, semantic, procedural)")
    importance: float = Field(default=0.5, description="Importance level (0.0-1.0)")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")

class RecallRequest(BaseModel):
    """記憶想起リクエスト"""
    persona: str = Field(description="Persona name")
    query: str = Field(description="Search query")
    limit: int = Field(default=5, description="Maximum results")
    include_context: bool = Field(default=False, description="Include current task context")

class ShareMemoryRequest(BaseModel):
    """記憶共有リクエスト"""
    from_persona: str = Field(description="Source persona")
    to_persona: str = Field(description="Target persona")
    query: str = Field(description="Memory search query to share")

class ConsolidateRequest(BaseModel):
    """記憶固定化リクエスト"""
    persona: str = Field(description="Persona name")
    force: bool = Field(default=False, description="Force immediate consolidation")

# MCP Tools
async def create_memory_tools():
    """記憶システムMCPツールを作成"""
    tools = []
    
    # Remember Tool
    @Tool(
        name="trinitas_remember",
        description="Store information in Trinitas agent memory for future recall"
    )
    async def remember_tool(ctx: Context, request: RememberRequest) -> Dict[str, Any]:
        """記憶を保存"""
        try:
            manager = await get_enhanced_memory_manager()
            
            # Parse memory type
            memory_type = None
            if request.memory_type:
                memory_type = MemoryType[request.memory_type.upper()]
            
            # Parse content (support JSON)
            content = request.content
            try:
                content = json.loads(content)
            except:
                pass  # Keep as string if not JSON
            
            # Store memory
            item = await manager.remember(
                persona=request.persona,
                content=content,
                memory_type=memory_type,
                importance=request.importance,
                tags=request.tags
            )
            
            return {
                "success": True,
                "memory_id": item.id,
                "persona": request.persona,
                "type": item.type.value,
                "timestamp": item.timestamp.isoformat(),
                "message": f"Successfully stored {item.type.value} memory for {request.persona}"
            }
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Recall Tool
    @Tool(
        name="trinitas_recall",
        description="Retrieve relevant memories from Trinitas agent's past experiences"
    )
    async def recall_tool(ctx: Context, request: RecallRequest) -> Dict[str, Any]:
        """記憶を想起"""
        try:
            manager = await get_enhanced_memory_manager()
            
            # Build context if requested
            context = None
            if request.include_context:
                # Extract context from current conversation
                context = MemoryContext(
                    current_task=request.query,
                    constraints=[],
                    preferences={},
                    history=[]
                )
            
            # Recall memories
            memories = await manager.recall(
                persona=request.persona,
                query_text=request.query,
                context=context,
                limit=request.limit
            )
            
            # Format results
            results = []
            for memory in memories:
                result = {
                    "id": memory.id,
                    "content": memory.content,
                    "type": memory.type.value,
                    "timestamp": memory.timestamp.isoformat(),
                    "access_count": memory.access_count,
                    "importance": memory.importance,
                    "tags": memory.tags
                }
                results.append(result)
            
            return {
                "success": True,
                "persona": request.persona,
                "query": request.query,
                "count": len(results),
                "memories": results,
                "message": f"Found {len(results)} relevant memories for {request.persona}"
            }
        except Exception as e:
            logger.error(f"Failed to recall memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Share Memory Tool
    @Tool(
        name="trinitas_share_memory",
        description="Share memories between Trinitas personas for collaborative problem-solving"
    )
    async def share_memory_tool(ctx: Context, request: ShareMemoryRequest) -> Dict[str, Any]:
        """ペルソナ間で記憶を共有"""
        try:
            manager = await get_enhanced_memory_manager()
            
            # Find memories to share
            memories = await manager.recall(
                persona=request.from_persona,
                query_text=request.query,
                limit=5
            )
            
            if not memories:
                return {
                    "success": False,
                    "message": f"No memories found for query: {request.query}"
                }
            
            # Share each memory
            shared_count = 0
            for memory in memories:
                await manager.share_memory(
                    from_persona=request.from_persona,
                    to_persona=request.to_persona,
                    memory_id=memory.id
                )
                shared_count += 1
            
            return {
                "success": True,
                "from_persona": request.from_persona,
                "to_persona": request.to_persona,
                "shared_count": shared_count,
                "message": f"Shared {shared_count} memories from {request.from_persona} to {request.to_persona}"
            }
        except Exception as e:
            logger.error(f"Failed to share memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Consolidate Memory Tool
    @Tool(
        name="trinitas_consolidate",
        description="Consolidate short-term memories to long-term storage"
    )
    async def consolidate_tool(ctx: Context, request: ConsolidateRequest) -> Dict[str, Any]:
        """記憶を固定化"""
        try:
            manager = await get_enhanced_memory_manager()
            
            if request.persona not in manager.personas:
                return {
                    "success": False,
                    "error": f"Unknown persona: {request.persona}"
                }
            
            # Run consolidation
            consolidator = manager.consolidators[request.persona]
            await consolidator.consolidate()
            
            return {
                "success": True,
                "persona": request.persona,
                "message": f"Successfully consolidated memories for {request.persona}"
            }
        except Exception as e:
            logger.error(f"Failed to consolidate memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Memory Statistics Tool
    @Tool(
        name="trinitas_memory_stats",
        description="Get memory system statistics for monitoring and optimization"
    )
    async def memory_stats_tool(ctx: Context) -> Dict[str, Any]:
        """記憶統計を取得"""
        try:
            manager = await get_enhanced_memory_manager()
            stats = manager.get_statistics()
            
            return {
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Memory Search Tool (Advanced)
    @Tool(
        name="trinitas_memory_search",
        description="Advanced cross-persona memory search for complex queries"
    )
    async def memory_search_tool(ctx: Context, 
                                personas: Optional[List[str]] = None,
                                query: str = "",
                                memory_types: Optional[List[str]] = None,
                                min_importance: float = 0.0,
                                limit: int = 10) -> Dict[str, Any]:
        """高度な記憶検索"""
        try:
            manager = await get_enhanced_memory_manager()
            
            # Default to all personas
            if not personas:
                personas = list(manager.personas.keys())
            
            all_results = []
            
            for persona in personas:
                if persona not in manager.personas:
                    continue
                
                memories = await manager.recall(
                    persona=persona,
                    query_text=query,
                    limit=limit
                )
                
                for memory in memories:
                    # Filter by type
                    if memory_types and memory.type.value not in memory_types:
                        continue
                    
                    # Filter by importance
                    if memory.importance < min_importance:
                        continue
                    
                    all_results.append({
                        "persona": persona,
                        "id": memory.id,
                        "content": memory.content,
                        "type": memory.type.value,
                        "importance": memory.importance,
                        "timestamp": memory.timestamp.isoformat(),
                        "tags": memory.tags
                    })
            
            # Sort by importance and limit
            all_results.sort(key=lambda x: x["importance"], reverse=True)
            all_results = all_results[:limit]
            
            return {
                "success": True,
                "query": query,
                "searched_personas": personas,
                "count": len(all_results),
                "results": all_results
            }
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    tools = [
        remember_tool,
        recall_tool,
        share_memory_tool,
        consolidate_tool,
        memory_stats_tool,
        memory_search_tool
    ]
    
    return tools

# Integration with existing MCP tools
def register_memory_tools(mcp_server):
    """既存のMCPサーバーに記憶ツールを登録"""
    import asyncio
    
    async def _register():
        tools = await create_memory_tools()
        for tool in tools:
            mcp_server.register_tool(tool)
        logger.info(f"Registered {len(tools)} memory tools")
    
    asyncio.run(_register())

# Standalone usage
if __name__ == "__main__":
    import asyncio
    from fastmcp import FastMCP
    
    async def main():
        # Initialize memory manager
        await get_memory_manager()
        
        # Create MCP server with memory tools
        mcp = FastMCP("trinitas-memory")
        
        # Register tools
        tools = await create_memory_tools()
        for tool in tools:
            mcp.tool(tool)
        
        # Run server
        await mcp.run()
    
    asyncio.run(main())