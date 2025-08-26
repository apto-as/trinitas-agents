#!/usr/bin/env python3
"""
MCP Server entry point for v35-mcp-tools
Provides MCP protocol interface for Claude Code integration
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for compatibility
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.trinitas_mcp_tools import TrinitasMCPTools
from src.core.engine_client import engine_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation for Trinitas tools"""
    
    def __init__(self):
        self.tools = TrinitasMCPTools()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the MCP server"""
        if not self.initialized:
            # TrinitasMCPTools initializes in __init__, no need to call initialize
            await engine_client.initialize()
            self.initialized = True
            logger.info("MCP Server initialized")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        if not self.initialized:
            await self.initialize()
        
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "capabilities": {
                            "tools": ["trinitas_execute", "trinitas_collaborate", "trinitas_status"]
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "trinitas_execute",
                                "description": "Execute task with specified Trinitas persona",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "persona": {"type": "string"},
                                        "task": {"type": "string"},
                                        "context": {"type": "object"}
                                    },
                                    "required": ["persona", "task"]
                                }
                            },
                            {
                                "name": "trinitas_collaborate",
                                "description": "Execute task collaboratively with multiple personas",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string"},
                                        "personas": {"type": "array", "items": {"type": "string"}},
                                        "mode": {"type": "string", "enum": ["sequential", "parallel"]}
                                    },
                                    "required": ["task", "personas"]
                                }
                            },
                            {
                                "name": "trinitas_status",
                                "description": "Get Trinitas system status",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "trinitas_execute":
                    result = await self.tools.persona_execute(
                        persona=arguments.get("persona"),
                        task=arguments.get("task"),
                        context=arguments.get("context")
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result.__dict__ if hasattr(result, '__dict__') else result
                    }
                
                elif tool_name == "trinitas_collaborate":
                    result = await engine_client.execute_collaborative(
                        task=arguments.get("task"),
                        personas=arguments.get("personas"),
                        context=arguments.get("context"),
                        mode=arguments.get("mode", "sequential")
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                elif tool_name == "trinitas_status":
                    status = await engine_client.get_engine_status()
                    if not status:
                        status = {
                            "engine": "unavailable",
                            "mode": self.tools.mode_manager.current_mode.value,
                            "fallback": "active"
                        }
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": status
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run_stdio(self):
        """Run MCP server in STDIO mode"""
        logger.info("Starting MCP Server in STDIO mode")
        
        while True:
            try:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                # Parse request
                request = json.loads(line)
                
                # Handle request
                response = await self.handle_request(request)
                
                # Write response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Server error: {e}")
                break
        
        # Cleanup
        await engine_client.shutdown()
        logger.info("MCP Server stopped")

async def main():
    """Main entry point"""
    server = MCPServer()
    await server.run_stdio()

def run_server():
    """Entry point for uv command"""
    asyncio.run(main())

if __name__ == "__main__":
    run_server()