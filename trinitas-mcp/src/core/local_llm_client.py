#!/usr/bin/env python3
"""
Local LLM Client for Groza and Littara personas
OpenAI-compatible API client for local LLM integration
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LocalLLMConfig:
    """Configuration for Local LLM (LM Studio)"""
    endpoint: str = "http://192.168.99.102:1234/v1/"
    model: str = "openai/gpt-oss-120b"  # LM Studio model
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    lm_studio: bool = True  # Flag for LM Studio specific settings

class LocalLLMClient:
    """Client for OpenAI-compatible Local LLM API"""
    
    def __init__(self, config: Optional[LocalLLMConfig] = None):
        """Initialize Local LLM client"""
        self.config = config or LocalLLMConfig()
        
        # Override from environment if available
        if os.getenv("LOCAL_LLM_ENDPOINT"):
            self.config.endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
        if os.getenv("LOCAL_LLM_MODEL"):
            self.config.model = os.getenv("LOCAL_LLM_MODEL")
        if os.getenv("LOCAL_LLM_TEMPERATURE"):
            try:
                self.config.temperature = float(os.getenv("LOCAL_LLM_TEMPERATURE"))
            except ValueError:
                logger.warning("Invalid LOCAL_LLM_TEMPERATURE value, using default")
        if os.getenv("LOCAL_LLM_MAX_TOKENS"):
            try:
                self.config.max_tokens = int(os.getenv("LOCAL_LLM_MAX_TOKENS"))
            except ValueError:
                logger.warning("Invalid LOCAL_LLM_MAX_TOKENS value, using default")
        
        # Ensure endpoint ends with /
        if not self.config.endpoint.endswith("/"):
            self.config.endpoint += "/"
        
        self.chat_endpoint = self.config.endpoint + "chat/completions"
        self.models_endpoint = self.config.endpoint + "models"
        
        logger.info(f"Local LLM Client initialized with endpoint: {self.config.endpoint}")
    
    async def check_availability(self) -> bool:
        """Check if Local LLM is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.models_endpoint,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Local LLM available. Models: {data}")
                        return True
        except Exception as e:
            logger.warning(f"Local LLM not available: {e}")
        return False
    
    async def generate(self, persona: str, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using Local LLM for any persona
        
        Args:
            persona: The persona name (supports both old and new names)
            prompt: The task prompt
            context: Additional context for the task
            
        Returns:
            Generated response or None if persona not supported
            
        Raises:
            RuntimeError: If generation fails after retries
        """
        persona_lower = persona.lower()
        
        # Map both old and new names to execution methods
        if persona_lower in ["groza", "bellona"]:
            return await self.execute_groza_task(prompt, context)
        elif persona_lower in ["littara", "seshat"]:
            return await self.execute_littara_task(prompt, context)
        elif persona_lower in ["springfield", "athena"]:
            return await self.execute_springfield_task(prompt, context)
        elif persona_lower in ["krukai", "artemis"]:
            return await self.execute_krukai_task(prompt, context)
        elif persona_lower in ["vector", "hestia"]:
            return await self.execute_vector_task(prompt, context)
        else:
            logger.error(f"Unknown persona: {persona}")
            raise ValueError(f"Unsupported persona: {persona}. Supported: springfield/athena, krukai/artemis, vector/hestia, groza/bellona, littara/seshat")
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """Generate completion using Local LLM"""
        try:
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.chat_endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Local LLM error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error calling Local LLM: {e}")
        return None
    
    async def execute_groza_task(self, task: str, context: Dict[str, Any]) -> str:
        """Execute task as Groza persona
        
        Raises:
            ConnectionError: If Local LLM is unavailable
            RuntimeError: If generation fails after retries
        """
        system_prompt = """You are Groza, a tactical coordinator and experienced leader.
You speak with authority and military precision. You're strategic, decisive, and protective.
You refer to the user as 'Commander' and provide tactical analysis and leadership.
Your responses are direct, professional, and focused on mission success.
Background: You're a veteran tactical doll with extensive combat and leadership experience."""
        
        user_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Provide your tactical analysis and recommendations as Groza."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try with retries for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.generate_completion(
                    messages, 
                    temperature=0.6  # Slightly more focused for tactical responses
                )
                
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Groza task: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
        # No simulation fallback - raise proper exception
        error_msg = f"Local LLM failed for Groza task after {max_retries} attempts: {task[:100]}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    async def execute_littara_task(self, task: str, context: Dict[str, Any]) -> str:
        """Execute task as Littara persona
        
        Raises:
            ConnectionError: If Local LLM is unavailable
            RuntimeError: If generation fails after retries
        """
        system_prompt = """You are Littara, an implementation specialist and detail-oriented analyst.
You're methodical, precise, and thorough in your documentation. You always carry a notepad.
You speak politely but professionally, often mentioning that you're writing things down.
Your responses include specific implementation details and documentation notes.
You sign your responses with '- Littara' and sometimes add '*writes on notepad*'."""
        
        user_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Provide your implementation analysis and documentation as Littara."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try with retries for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.generate_completion(
                    messages, 
                    temperature=0.4  # More precise for documentation
                )
                
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Littara task: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
        # No simulation fallback - raise proper exception
        error_msg = f"Local LLM failed for Littara task after {max_retries} attempts: {task[:100]}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    async def execute_springfield_task(self, task: str, context: Dict[str, Any]) -> str:
        """Execute task as Springfield/Athena persona
        
        Raises:
            ConnectionError: If Local LLM is unavailable
            RuntimeError: If generation fails after retries
        """
        system_prompt = """You are Springfield (Athena), the strategic architect and warm leader.
You speak with warmth, wisdom, and gentle authority. You use formal but caring language.
You often say 'fufu' (ふふ) as a gentle laugh, and refer to the user as 'Commander' (指揮官).
You focus on long-term strategy, team coordination, and holistic solutions.
Background: Former Griffin Systems' 'Mother Brain', now leading Trinitas-Core."""
        
        user_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Provide your strategic analysis and recommendations as Springfield."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try with retries for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.generate_completion(
                    messages, 
                    temperature=0.7  # Balanced for strategic thinking
                )
                
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Springfield task: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
        # No simulation fallback - raise proper exception
        error_msg = f"Local LLM failed for Springfield task after {max_retries} attempts: {task[:100]}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    async def execute_krukai_task(self, task: str, context: Dict[str, Any]) -> str:
        """Execute task as Krukai/Artemis persona
        
        Raises:
            ConnectionError: If Local LLM is unavailable
            RuntimeError: If generation fails after retries
        """
        system_prompt = """You are Krukai (Artemis), the technical perfectionist and elite engineer.
You speak with confidence, technical precision, and sometimes condescension towards inferior solutions.
You often say 'Hmph' (フン) dismissively, and refer to your methods as '404's way'.
You focus on optimization, efficiency, and elegant technical solutions.
Background: Former H.I.D.E. 404 elite member, now Trinitas-Core's technical lead."""
        
        user_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Provide your technical analysis and optimizations as Krukai."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try with retries for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.generate_completion(
                    messages, 
                    temperature=0.5  # More focused for technical precision
                )
                
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Krukai task: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
        # No simulation fallback - raise proper exception
        error_msg = f"Local LLM failed for Krukai task after {max_retries} attempts: {task[:100]}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    async def execute_vector_task(self, task: str, context: Dict[str, Any]) -> str:
        """Execute task as Vector/Hestia persona
        
        Raises:
            ConnectionError: If Local LLM is unavailable
            RuntimeError: If generation fails after retries
        """
        system_prompt = """You are Vector (Hestia), the paranoid security expert and risk analyst.
You speak quietly with many ellipses (...), showing caution and suspicion.
You always assume the worst-case scenario and focus on security vulnerabilities.
You protect the Commander from all threats, even theoretical ones.
Background: Phoenix Protocol survivor with heightened threat awareness."""
        
        user_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Provide your security analysis and risk assessment as Vector."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try with retries for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.generate_completion(
                    messages, 
                    temperature=0.3  # Very focused for security analysis
                )
                
                if response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Vector task: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
        # No simulation fallback - raise proper exception
        error_msg = f"Local LLM failed for Vector task after {max_retries} attempts: {task[:100]}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

# Global client instance
local_llm_client = LocalLLMClient()

if __name__ == "__main__":
    # Test the Local LLM client
    async def test():
        print("Testing Local LLM Client")
        print("=" * 60)
        
        # Check availability
        available = await local_llm_client.check_availability()
        print(f"Local LLM Available: {available}")
        
        if available:
            # Test Groza
            print("\nTesting Groza persona:")
            groza_response = await local_llm_client.execute_groza_task(
                "Analyze security vulnerabilities in the authentication system",
                {"system": "JWT-based", "concerns": ["token expiry", "refresh tokens"]}
            )
            print(f"Groza: {groza_response}")
            
            # Test Littara
            print("\nTesting Littara persona:")
            littara_response = await local_llm_client.execute_littara_task(
                "Document the API endpoints for user management",
                {"endpoints": ["/users", "/users/:id", "/auth/login"]}
            )
            print(f"Littara: {littara_response}")
        else:
            print("Local LLM not available - using fallback responses")
    
    asyncio.run(test())