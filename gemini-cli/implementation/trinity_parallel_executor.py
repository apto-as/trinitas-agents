#!/usr/bin/env python3
"""
Trinity Parallel Executor - 三位一体並列実行エンジン
真の並列思考と多機能Hooksシステムの実装
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


# =====================================
# Execution Patterns
# =====================================

class ExecutionPattern(Enum):
    """並列実行パターン"""
    PARALLEL_INDEPENDENT = "parallel_independent"  # 完全独立並列
    PARALLEL_INTERACTIVE = "parallel_interactive"  # 相互参照並列
    PARALLEL_COMPETITIVE = "parallel_competitive"  # 競争的並列
    SEQUENTIAL_PIPELINE = "sequential_pipeline"   # パイプライン
    RACE_TO_FINISH = "race_to_finish"            # 最速優先
    CONSENSUS_REQUIRED = "consensus_required"     # 合意必須


# =====================================
# Shared Context Manager
# =====================================

class SharedContextManager:
    """ペルソナ間共有コンテキスト管理"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.revision_history: List[Dict] = []
    
    async def get(self, key: str, persona: str = None) -> Any:
        """コンテキスト取得"""
        self._log_access(key, persona, "read")
        return self.context.get(key)
    
    async def set(self, key: str, value: Any, persona: str = None) -> None:
        """コンテキスト設定"""
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            old_value = self.context.get(key)
            self.context[key] = value
            self._log_access(key, persona, "write", old_value, value)
    
    async def update_atomic(self, key: str, updater: Callable, persona: str = None) -> Any:
        """アトミックな更新"""
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            old_value = self.context.get(key)
            new_value = await updater(old_value)
            self.context[key] = new_value
            self._log_access(key, persona, "atomic_update", old_value, new_value)
            return new_value
    
    def _log_access(self, key: str, persona: str, operation: str, 
                    old_value: Any = None, new_value: Any = None):
        """アクセスログ記録"""
        self.revision_history.append({
            "timestamp": time.time(),
            "key": key,
            "persona": persona,
            "operation": operation,
            "old_value": old_value,
            "new_value": new_value
        })
    
    def get_conflicts(self) -> List[Dict]:
        """競合状態の検出"""
        conflicts = []
        # 短時間に同じキーへの複数書き込みを検出
        for i in range(len(self.revision_history) - 1):
            curr = self.revision_history[i]
            next = self.revision_history[i + 1]
            
            if (curr["key"] == next["key"] and 
                curr["operation"] == "write" and 
                next["operation"] == "write" and
                next["timestamp"] - curr["timestamp"] < 0.1):  # 100ms以内
                
                conflicts.append({
                    "key": curr["key"],
                    "personas": [curr["persona"], next["persona"]],
                    "conflict_type": "rapid_succession_writes"
                })
        
        return conflicts


# =====================================
# Extended Hooks System
# =====================================

class HookCategory(Enum):
    """Hook categories with expanded roles"""
    QUALITY = "quality"              # 品質強制
    COORDINATION = "coordination"    # ペルソナ調整
    SEQUENCING = "sequencing"        # 実行順序制御
    CONTEXT = "context"              # コンテキスト管理
    INTEGRATION = "integration"      # 結果統合
    LEARNING = "learning"            # 学習・適応
    MONITORING = "monitoring"        # 監視・計測
    SECURITY = "security"            # セキュリティ
    VALIDATION = "validation"        # 検証
    TRANSFORMATION = "transformation" # 変換・加工


@dataclass
class HookResult:
    """Hook実行結果"""
    success: bool
    modified_data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    reason: Optional[str] = None


