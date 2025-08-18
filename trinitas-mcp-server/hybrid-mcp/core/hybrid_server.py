#!/usr/bin/env python3
"""
Trinity Hybrid MCP Server
Automatically switches between Claude-optimized and Universal implementations
"""

from fastmcp import FastMCP, Context
from typing import Dict, Any, Optional, Literal
from enum import Enum
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================
# Client Detection
# =====================================

class ClientType(Enum):
    """Detected client types"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    QWEN = "qwen"
    UNKNOWN = "unknown"


class ClientDetector:
    """Detect and classify MCP clients"""
    
    @staticmethod
    def detect(context: Optional[Context] = None) -> ClientType:
        """Detect client type from context"""
        if not context:
            return ClientType.UNKNOWN
            
        # Check various indicators
        headers = context.request_headers if hasattr(context, 'request_headers') else {}
        user_agent = headers.get('user-agent', '').lower()
        
        # Detection logic
        client_name = ""
        if hasattr(context, 'client_info') and hasattr(context.client_info, 'name'):
            client_name = str(context.client_info.name).lower()
        
        if 'claude' in user_agent or client_name == "claude-code":
            return ClientType.CLAUDE
        elif 'gemini' in user_agent or 'gemini' in client_name:
            return ClientType.GEMINI
        elif 'qwen' in user_agent or 'qwen' in client_name:
            return ClientType.QWEN
            
        # Check for Claude-specific features
        if hasattr(context, 'supports_sampling') and context.supports_sampling:
            return ClientType.CLAUDE
            
        return ClientType.UNKNOWN
    
    @staticmethod
    def get_capabilities(client_type: ClientType) -> Dict[str, Any]:
        """Get client capabilities"""
        capabilities = {
            ClientType.CLAUDE: {
                "supports_parallel": True,
                "supports_sampling": True,
                "supports_native_agents": True,
                "max_context": 200000,
                "has_todo_write": True,
                "has_web_search": True,
            },
            ClientType.GEMINI: {
                "supports_parallel": False,
                "supports_sampling": False,
                "supports_native_agents": False,
                "max_context": 32000,
                "has_todo_write": False,
                "has_web_search": False,
            },
            ClientType.QWEN: {
                "supports_parallel": False,
                "supports_sampling": False,
                "supports_native_agents": False,
                "max_context": 8192,
                "has_todo_write": False,
                "has_web_search": False,
            },
            ClientType.UNKNOWN: {
                "supports_parallel": False,
                "supports_sampling": False,
                "supports_native_agents": False,
                "max_context": 4096,
                "has_todo_write": False,
                "has_web_search": False,
            }
        }
        
        return capabilities.get(client_type, capabilities[ClientType.UNKNOWN])


# =====================================
# Hybrid MCP Server
# =====================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def initialize_hybrid_server(app):
    """Initialize hybrid server components"""
    logger.info("Trinity Hybrid MCP Server starting...")
    
    # Load persona definitions
    personas_path = Path(__file__).parent.parent.parent / "personas"
    if personas_path.exists():
        logger.info(f"Loading personas from {personas_path}")
    
    # Initialize implementations
    global claude_impl, universal_impl
    
    # Load implementations (lazy loading)
    try:
        from claude.claude_optimized import initialize_claude
        claude_impl = initialize_claude  # Store the function, not the result
        logger.info("Claude optimizations available")
    except ImportError:
        logger.warning("Claude optimizations not available")
    
    try:
        from universal.universal_impl import initialize_universal
        universal_impl = initialize_universal  # Store the function, not the result
        logger.info("Universal implementation available")
    except ImportError:
        logger.warning("Universal implementation not available")
    
    logger.info("Trinity Hybrid MCP Server ready")
    yield  # Server is running
    logger.info("Trinity Hybrid MCP Server shutting down")

app = FastMCP(
    name="trinity-hybrid-mcp",
    version="1.0.0",
    instructions="Hybrid Trinity MCP Server - Optimized for Claude, Compatible with All",
    lifespan=initialize_hybrid_server
)

# Global instances (will be initialized on startup)
client_detector = ClientDetector()
claude_impl = None  # Will be loaded if Claude detected
universal_impl = None  # Always loaded as fallback


# =====================================
# Core Tools - Auto-switching
# =====================================

@app.tool()
async def set_persona(
    persona: Literal["springfield", "krukai", "vector", "trinity"],
    context: Context
) -> Dict[str, Any]:
    """
    Set active persona - automatically optimized for client
    """
    client_type = client_detector.detect(context)
    capabilities = client_detector.get_capabilities(client_type)
    
    logger.info(f"Client detected: {client_type.value}, using optimized path")
    
    if client_type == ClientType.CLAUDE and capabilities["supports_native_agents"]:
        # Claude-optimized path
        from ..claude.claude_optimized import set_persona_claude
        return await set_persona_claude(persona, context)
    else:
        # Universal fallback
        from ..universal.universal_impl import set_persona_universal
        return await set_persona_universal(persona, context)


@app.tool()
async def trinity_analyze(
    task: str,
    mode: Literal["sequential", "parallel", "consensus"] = "sequential",
    context: Context = None
) -> Dict[str, Any]:
    """
    Trinity analysis - switches between native parallel and simulated
    """
    client_type = client_detector.detect(context)
    capabilities = client_detector.get_capabilities(client_type)
    
    result = {
        "task": task,
        "mode": mode,
        "client": client_type.value,
        "execution_path": "optimized" if client_type == ClientType.CLAUDE else "universal"
    }
    
    if mode == "parallel":
        if capabilities["supports_parallel"]:
            # True parallel for Claude
            logger.info("Using native parallel execution")
            from ..claude.claude_optimized import execute_parallel_claude
            result["analysis"] = await execute_parallel_claude(task, context)
            result["parallel_type"] = "native"
        else:
            # Simulated parallel for others
            logger.info("Using simulated parallel execution")
            from ..universal.universal_impl import simulate_parallel
            result["analysis"] = await simulate_parallel(task)
            result["parallel_type"] = "simulated"
    else:
        # Sequential execution (works for all)
        from ..universal.universal_impl import execute_sequential
        result["analysis"] = await execute_sequential(task, mode)
        
    return result


@app.tool()
async def execute_with_hooks(
    operation: str,
    params: Dict[str, Any],
    context: Context = None
) -> Dict[str, Any]:
    """
    Execute with Trinity hooks - adapts to client capabilities
    """
    client_type = client_detector.detect(context)
    
    if client_type == ClientType.CLAUDE:
        # Use Claude's native hooks
        from ..claude.claude_hooks import execute_with_claude_hooks
        return await execute_with_claude_hooks(operation, params)
    else:
        # Use internal hook system
        from ..universal.universal_hooks import execute_with_universal_hooks
        return await execute_with_universal_hooks(operation, params)


@app.tool()
async def manage_state(
    operation: Literal["get", "set", "list", "clear"],
    key: Optional[str] = None,
    value: Optional[Any] = None,
    context: Context = None
) -> Dict[str, Any]:
    """
    State management - uses TodoWrite for Claude, internal for others
    """
    client_type = client_detector.detect(context)
    capabilities = client_detector.get_capabilities(client_type)
    
    if client_type == ClientType.CLAUDE and capabilities["has_todo_write"]:
        # Use TodoWrite for state
        from ..claude.claude_state import manage_with_todowrite
        return await manage_with_todowrite(operation, key, value)
    else:
        # Use internal state manager
        from ..universal.state_manager import manage_internal_state
        return await manage_internal_state(operation, key, value, context)


@app.tool()
async def enhanced_search(
    query: str,
    search_type: Literal["web", "code", "both"] = "both",
    context: Context = None
) -> Dict[str, Any]:
    """
    Enhanced search - uses WebSearch for Claude, alternatives for others
    """
    client_type = client_detector.detect(context)
    capabilities = client_detector.get_capabilities(client_type)
    
    results = {"query": query, "search_type": search_type}
    
    if capabilities["has_web_search"] and search_type in ["web", "both"]:
        # Use Claude's WebSearch
        results["web_results"] = {
            "tool": "WebSearch",
            "query": query,
            "instruction": "Use Claude's native WebSearch tool"
        }
    
    if search_type in ["code", "both"]:
        # Code search (universal)
        from ..universal.search_impl import search_codebase
        results["code_results"] = await search_codebase(query)
    
    return results


# =====================================
# Capability Declaration
# =====================================

@app.resource("capabilities/{client_type}")
async def get_capabilities(client_type: str) -> Dict[str, Any]:
    """Get capabilities for specific client type"""
    try:
        client_enum = ClientType(client_type.lower())
        return client_detector.get_capabilities(client_enum)
    except ValueError:
        return client_detector.get_capabilities(ClientType.UNKNOWN)


@app.resource("trinity://hybrid/status")
async def get_hybrid_status() -> Dict[str, Any]:
    """Get current hybrid server status"""
    return {
        "mode": "hybrid",
        "version": "1.0.0",
        "supported_clients": [c.value for c in ClientType],
        "optimizations": {
            "claude": "Native agents, TodoWrite, WebSearch, Parallel",
            "universal": "Simulated parallel, Internal state, Fallback search"
        },
        "auto_detection": True,
        "graceful_degradation": True
    }


# =====================================
# Middleware for Quality Enforcement
# =====================================

async def trinity_quality_gate(request, handler):
    """
    Universal quality gate - 100% standard for all clients
    """
    # Pre-execution check
    if hasattr(request, 'quality_requirement'):
        if request.quality_requirement != 1.0:
            raise ValueError("Trinity requires 100% quality standard")
    
    # Execute
    response = await handler(request)
    
    # Post-execution validation
    if hasattr(response, 'quality_score'):
        if response.quality_score < 1.0:
            # Springfield's gentle enforcement
            raise ValueError(
                "ふふ、素晴らしい努力ですわ。"
                "でも、100%を目指しましょうね♪"
                f"（現在: {response.quality_score:.1%}）"
            )
    
    return response


async def client_detection_middleware(request, handler):
    """
    Detect and log client for every request
    """
    # Note: Context not available in FastMCP v2 middleware
    # Client detection happens in tool handlers via context parameter
    logger.info(f"Processing request")
    
    return await handler(request)

# Add middleware to app after definition
app.add_middleware(trinity_quality_gate)
app.add_middleware(client_detection_middleware)


# Note: Initialization is handled in the lifespan function above


# =====================================
# Main Entry Point
# =====================================

if __name__ == "__main__":
    import asyncio
    
    # For development/testing
    async def test_server():
        await initialize_hybrid_server()
        
        # Test client detection
        mock_context = Context()
        client = client_detector.detect(mock_context)
        print(f"Detected client: {client}")
        
        # Test capability check
        caps = client_detector.get_capabilities(client)
        print(f"Capabilities: {caps}")
    
    asyncio.run(test_server())