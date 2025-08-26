#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Engine
Main engine for executing persona tasks through real LLM backends
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import redis.asyncio as redis

from .engine_config import config, personas, PersonaConfig

logger = logging.getLogger(__name__)

class MCPEngine:
    """Main MCP Engine for persona execution"""
    
    def __init__(self):
        """Initialize MCP Engine"""
        self.config = config
        self.personas = personas
        self.redis_client = None
        self.session = None
        self.initialized = False
        
        # Track service availability
        self.claude_available = False
        self.local_llm_available = False
        
        logger.info(f"MCP Engine initialized in {config.mode.value} mode")
    
    async def initialize(self):
        """Initialize connections and services"""
        if self.initialized:
            return
        
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
            )
            
            # Initialize Redis connection
            self.redis_client = await redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Check service availability
            self.claude_available = await self._check_claude_service()
            self.local_llm_available = await self._check_local_llm_service()
            
            self.initialized = True
            logger.info(f"MCP Engine initialized - Claude: {self.claude_available}, Local LLM: {self.local_llm_available}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Engine: {e}")
            raise
    
    async def shutdown(self):
        """Clean shutdown of engine"""
        if self.session:
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()
        self.initialized = False
        logger.info("MCP Engine shutdown complete")
    
    async def _check_claude_service(self) -> bool:
        """Check if Claude MCP service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.claude_mcp_url}/health", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def _check_local_llm_service(self) -> bool:
        """Check if Local LLM service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.local_llm_url}/health", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def execute_task(
        self,
        persona: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        force_executor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a task with specified persona
        
        Args:
            persona: Persona name (any variant)
            task: Task description
            context: Optional context for the task
            force_executor: Force specific executor ('claude' or 'local_llm')
            
        Returns:
            Execution result with metadata
            
        Raises:
            ValueError: If persona not found
            RuntimeError: If execution fails
        """
        if not self.initialized:
            await self.initialize()
        
        # Get persona configuration
        persona_config = personas.get_by_name(persona)
        if not persona_config:
            raise ValueError(f"Unknown persona: {persona}")
        
        # Determine executor
        executor = self._determine_executor(persona_config, force_executor)
        
        # Execute based on executor
        start_time = datetime.now()
        
        try:
            if executor == "claude":
                result = await self._execute_claude(persona_config, task, context)
            elif executor == "local_llm":
                result = await self._execute_local_llm(persona_config, task, context)
            else:
                raise RuntimeError(f"Unknown executor: {executor}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "persona": persona_config.display_name,
                "mythology_name": persona_config.mythology_name,
                "executor": executor,
                "result": result,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task execution failed for {persona_config.name}: {e}")
            raise RuntimeError(f"Execution failed: {str(e)}")
    
    def _determine_executor(self, persona_config: PersonaConfig, force_executor: Optional[str]) -> str:
        """Determine which executor to use"""
        if force_executor:
            return force_executor
        
        # Check preferred executor availability
        if persona_config.executor_preference == "claude" and self.claude_available:
            return "claude"
        elif persona_config.executor_preference == "local_llm" and self.local_llm_available:
            return "local_llm"
        
        # Fallback logic (no simulation!)
        if self.claude_available:
            return "claude"
        elif self.local_llm_available:
            return "local_llm"
        else:
            raise RuntimeError("No execution backend available - both Claude and Local LLM are offline")
    
    async def _execute_claude(self, persona_config: PersonaConfig, task: str, context: Optional[Dict[str, Any]]) -> str:
        """Execute task using Claude MCP service"""
        payload = {
            "persona": persona_config.name,
            "task": task,
            "context": context or {},
            "temperature": persona_config.temperature,
            "max_tokens": persona_config.max_tokens
        }
        
        async with self.session.post(
            f"{self.config.claude_mcp_url}/execute",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"Claude MCP error: {response.status} - {error_text}")
            
            result = await response.json()
            return result.get("response", "")
    
    async def _execute_local_llm(self, persona_config: PersonaConfig, task: str, context: Optional[Dict[str, Any]]) -> str:
        """Execute task using Local LLM service"""
        payload = {
            "persona": persona_config.name,
            "task": task,
            "context": context or {},
            "temperature": persona_config.temperature,
            "max_tokens": persona_config.max_tokens
        }
        
        async with self.session.post(
            f"{self.config.local_llm_url}/execute",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"Local LLM error: {response.status} - {error_text}")
            
            result = await response.json()
            return result.get("response", "")
    
    async def execute_collaborative(
        self,
        task: str,
        personas: List[str],
        context: Optional[Dict[str, Any]] = None,
        mode: str = "sequential"
    ) -> Dict[str, Any]:
        """Execute task collaboratively with multiple personas
        
        Args:
            task: Task description
            personas: List of persona names
            context: Optional context
            mode: 'sequential' or 'parallel'
            
        Returns:
            Collaborative execution results
        """
        if not self.initialized:
            await self.initialize()
        
        results = {}
        
        if mode == "parallel":
            # Execute all personas in parallel
            tasks = []
            for persona in personas:
                tasks.append(self.execute_task(persona, task, context))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for persona, response in zip(personas, responses):
                if isinstance(response, Exception):
                    results[persona] = {"error": str(response)}
                else:
                    results[persona] = response
        
        else:  # sequential
            # Execute personas one by one, passing context forward
            accumulated_context = context or {}
            
            for persona in personas:
                try:
                    response = await self.execute_task(persona, task, accumulated_context)
                    results[persona] = response
                    
                    # Add response to context for next persona
                    accumulated_context[f"{persona}_response"] = response["result"]
                    
                except Exception as e:
                    results[persona] = {"error": str(e)}
                    logger.error(f"Failed to execute {persona}: {e}")
        
        return {
            "task": task,
            "mode": mode,
            "personas": personas,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "initialized": self.initialized,
            "mode": self.config.mode.value,
            "services": {
                "claude": self.claude_available,
                "local_llm": self.local_llm_available,
                "redis": self.redis_client is not None and await self.redis_client.ping()
            },
            "personas": {
                name: {
                    "display_name": config.display_name,
                    "mythology_name": config.mythology_name,
                    "preferred_executor": config.executor_preference,
                    "available": (
                        (config.executor_preference == "claude" and self.claude_available) or
                        (config.executor_preference == "local_llm" and self.local_llm_available) or
                        self.claude_available  # Claude as fallback
                    )
                }
                for name, config in personas.get_all().items()
            }
        }

# Global engine instance
engine = MCPEngine()