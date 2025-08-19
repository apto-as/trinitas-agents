#!/usr/bin/env python3
"""
Trinitas v3.5 - Local LLM Connector
Manages communication with Qwen Code + GPT-OSS-120B
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import aiohttp
import yaml
from pathlib import Path


class ExecutorType(Enum):
    """Task executor types"""
    CLAUDE = "claude"
    LOCAL = "local"
    HYBRID = "hybrid"


class CognitiveComplexity(Enum):
    """Cognitive complexity levels"""
    MECHANICAL = 1  # Simple, repetitive
    ANALYTICAL = 2  # Pattern matching
    REASONING = 3   # Logic required
    CREATIVE = 4    # Novel solutions
    STRATEGIC = 5   # Long-term planning


@dataclass
class TaskRequest:
    """Request to process a task"""
    id: str
    type: str
    description: str
    estimated_tokens: int
    required_tools: List[str]
    complexity: Optional[CognitiveComplexity] = None
    priority: str = "normal"
    context: Optional[Dict] = None


@dataclass
class TaskResponse:
    """Response from task execution"""
    id: str
    executor: str
    result: Any
    tokens_used: int
    duration: float
    confidence: float
    errors: List[str] = None


class LocalLLMConnector:
    """
    Connector for Local LLM (Qwen Code + GPT-OSS-120B)
    Optimized for English processing and tool use
    """
    
    def __init__(self, config_path: str = None):
        """Initialize connector with configuration"""
        self.config = self._load_config(config_path)
        self.endpoint = self.config['local_llm']['connection']['endpoint']
        self.api_key = os.getenv('LOCAL_LLM_API_KEY', '')
        self.session = None
        self.health_status = "unknown"
        self.last_health_check = 0
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize HTTP session and check health"""
        self.session = aiohttp.ClientSession()
        await self.check_health()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> bool:
        """Check if Local LLM is available"""
        try:
            async with self.session.get(
                f"{self.endpoint}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            ) as response:
                if response.status == 200:
                    self.health_status = "healthy"
                    self.last_health_check = time.time()
                    return True
        except Exception as e:
            self.health_status = f"unhealthy: {str(e)}"
        
        return False
    
    async def execute(
        self,
        task: TaskRequest,
        tools: Optional[List[Dict]] = None
    ) -> TaskResponse:
        """
        Execute task using Local LLM
        Optimized for English and tool use
        """
        start_time = time.time()
        
        # Format prompt for English optimization
        prompt = self._format_english_prompt(task)
        
        # Prepare request payload
        payload = {
            "model": self.config['local_llm']['model']['name'],
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config['local_llm']['optimization']['temperature'],
            "max_tokens": self.config['local_llm']['optimization']['max_tokens'],
            "top_p": self.config['local_llm']['optimization']['top_p'],
        }
        
        # Add tools if required
        if tools or task.required_tools:
            payload["tools"] = self._prepare_tools(tools, task.required_tools)
            payload["tool_choice"] = "auto"
        
        try:
            # Make API call
            async with self.session.post(
                f"{self.endpoint}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.config['local_llm']['connection']['timeout']
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return TaskResponse(
                        id=task.id,
                        executor="local",
                        result=None,
                        tokens_used=0,
                        duration=time.time() - start_time,
                        confidence=0.0,
                        errors=[f"API error: {response.status} - {error_text}"]
                    )
                
                # Parse response
                data = await response.json()
                
                # Extract result and tool calls
                result = self._parse_response(data)
                
                return TaskResponse(
                    id=task.id,
                    executor="local",
                    result=result,
                    tokens_used=data.get('usage', {}).get('total_tokens', 0),
                    duration=time.time() - start_time,
                    confidence=self._calculate_confidence(task, result),
                    errors=[]
                )
                
        except asyncio.TimeoutError:
            return TaskResponse(
                id=task.id,
                executor="local",
                result=None,
                tokens_used=0,
                duration=time.time() - start_time,
                confidence=0.0,
                errors=["Request timeout"]
            )
        except Exception as e:
            return TaskResponse(
                id=task.id,
                executor="local",
                result=None,
                tokens_used=0,
                duration=time.time() - start_time,
                confidence=0.0,
                errors=[f"Execution error: {str(e)}"]
            )
    
    def _format_english_prompt(self, task: TaskRequest) -> str:
        """
        Format prompt optimized for English processing
        """
        prompt_parts = [
            f"Task ID: {task.id}",
            f"Task Type: {task.type}",
            f"Priority: {task.priority}",
            "",
            "Description:",
            task.description,
            ""
        ]
        
        if task.required_tools:
            prompt_parts.extend([
                "Required Tools:",
                "- " + "\n- ".join(task.required_tools),
                ""
            ])
        
        if task.context:
            prompt_parts.extend([
                "Context:",
                json.dumps(task.context, indent=2),
                ""
            ])
        
        prompt_parts.extend([
            "Instructions:",
            "1. Analyze the task thoroughly",
            "2. Use the required tools effectively",
            "3. Provide structured output",
            "4. Include confidence assessment",
            "5. Report any issues encountered"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for Local LLM"""
        return """You are an expert software engineer assistant optimized for:
- Processing large amounts of data efficiently
- Using tools and MCP servers effectively
- Generating comprehensive test cases
- Analyzing code patterns and metrics
- Providing structured, actionable output

Focus on mechanical precision and thorough analysis.
Always use tools when available to gather accurate information.
Provide JSON-structured output when possible."""
    
    def _prepare_tools(
        self,
        tools: Optional[List[Dict]],
        required_tools: List[str]
    ) -> List[Dict]:
        """Prepare tool definitions for API call"""
        tool_definitions = []
        
        # Add MCP tools
        if "mcp_server" in required_tools:
            tool_definitions.append({
                "type": "function",
                "function": {
                    "name": "mcp_server_call",
                    "description": "Call MCP server tools",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool": {"type": "string"},
                            "params": {"type": "object"}
                        },
                        "required": ["tool", "params"]
                    }
                }
            })
        
        # Add file operations
        if "file_operations" in required_tools:
            tool_definitions.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": "Read file contents",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            },
                            "required": ["path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "search_files",
                        "description": "Search for patterns in files",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pattern": {"type": "string"},
                                "path": {"type": "string"},
                                "file_type": {"type": "string"}
                            },
                            "required": ["pattern"]
                        }
                    }
                }
            ])
        
        # Add bash execution
        if "bash" in required_tools:
            tool_definitions.append({
                "type": "function",
                "function": {
                    "name": "execute_bash",
                    "description": "Execute bash commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "working_dir": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            })
        
        # Add custom tools if provided
        if tools:
            tool_definitions.extend(tools)
        
        return tool_definitions
    
    def _parse_response(self, data: Dict) -> Dict:
        """Parse API response and extract results"""
        choices = data.get('choices', [])
        if not choices:
            return {"error": "No response generated"}
        
        message = choices[0].get('message', {})
        
        result = {
            "content": message.get('content', ''),
            "tool_calls": []
        }
        
        # Extract tool calls if present
        if 'tool_calls' in message:
            for tool_call in message['tool_calls']:
                result["tool_calls"].append({
                    "id": tool_call.get('id'),
                    "function": tool_call.get('function', {}).get('name'),
                    "arguments": json.loads(
                        tool_call.get('function', {}).get('arguments', '{}')
                    )
                })
        
        return result
    
    def _calculate_confidence(self, task: TaskRequest, result: Dict) -> float:
        """Calculate confidence in the result"""
        confidence = 0.5  # Base confidence
        
        # Adjust based on task complexity
        if task.complexity:
            if task.complexity.value <= 2:  # Mechanical or Analytical
                confidence = 0.9  # High confidence for simple tasks
            elif task.complexity.value == 3:  # Reasoning
                confidence = 0.7  # Moderate confidence
            else:  # Creative or Strategic
                confidence = 0.5  # Lower confidence for complex tasks
        
        # Adjust based on tool usage
        if result.get("tool_calls"):
            confidence += 0.1  # Higher confidence with tool use
        
        # Adjust based on result completeness
        if result.get("content") and len(result["content"]) > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)


# Example usage
async def main():
    """Example of using Local LLM Connector"""
    connector = LocalLLMConnector()
    await connector.initialize()
    
    # Create a test task
    task = TaskRequest(
        id="test-001",
        type="file_search",
        description="Search for all Python files containing 'async def'",
        estimated_tokens=5000,
        required_tools=["file_operations"],
        complexity=CognitiveComplexity.MECHANICAL
    )
    
    # Execute task
    response = await connector.execute(task)
    
    print(f"Task ID: {response.id}")
    print(f"Executor: {response.executor}")
    print(f"Tokens Used: {response.tokens_used}")
    print(f"Duration: {response.duration:.2f}s")
    print(f"Confidence: {response.confidence:.2%}")
    print(f"Result: {json.dumps(response.result, indent=2)}")
    
    await connector.cleanup()


if __name__ == "__main__":
    asyncio.run(main())