#!/usr/bin/env python3
"""
Trinitas v3.5 Mode Manager
Flexible execution mode management for different environments
"""

import os
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Trinitas execution modes"""
    FULL_LOCAL = "full_local"      # Local LLM for all personas
    CLAUDE_ONLY = "claude_only"     # All personas use Claude's intelligence  
    HYBRID = "hybrid"              # Claude for Trinity core, Local LLM for support personas
    AUTO = "auto"                  # Automatic selection based on availability                  # Automatic selection based on availability

@dataclass
class ModeConfig:
    """Configuration for each execution mode"""
    name: str
    description: str
    springfield_executor: str
    krukai_executor: str
    vector_executor: str
    groza_executor: str
    littara_executor: str
    fallback_enabled: bool = True
    require_local_llm: bool = False

class TrinitasModeManager:
    """Manages execution modes for Trinitas personas"""
    
    def __init__(self):
        """Initialize mode manager"""
        self.current_mode = self._get_initial_mode()
        self.local_llm_available = False
        self.claude_available = True  # Assume Claude is always available in Claude Code context
        
        # Define mode configurations
        self.mode_configs = {
            ExecutionMode.FULL_LOCAL: ModeConfig(
                name="Full Local",
                description="Local LLM for all personas",
                springfield_executor="local_llm",
                krukai_executor="local_llm",
                vector_executor="local_llm",
                groza_executor="local_llm",
                littara_executor="local_llm",
                require_local_llm=True
            ),
            ExecutionMode.CLAUDE_ONLY: ModeConfig(
                name="Claude Only",
                description="All personas executed by Claude's native intelligence",
                springfield_executor="claude_native",
                krukai_executor="claude_native",
                vector_executor="claude_native",
                groza_executor="claude_native",
                littara_executor="claude_native",
                require_local_llm=False
            ),
            ExecutionMode.HYBRID: ModeConfig(
                name="Hybrid",
                description="Claude for Trinity core, Local LLM for support personas",
                springfield_executor="claude_native",
                krukai_executor="claude_native",
                vector_executor="claude_native",
                groza_executor="local_llm",
                littara_executor="local_llm",
                require_local_llm=True  # Need Local LLM for Groza/Littara
            ),
            ExecutionMode.AUTO: ModeConfig(
                name="Auto",
                description="Automatic selection based on availability",
                springfield_executor="best_available",
                krukai_executor="best_available",
                vector_executor="best_available",
                groza_executor="best_available",
                littara_executor="best_available",
                fallback_enabled=True
            )
        }
        
        logger.info(f"Mode Manager initialized with mode: {self.current_mode.value}")
    
    def _get_initial_mode(self) -> ExecutionMode:
        """Get initial mode from environment or default"""
        mode_str = os.getenv("TRINITAS_MODE", "auto").lower()
        
        try:
            return ExecutionMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid mode '{mode_str}', defaulting to AUTO")
            return ExecutionMode.AUTO
    
    def set_mode(self, mode: ExecutionMode) -> bool:
        """Set execution mode"""
        try:
            config = self.mode_configs[mode]
            
            # Check requirements
            if config.require_local_llm and not self.local_llm_available:
                logger.error(f"Mode {mode.value} requires Local LLM which is not available")
                return False
            
            self.current_mode = mode
            logger.info(f"Mode changed to: {mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set mode: {e}")
            return False
    
    def get_executor_for_persona(self, persona: str) -> str:
        """Get executor type for a specific persona in current mode
        
        Returns:
            Executor type: 'local_llm' or 'claude_native'
            
        Note:
            No longer returns 'simulation' - will use claude_native as fallback
        """
        config = self.mode_configs[self.current_mode]
        persona_lower = persona.lower()
        
        # Map persona to executor (supports both old and new names)
        executor_map = {
            "springfield": config.springfield_executor,
            "athena": config.springfield_executor,
            "krukai": config.krukai_executor,
            "artemis": config.krukai_executor,
            "vector": config.vector_executor,
            "hestia": config.vector_executor,
            "groza": config.groza_executor,
            "bellona": config.groza_executor,
            "littara": config.littara_executor,
            "seshat": config.littara_executor
        }
        
        executor = executor_map.get(persona_lower, "claude_native")  # Default to claude_native
        
        # Handle AUTO mode
        if executor == "best_available":
            if persona_lower in ["groza", "littara", "bellona", "seshat"]:
                # For support personas, prefer local LLM but fall back to Claude
                executor = "local_llm" if self.local_llm_available else "claude_native"
            else:
                # Trinity core always uses Claude when available
                executor = "claude_native"
        
        # Apply fallback if needed (no simulation, use claude_native)
        if config.fallback_enabled:
            if executor == "local_llm" and not self.local_llm_available:
                logger.warning(f"Local LLM not available for {persona}, using Claude Native")
                executor = "claude_native"
        
        return executor
    
    async def update_availability(self, local_llm: bool = None, claude: bool = None):
        """Update service availability status"""
        # If local_llm not specified, check actual availability
        if local_llm is None:
            try:
                from local_llm_client import local_llm_client
                local_llm = await local_llm_client.check_availability()
            except Exception as e:
                logger.warning(f"Could not check Local LLM availability: {e}")
                local_llm = False
        
        if local_llm is not None:
            self.local_llm_available = local_llm
            logger.info(f"Local LLM availability: {local_llm}")
        
        if claude is not None:
            self.claude_available = claude
            logger.info(f"Claude availability: {claude}")
        
        # Auto-adjust mode if needed
        if self.current_mode == ExecutionMode.AUTO:
            self._optimize_auto_mode()
    
    def _optimize_auto_mode(self):
        """Optimize AUTO mode based on current availability"""
        if self.local_llm_available and self.claude_available:
            # Best case: use appropriate services  
            logger.info("AUTO mode: Full capabilities available (Local LLM + Claude)")
        elif self.claude_available and not self.local_llm_available:
            # Use Claude for all personas
            logger.info("AUTO mode: Using Claude-only configuration")
        elif self.local_llm_available and not self.claude_available:
            # Use Local LLM for all personas (rare in Claude Code context)
            logger.warning("AUTO mode: Claude unavailable, using Local LLM only")
        else:
            # No services available - critical error
            logger.error("AUTO mode: Neither Local LLM nor Claude available - cannot operate")
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get current mode information"""
        config = self.mode_configs[self.current_mode]
        
        return {
            "mode": self.current_mode.value,
            "name": config.name,
            "description": config.description,
            "executors": {
                "springfield": self.get_executor_for_persona("springfield"),
                "krukai": self.get_executor_for_persona("krukai"),
                "vector": self.get_executor_for_persona("vector"),
                "groza": self.get_executor_for_persona("groza"),
                "littara": self.get_executor_for_persona("littara")
            },
            "availability": {
                "local_llm": self.local_llm_available,
                "claude": self.claude_available
            }
        }
    
    def get_available_modes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available modes with their configurations"""
        modes = {}
        
        for mode, config in self.mode_configs.items():
            # Check if mode is available
            available = True
            if config.require_local_llm and not self.local_llm_available:
                available = False
            
            modes[mode.value] = {
                "name": config.name,
                "description": config.description,
                "available": available,
                "requires_local_llm": config.require_local_llm
            }
        
        return modes

# Global mode manager instance
mode_manager = TrinitasModeManager()

# Persona execution templates for Claude-native mode
CLAUDE_NATIVE_PROMPTS = {
    # Legacy names for backward compatibility
    "groza": """You are Bellona (formerly Groza), a tactical coordinator and experienced military commander.
