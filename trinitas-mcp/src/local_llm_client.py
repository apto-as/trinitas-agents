"""
Local LLM Client for Trinitas v4.0
ローカルLLMとの実際の統合
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """LLM応答"""
    content: str
    model: str
    tokens_used: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None

class LocalLLMClient:
    """
    Local LLM Client
    OpenAI互換API (LM Studio, Ollama, etc.) をサポート
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("local_llm", {}).get("enabled", False)
        self.endpoint = config.get("local_llm", {}).get("endpoint", "http://localhost:1234/v1")
        self.model = config.get("local_llm", {}).get("model", "auto")
        self.api_key = os.getenv("LOCAL_LLM_API_KEY", "not-needed")  # Some local LLMs require dummy key
        
        # Request configuration
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout
        self.max_tokens = 2000
        self.temperature = 0.7
        
        # Performance tracking
        self.total_requests = 0
        self.total_tokens = 0
        self.average_response_time = 0
        
        logger.info(f"Local LLM Client initialized: enabled={self.enabled}, endpoint={self.endpoint}")
    
    async def check_connection(self) -> bool:
        """
        LLMサーバーとの接続をチェック
        """
        if not self.enabled:
            return False
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Try to get models list (OpenAI compatible endpoint)
                async with session.get(
                    f"{self.endpoint}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        if models:
                            logger.info(f"Available models: {[m.get('id') for m in models]}")
                            # Auto-select first model if set to "auto"
                            if self.model == "auto" and models:
                                self.model = models[0].get("id")
                                logger.info(f"Auto-selected model: {self.model}")
                        return True
                    else:
                        logger.warning(f"LLM connection check failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to connect to Local LLM: {e}")
            return False
    
    async def process_task(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """
        タスクをLocal LLMで処理
        
        Args:
            task: 処理するタスク
            context: 追加コンテキスト
            
        Returns:
            LLMResponse
        """
        if not self.enabled:
            return LLMResponse(
                content="Local LLM is disabled",
                model="none",
                tokens_used=0,
                response_time_ms=0,
                success=False,
                error="LLM disabled"
            )
        
        start_time = datetime.now()
        
        try:
            # Prepare prompt
            prompt = self._prepare_prompt(task, context)
            
            # Prepare request payload (OpenAI format)
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.endpoint}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract response
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        model_used = data.get("model", self.model)
                        
                        # Calculate response time
                        response_time = (datetime.now() - start_time).total_seconds() * 1000
                        
                        # Update statistics
                        self.total_requests += 1
                        self.total_tokens += tokens
                        self.average_response_time = (
                            (self.average_response_time * (self.total_requests - 1) + response_time) 
                            / self.total_requests
                        )
                        
                        logger.info(f"LLM processed task in {response_time:.0f}ms, tokens: {tokens}")
                        
                        return LLMResponse(
                            content=content,
                            model=model_used,
                            tokens_used=tokens,
                            response_time_ms=response_time,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM request failed: {response.status} - {error_text}")
                        return LLMResponse(
                            content="",
                            model=self.model,
                            tokens_used=0,
                            response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                            success=False,
                            error=f"HTTP {response.status}: {error_text[:100]}"
                        )
                        
        except asyncio.TimeoutError:
            logger.error("LLM request timed out")
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                response_time_ms=self.timeout.total * 1000,
                success=False,
                error="Request timed out"
            )
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                error=str(e)
            )
    
    async def process_batch(self, tasks: List[str], max_parallel: int = 3) -> List[LLMResponse]:
        """
        複数タスクをバッチ処理
        
        Args:
            tasks: タスクリスト
            max_parallel: 最大並列数
            
        Returns:
            応答リスト
        """
        results = []
        
        # Process in chunks
        for i in range(0, len(tasks), max_parallel):
            chunk = tasks[i:i + max_parallel]
            chunk_results = await asyncio.gather(
                *[self.process_task(task) for task in chunk],
                return_exceptions=True
            )
            
            for result in chunk_results:
                if isinstance(result, Exception):
                    results.append(LLMResponse(
                        content="",
                        model=self.model,
                        tokens_used=0,
                        response_time_ms=0,
                        success=False,
                        error=str(result)
                    ))
                else:
                    results.append(result)
        
        return results
    
    def _prepare_prompt(self, task: str, context: Optional[Dict]) -> str:
        """
        プロンプトを準備
        """
        prompt_parts = []
        
        # Add task
        prompt_parts.append(f"Task: {task}")
        
        # Add context if available
        if context:
            if context.get("project"):
                prompt_parts.append(f"Project: {context['project']}")
            if context.get("requirements"):
                prompt_parts.append(f"Requirements: {context['requirements']}")
            if context.get("constraints"):
                prompt_parts.append(f"Constraints: {context['constraints']}")
            if context.get("memory_context"):
                # Add relevant memories
                memories = context['memory_context']
                if memories:
                    prompt_parts.append("\nRelevant Context from Memory:")
                    for key, value in memories.items():
                        if value:
                            prompt_parts.append(f"- {key}: {str(value)[:200]}")
        
        return "\n".join(prompt_parts)
    
    def _get_system_prompt(self) -> str:
        """
        システムプロンプトを取得
        """
        return """You are an AI assistant integrated with the Trinitas system.
You are handling lower-priority tasks that have been delegated by Bellona's tactical distribution system.
Your responses should be:
1. Concise and actionable
2. Technically accurate
3. Following the project's coding standards
4. Optimized for the specific task type

Focus on efficiency and correctness. You are part of a larger intelligent system."""
    
    async def estimate_tokens(self, text: str) -> int:
        """
        トークン数を推定
        
        Simple estimation: ~4 chars per token for English, ~2 chars per token for Japanese
        """
        # Rough estimation
        english_chars = sum(1 for c in text if ord(c) < 128)
        japanese_chars = len(text) - english_chars
        
        estimated = (english_chars / 4) + (japanese_chars / 2)
        return int(estimated * 1.2)  # Add 20% buffer
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        使用統計を取得
        """
        return {
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "model": self.model,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "average_response_time_ms": self.average_response_time,
            "average_tokens_per_request": self.total_tokens / max(1, self.total_requests)
        }
    
    async def optimize_model_selection(self, task_type: str) -> str:
        """
        タスクタイプに基づいてモデルを最適化選択
        
        Args:
            task_type: タスクタイプ
            
        Returns:
            最適なモデル名
        """
        # Model selection based on task type
        model_preferences = {
            "code_formatting": "codellama",  # Good for code
            "documentation_generation": "mistral",  # Good for text
            "simple_analysis": "llama3",  # Balanced
            "data_transformation": "phi",  # Fast and lightweight
        }
        
        preferred_model = model_preferences.get(task_type)
        
        if preferred_model:
            # Check if preferred model is available
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(
                        f"{self.endpoint}/models",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            models = [m.get("id") for m in data.get("data", [])]
                            
                            # Check if preferred model is available
                            for model in models:
                                if preferred_model.lower() in model.lower():
                                    logger.info(f"Selected optimized model for {task_type}: {model}")
                                    return model
            except:
                pass
        
        # Return default model
        return self.model

class LocalLLMManager:
    """
    Local LLM Manager
    複数のLLMインスタンスを管理
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.primary_client = LocalLLMClient(config)
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.worker_task = None
        
    async def start(self):
        """マネージャーを開始"""
        # Check connection
        connected = await self.primary_client.check_connection()
        if connected:
            logger.info("Local LLM Manager started successfully")
            # Start worker
            self.worker_task = asyncio.create_task(self._process_queue())
        else:
            logger.warning("Local LLM Manager started but LLM is not available")
    
    async def stop(self):
        """マネージャーを停止"""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _process_queue(self):
        """キューを処理"""
        while True:
            try:
                task_data = await self.task_queue.get()
                task_id = task_data["id"]
                task = task_data["task"]
                context = task_data.get("context")
                
                # Process task
                result = await self.primary_client.process_task(task, context)
                
                # Store result
                self.results[task_id] = result
                
                logger.info(f"Processed queued task: {task_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    async def submit_task(self, task_id: str, task: str, context: Optional[Dict] = None) -> str:
        """
        タスクをキューに送信
        
        Returns:
            Task ID for tracking
        """
        await self.task_queue.put({
            "id": task_id,
            "task": task,
            "context": context
        })
        return task_id
    
    async def get_result(self, task_id: str, timeout: float = 60) -> Optional[LLMResponse]:
        """
        結果を取得（ポーリング）
        """
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            if task_id in self.results:
                return self.results.pop(task_id)
            await asyncio.sleep(0.5)
        return None