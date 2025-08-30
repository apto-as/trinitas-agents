"""
Seshat Memory Monitor for Trinitas v4.0
メモリ使用パターン監視・分析システム
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class MemoryAccessPattern:
    """メモリアクセスパターン"""
    timestamp: datetime
    persona: str
    task_type: str
    memory_sections: List[str]
    access_type: str  # "read", "write", "update", "delete"
    data_size: int
    response_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class UsageReport:
    """メモリ使用レポート"""
    total_accesses: int
    patterns: List[Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]
    unused_ratio: float
    peak_usage_times: List[Tuple[str, int]]
    persona_usage: Dict[str, int]
    optimization_potential: float  # 0.0-1.0

class SeshatMemoryMonitor:
    """
    Seshat - メモリ使用監視担当
    いつ、どのようにメモリが使用されるかを監視・分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reporting_interval = config.get("personas", {}).get(
            "seshat", {}
        ).get("reporting_interval", 300)  # デフォルト5分
        
        # アクセスパターン記録
        self.access_history: List[MemoryAccessPattern] = []
        self.pattern_cache = defaultdict(list)
        
        # 統計情報
        self.access_count = 0
        self.identified_patterns = []
        self.performance_bottlenecks = []
        self.optimization_recommendations = []
        
        # モニタリング設定
        self.monitoring_enabled = True
        self.auto_optimize = config.get("memory", {}).get("auto_optimize", True)
        
        logger.info(f"Seshat初期化: レポート間隔={self.reporting_interval}秒")
    
    async def analyze_usage_pattern(self, persona: str, task: str, context: Optional[Dict] = None) -> Dict:
        """
        メモリ使用パターンを分析
        
        Args:
            persona: 使用ペルソナ
            task: タスク内容
            context: タスクコンテキスト
            
        Returns:
            使用パターン分析結果
        """
        analysis_start = datetime.now()
        
        # タスク分類
        task_type = self._classify_task(task)
        
        # 必要なメモリセクションを特定
        needed_sections = await self._identify_needed_sections(task, task_type, persona)
        
        # 最適化提案を生成
        suggestions = await self._suggest_optimizations(persona, task_type, needed_sections)
        
        # パターンを記録
        pattern = MemoryAccessPattern(
            timestamp=analysis_start,
            persona=persona,
            task_type=task_type,
            memory_sections=needed_sections,
            access_type="read",  # 分析段階は読み取りのみ
            data_size=0,  # 後で更新
            response_time_ms=(datetime.now() - analysis_start).total_seconds() * 1000,
            metadata=context or {}
        )
        
        self.access_history.append(pattern)
        self.access_count += 1
        
        # パターンキャッシュを更新
        pattern_key = f"{persona}:{task_type}"
        self.pattern_cache[pattern_key].append(pattern)
        
        # 効率的なパターン分析（CPU負荷を軽減） - Bellona戦術的最適化
        if self.access_count % 100 == 0 and self.access_count > 0:
            # 循環参照を防ぐため、軽量版パターン分析のみ実行
            asyncio.create_task(self._force_analyze_patterns())
        
        return {
            "access_time": analysis_start.isoformat(),
            "persona": persona,
            "task_type": task_type,
            "memory_sections_needed": needed_sections,
            "optimization_suggestions": suggestions,
            "estimated_memory_usage": self._estimate_memory_usage(needed_sections),
            "cache_hit_probability": self._calculate_cache_hit_probability(pattern_key)
        }
    
    async def get_usage_report(self) -> Dict:
        """
        包括的な使用レポートを生成
        
        Returns:
            UsageReport形式の辞書
        """
        if not self.access_history:
            return self._empty_report()
        
        # 基本統計
        total_accesses = len(self.access_history)
        
        # パターン分析
        patterns = await self._identify_frequent_patterns()
        
        # ボトルネック検出
        bottlenecks = self._detect_bottlenecks()
        
        # 未使用メモリ比率を計算
        unused_ratio = await self._calculate_unused_ratio()
        
        # ピーク使用時間を特定
        peak_times = self._identify_peak_usage_times()
        
        # ペルソナ別使用統計
        persona_usage = self._calculate_persona_usage()
        
        # 最適化ポテンシャルを評価
        optimization_potential = self._evaluate_optimization_potential(
            patterns, bottlenecks, unused_ratio
        )
        
        # 推奨事項を生成
        recommendations = self._generate_recommendations(
            patterns, bottlenecks, unused_ratio, optimization_potential
        )
        
        report = {
            "total_accesses": total_accesses,
            "patterns": patterns,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "unused_ratio": unused_ratio,
            "peak_usage_times": peak_times,
            "persona_usage": persona_usage,
            "optimization_potential": optimization_potential,
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_period_hours": self._calculate_monitoring_period()
        }
        
        logger.info(f"Seshat使用レポート生成: {total_accesses}アクセス, 最適化ポテンシャル={optimization_potential:.2f}")
        
        return report
    
    def _classify_task(self, task: str) -> str:
        """タスクを分類"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["記憶", "覚える", "remember", "store"]):
            return "memory_write"
        elif any(word in task_lower for word in ["思い出", "取得", "recall", "retrieve"]):
            return "memory_read"
        elif any(word in task_lower for word in ["分析", "analyze", "review"]):
            return "analysis"
        elif any(word in task_lower for word in ["学習", "learn", "training"]):
            return "learning"
        elif any(word in task_lower for word in ["最適化", "optimize"]):
            return "optimization"
        else:
            return "general"
    
    async def _identify_needed_sections(self, task: str, task_type: str, persona: str) -> List[str]:
        """必要なメモリセクションを特定"""
        sections = []
        
        # タスクタイプ別のセクション
        type_sections = {
            "memory_write": ["working_memory", "episodic_memory"],
            "memory_read": ["semantic_memory", "cache"],
            "analysis": ["working_memory", "semantic_memory", "pattern_storage"],
            "learning": ["learning_data", "pattern_storage", "episodic_memory"],
            "optimization": ["performance_metrics", "cache", "indices"],
            "general": ["working_memory", "cache"]
        }
        
        sections.extend(type_sections.get(task_type, ["working_memory"]))
        
        # ペルソナ別の追加セクション
        persona_sections = {
            "athena": ["strategic_patterns", "long_term_plans"],
            "artemis": ["optimization_history", "performance_cache"],
            "hestia": ["security_logs", "threat_database"],
            "bellona": ["task_queue", "distribution_history"],
            "seshat": ["documentation", "usage_statistics"]
        }
        
        if persona in persona_sections:
            sections.extend(persona_sections[persona])
        
        # 重複を除去
        return list(set(sections))
    
    async def _suggest_optimizations(self, persona: str, task_type: str, sections: List[str]) -> List[str]:
        """最適化提案を生成"""
        suggestions = []
        
        # セクション数が多い場合
        if len(sections) > 5:
            suggestions.append("メモリアクセスを段階的に実行して負荷を分散")
        
        # 頻繁にアクセスされるパターン
        pattern_key = f"{persona}:{task_type}"
        if len(self.pattern_cache[pattern_key]) > 10:
            suggestions.append(f"'{pattern_key}'パターンのキャッシュ拡張を推奨")
        
        # 特定のペルソナ向け提案
        if persona == "artemis" and "optimization_history" in sections:
            suggestions.append("過去の最適化結果をプリロードして高速化")
        elif persona == "hestia" and "security_logs" in sections:
            suggestions.append("セキュリティログのインデックスを更新")
        
        return suggestions
    
    async def _analyze_patterns(self):
        """アクセスパターンを分析 - 循環呼び出し防止版"""
        # 直接 _force_analyze_patterns を呼び出さず、ステートチェック追加
        if not hasattr(self, '_analyzing'):
            self._analyzing = True
            try:
                await self._force_analyze_patterns()
            finally:
                self._analyzing = False
    
    async def _force_analyze_patterns(self):
        """強制的にパターン分析を実行（循環呼び出し安全版）"""
        # 最近の100アクセスを効率的に分析（インデックスベース）
        history_len = len(self.access_history)
        if history_len == 0:
            self.identified_patterns = []
            self.performance_bottlenecks = []
            return
            
        # Convert deque to list for safe indexing
        access_list = list(self.access_history)
        
        # メモリ効率的なアクセス（コピーしない）
        start_idx = max(0, history_len - 100)
        
        # パターンを識別
        pattern_counts = defaultdict(int)
        slow_accesses = []
        
        # 単一ループで両方の処理を実行（効率化）
        for i in range(start_idx, history_len):
            access = access_list[i]
            
            # パターンカウント
            pattern = f"{access.persona}:{access.task_type}:{','.join(access.memory_sections[:3])}"
            pattern_counts[pattern] += 1
            
            # ボトルネック検出
            if access.response_time_ms > 100:
                slow_accesses.append(access)
        
        # 頻出パターンを記録
        self.identified_patterns = [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counts.items()
            if count > 5
        ]
        
        # ボトルネックを記録
        if slow_accesses:
            self.performance_bottlenecks = [
                {
                    "persona": a.persona,
                    "task_type": a.task_type,
                    "response_time_ms": a.response_time_ms,
                    "sections": a.memory_sections
                }
                for a in sorted(slow_accesses, key=lambda x: x.response_time_ms, reverse=True)[:5]
            ]
        else:
            self.performance_bottlenecks = []
    
    async def _identify_frequent_patterns(self) -> List[Dict]:
        """頻繁なパターンを識別"""
        # 無限再帰を回避: _analyze_patterns()を直接呼ばず、既存結果を使用
        if not self.identified_patterns:
            # 初回のみパターンを強制分析
            await self._force_analyze_patterns()
        return self.identified_patterns
    
    def _detect_bottlenecks(self) -> List[Dict]:
        """パフォーマンスボトルネックを検出"""
        return self.performance_bottlenecks
    
    async def _calculate_unused_ratio(self) -> float:
        """未使用メモリの比率を計算"""
        # 簡易実装: アクセス頻度から推定
        if not self.access_history:
            return 0.0
        
        # 最近7日間のアクセスを確認
        week_ago = datetime.now() - timedelta(days=7)
        recent_sections = set()
        
        for access in self.access_history:
            if access.timestamp > week_ago:
                recent_sections.update(access.memory_sections)
        
        # 全セクション数を仮定（実際は設定から取得）
        total_sections = 20
        used_sections = len(recent_sections)
        
        return max(0.0, 1.0 - (used_sections / total_sections))
    
    def _identify_peak_usage_times(self) -> List[Tuple[str, int]]:
        """ピーク使用時間を特定"""
        hour_counts = defaultdict(int)
        
        for access in self.access_history:
            hour = access.timestamp.strftime("%H:00")
            hour_counts[hour] += 1
        
        # 上位5つの時間帯
        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_persona_usage(self) -> Dict[str, int]:
        """ペルソナ別の使用統計"""
        persona_counts = defaultdict(int)
        
        for access in self.access_history:
            persona_counts[access.persona] += 1
        
        return dict(persona_counts)
    
    def _evaluate_optimization_potential(self, patterns, bottlenecks, unused_ratio) -> float:
        """最適化ポテンシャルを評価（0.0-1.0）"""
        score = 0.0
        
        # パターンの重複が多いほど最適化の余地あり
        if patterns:
            pattern_score = min(1.0, len(patterns) * 0.1)
            score += pattern_score * 0.3
        
        # ボトルネックが多いほど改善の余地あり
        if bottlenecks:
            bottleneck_score = min(1.0, len(bottlenecks) * 0.2)
            score += bottleneck_score * 0.4
        
        # 未使用領域が多いほどクリーンアップの余地あり
        score += unused_ratio * 0.3
        
        return min(1.0, score)
    
    def _generate_recommendations(self, patterns, bottlenecks, unused_ratio, optimization_potential) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        if optimization_potential > 0.7:
            recommendations.append("緊急: メモリシステムの包括的な最適化が必要")
        elif optimization_potential > 0.4:
            recommendations.append("推奨: 定期的なメモリ最適化を実施")
        
        if patterns and len(patterns) > 3:
            recommendations.append(f"頻出パターン{len(patterns)}個をキャッシュ化")
        
        if bottlenecks:
            slowest = bottlenecks[0]
            recommendations.append(
                f"最遅アクセス（{slowest['response_time_ms']:.0f}ms）の改善が必要"
            )
        
        if unused_ratio > 0.3:
            recommendations.append(f"未使用メモリ{unused_ratio*100:.0f}%のクリーンアップを推奨")
        
        return recommendations
    
    def _calculate_monitoring_period(self) -> float:
        """監視期間を計算（時間）"""
        if not self.access_history:
            return 0.0
        
        # Convert deque to list for safe indexing
        access_list = list(self.access_history)
        first = access_list[0].timestamp
        last = access_list[-1].timestamp
        
        return (last - first).total_seconds() / 3600
    
    def _estimate_memory_usage(self, sections: List[str]) -> Dict[str, Any]:
        """メモリ使用量を推定"""
        # セクション別の推定サイズ（MB）
        section_sizes = {
            "working_memory": 10,
            "episodic_memory": 50,
            "semantic_memory": 100,
            "cache": 20,
            "learning_data": 200,
            "pattern_storage": 30,
            "performance_metrics": 5,
            "indices": 15
        }
        
        total_size = sum(section_sizes.get(s, 10) for s in sections)
        
        return {
            "estimated_mb": total_size,
            "sections_count": len(sections),
            "largest_section": max(sections, key=lambda s: section_sizes.get(s, 10))
        }
    
    def _calculate_cache_hit_probability(self, pattern_key: str) -> float:
        """キャッシュヒット率を計算"""
        if pattern_key not in self.pattern_cache:
            return 0.0
        
        pattern_count = len(self.pattern_cache[pattern_key])
        
        # 10回以上のアクセスで高確率
        if pattern_count > 10:
            return min(0.95, 0.5 + pattern_count * 0.05)
        
        return pattern_count * 0.1
    
    def _empty_report(self) -> Dict:
        """空のレポートを返す"""
        return {
            "total_accesses": 0,
            "patterns": [],
            "bottlenecks": [],
            "recommendations": ["メモリシステムの使用を開始してください"],
            "unused_ratio": 1.0,
            "peak_usage_times": [],
            "persona_usage": {},
            "optimization_potential": 0.0,
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_period_hours": 0.0
        }
    
    def get_status(self) -> Dict:
        """Seshatの現在状態を取得"""
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "total_accesses": self.access_count,
            "identified_patterns": len(self.identified_patterns),
            "performance_bottlenecks": len(self.performance_bottlenecks),
            "reporting_interval_seconds": self.reporting_interval,
            "auto_optimize": self.auto_optimize,
            "cache_patterns": len(self.pattern_cache)
        }