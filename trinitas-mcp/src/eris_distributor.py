"""
Eris Task Distributor for Trinitas v5.0
分散処理とLLMルーティング統合システム

LocalLLMがOFFの場合、自動的にClaude/Qwen Code headlessへフォールバック
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """タスク重要度レベル"""
    CRITICAL = 0.9  # 最重要 - Main処理必須
    HIGH = 0.7      # 高重要 - Main処理推奨
    MEDIUM = 0.5    # 中重要 - 判断による
    LOW = 0.3       # 低重要 - LLM処理可能
    TRIVIAL = 0.1   # 些細 - LLM処理推奨

@dataclass
class TaskDistribution:
    """タスク振り分け決定"""
    task_id: str
    send_to_llm: bool
    reason: str
    priority: float
    estimated_tokens: int
    assigned_processor: str  # "main", "local_llm", "claude_code", "qwen_code"
    metadata: Dict[str, Any]

class ErisTaskDistributor:
    """
    Eris - 分散処理とタスク振り分け担当
    
    動作モード:
    1. Local LLM有効時: タスクの重要度を判定してLLMへ振り分け
    2. Local LLM無効時: Claude/Qwen Code headlessへ自動フォールバック
    3. 全て無効時: メインClaudeで処理
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_enabled = config.get("local_llm", {}).get("enabled", False)
        self.priority_threshold = config.get("local_llm", {}).get(
            "distribution", {}
        ).get("priority_threshold", 0.3)
        
        # LLMルーターを初期化
        from .llm_router import ErisLLMRouter
        self.llm_router = ErisLLMRouter(config)
        
        # 並列タスク管理 - Eris分散処理拡張
        self.max_parallel_tasks = config.get("local_llm", {}).get(
            "distribution", {}
        ).get("max_parallel_tasks", 8)  # 最大8並列
        self.active_llm_tasks = []
        
        # 分散処理リソースプール
        self.resource_pool = {
            "memory_operations": 0,
            "analysis_tasks": 0,
            "optimization_tasks": 0
        }
        self.max_resource_per_type = 3
        
        # タスクタイプ定義
        self.llm_suitable_tasks = config.get("local_llm", {}).get(
            "distribution", {}
        ).get("task_types", [
            "documentation_generation",
            "code_formatting",
            "simple_analysis",
            "data_transformation"
        ])
        
        logger.info(
            f"Eris分散システム初期化: "
            f"LLM={'有効' if self.llm_enabled else '無効(ヘッドレスモード自動有効)'}, "
            f"閾値={self.priority_threshold}, "
            f"並列度={self.max_parallel_tasks}"
        )
    
    async def evaluate_task(self, task: str, context: Optional[Dict] = None) -> TaskDistribution:
        """
        タスクを評価して振り分け決定
        
        Args:
            task: タスク内容
            context: タスクコンテキスト
            
        Returns:
            TaskDistribution: 振り分け決定
        """
        task_id = self._generate_task_id()
        
        # タスク分析
        task_type = self._classify_task(task)
        importance = await self._calculate_importance(task, task_type, context)
        tokens = self._estimate_tokens(task)
        
        # LLMルーターを使用して最適なプロバイダーを決定
        route = await self.llm_router.route_task(task, importance, context)
        
        # ルーティング結果に基づいて振り分け決定を生成
        if route.provider.value == "main_claude":
            return TaskDistribution(
                task_id=task_id,
                send_to_llm=False,
                reason=route.reason,
                priority=importance,
                estimated_tokens=tokens,
                assigned_processor="main",
                metadata={
                    "task_type": task_type,
                    "provider": route.provider.value,
                    "route_metadata": route.metadata
                }
            )
        elif route.provider.value == "local_llm":
            return TaskDistribution(
                task_id=task_id,
                send_to_llm=True,
                reason=route.reason,
                priority=importance,
                estimated_tokens=tokens,
                assigned_processor="local_llm",
                metadata={
                    "task_type": task_type,
                    "provider": route.provider.value,
                    "route_metadata": route.metadata
                }
            )
        else:
            # ヘッドレスモード (claude_code or qwen_code)
            return TaskDistribution(
                task_id=task_id,
                send_to_llm=True,  # ヘッドレスモードを使用
                reason=f"Using {route.provider.value} headless mode",
                priority=importance,
                estimated_tokens=tokens,
                assigned_processor=route.provider.value,
                metadata={
                    "task_type": task_type,
                    "provider": route.provider.value,
                    "headless_mode": True,
                    "route_metadata": route.metadata
                }
            )
    
    async def analyze_task(self, task: str) -> Dict[str, Any]:
        """
        タスクを分析してメタデータを生成
        """
        distribution = await self.evaluate_task(task)
        
        # 現在のリソース状況を追加
        resource_status = await self._get_resource_status()
        
        return {
            "task_id": distribution.task_id,
            "distribution": distribution,
            "resource_status": resource_status,
            "parallel_capacity": self.max_parallel_tasks - len(self.active_llm_tasks),
            "llm_router_status": await self.llm_router.get_provider_status()
        }
    
    def _classify_task(self, task: str) -> str:
        """タスクタイプを分類"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["doc", "document", "説明", "マニュアル"]):
            return "documentation"
        elif any(word in task_lower for word in ["format", "整形", "フォーマット"]):
            return "formatting"
        elif any(word in task_lower for word in ["analyze", "分析", "解析"]):
            return "analysis"
        elif any(word in task_lower for word in ["transform", "変換", "変更"]):
            return "transformation"
        elif any(word in task_lower for word in ["optimize", "最適化", "改善"]):
            return "optimization"
        else:
            return "general"
    
    async def _calculate_importance(self, 
                                   task: str, 
                                   task_type: str,
                                   context: Optional[Dict] = None) -> float:
        """タスクの重要度を計算"""
        base_importance = 0.5
        
        # タスクタイプによる調整
        type_weights = {
            "documentation": -0.2,  # ドキュメントは低重要度
            "formatting": -0.3,     # フォーマットは最低重要度
            "analysis": 0.1,        # 分析は中重要度
            "transformation": 0.0,  # 変換は標準
            "optimization": 0.2,    # 最適化は高重要度
            "general": 0.0
        }
        base_importance += type_weights.get(task_type, 0.0)
        
        # コンテキストによる調整
        if context:
            if context.get("is_production", False):
                base_importance += 0.3
            if context.get("is_critical", False):
                base_importance = max(base_importance, 0.9)
            if context.get("user_priority"):
                base_importance = context["user_priority"]
        
        # 範囲を0.0-1.0に制限
        return max(0.0, min(1.0, base_importance))
    
    def _estimate_tokens(self, task: str) -> int:
        """トークン数を推定"""
        # 簡易推定: 1単語 ≈ 1.3トークン
        words = len(task.split())
        return int(words * 1.3)
    
    def _generate_task_id(self) -> str:
        """ユニークなタスクIDを生成"""
        from uuid import uuid4
        return f"eris_task_{uuid4().hex[:8]}"
    
    async def _get_resource_status(self) -> Dict[str, Any]:
        """現在のリソース状況を取得"""
        return {
            "active_tasks": len(self.active_llm_tasks),
            "max_parallel": self.max_parallel_tasks,
            "resource_usage": self.resource_pool,
            "capacity": {
                "available": self.max_parallel_tasks - len(self.active_llm_tasks),
                "percentage": (1 - len(self.active_llm_tasks) / self.max_parallel_tasks) * 100
            }
        }
    
    async def execute_distributed_task(self, 
                                      task: str,
                                      distribution: TaskDistribution) -> Dict[str, Any]:
        """
        分散タスクを実行
        """
        if distribution.assigned_processor in ["claude_code", "qwen_code", "local_llm"]:
            # LLMルーター経由で実行
            route_data = {
                "task_id": distribution.task_id,
                "provider": distribution.assigned_processor,
                "reason": distribution.reason,
                "estimated_tokens": distribution.estimated_tokens,
                "priority": distribution.priority,
                "metadata": distribution.metadata
            }
            
            # TaskRouteオブジェクトを作成
            from .llm_router import TaskRoute, LLMProvider
            provider_map = {
                "local_llm": LLMProvider.LOCAL_LLM,
                "claude_code": LLMProvider.CLAUDE_CODE_HEADLESS,
                "qwen_code": LLMProvider.QWEN_CODE_HEADLESS,
                "main": LLMProvider.MAIN_CLAUDE
            }
            
            route = TaskRoute(
                task_id=distribution.task_id,
                provider=provider_map[distribution.assigned_processor],
                reason=distribution.reason,
                estimated_tokens=distribution.estimated_tokens,
                priority=distribution.priority,
                metadata=distribution.metadata
            )
            
            # 実行
            result = await self.llm_router.execute_on_provider(
                route=route,
                prompt=task,
                system_prompt="You are a helpful assistant specialized in the requested task."
            )
            
            return result
        else:
            # メインClaudeで実行
            return {
                "provider": "main_claude",
                "execute_locally": False,
                "task": task,
                "distribution": distribution.__dict__
            }