class ExtendedHooksSystem:
    """拡張Hooksシステム - 品質強制を超えた多機能実装"""
    
    def __init__(self):
        self.hooks: Dict[HookCategory, List[Callable]] = {
            category: [] for category in HookCategory
        }
        self.execution_history: List[Dict] = []
        self.performance_metrics: Dict[str, List[float]] = {}
        
    def register(self, category: HookCategory, hook: Callable, priority: int = 0):
        """Hookを優先度付きで登録"""
        self.hooks[category].append((priority, hook))
        # 優先度でソート（高い順）
        self.hooks[category].sort(key=lambda x: x[0], reverse=True)
    
    async def execute_category(self, category: HookCategory, data: Any) -> HookResult:
        """カテゴリ内の全Hookを実行"""
        result = HookResult(success=True, modified_data=data)
        
        for priority, hook in self.hooks[category]:
            try:
                hook_result = await hook(result.modified_data)
                
                if isinstance(hook_result, dict):
                    if hook_result.get("blocked"):
                        result.blocked = True
                        result.reason = hook_result.get("reason", "Blocked by hook")
                        break
                    result.modified_data = hook_result
                    
            except Exception as e:
                result.success = False
                result.metadata["error"] = str(e)
                break
        
        return result
    
    # === Coordination Hooks ===
    
    async def consensus_building_hook(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """ペルソナ間の合意形成"""
        
        # 各ペルソナの判断を抽出
        springfield = results.get("springfield", {})
        krukai = results.get("krukai", {})
        vector = results.get("vector", {})
        
        # スコアベースの合意度計算
        scores = {
            "springfield": springfield.get("confidence", 0),
            "krukai": krukai.get("confidence", 0),
            "vector": vector.get("confidence", 0)
        }
        
        avg_confidence = sum(scores.values()) / len(scores)
        
        # 意見の相違を検出
        divergence = max(scores.values()) - min(scores.values())
        
        if divergence > 0.3:  # 30%以上の相違
            # 調整プロセス起動
            results["requires_mediation"] = True
            results["divergence_level"] = divergence
            results["mediation_strategy"] = self._determine_mediation_strategy(results)
        
        results["consensus_score"] = avg_confidence
        results["consensus_achieved"] = divergence < 0.1  # 10%未満なら合意
        
        return results
    
    def _determine_mediation_strategy(self, results: Dict) -> str:
        """調停戦略の決定"""
        # Springfieldが最も高い信頼度なら戦略的調整
        # Krukaiが最も高いなら技術的調整
        # Vectorが最も高いならリスクベース調整
        scores = {
            "springfield": results.get("springfield", {}).get("confidence", 0),
            "krukai": results.get("krukai", {}).get("confidence", 0),
            "vector": results.get("vector", {}).get("confidence", 0)
        }
        
        leader = max(scores, key=scores.get)
        strategies = {
            "springfield": "strategic_alignment",
            "krukai": "technical_optimization",
            "vector": "risk_mitigation"
        }
        
        return strategies.get(leader, "balanced_approach")
    
    # === Sequencing Hooks ===
    
    async def dependency_check_hook(self, operation: str, context: Dict) -> Dict:
        """依存関係のチェックと順序制御"""
        
        # 操作の依存関係定義
        dependencies = {
            "optimize_code": {
                "requires": ["analyze_code", "test_code"],
                "message": "基礎分析とテストが必要"
            },
            "deploy": {
                "requires": ["test_all", "security_audit", "performance_test"],
                "message": "全テストと監査が必要"
            },
            "scale_system": {
                "requires": ["optimize_code", "load_test", "capacity_planning"],
                "message": "最適化と負荷試験が必要"
            }
        }
        
        if operation in dependencies:
            dep_info = dependencies[operation]
            completed = context.get("completed_operations", [])
            
            missing = [req for req in dep_info["requires"] if req not in completed]
            
            if missing:
                return {
                    **context,
                    "blocked": True,
                    "reason": dep_info["message"],
                    "missing_dependencies": missing,
                    "suggested_order": dep_info["requires"]
                }
        
        return context
    
    # === Context Sharing Hooks ===
    
    async def cross_persona_insight_hook(self, persona: str, data: Dict, 
                                        shared_ctx: SharedContextManager) -> Dict:
        """ペルソナ間の洞察共有"""
        
        # 現在のペルソナの重要な洞察を抽出
        if "key_insights" in data:
            await shared_ctx.set(
                f"{persona}_insights",
                data["key_insights"],
                persona
            )
        
        # 他ペルソナの洞察を取得
        other_personas = ["springfield", "krukai", "vector"]
        other_personas.remove(persona)
        
        cross_insights = {}
        for other in other_personas:
            insights = await shared_ctx.get(f"{other}_insights")
            if insights:
                cross_insights[other] = insights
        
        if cross_insights:
            data["cross_persona_insights"] = cross_insights
            data["context_enriched"] = True
            
            # 洞察の統合提案
            data["integration_suggestions"] = self._suggest_insight_integration(
                data.get("key_insights", {}),
                cross_insights
            )
        
        return data
    
    def _suggest_insight_integration(self, own: Dict, others: Dict) -> List[str]:
        """洞察統合の提案"""
        suggestions = []
        
        # 簡単な例：キーワードの重複を検出
        own_keywords = set(str(own).lower().split())
        
        for persona, insights in others.items():
            other_keywords = set(str(insights).lower().split())
            overlap = own_keywords & other_keywords
            
            if overlap:
                suggestions.append(
                    f"Consider {persona}'s perspective on: {', '.join(overlap)}"
                )
        
        return suggestions
    
    # === Learning Hooks ===
    
    async def pattern_learning_hook(self, execution: Dict, outcome: Dict) -> Dict:
        """実行パターンの学習と最適化"""
        
        # 実行履歴に追加
        self.execution_history.append({
            "timestamp": time.time(),
            "execution": execution,
            "outcome": outcome,
            "success": outcome.get("success", False)
        })
        
        # パターン分析（最近10回の実行）
        recent = self.execution_history[-10:]
        
        if len(recent) >= 3:
            # 成功率計算
            success_rate = sum(1 for r in recent if r["success"]) / len(recent)
            
            # パフォーマンストレンド
            if "execution_time" in outcome:
                execution_times = [
                    r["outcome"].get("execution_time", 0) 
                    for r in recent 
                    if "execution_time" in r["outcome"]
                ]
                
                if execution_times:
                    avg_time = sum(execution_times) / len(execution_times)
                    trend = "improving" if execution_times[-1] < avg_time else "degrading"
                    
                    outcome["performance_trend"] = trend
                    outcome["avg_execution_time"] = avg_time
            
            outcome["success_rate"] = success_rate
            
            # 最適化提案
            if success_rate < 0.8:
                outcome["optimization_needed"] = True
                outcome["suggestions"] = [
                    "Consider adjusting timeout values",
                    "Review error patterns in failed executions",
                    "Check resource constraints"
                ]
        
        return outcome
    
    # === Monitoring Hooks ===
    
    async def performance_monitoring_hook(self, operation: str, data: Dict) -> Dict:
        """パフォーマンス監視と異常検知"""
        
        start_time = time.time()
        operation_hash = hashlib.md5(operation.encode()).hexdigest()[:8]
        
        # メトリクス収集
        metrics = {
            "operation": operation,
            "operation_id": operation_hash,
            "start_time": start_time,
            "data_size": len(json.dumps(data)),
            "timestamp": datetime.now().isoformat()
        }
        
        # 過去のパフォーマンスと比較
        if operation in self.performance_metrics:
            history = self.performance_metrics[operation]
            if len(history) > 5:
                avg_time = sum(history[-5:]) / 5
                
                # 異常検知（2倍以上遅い場合）
                if start_time > avg_time * 2:
                    data["performance_warning"] = {
                        "message": "Slower than usual",
                        "current": start_time,
                        "average": avg_time,
                        "degradation": (start_time / avg_time - 1) * 100
                    }
        
        # メトリクス記録
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        self.performance_metrics[operation].append(start_time)
        
        data["monitoring_metrics"] = metrics
        return data


# =====================================
# Trinity Parallel Executor
# =====================================

class TrinityParallelExecutor:
    """三位一体並列実行エンジン"""
    
    def __init__(self):
        self.active_personas: Dict[str, Any] = {}
        self.shared_context = SharedContextManager()
        self.hooks = ExtendedHooksSystem()
        self.execution_pool = asyncio.Semaphore(3)  # 最大3並列
        
        # デフォルトHooksを登録
        self._register_default_hooks()
    
    def _register_default_hooks(self):
        """デフォルトHooksの登録"""
        self.hooks.register(
            HookCategory.COORDINATION,
            self.hooks.consensus_building_hook,
            priority=10
        )
        self.hooks.register(
            HookCategory.SEQUENCING,
            self.hooks.dependency_check_hook,
            priority=20
        )
        self.hooks.register(
            HookCategory.LEARNING,
            self.hooks.pattern_learning_hook,
            priority=5
        )
        self.hooks.register(
            HookCategory.MONITORING,
            self.hooks.performance_monitoring_hook,
            priority=15
        )
    
    async def activate_trinity(self) -> Dict[str, Any]:
        """三位一体モードを起動 - 全ペルソナを同時活性化"""
        
        personas = ["springfield", "krukai", "vector"]
        
        # 並列でペルソナを初期化
        activation_tasks = []
        for persona in personas:
            activation_tasks.append(self._activate_persona(persona))
        
        # 全ペルソナを同時に起動
        results = await asyncio.gather(*activation_tasks)
        
        # 結果を統合
        for persona, result in zip(personas, results):
            self.active_personas[persona] = result
        
        return {
            "mode": "trinity_parallel",
            "active_personas": personas,
            "status": "all_active",
            "capabilities": {
                "parallel_execution": True,
                "shared_context": True,
                "coordination": True,
                "consensus_building": True
            }
        }
    
    async def _activate_persona(self, persona: str) -> Dict:
        """個別ペルソナの活性化"""
        # 簡略化された活性化ロジック
        return {
            "persona": persona,
            "active": True,
            "initialized_at": time.time()
        }
    
    async def execute_parallel(self, 
                              pattern: ExecutionPattern,
                              task: Dict[str, Any]) -> Dict[str, Any]:
        """指定パターンで並列実行"""
        
        # 実行前Hooks
        pre_result = await self.hooks.execute_category(
            HookCategory.SEQUENCING,
            task
        )
        
        if pre_result.blocked:
            return {"blocked": True, "reason": pre_result.reason}
        
        # パターンに応じた実行
        if pattern == ExecutionPattern.PARALLEL_INDEPENDENT:
            result = await self._execute_independent(task)
        elif pattern == ExecutionPattern.PARALLEL_INTERACTIVE:
            result = await self._execute_interactive(task)
        elif pattern == ExecutionPattern.PARALLEL_COMPETITIVE:
            result = await self._execute_competitive(task)
        elif pattern == ExecutionPattern.RACE_TO_FINISH:
            result = await self._execute_race(task)
        else:
            result = await self._execute_consensus(task)
        
        # 実行後Hooks
        post_result = await self.hooks.execute_category(
            HookCategory.COORDINATION,
            result
        )
        
        # 学習Hooks
        learning_result = await self.hooks.execute_category(
            HookCategory.LEARNING,
            {"execution": task, "outcome": post_result.modified_data}
        )
        
        return learning_result.modified_data
    
    async def _execute_independent(self, task: Dict) -> Dict:
        """完全独立並列実行"""
        results = await asyncio.gather(
            self._persona_execute("springfield", task),
            self._persona_execute("krukai", task),
            self._persona_execute("vector", task)
        )
        
        return {
            "pattern": "independent",
            "springfield": results[0],
            "krukai": results[1],
            "vector": results[2]
        }
    
    async def _execute_interactive(self, task: Dict) -> Dict:
        """相互参照並列実行"""
        
        # 共有コンテキストを使用
        async def execute_with_context(persona: str):
            # 他ペルソナの途中結果を参照可能
            result = await self._persona_execute(persona, task)
            
            # コンテキストに結果を共有
            await self.shared_context.set(
                f"{persona}_result",
                result,
                persona
            )
            
            # 他ペルソナの結果を取得
            other_results = {}
            for other in ["springfield", "krukai", "vector"]:
                if other != persona:
                    other_result = await self.shared_context.get(f"{other}_result")
                    if other_result:
                        other_results[other] = other_result
            
            # 相互参照結果を追加
            result["cross_references"] = other_results
            return result
        
        results = await asyncio.gather(
            execute_with_context("springfield"),
            execute_with_context("krukai"),
            execute_with_context("vector")
        )
        
        return {
            "pattern": "interactive",
            "springfield": results[0],
            "krukai": results[1],
            "vector": results[2],
            "shared_context": dict(self.shared_context.context)
        }
    
    async def _execute_competitive(self, task: Dict) -> Dict:
        """競争的並列実行"""
        
        # 各ペルソナが解を提案
        solutions = await asyncio.gather(
            self._persona_propose("springfield", task),
            self._persona_propose("krukai", task),
            self._persona_propose("vector", task)
        )
        
        # 最良解を選択
        best = max(solutions, key=lambda x: x.get("score", 0))
        
        return {
            "pattern": "competitive",
            "solutions": solutions,
            "winner": best["persona"],
            "winning_solution": best
        }
    
    async def _execute_race(self, task: Dict) -> Dict:
        """最速実行（最初に完了したものを採用）"""
        
        tasks = [
            self._persona_execute("springfield", task),
            self._persona_execute("krukai", task),
            self._persona_execute("vector", task)
        ]
        
        # 最初に完了したタスクの結果を取得
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 残りのタスクをキャンセル
        for task in pending:
            task.cancel()
        
        # 完了したタスクの結果
        result = await list(done)[0]
        
        return {
            "pattern": "race",
            "winner": result.get("persona"),
            "result": result,
            "execution_time": result.get("execution_time")
        }
    
    async def _execute_consensus(self, task: Dict) -> Dict:
        """合意形成必須の実行"""
        
        # 全ペルソナで分析
        results = await asyncio.gather(
            self._persona_execute("springfield", task),
            self._persona_execute("krukai", task),
            self._persona_execute("vector", task)
        )
        
        # 合意形成プロセス
        consensus = await self._build_consensus(results)
        
        return {
            "pattern": "consensus",
            "individual_results": results,
            "consensus": consensus,
            "unanimous": consensus.get("unanimous", False)
        }
    
    async def _persona_execute(self, persona: str, task: Dict) -> Dict:
        """個別ペルソナの実行（シミュレーション）"""
        start = time.time()
        
        # 実行シミュレーション
        await asyncio.sleep(0.1)  # 処理時間のシミュレーション
        
        return {
            "persona": persona,
            "result": f"{persona} analysis of {task.get('topic', 'task')}",
            "confidence": 0.85 + (hash(persona) % 15) / 100,
            "execution_time": time.time() - start
        }
    
    async def _persona_propose(self, persona: str, task: Dict) -> Dict:
        """ペルソナによる解の提案"""
        result = await self._persona_execute(persona, task)
        result["score"] = result["confidence"] * (1 + hash(persona) % 3) / 2
        return result
    
    async def _build_consensus(self, results: List[Dict]) -> Dict:
        """合意形成ロジック"""
        
        # 信頼度の平均
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        
        # 全員が0.8以上なら全会一致
        unanimous = all(r["confidence"] > 0.8 for r in results)
        
        return {
            "average_confidence": avg_confidence,
            "unanimous": unanimous,
            "decision": "approved" if avg_confidence > 0.75 else "requires_revision"
        }


# =====================================
# Example Usage
# =====================================

async def example_usage():
    """使用例"""
    
    executor = TrinityParallelExecutor()
    
    # Trinity モードを起動
    activation = await executor.activate_trinity()
    print("Trinity Activated:", activation)
    
    # 並列実行例
    task = {
        "topic": "System Architecture Review",
        "context": "Microservices migration"
    }
    
    # 独立並列実行
    result = await executor.execute_parallel(
        ExecutionPattern.PARALLEL_INDEPENDENT,
        task
    )
    print("Independent Result:", json.dumps(result, indent=2))
    
    # 相互参照実行
    result = await executor.execute_parallel(
        ExecutionPattern.PARALLEL_INTERACTIVE,
        task
    )
    print("Interactive Result:", json.dumps(result, indent=2))
    
    # 競争実行
    result = await executor.execute_parallel(
        ExecutionPattern.PARALLEL_COMPETITIVE,
        task
    )
    print("Competitive Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(example_usage())