"""
Trinitas v3.5 MCP Tools
Claude Code Integration Package
"""

from .trinitas_mcp_tools import (
    TrinitasMCPTools,
    PersonaType,
    CollaborationMode,
    QualityLevel,
    OptimizationTarget,
    ToolResult,
    trinitas_tools
)

from .component_wrapper import (
    ComponentWrapper,
    DelegationEngine,
    component_wrapper
)

__version__ = "3.5.0"
__author__ = "Trinitas Core Team"

__all__ = [
    "TrinitasMCPTools",
    "PersonaType",
    "CollaborationMode",
    "QualityLevel",
    "OptimizationTarget",
    "ToolResult",
    "trinitas_tools",
    "ComponentWrapper",
    "DelegationEngine",
    "component_wrapper"
]