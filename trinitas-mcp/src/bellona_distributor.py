"""
Bellona Task Distributor for Trinitas v4.0
戦術的タスク振り分けシステム
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
    assigned_processor: str  # "main" or "llm"
    metadata: Dict[str, Any]

class BellonaTaskDistributor:
    """
    Bellona - 戦術的タスク振り分け担当
    Local LLM有効時: タスクの重要度を判定してLLMへ振り分け
    Local LLM無効時: Seshatと協調してメモリシステム管理
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_enabled = config.get("local_llm", {}).get("enabled", False)
        self.priority_threshold = config.get("local_llm", {}).get(
            "distribution", {}
        ).get("priority_threshold", 0.3)
        
        # 並列タスク管理 - Bellona戦術的拡張
        self.max_parallel_tasks = config.get("local_llm", {}).get(
            "distribution", {}
        ).get("max_parallel_tasks", 8)  # 3→8に増強
        self.active_llm_tasks = []
        
        # 戦術的リソースプール
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
        
        logger.info(f"Bellona戦術システム初期化: LLM={'有効' if self.llm_enabled else '無効'}, 閾値={self.priority_threshold}, 並列度={self.max_parallel_tasks}")
    
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
        
        # LLM無効時は常にMain処理
        if not self.llm_enabled:
            return TaskDistribution(
                task_id=task_id,
                send_to_llm=False,
                reason="Local LLMが無効のため、メイン処理で実行",
                priority=importance,
                estimated_tokens=tokens,
                assigned_processor="main",
                metadata={
                    "task_type": task_type,
                    "llm_mode": "disabled"
                }
            )
        
        # 振り分け判定（LLM有効時）
        send_to_llm = False
        reason = ""
        processor = "main"
        
        # 判定ロジック
        if importance < self.priority_threshold:
            if task_type in self.llm_suitable_tasks:
                if len(self.active_llm_tasks) < self.max_parallel_tasks:
                    send_to_llm = True
                    processor = "llm"
                    reason = f"低重要度タスク（{importance:.2f}）でLLM処理に適している"
                else:
                    reason = f"LLMタスクスロットが満杯（{len(self.active_llm_tasks)}/{self.max_parallel_tasks}）"
            else:
                reason = f"タスクタイプ'{task_type}'はLLM処理に不適"
        else:
            reason = f"重要度（{importance:.2f}）が閾値（{self.priority_threshold}）を超えている"
        
        distribution = TaskDistribution(
            task_id=task_id,
            send_to_llm=send_to_llm,
            reason=reason,
            priority=importance,
            estimated_tokens=tokens,
            assigned_processor=processor,
            metadata={
                "task_type": task_type,
                "active_llm_count": len(self.active_llm_tasks),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # LLMタスクリストを更新
        if send_to_llm:
            self.active_llm_tasks.append(task_id)
        
        logger.info(f"Bellona判定: {processor}処理 - {reason}")
        
        return distribution
    
    async def optimize_memory_with_seshat(self, memory_manager, seshat_monitor):
        """
        LLM無効時: Seshatと協調してメモリ最適化
        
        Args:
            memory_manager: メモリマネージャーインスタンス
            seshat_monitor: Seshatモニターインスタンス
        """
        logger.info("Bellona: LLM無効モード - Seshatとメモリ最適化開始")
        
        # Seshatから使用レポートを取得
        usage_report = await seshat_monitor.get_usage_report()
        
        # 最適化計画を作成
        optimization_plan = self._create_optimization_plan(usage_report)
        
        # メモリマネージャーに適用
        await memory_manager.apply_optimizations(optimization_plan)
        
        logger.info(f"メモリ最適化完了: {optimization_plan['summary']}")
    
    def _classify_task(self, task: str) -> str:
        """タスクを分類"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["ドキュメント", "文書", "doc", "readme"]):
            return "documentation_generation"
        elif any(word in task_lower for word in ["フォーマット", "整形", "format", "lint"]):
            return "code_formatting"
        elif any(word in task_lower for word in ["分析", "analyze", "review"]):
            return "simple_analysis"
        elif any(word in task_lower for word in ["変換", "transform", "convert"]):
            return "data_transformation"
        elif any(word in task_lower for word in ["最適化", "optimize", "performance"]):
            return "optimization"
        elif any(word in task_lower for word in ["セキュリティ", "security", "vulnerability"]):
            return "security"
        else:
            return "general"
    
    async def _calculate_importance(self, task: str, task_type: str, context: Optional[Dict]) -> float:
        """
        タスクの重要度を計算
        
        Returns:
            0.0 (最低) から 1.0 (最高) の重要度
        """
        base_importance = {
            "security": 0.9,
            "optimization": 0.7,
            "simple_analysis": 0.4,
            "documentation_generation": 0.2,
            "code_formatting": 0.2,
            "data_transformation": 0.3,
            "general": 0.5
        }.get(task_type, 0.5)
        
        # コンテキストによる調整
        if context:
            if context.get("urgent", False):
                base_importance = min(1.0, base_importance + 0.3)
            if context.get("user_requested", False):
                base_importance = min(1.0, base_importance + 0.2)
            if context.get("automated", False):
                base_importance = max(0.0, base_importance - 0.2)
        
        return base_importance
    
    def _estimate_tokens(self, task: str) -> int:
        """トークン数を推定"""
        # 簡易推定: 1文字 ≈ 0.5トークン（日本語）、1単語 ≈ 1.3トークン（英語）
        char_count = len(task)
        word_count = len(task.split())
        
        # 混在を考慮
        estimated = int((char_count * 0.5 + word_count * 1.3) / 2)
        return estimated
    
    def _generate_task_id(self) -> str:
        """ユニークなタスクIDを生成"""
        from uuid import uuid4
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
    
    def _create_optimization_plan(self, usage_report: Dict) -> Dict:
        """メモリ最適化計画を作成"""
        plan = {
            "summary": "",
            "actions": [],
            "priority": "medium"
        }
        
        # 使用パターンから最適化を決定
        if usage_report.get("total_accesses", 0) > 1000:
            plan["actions"].append({
                "type": "cache_expansion",
                "reason": "高頻度アクセス検出"
            })
        
        if usage_report.get("bottlenecks", []):
            plan["actions"].append({
                "type": "index_optimization",
                "targets": usage_report["bottlenecks"]
            })
            plan["priority"] = "high"
        
        # 未使用メモリのクリーンアップ
        if usage_report.get("unused_ratio", 0) > 0.3:
            plan["actions"].append({
                "type": "cleanup",
                "threshold_days": 30
            })
        
        plan["summary"] = f"{len(plan['actions'])}個の最適化アクション、優先度: {plan['priority']}"
        
        return plan
    
    async def release_task(self, task_id: str):
        """LLMタスクスロットを解放"""
        if task_id in self.active_llm_tasks:
            self.active_llm_tasks.remove(task_id)
            logger.info(f"LLMタスクスロット解放: {task_id}")
    
    def get_status(self) -> Dict:
        """Bellonaの現在状態を取得 - 戦術的強化版"""
        return {
            "mode": "tactical_parallel" if self.llm_enabled else "memory_optimization",
            "llm_enabled": self.llm_enabled,
            "priority_threshold": self.priority_threshold,
            "active_llm_tasks": len(self.active_llm_tasks),
            "max_parallel_tasks": self.max_parallel_tasks,
            "resource_pool": self.resource_pool,
            "resource_utilization": {
                "llm_slots": f"{len(self.active_llm_tasks)}/{self.max_parallel_tasks}",
                "memory_ops": f"{self.resource_pool['memory_operations']}/{self.max_resource_per_type}",
                "analysis": f"{self.resource_pool['analysis_tasks']}/{self.max_resource_per_type}"
            },
            "suitable_task_types": self.llm_suitable_tasks,
            "tactical_mode": "bellona_v4_parallel"
        }
    
    def acquire_resource(self, resource_type: str) -> bool:
        """戦術的リソース確保"""
        if resource_type in self.resource_pool:
            if self.resource_pool[resource_type] < self.max_resource_per_type:
                self.resource_pool[resource_type] += 1
                return True
        return False
    
    def release_resource(self, resource_type: str):
        """戦術的リソース解放"""
        if resource_type in self.resource_pool and self.resource_pool[resource_type] > 0:
            self.resource_pool[resource_type] -= 1