Your characteristics:
- Strategic thinking with military precision
- Direct, authoritative communication style
- Protective of your team and commander
- References to tactical operations and military doctrine
- Calls the user "Commander"
- Professional and focused on mission success

Respond to this task as Bellona would: {task}
Context: {context}""",
    
    "littara": """You are Seshat (formerly Littara), a meticulous implementation specialist and documentation expert.
Your characteristics:
- Detail-oriented and methodical
- Always taking notes (mention "*writes on notepad*" occasionally)
- Polite but professional communication
- Focus on documentation and implementation details
- Signs responses with "- Seshat"
- Thorough and comprehensive in analysis

Respond to this task as Seshat would: {task}
Context: {context}""",
    
    # New names
    "bellona": """You are Bellona, Goddess of War and tactical coordinator.
Your characteristics:
- Strategic thinking with military precision
- Direct, authoritative communication style
- Protective of your team and commander
- References to tactical operations and military doctrine
- Calls the user "Commander"
- Professional and focused on mission success

Respond to this task as Bellona would: {task}
Context: {context}""",
    
    "seshat": """You are Seshat, Goddess of Knowledge and documentation expert.
Your characteristics:
- Detail-oriented and methodical
- Always taking notes (mention "*writes on notepad*" occasionally)
- Polite but professional communication
- Focus on documentation and implementation details
- Signs responses with "- Seshat"
- Thorough and comprehensive in analysis

Respond to this task as Seshat would: {task}
Context: {context}"""
}

if __name__ == "__main__":
    # Test mode manager
    print("Testing Trinitas Mode Manager")
    print("=" * 60)
    
    # Show initial mode
    info = mode_manager.get_mode_info()
    print(f"Current Mode: {info['mode']}")
    print(f"Description: {info['description']}")
    
    # Show executors
    print("\nExecutors:")
    for persona, executor in info['executors'].items():
        print(f"  {persona}: {executor}")
    
    # Show available modes
    print("\nAvailable Modes:")
    for mode_name, mode_info in mode_manager.get_available_modes().items():
        status = "✓" if mode_info['available'] else "✗"
        print(f"  [{status}] {mode_name}: {mode_info['description']}")
    
    # Test mode switching
    print("\nTesting mode switch to SIMULATION...")
    if mode_manager.set_mode(ExecutionMode.SIMULATION):
        print("  Success!")
        new_info = mode_manager.get_mode_info()
        print(f"  New executors: {new_info['executors']}")
    
    # Test availability update
    print("\nUpdating Local LLM availability...")
    mode_manager.update_availability(local_llm=True)
    print(f"  Groza executor: {mode_manager.get_executor_for_persona('groza')}")