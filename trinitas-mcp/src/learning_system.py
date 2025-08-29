"""
Learning System for Trinitas v4.0
学習・パターン認識システム
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """学習パターン"""
    id: str
    pattern_type: str  # "task", "solution", "optimization", "error"
    content: Dict[str, Any]
    frequency: int
    confidence: float
    personas: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LearningResult:
    """学習結果"""
    pattern_id: str
    success: bool
    confidence_delta: float
    insights: List[str]
    recommendations: List[str]
    timestamp: datetime

class LearningSystem:
    """
    学習システム - パターン認識と知識蓄積
    Trinitasの経験から学習し、最適化を提案
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("learning", {}).get("enabled", True)
        self.storage_path = Path(config.get("learning", {}).get("storage", "./learning_data"))
        self.auto_learn = config.get("learning", {}).get("auto_learn", True)
        self.pattern_recognition = config.get("learning", {}).get("pattern_recognition", True)
        
        # パターンストレージ
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(list)  # type -> pattern_ids
        
        # 学習メトリクス
        self.learning_count = 0
        self.pattern_matches = 0
        self.success_rate = 0.0
        
        # 初期化
        self._initialize_storage()
        self._load_existing_patterns()
        
        logger.info(f"Learning System initialized: enabled={self.enabled}, patterns={len(self.patterns)}")
    
    def _initialize_storage(self):
        """ストレージ初期化"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # サブディレクトリ作成
        (self.storage_path / "patterns").mkdir(exist_ok=True)
        (self.storage_path / "models").mkdir(exist_ok=True)
        (self.storage_path / "metrics").mkdir(exist_ok=True)
        (self.storage_path / "insights").mkdir(exist_ok=True)
    
    def _load_existing_patterns(self):
        """既存パターンをロード"""
        patterns_dir = self.storage_path / "patterns"
        
        for pattern_file in patterns_dir.glob("*.json"):
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pattern = Pattern(**data)
                    self.patterns[pattern.id] = pattern
                    self.pattern_index[pattern.pattern_type].append(pattern.id)
                    
            except Exception as e:
                logger.warning(f"Failed to load pattern {pattern_file}: {e}")
        
        logger.info(f"Loaded {len(self.patterns)} existing patterns")
    
    async def learn_from_execution(self, persona: str, task: str, result: Dict) -> LearningResult:
        """
        実行結果から学習
        
        Args:
            persona: 実行ペルソナ
            task: 実行タスク
            result: 実行結果
            
        Returns:
            学習結果
        """
        if not self.enabled:
            return self._empty_result()
        
        self.learning_count += 1
        
        # パターン抽出
        extracted_pattern = await self._extract_pattern(persona, task, result)
        
        # 既存パターンとのマッチング
        matched_pattern = await self._match_pattern(extracted_pattern)
        
        if matched_pattern:
            # 既存パターンを強化
            learning_result = await self._reinforce_pattern(matched_pattern, extracted_pattern, result)
            self.pattern_matches += 1
        else:
            # 新規パターンとして登録
            learning_result = await self._register_new_pattern(extracted_pattern)
        
        # 成功率を更新
        if result.get("success", False):
            self.success_rate = (self.success_rate * (self.learning_count - 1) + 1) / self.learning_count
        else:
            self.success_rate = (self.success_rate * (self.learning_count - 1)) / self.learning_count
        
        # 学習結果を保存
        await self._save_learning_result(learning_result)
        
        # インサイトを生成
        if self.learning_count % 10 == 0:
            await self._generate_insights()
        
        return learning_result
    
    async def apply_pattern(self, pattern: str, task: str, context: Dict) -> Dict:
        """
        パターンを適用
        
        Args:
            pattern: パターン名またはID
            task: 適用先タスク
            context: コンテキスト
            
        Returns:
            適用結果
        """
        # パターンを検索
        target_pattern = None
        if pattern in self.patterns:
            target_pattern = self.patterns[pattern]
        else:
            # パターン名で検索
            for p in self.patterns.values():
                if p.metadata.get("name") == pattern:
                    target_pattern = p
                    break
        
        if not target_pattern:
            return {
                "applied": False,
                "error": f"Pattern '{pattern}' not found",
                "available_patterns": list(self.patterns.keys())[:10]
            }
        
        # パターンを適用
        application = await self._apply_pattern_to_task(target_pattern, task, context)
        
        return {
            "applied": True,
            "pattern_id": target_pattern.id,
            "confidence": target_pattern.confidence,
            "application": application,
            "recommendations": self._generate_recommendations(target_pattern, task)
        }
    
    async def _extract_pattern(self, persona: str, task: str, result: Dict) -> Dict:
        """パターンを抽出"""
        # タスクを分析
        task_tokens = self._tokenize_task(task)
        task_type = self._classify_task(task_tokens)
        
        # 結果を分析
        success = result.get("success", False)
        execution_time = result.get("execution_time_seconds", 0)
        memory_usage = result.get("memory_usage", {})
        
        # パターン構造を作成
        pattern = {
            "task_tokens": task_tokens,
            "task_type": task_type,
            "persona": persona,
            "success": success,
            "performance": {
                "execution_time": execution_time,
                "memory_sections": memory_usage.get("memory_sections_needed", []),
                "optimization_level": memory_usage.get("optimization_potential", 0)
            },
            "result_structure": self._analyze_result_structure(result),
            "timestamp": datetime.now().isoformat()
        }
        
        return pattern
    
    async def _match_pattern(self, pattern: Dict) -> Optional[Pattern]:
        """既存パターンとマッチング"""
        task_type = pattern.get("task_type", "general")
        candidates = self.pattern_index.get(task_type, [])
        
        best_match = None
        best_score = 0.0
        
        for pattern_id in candidates:
            existing = self.patterns[pattern_id]
            score = self._calculate_similarity(pattern, existing.content)
            
            if score > 0.7 and score > best_score:  # 70%以上の類似度
                best_match = existing
                best_score = score
        
        return best_match
    
    async def _reinforce_pattern(self, existing: Pattern, new_pattern: Dict, result: Dict) -> LearningResult:
        """既存パターンを強化"""
        # 頻度を増加
        existing.frequency += 1
        
        # 信頼度を調整
        if result.get("success", False):
            confidence_delta = 0.05  # 成功で信頼度上昇
            existing.confidence = min(1.0, existing.confidence + confidence_delta)
        else:
            confidence_delta = -0.02  # 失敗で信頼度微減
            existing.confidence = max(0.1, existing.confidence + confidence_delta)
        
        # パターン内容を更新
        existing.content = self._merge_patterns(existing.content, new_pattern)
        existing.updated_at = datetime.now()
        
        # パターンを保存
        await self._save_pattern(existing)
        
        # インサイトを生成
        insights = [
            f"Pattern reinforced: {existing.id}",
            f"New confidence: {existing.confidence:.2f}",
            f"Total occurrences: {existing.frequency}"
        ]
        
        # 推奨事項
        recommendations = []
        if existing.confidence > 0.8 and existing.frequency > 5:
            recommendations.append(f"High confidence pattern - consider automation")
        if existing.confidence < 0.5:
            recommendations.append(f"Low confidence - review pattern validity")
        
        return LearningResult(
            pattern_id=existing.id,
            success=True,
            confidence_delta=confidence_delta,
            insights=insights,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _register_new_pattern(self, pattern: Dict) -> LearningResult:
        """新規パターンを登録"""
        pattern_id = self._generate_pattern_id()
        
        new_pattern = Pattern(
            id=pattern_id,
            pattern_type=pattern.get("task_type", "general"),
            content=pattern,
            frequency=1,
            confidence=0.5,  # 初期信頼度
            personas=[pattern.get("persona", "unknown")],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                "origin": "automatic_learning",
                "version": 1
            }
        )
        
        # パターンを登録
        self.patterns[pattern_id] = new_pattern
        self.pattern_index[new_pattern.pattern_type].append(pattern_id)
        
        # パターンを保存
        await self._save_pattern(new_pattern)
        
        return LearningResult(
            pattern_id=pattern_id,
            success=True,
            confidence_delta=0.5,
            insights=[f"New pattern discovered: {pattern_id}"],
            recommendations=["Monitor pattern evolution"],
            timestamp=datetime.now()
        )
    
    async def _apply_pattern_to_task(self, pattern: Pattern, task: str, context: Dict) -> Dict:
        """パターンをタスクに適用"""
        application = {
            "suggested_approach": self._suggest_approach(pattern, task),
            "expected_performance": {
                "execution_time": pattern.content.get("performance", {}).get("execution_time", "unknown"),
                "memory_sections": pattern.content.get("performance", {}).get("memory_sections", [])
            },
            "best_personas": pattern.personas,
            "confidence": pattern.confidence,
            "precedents": pattern.frequency
        }
        
        # コンテキストによる調整
        if context.get("priority") == "performance":
            application["optimization_hints"] = self._get_optimization_hints(pattern)
        elif context.get("priority") == "security":
            application["security_considerations"] = self._get_security_considerations(pattern)
        
        return application
    
    def _tokenize_task(self, task: str) -> List[str]:
        """タスクをトークン化"""
        # 簡易トークナイザー
        import re
        tokens = re.findall(r'\w+', task.lower())
        return tokens
    
    def _classify_task(self, tokens: List[str]) -> str:
        """タスクを分類"""
        # キーワードベースの分類
        categories = {
            "optimization": ["optimize", "performance", "speed", "最適化"],
            "security": ["security", "vulnerability", "audit", "セキュリティ"],
            "analysis": ["analyze", "review", "evaluate", "分析"],
            "implementation": ["implement", "create", "build", "実装"],
            "documentation": ["document", "describe", "explain", "文書"],
            "debugging": ["debug", "fix", "error", "バグ"],
            "refactoring": ["refactor", "restructure", "improve", "リファクタ"]
        }
        
        scores = defaultdict(int)
        for token in tokens:
            for category, keywords in categories.items():
                if token in keywords:
                    scores[category] += 1
        
        if scores:
            return max(scores, key=scores.get)
        return "general"
    
    def _analyze_result_structure(self, result: Dict) -> Dict:
        """結果の構造を分析"""
        structure = {
            "keys": list(result.keys()),
            "depth": self._get_dict_depth(result),
            "has_error": "error" in result,
            "has_data": "data" in result or "result" in result,
            "size_estimate": len(json.dumps(result, default=str))
        }
        return structure
    
    def _get_dict_depth(self, d: Dict, level: int = 0) -> int:
        """辞書の深さを取得"""
        if not isinstance(d, dict) or not d:
            return level
        
        nested_dicts = [v for v in d.values() if isinstance(v, dict)]
        if not nested_dicts:
            return level
        
        return max(self._get_dict_depth(v, level + 1) for v in nested_dicts)
    
    def _calculate_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """パターン間の類似度を計算"""
        # 簡易類似度計算
        score = 0.0
        weights = {
            "task_type": 0.3,
            "persona": 0.2,
            "success": 0.2,
            "result_structure": 0.3
        }
        
        for key, weight in weights.items():
            if key in pattern1 and key in pattern2:
                if pattern1[key] == pattern2[key]:
                    score += weight
                elif key == "result_structure":
                    # 構造の部分一致を評価
                    struct1 = pattern1[key]
                    struct2 = pattern2[key]
                    if struct1.get("keys") and struct2.get("keys"):
                        common = set(struct1["keys"]) & set(struct2["keys"])
                        union = set(struct1["keys"]) | set(struct2["keys"])
                        if union:
                            score += weight * (len(common) / len(union))
        
        return score
    
    def _merge_patterns(self, existing: Dict, new: Dict) -> Dict:
        """パターンをマージ"""
        merged = existing.copy()
        
        # パフォーマンスメトリクスの平均化
        if "performance" in new and "performance" in merged:
            perf_existing = merged["performance"]
            perf_new = new["performance"]
            
            if "execution_time" in perf_existing and "execution_time" in perf_new:
                # 加重平均
                merged["performance"]["execution_time"] = (
                    perf_existing["execution_time"] * 0.7 + 
                    perf_new["execution_time"] * 0.3
                )
        
        # タイムスタンプ更新
        merged["last_updated"] = datetime.now().isoformat()
        
        return merged
    
    async def _save_pattern(self, pattern: Pattern):
        """パターンを保存"""
        pattern_file = self.storage_path / "patterns" / f"{pattern.id}.json"
        
        data = {
            "id": pattern.id,
            "pattern_type": pattern.pattern_type,
            "content": pattern.content,
            "frequency": pattern.frequency,
            "confidence": pattern.confidence,
            "personas": pattern.personas,
            "created_at": pattern.created_at.isoformat(),
            "updated_at": pattern.updated_at.isoformat(),
            "metadata": pattern.metadata
        }
        
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def _save_learning_result(self, result: LearningResult):
        """学習結果を保存"""
        metrics_file = self.storage_path / "metrics" / f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        data = {
            "pattern_id": result.pattern_id,
            "success": result.success,
            "confidence_delta": result.confidence_delta,
            "insights": result.insights,
            "recommendations": result.recommendations,
            "timestamp": result.timestamp.isoformat()
        }
        
        with open(metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    async def _generate_insights(self):
        """インサイトを生成"""
        insights = []
        
        # パターン分析
        if self.patterns:
            high_confidence = [p for p in self.patterns.values() if p.confidence > 0.8]
            low_confidence = [p for p in self.patterns.values() if p.confidence < 0.3]
            
            insights.append(f"High confidence patterns: {len(high_confidence)}")
            insights.append(f"Low confidence patterns: {len(low_confidence)}")
            
            # 最頻出パターンタイプ
            type_counts = defaultdict(int)
            for pattern in self.patterns.values():
                type_counts[pattern.pattern_type] += 1
            
            if type_counts:
                most_common = max(type_counts, key=type_counts.get)
                insights.append(f"Most common pattern type: {most_common} ({type_counts[most_common]} patterns)")
        
        # 成功率分析
        insights.append(f"Overall success rate: {self.success_rate:.2%}")
        insights.append(f"Pattern match rate: {self.pattern_matches / max(1, self.learning_count):.2%}")
        
        # インサイトを保存
        insights_file = self.storage_path / "insights" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "insights": insights,
                "metrics": {
                    "total_patterns": len(self.patterns),
                    "learning_count": self.learning_count,
                    "pattern_matches": self.pattern_matches,
                    "success_rate": self.success_rate
                }
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Generated {len(insights)} insights")
    
    def _generate_recommendations(self, pattern: Pattern, task: str) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        # 信頼度ベースの推奨
        if pattern.confidence > 0.8:
            recommendations.append("High confidence pattern - proceed with standard approach")
        elif pattern.confidence < 0.5:
            recommendations.append("Low confidence - consider alternative approaches")
        
        # 頻度ベースの推奨
        if pattern.frequency > 10:
            recommendations.append("Well-established pattern - optimize for speed")
        elif pattern.frequency < 3:
            recommendations.append("Rare pattern - monitor carefully")
        
        # パフォーマンスベースの推奨
        perf = pattern.content.get("performance", {})
        if perf.get("execution_time", 0) > 5:
            recommendations.append("Consider breaking into smaller tasks")
        
        return recommendations
    
    def _suggest_approach(self, pattern: Pattern, task: str) -> Dict:
        """アプローチを提案"""
        return {
            "personas": pattern.personas,
            "strategy": f"Use {pattern.pattern_type} approach",
            "precedents": f"Successfully applied {pattern.frequency} times",
            "confidence": f"{pattern.confidence:.0%} confidence level"
        }
    
    def _get_optimization_hints(self, pattern: Pattern) -> List[str]:
        """最適化ヒントを取得"""
        hints = []
        perf = pattern.content.get("performance", {})
        
        if perf.get("memory_sections"):
            hints.append(f"Preload memory sections: {', '.join(perf['memory_sections'][:3])}")
        
        if perf.get("execution_time", 0) < 1:
            hints.append("Fast execution expected - use synchronous processing")
        else:
            hints.append("Consider asynchronous processing for better performance")
        
        return hints
    
    def _get_security_considerations(self, pattern: Pattern) -> List[str]:
        """セキュリティ考慮事項を取得"""
        considerations = []
        
        if "hestia" in pattern.personas:
            considerations.append("Security-reviewed pattern")
        else:
            considerations.append("Consider security review by Hestia")
        
        if pattern.content.get("result_structure", {}).get("has_error"):
            considerations.append("Pattern includes error handling")
        
        return considerations
    
    def _generate_pattern_id(self) -> str:
        """パターンIDを生成"""
        from uuid import uuid4
        return f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
    
    def _empty_result(self) -> LearningResult:
        """空の結果を返す"""
        return LearningResult(
            pattern_id="none",
            success=False,
            confidence_delta=0.0,
            insights=["Learning system disabled"],
            recommendations=[],
            timestamp=datetime.now()
        )
    
    async def get_status(self) -> Dict:
        """学習システムのステータス"""
        return {
            "enabled": self.enabled,
            "auto_learn": self.auto_learn,
            "pattern_recognition": self.pattern_recognition,
            "total_patterns": len(self.patterns),
            "pattern_types": list(self.pattern_index.keys()),
            "learning_count": self.learning_count,
            "pattern_matches": self.pattern_matches,
            "success_rate": self.success_rate,
            "storage_path": str(self.storage_path),
            "storage_size_mb": self._calculate_storage_size()
        }
    
    async def get_learning_report(self) -> Dict:
        """学習レポートを生成"""
        report = {
            "summary": {
                "total_patterns": len(self.patterns),
                "active_patterns": len([p for p in self.patterns.values() if p.confidence > 0.5]),
                "learning_sessions": self.learning_count,
                "success_rate": self.success_rate
            },
            "patterns_by_type": {},
            "top_patterns": [],
            "recent_insights": [],
            "recommendations": []
        }
        
        # タイプ別パターン数
        for ptype, pattern_ids in self.pattern_index.items():
            report["patterns_by_type"][ptype] = len(pattern_ids)
        
        # トップパターン（信頼度×頻度）
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.confidence * p.frequency,
            reverse=True
        )[:5]
        
        for pattern in sorted_patterns:
            report["top_patterns"].append({
                "id": pattern.id,
                "type": pattern.pattern_type,
                "confidence": pattern.confidence,
                "frequency": pattern.frequency,
                "score": pattern.confidence * pattern.frequency
            })
        
        # 最近のインサイト
        insights_dir = self.storage_path / "insights"
        recent_files = sorted(insights_dir.glob("*.json"), reverse=True)[:3]
        for file in recent_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    report["recent_insights"].extend(data.get("insights", [])[:3])
            except:
                pass
        
        # 全体的な推奨事項
        if self.success_rate > 0.8:
            report["recommendations"].append("System performing well - consider expanding automation")
        if len(self.patterns) > 100:
            report["recommendations"].append("Many patterns learned - consider pattern consolidation")
        if self.pattern_matches / max(1, self.learning_count) < 0.3:
            report["recommendations"].append("Low pattern reuse - review pattern quality")
        
        return report
    
    def _calculate_storage_size(self) -> float:
        """ストレージサイズを計算（MB）"""
        total_size = 0
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size / (1024 * 1024)