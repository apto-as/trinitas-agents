"""
LLM Router for Trinitas v5.0
タスク分散とローカルLLM/Claude Code headless統合

This module provides intelligent task routing between:
- Main Claude instance (for critical tasks)
- Local LLM (for routine tasks)
- Claude Code headless (fallback)
- Qwen Code headless (alternative)
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """LLMプロバイダー種別"""
    MAIN_CLAUDE = "main_claude"           # メインClaude（重要タスク用）
    LOCAL_LLM = "local_llm"                # ローカルLLM（定型タスク用）
    CLAUDE_CODE_HEADLESS = "claude_code"  # Claude Code headless（フォールバック）
    QWEN_CODE_HEADLESS = "qwen_code"      # Qwen Code headless（代替）

@dataclass
class TaskRoute:
    """タスクルーティング決定"""
    task_id: str
    provider: LLMProvider
    reason: str
    estimated_tokens: int
    priority: float
    metadata: Dict[str, Any]

class ErisLLMRouter:
    """
    Eris - 分散処理コーディネーター
    タスクの性質に基づいて最適なLLMプロバイダーへルーティング
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers(config)
        self.routing_rules = self._load_routing_rules(config)
        self.performance_stats = {}
        
    def _initialize_providers(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """プロバイダーを初期化"""
        providers = {}
        
        # Local LLM設定
        if config.get("local_llm", {}).get("enabled", False):
            providers[LLMProvider.LOCAL_LLM] = {
                "endpoint": config["local_llm"].get("endpoint", "http://localhost:1234/v1"),
                "model": config["local_llm"].get("model", "auto"),
                "max_tokens": config["local_llm"].get("max_tokens", 2000),
                "available": True
            }
        
        # Claude Code headless設定
        if config.get("claude_code_headless", {}).get("enabled", False):
            providers[LLMProvider.CLAUDE_CODE_HEADLESS] = {
                "endpoint": config["claude_code_headless"].get("endpoint"),
                "api_key": config["claude_code_headless"].get("api_key"),
                "available": True
            }
        
        # Qwen Code headless設定
        if config.get("qwen_code_headless", {}).get("enabled", False):
            providers[LLMProvider.QWEN_CODE_HEADLESS] = {
                "endpoint": config["qwen_code_headless"].get("endpoint"),
                "api_key": config["qwen_code_headless"].get("api_key"),
                "available": True
            }
        
        return providers
    
    def _load_routing_rules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """ルーティングルールをロード"""
        return {
            "critical_keywords": ["security", "authentication", "payment", "database", "production"],
            "local_keywords": ["format", "template", "list", "summary", "translate"],
            "token_threshold": config.get("routing", {}).get("token_threshold", 1000),
            "priority_threshold": config.get("routing", {}).get("priority_threshold", 0.7)
        }
    
    async def route_task(self, 
                        task: str,
                        priority: float,
                        context: Optional[Dict[str, Any]] = None) -> TaskRoute:
        """タスクを最適なプロバイダーへルーティング"""
        
        # タスク分析
        analysis = await self._analyze_task(task, context)
        
        # ルーティング決定
        if analysis["is_critical"] or priority >= self.routing_rules["priority_threshold"]:
            # 重要タスクはメインClaudeへ
            provider = LLMProvider.MAIN_CLAUDE
            reason = "Critical task requiring main Claude's capabilities"
        elif analysis["estimated_tokens"] < self.routing_rules["token_threshold"] and \
             LLMProvider.LOCAL_LLM in self.providers:
            # 軽量タスクはローカルLLMへ
            provider = LLMProvider.LOCAL_LLM
            reason = "Lightweight task suitable for local LLM"
        elif LLMProvider.CLAUDE_CODE_HEADLESS in self.providers:
            # 中規模タスクはClaude Code headlessへ
            provider = LLMProvider.CLAUDE_CODE_HEADLESS
            reason = "Medium complexity task routed to Claude Code headless"
        elif LLMProvider.QWEN_CODE_HEADLESS in self.providers:
            # 代替としてQwen Codeへ
            provider = LLMProvider.QWEN_CODE_HEADLESS
            reason = "Task routed to Qwen Code as alternative"
        else:
            # フォールバック：メインClaudeへ
            provider = LLMProvider.MAIN_CLAUDE
            reason = "No alternative providers available"
        
        return TaskRoute(
            task_id=self._generate_task_id(),
            provider=provider,
            reason=reason,
            estimated_tokens=analysis["estimated_tokens"],
            priority=priority,
            metadata=analysis
        )
    
    async def execute_on_provider(self,
                                 route: TaskRoute,
                                 prompt: str,
                                 system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """指定されたプロバイダーでタスクを実行"""
        
        provider = route.provider
        
        if provider == LLMProvider.MAIN_CLAUDE:
            # メインClaudeでの実行（MCP経由で返す）
            return {
                "provider": "main_claude",
                "execute_locally": False,
                "prompt": prompt,
                "system_prompt": system_prompt
            }
        
        elif provider == LLMProvider.LOCAL_LLM:
            return await self._execute_on_local_llm(prompt, system_prompt)
        
        elif provider == LLMProvider.CLAUDE_CODE_HEADLESS:
            return await self._execute_on_claude_code(prompt, system_prompt)
        
        elif provider == LLMProvider.QWEN_CODE_HEADLESS:
            return await self._execute_on_qwen_code(prompt, system_prompt)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _execute_on_local_llm(self, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        """ローカルLLMで実行"""
        provider_config = self.providers[LLMProvider.LOCAL_LLM]
        
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "model": provider_config["model"],
                    "messages": [
                        {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": provider_config["max_tokens"],
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{provider_config['endpoint']}/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "provider": "local_llm",
                            "response": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {}),
                            "success": True
                        }
                    else:
                        logger.error(f"Local LLM error: {response.status}")
                        return await self._fallback_execution(prompt, system_prompt)
                        
            except Exception as e:
                logger.error(f"Local LLM execution failed: {e}")
                return await self._fallback_execution(prompt, system_prompt)
    
    async def _execute_on_claude_code(self, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        """Claude Code headlessで実行"""
        provider_config = self.providers[LLMProvider.CLAUDE_CODE_HEADLESS]
        
        # Claude Code headless API実装
        # TODO: 実際のClaude Code headless APIエンドポイントに合わせて実装
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    "Authorization": f"Bearer {provider_config['api_key']}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "prompt": prompt,
                    "system": system_prompt,
                    "max_tokens": 2000
                }
                
                async with session.post(
                    provider_config["endpoint"],
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "provider": "claude_code_headless",
                            "response": result.get("completion", ""),
                            "success": True
                        }
                    else:
                        return await self._fallback_execution(prompt, system_prompt)
                        
            except Exception as e:
                logger.error(f"Claude Code execution failed: {e}")
                return await self._fallback_execution(prompt, system_prompt)
    
    async def _execute_on_qwen_code(self, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        """Qwen Code headlessで実行"""
        provider_config = self.providers[LLMProvider.QWEN_CODE_HEADLESS]
        
        # Qwen Code headless API実装
        # TODO: 実際のQwen Code APIエンドポイントに合わせて実装
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    "Authorization": f"Bearer {provider_config['api_key']}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "qwen-code",
                    "messages": [
                        {"role": "system", "content": system_prompt or ""},
                        {"role": "user", "content": prompt}
                    ]
                }
                
                async with session.post(
                    provider_config["endpoint"],
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "provider": "qwen_code_headless",
                            "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "success": True
                        }
                    else:
                        return await self._fallback_execution(prompt, system_prompt)
                        
            except Exception as e:
                logger.error(f"Qwen Code execution failed: {e}")
                return await self._fallback_execution(prompt, system_prompt)
    
    async def _fallback_execution(self, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        """フォールバック実行（メインClaudeへ戻す）"""
        logger.info("Falling back to main Claude")
        return {
            "provider": "main_claude",
            "execute_locally": False,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "fallback": True
        }
    
    async def _analyze_task(self, task: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """タスクを分析して特性を判定"""
        task_lower = task.lower()
        
        # 重要タスクの判定
        is_critical = any(keyword in task_lower for keyword in self.routing_rules["critical_keywords"])
        
        # ローカル処理可能タスクの判定
        is_local_suitable = any(keyword in task_lower for keyword in self.routing_rules["local_keywords"])
        
        # トークン数の推定（簡易版）
        estimated_tokens = len(task.split()) * 1.3  # 単語数 × 1.3（概算）
        
        return {
            "is_critical": is_critical,
            "is_local_suitable": is_local_suitable,
            "estimated_tokens": int(estimated_tokens),
            "has_context": context is not None,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _generate_task_id(self) -> str:
        """ユニークなタスクIDを生成"""
        import uuid
        return f"task_{uuid.uuid4().hex[:8]}"
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """全プロバイダーの状態を取得"""
        status = {}
        
        for provider, config in self.providers.items():
            # 各プロバイダーのヘルスチェック
            is_healthy = await self._health_check(provider)
            status[provider.value] = {
                "available": config.get("available", False),
                "healthy": is_healthy,
                "endpoint": config.get("endpoint", "N/A")
            }
        
        return status
    
    async def _health_check(self, provider: LLMProvider) -> bool:
        """プロバイダーのヘルスチェック"""
        if provider not in self.providers:
            return False
        
        if provider == LLMProvider.LOCAL_LLM:
            # ローカルLLMのヘルスチェック
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.providers[provider]['endpoint']}/models",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        return response.status == 200
            except:
                return False
        
        # 他のプロバイダーは設定があれば利用可能とみなす
        return True