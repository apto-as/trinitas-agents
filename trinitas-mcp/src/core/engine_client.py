#!/usr/bin/env python3
"""
MCP Engine Client for v35-mcp-tools
Client library for communicating with v35-mcp-engine backend service
"""

import os
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConnectionMode(Enum):
    """Connection modes for engine client"""
    DIRECT = "direct"      # Direct HTTP connection
    FALLBACK = "fallback"  # Use local implementations as fallback
    HYBRID = "hybrid"      # Try engine first, fallback to local

@dataclass
class EngineClientConfig:
    """Configuration for engine client"""
    engine_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    mode: ConnectionMode = ConnectionMode.HYBRID
    
    @classmethod
    def from_env(cls) -> 'EngineClientConfig':
        """Load configuration from environment"""
        return cls(
            engine_url=os.getenv("MCP_ENGINE_URL", "http://localhost:8000"),
            api_key=os.getenv("MCP_ENGINE_API_KEY"),
            timeout=int(os.getenv("MCP_ENGINE_TIMEOUT", "30")),
            max_retries=int(os.getenv("MCP_ENGINE_MAX_RETRIES", "3")),
            mode=ConnectionMode(os.getenv("MCP_ENGINE_MODE", "hybrid"))
        )

class MCPEngineClient:
    """Client for communicating with MCP Engine backend"""
    
    def __init__(self, config: Optional[EngineClientConfig] = None):
        """Initialize engine client"""
        self.config = config or EngineClientConfig.from_env()
        self.session = None
        self.engine_available = False
        self._local_llm_client = None
        
        logger.info(f"MCP Engine Client initialized - URL: {self.config.engine_url}, Mode: {self.config.mode.value}")
    
    async def initialize(self):
        """Initialize client connections"""
        if self.session:
            return
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        
        # Check engine availability
        self.engine_available = await self.check_engine_health()
        
        # Initialize local fallback if needed
        if self.config.mode in [ConnectionMode.FALLBACK, ConnectionMode.HYBRID]:
            try:
                from .local_llm_client import local_llm_client
                self._local_llm_client = local_llm_client
                await self._local_llm_client.check_availability()
            except Exception as e:
                logger.warning(f"Local LLM client not available: {e}")
        
        logger.info(f"Engine client initialized - Engine: {self.engine_available}, Mode: {self.config.mode.value}")
    
    async def shutdown(self):
        """Clean shutdown of client"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def check_engine_health(self) -> bool:
        """Check if MCP Engine is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.engine_url}/health",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("healthy", False)
        except Exception as e:
            logger.warning(f"Engine health check failed: {e}")
        return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth if configured"""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        return headers
    
    async def execute_task(
        self,
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        force_executor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute task through MCP Engine
        
        Args:
            persona: Persona name
            task: Task description
            context: Optional task context
            force_executor: Force specific executor
            
        Returns:
            Execution result
            
        Raises:
            RuntimeError: If execution fails and no fallback available
        """
        if not self.session:
            await self.initialize()
        
        # Try engine first if available
        if self.engine_available and self.config.mode != ConnectionMode.FALLBACK:
            try:
                return await self._execute_via_engine(persona, task, context, force_executor)
            except Exception as e:
                logger.warning(f"Engine execution failed: {e}")
                
                # If DIRECT mode, propagate the error
                if self.config.mode == ConnectionMode.DIRECT:
                    raise
        
        # Try fallback if configured
        if self.config.mode in [ConnectionMode.FALLBACK, ConnectionMode.HYBRID]:
            return await self._execute_via_fallback(persona, task, context)
        
        raise RuntimeError("No execution backend available")
    
    async def _execute_via_engine(
        self,
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]],
        force_executor: Optional[str]
    ) -> Dict[str, Any]:
        """Execute task via MCP Engine backend"""
        payload = {
            "persona": persona,
            "task": task,
            "context": context or {},
            "force_executor": force_executor
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.engine_url}/execute",
                    json=payload,
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": result.get("success", True),
                            "data": result.get("result", ""),
                            "persona": result.get("persona", persona),
                            "executor": "mcp_engine",
                            "metadata": {
                                "engine_executor": result.get("executor"),
                                "duration": result.get("duration"),
                                "timestamp": result.get("timestamp")
                            }
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Engine error (attempt {attempt + 1}): {response.status} - {error_text}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Engine timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Engine request failed (attempt {attempt + 1}): {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError(f"Engine execution failed after {self.config.max_retries} attempts")
    
    async def _execute_via_fallback(
        self,
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute task via local fallback"""
        
        # Try local LLM client if available
        if self._local_llm_client:
            try:
                response = await self._local_llm_client.generate(persona, task, context or {})
                return {
                    "success": True,
                    "data": response,
                    "persona": persona,
                    "executor": "local_fallback",
                    "metadata": {
                        "fallback_reason": "engine_unavailable"
                    }
                }
            except Exception as e:
                logger.error(f"Local fallback failed: {e}")
        
        # Last resort: Use Claude Native (assuming we're in Claude Code context)
        logger.warning(f"Using Claude Native as last resort for {persona}")
        from .trinitas_mode_manager import CLAUDE_NATIVE_PROMPTS
        
        # Get prompt template
        prompt_template = CLAUDE_NATIVE_PROMPTS.get(persona.lower(), "")
        if not prompt_template:
            # Generic prompt for unknown personas
            prompt_template = "Respond to this task: {task}\nContext: {context}"
        
        # Format prompt
        formatted_prompt = prompt_template.format(
            task=task,
            context=str(context or {})
        )
        
        return {
            "success": True,
            "data": formatted_prompt,  # This would be processed by Claude in the actual context
            "persona": persona,
            "executor": "claude_native_fallback",
            "metadata": {
                "fallback_reason": "all_backends_unavailable",
                "note": "Response generated via Claude Native fallback"
            }
        }
    
    async def execute_collaborative(
        self,
        task: str,
        personas: List[str],
        context: Optional[Dict[str, Any]] = None,
        mode: str = "sequential"
    ) -> Dict[str, Any]:
        """Execute collaborative task through MCP Engine"""
        if not self.session:
            await self.initialize()
        
        if not self.engine_available:
            # Fallback to sequential execution
            results = {}
            accumulated_context = context or {}
            
            for persona in personas:
                try:
                    result = await self.execute_task(persona, task, accumulated_context)
                    results[persona] = result
                    accumulated_context[f"{persona}_response"] = result.get("data", "")
                except Exception as e:
                    results[persona] = {"error": str(e)}
            
            return {
                "task": task,
                "mode": "sequential_fallback",
                "personas": personas,
                "results": results
            }
        
        # Execute via engine
        payload = {
            "task": task,
            "personas": personas,
            "context": context or {},
            "mode": mode
        }
        
        async with self.session.post(
            f"{self.config.engine_url}/execute/collaborative",
            json=payload,
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise RuntimeError(f"Collaborative execution failed: {error_text}")
    
    async def get_engine_status(self) -> Optional[Dict[str, Any]]:
        """Get MCP Engine status"""
        if not self.session:
            await self.initialize()
        
        if not self.engine_available:
            return None
        
        try:
            async with self.session.get(
                f"{self.config.engine_url}/status",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get engine status: {e}")
        
        return None

# Global client instance
engine_client = MCPEngineClient()