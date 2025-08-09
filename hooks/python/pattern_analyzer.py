#!/usr/bin/env python3
"""
pattern_analyzer.py - パターン分析エンジン
実行履歴から有用なパターンを抽出し、分類
"""

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple


class PatternType(Enum):
    """パターンタイプ"""

    SEQUENCE = "sequence"  # 順序パターン
    CORRELATION = "correlation"  # 相関パターン
    FREQUENCY = "frequency"  # 頻度パターン
    ANOMALY = "anomaly"  # 異常パターン
    OPTIMIZATION = "optimization"  # 最適化パターン


@dataclass
class ExtractedPattern:
    """抽出されたパターン"""

    pattern_type: PatternType
    description: str
    elements: List[Any]
    frequency: int
    confidence: float
    context: Dict[str, Any]
    examples: List[Dict[str, Any]]


@dataclass
class PatternRelation:
    """パターン間の関係"""

    pattern1_id: str
    pattern2_id: str
    relation_type: str  # "causes", "follows", "conflicts", "enhances"
    strength: float
    evidence_count: int


class PatternAnalyzer:
    """パターン分析のメインクラス"""

    def __init__(self):
        self.data_dir = Path.home() / ".claude" / "trinitas" / "patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_db = self.data_dir / "pattern_database.json"
        self.relations_db = self.data_dir / "pattern_relations.json"

        self.patterns = self._load_patterns()
        self.relations = self._load_relations()

        # 分析パラメータ
        self.min_frequency = 3
        self.min_confidence = 0.6
        self.sequence_window = 5

    def _load_patterns(self) -> Dict[str, ExtractedPattern]:
        """パターンデータベースを読み込む"""
        if self.patterns_db.exists():
            with open(self.patterns_db) as f:
                data = json.load(f)
                patterns = {}
                for pid, pdata in data.items():
                    patterns[pid] = ExtractedPattern(
                        pattern_type=PatternType(pdata["pattern_type"]),
                        description=pdata["description"],
                        elements=pdata["elements"],
                        frequency=pdata["frequency"],
                        confidence=pdata["confidence"],
                        context=pdata["context"],
                        examples=pdata["examples"],
                    )
                return patterns
        return {}

    def _load_relations(self) -> List[PatternRelation]:
        """パターン関係を読み込む"""
        if self.relations_db.exists():
            with open(self.relations_db) as f:
                data = json.load(f)
                relations = []
                for rdata in data:
                    relations.append(
                        PatternRelation(
                            pattern1_id=rdata["pattern1_id"],
                            pattern2_id=rdata["pattern2_id"],
                            relation_type=rdata["relation_type"],
                            strength=rdata["strength"],
                            evidence_count=rdata["evidence_count"],
                        )
                    )
                return relations
        return []

    def analyze_execution_history(
        self, history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """実行履歴を分析してパターンを抽出"""
        analysis_results = {
            "sequence_patterns": [],
            "correlation_patterns": [],
            "frequency_patterns": [],
            "anomaly_patterns": [],
            "optimization_patterns": [],
        }

        # 各種パターンを分析
        analysis_results["sequence_patterns"] = self._analyze_sequences(history)
        analysis_results["correlation_patterns"] = self._analyze_correlations(history)
        analysis_results["frequency_patterns"] = self._analyze_frequencies(history)
        analysis_results["anomaly_patterns"] = self._detect_anomalies(history)
        analysis_results["optimization_patterns"] = self._find_optimizations(history)

        # パターン間の関係を分析
        self._analyze_pattern_relations(analysis_results)

        # 結果を保存
        self._save_analysis_results(analysis_results)

        return analysis_results

    def _analyze_sequences(
        self, history: List[Dict[str, Any]]
    ) -> List[ExtractedPattern]:
        """シーケンシャルパターンを分析"""
        sequences = []

        # アクションのシーケンスを抽出
        for i in range(len(history) - self.sequence_window + 1):
            window = history[i : i + self.sequence_window]

            # アクションの順序を抽出
            action_sequence = []
            for entry in window:
                action = entry.get("action", {})
                action_type = action.get("type", "unknown")
                action_sequence.append(action_type)

            # 頻出シーケンスを検出
            sequence_key = "_".join(action_sequence)

            # 既存のシーケンスパターンを更新または作成
            existing = next(
                (s for s in sequences if "_".join(s.elements) == sequence_key), None
            )

            if existing:
                existing.frequency += 1
                existing.examples.append(window[0])
            else:
                # 成功率を計算
                success_count = sum(
                    1
                    for entry in window
                    if entry.get("outcome", {}).get("success", False)
                )
                confidence = success_count / len(window)

                if confidence >= self.min_confidence:
                    pattern = ExtractedPattern(
                        pattern_type=PatternType.SEQUENCE,
                        description=f"Sequential pattern: {' -> '.join(action_sequence)}",
                        elements=action_sequence,
                        frequency=1,
                        confidence=confidence,
                        context=self._extract_common_context(window),
                        examples=[window[0]],
                    )
                    sequences.append(pattern)

        # 頻度でフィルタ
        return [s for s in sequences if s.frequency >= self.min_frequency]

    def _analyze_correlations(
        self, history: List[Dict[str, Any]]
    ) -> List[ExtractedPattern]:
        """相関パターンを分析"""
        correlations = []

        # 属性間の相関を検出
        # 例: 高複雑度 + セキュリティドメイン -> Vector persona

        # コンテキスト属性を収集
        context_outcomes = defaultdict(list)

        for entry in history:
            context = entry.get("context", {})
            outcome = entry.get("outcome", {})

            # キーコンテキストを抽出
            key = (
                context.get("complexity", "unknown"),
                tuple(sorted(context.get("domains", []))),
                context.get("resource_zone", "green"),
            )

            context_outcomes[key].append(outcome)

        # 相関を分析
        for context_key, outcomes in context_outcomes.items():
            if len(outcomes) >= self.min_frequency:
                # 成功パターンを検出
                success_actions = []
                for i, outcome in enumerate(outcomes):
                    if outcome.get("success", False):
                        # 対応するアクションを探す
                        if i < len(history):
                            action = history[i].get("action", {})
                            success_actions.append(action)

                if success_actions:
                    # 最も頻繁な成功アクション
                    action_types = [a.get("type", "unknown") for a in success_actions]
                    most_common = Counter(action_types).most_common(1)

                    if most_common:
                        common_action, count = most_common[0]
                        confidence = count / len(outcomes)

                        if confidence >= self.min_confidence:
                            pattern = ExtractedPattern(
                                pattern_type=PatternType.CORRELATION,
                                description=f"Context {context_key} correlates with {common_action}",
                                elements=[context_key, common_action],
                                frequency=len(outcomes),
                                confidence=confidence,
                                context={"correlation_type": "context_to_action"},
                                examples=outcomes[:3],
                            )
                            correlations.append(pattern)

        return correlations

    def _analyze_frequencies(
        self, history: List[Dict[str, Any]]
    ) -> List[ExtractedPattern]:
        """頻度パターンを分析"""
        frequencies = []

        # アクションの頻度を集計
        action_counts = defaultdict(int)
        action_contexts = defaultdict(list)

        for entry in history:
            action = entry.get("action", {})
            action_key = json.dumps(action, sort_keys=True)
            action_counts[action_key] += 1
            action_contexts[action_key].append(entry.get("context", {}))

        # 頻出アクションをパターンとして抽出
        for action_key, count in action_counts.items():
            if count >= self.min_frequency:
                action = json.loads(action_key)

                # 共通コンテキストを抽出
                contexts = action_contexts[action_key]
                common_context = self._extract_common_context(
                    [{"context": c} for c in contexts]
                )

                pattern = ExtractedPattern(
                    pattern_type=PatternType.FREQUENCY,
                    description=f"Frequent action: {action.get('type', 'unknown')}",
                    elements=[action],
                    frequency=count,
                    confidence=count / len(history),
                    context=common_context,
                    examples=contexts[:3],
                )
                frequencies.append(pattern)

        return sorted(frequencies, key=lambda p: p.frequency, reverse=True)

    def _detect_anomalies(
        self, history: List[Dict[str, Any]]
    ) -> List[ExtractedPattern]:
        """異常パターンを検出"""
        anomalies = []

        # 異常な実行時間
        exec_times = []
        for entry in history:
            exec_time = entry.get("outcome", {}).get("execution_time", 0)
            if exec_time > 0:
                exec_times.append(exec_time)

        if exec_times:
            avg_time = sum(exec_times) / len(exec_times)
            std_dev = (
                sum((t - avg_time) ** 2 for t in exec_times) / len(exec_times)
            ) ** 0.5

            # 3σを超える実行時間を異常とする
            threshold = avg_time + 3 * std_dev

            for entry in history:
                exec_time = entry.get("outcome", {}).get("execution_time", 0)
                if exec_time > threshold:
                    pattern = ExtractedPattern(
                        pattern_type=PatternType.ANOMALY,
                        description=f"Abnormally long execution: {exec_time:.1f}s (avg: {avg_time:.1f}s)",
                        elements=[entry],
                        frequency=1,
                        confidence=1.0,
                        context=entry.get("context", {}),
                        examples=[entry],
                    )
                    anomalies.append(pattern)

        # 連続失敗パターン
        consecutive_failures = 0
        failure_start = None

        for i, entry in enumerate(history):
            if not entry.get("outcome", {}).get("success", True):
                if consecutive_failures == 0:
                    failure_start = i
                consecutive_failures += 1
            else:
                if consecutive_failures >= 3:
                    # 3回以上の連続失敗を異常とする
                    failure_entries = history[
                        failure_start : failure_start + consecutive_failures
                    ]
                    pattern = ExtractedPattern(
                        pattern_type=PatternType.ANOMALY,
                        description=f"Consecutive failures: {consecutive_failures} in a row",
                        elements=failure_entries,
                        frequency=1,
                        confidence=1.0,
                        context=self._extract_common_context(failure_entries),
                        examples=failure_entries[:3],
                    )
                    anomalies.append(pattern)
                consecutive_failures = 0

        return anomalies

    def _find_optimizations(
        self, history: List[Dict[str, Any]]
    ) -> List[ExtractedPattern]:
        """最適化パターンを発見"""
        optimizations = []

        # 同じタスクタイプで異なる実行方法を比較
        task_variations = defaultdict(list)

        for entry in history:
            context = entry.get("context", {})
            task_type = context.get("task_type", "unknown")

            if task_type != "unknown":
                task_variations[task_type].append(entry)

        # 各タスクタイプで最適な方法を見つける
        for task_type, entries in task_variations.items():
            if len(entries) >= self.min_frequency * 2:
                # パフォーマンスメトリクスで分類
                performance_groups = defaultdict(list)

                for entry in entries:
                    outcome = entry.get("outcome", {})
                    exec_time = outcome.get("execution_time", float("inf"))
                    success = outcome.get("success", False)

                    if success:
                        # 実行時間でグループ化（10秒単位）
                        time_group = int(exec_time // 10) * 10
                        performance_groups[time_group].append(entry)

                if len(performance_groups) >= 2:
                    # 最速グループを最適化パターンとして抽出
                    fastest_group = min(performance_groups.keys())
                    fastest_entries = performance_groups[fastest_group]

                    if len(fastest_entries) >= self.min_frequency:
                        # 共通要素を抽出
                        common_actions = self._extract_common_elements(
                            [e.get("action", {}) for e in fastest_entries]
                        )

                        pattern = ExtractedPattern(
                            pattern_type=PatternType.OPTIMIZATION,
                            description=f"Optimized approach for {task_type}: ~{fastest_group}s execution",
                            elements=common_actions,
                            frequency=len(fastest_entries),
                            confidence=len(fastest_entries) / len(entries),
                            context={"task_type": task_type, "avg_time": fastest_group},
                            examples=fastest_entries[:3],
                        )
                        optimizations.append(pattern)

        return optimizations

    def _extract_common_context(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """エントリーから共通コンテキストを抽出"""
        if not entries:
            return {}

        # 全エントリーで共通する属性を見つける
        common = {}
        first_context = entries[0].get("context", {})

        for key, value in first_context.items():
            if all(entry.get("context", {}).get(key) == value for entry in entries):
                common[key] = value

        return common

    def _extract_common_elements(self, items: List[Dict[str, Any]]) -> List[Any]:
        """共通要素を抽出"""
        if not items:
            return []

        # 全アイテムで共通するキーと値を見つける
        common_elements = []

        # キーの頻度をカウント
        key_counts = defaultdict(int)
        for item in items:
            for key in item.keys():
                key_counts[key] += 1

        # 全アイテムに存在するキーを抽出
        for key, count in key_counts.items():
            if count == len(items):
                # 値も同じか確認
                values = [item.get(key) for item in items]
                if len(set(str(v) for v in values)) == 1:
                    common_elements.append({key: values[0]})

        return common_elements

    def _analyze_pattern_relations(self, analysis_results: Dict[str, Any]):
        """パターン間の関係を分析"""
        all_patterns = []

        # 全パターンを収集
        for pattern_list in analysis_results.values():
            all_patterns.extend(pattern_list)

        # パターン間の関係を検出
        for i, pattern1 in enumerate(all_patterns):
            for pattern2 in all_patterns[i + 1 :]:
                # 時系列的な関係
                if (
                    pattern1.pattern_type == PatternType.SEQUENCE
                    and pattern2.pattern_type == PatternType.SEQUENCE
                ):
                    # シーケンスの連続性をチェック
                    if pattern1.elements[-1] == pattern2.elements[0]:
                        relation = PatternRelation(
                            pattern1_id=self._generate_pattern_id(pattern1),
                            pattern2_id=self._generate_pattern_id(pattern2),
                            relation_type="follows",
                            strength=0.8,
                            evidence_count=min(pattern1.frequency, pattern2.frequency),
                        )
                        self.relations.append(relation)

                # 相関関係
                if (
                    pattern1.pattern_type == PatternType.CORRELATION
                    and pattern2.pattern_type == PatternType.OPTIMIZATION
                ):
                    # 同じコンテキストでの最適化
                    if pattern1.context.get("task_type") == pattern2.context.get(
                        "task_type"
                    ):
                        relation = PatternRelation(
                            pattern1_id=self._generate_pattern_id(pattern1),
                            pattern2_id=self._generate_pattern_id(pattern2),
                            relation_type="enhances",
                            strength=0.7,
                            evidence_count=min(pattern1.frequency, pattern2.frequency),
                        )
                        self.relations.append(relation)

    def _generate_pattern_id(self, pattern: ExtractedPattern) -> str:
        """パターンIDを生成"""
        import hashlib

        content = (
            f"{pattern.pattern_type.value}_{pattern.description}_{pattern.elements}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _save_analysis_results(self, results: Dict[str, Any]):
        """分析結果を保存"""
        # パターンをデータベースに追加
        for pattern_list in results.values():
            for pattern in pattern_list:
                pattern_id = self._generate_pattern_id(pattern)
                self.patterns[pattern_id] = pattern

        # パターンデータベースを保存
        patterns_data = {}
        for pid, pattern in self.patterns.items():
            patterns_data[pid] = {
                "pattern_type": pattern.pattern_type.value,
                "description": pattern.description,
                "elements": pattern.elements,
                "frequency": pattern.frequency,
                "confidence": pattern.confidence,
                "context": pattern.context,
                "examples": pattern.examples[:5],  # 最大5例を保存
            }

        with open(self.patterns_db, "w") as f:
            json.dump(patterns_data, f, indent=2)

        # 関係データベースを保存
        relations_data = []
        for relation in self.relations:
            relations_data.append(
                {
                    "pattern1_id": relation.pattern1_id,
                    "pattern2_id": relation.pattern2_id,
                    "relation_type": relation.relation_type,
                    "strength": relation.strength,
                    "evidence_count": relation.evidence_count,
                }
            )

        with open(self.relations_db, "w") as f:
            json.dump(relations_data, f, indent=2)

    def find_similar_patterns(
        self, target_pattern: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """類似パターンを検索"""
        similarities = []

        target_type = target_pattern.get("type", "unknown")
        target_context = target_pattern.get("context", {})

        # パターンデータベースが空の場合は空リストを返す
        if not self.patterns:
            return []

        for pattern_id, pattern in self.patterns.items():
            # タイプが一致するパターンのみ
            if pattern.pattern_type.value == target_type:
                # コンテキストの類似度を計算
                similarity = self._calculate_context_similarity(
                    target_context, pattern.context
                )

                if similarity > 0.5:
                    similarities.append((pattern_id, similarity))

        # 類似度でソート
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:10]  # Top 10

    def _calculate_context_similarity(
        self, context1: Dict[str, Any], context2: Dict[str, Any]
    ) -> float:
        """コンテキストの類似度を計算"""
        if not context1 or not context2:
            return 0.0

        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0

        matches = 0
        for key in common_keys:
            if context1[key] == context2[key]:
                matches += 1

        # Jaccard係数
        all_keys = set(context1.keys()) | set(context2.keys())
        return matches / len(all_keys) if all_keys else 0.0


def main():
    """Claude Code Hook として実行"""
    input_data = json.loads(sys.stdin.read())

    action = input_data.get("action", "analyze")
    analyzer = PatternAnalyzer()

    try:
        if action == "analyze":
            # 実行履歴を分析
            history = input_data.get("history", [])

            if not history:
                raise ValueError("No history provided for analysis")

            results = analyzer.analyze_execution_history(history)

            # サマリーを生成
            total_patterns = sum(len(patterns) for patterns in results.values())

            result = {
                "decision": "approve",
                "metadata": {
                    "analysis_results": {
                        "total_patterns": total_patterns,
                        "sequence_patterns": len(results["sequence_patterns"]),
                        "correlation_patterns": len(results["correlation_patterns"]),
                        "frequency_patterns": len(results["frequency_patterns"]),
                        "anomaly_patterns": len(results["anomaly_patterns"]),
                        "optimization_patterns": len(results["optimization_patterns"]),
                    },
                    "message": f"Analyzed {len(history)} entries, found {total_patterns} patterns",
                },
            }

        elif action == "find_similar":
            # 類似パターンを検索
            target_pattern = input_data.get("pattern", {})

            similar = analyzer.find_similar_patterns(target_pattern)

            result = {
                "decision": "approve",
                "metadata": {
                    "similar_patterns": [
                        {
                            "pattern_id": pid,
                            "similarity": sim,
                            "pattern": {
                                "type": analyzer.patterns[pid].pattern_type.value,
                                "description": analyzer.patterns[pid].description,
                                "frequency": analyzer.patterns[pid].frequency,
                                "confidence": analyzer.patterns[pid].confidence,
                            }
                            if pid in analyzer.patterns
                            else None,
                        }
                        for pid, sim in similar
                    ]
                },
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        result = {
            "decision": "reject",
            "message": f"Pattern analysis error: {str(e)}",
            "metadata": {"error": str(e)},
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # テストモード
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # テスト用の履歴データ
        test_history = []

        # シーケンシャルパターンを生成
        for _i in range(10):
            test_history.extend(
                [
                    {
                        "context": {"complexity": "complex", "domains": ["backend"]},
                        "action": {"type": "analyze", "persona": "springfield"},
                        "outcome": {"success": True, "execution_time": 10},
                    },
                    {
                        "context": {"complexity": "complex", "domains": ["backend"]},
                        "action": {"type": "design", "persona": "springfield"},
                        "outcome": {"success": True, "execution_time": 20},
                    },
                    {
                        "context": {"complexity": "complex", "domains": ["backend"]},
                        "action": {"type": "implement", "persona": "krukai"},
                        "outcome": {"success": True, "execution_time": 60},
                    },
                ]
            )

        # 異常パターンを追加
        test_history.append(
            {
                "context": {"complexity": "simple", "domains": ["frontend"]},
                "action": {"type": "implement", "persona": "krukai"},
                "outcome": {"success": True, "execution_time": 300},  # 異常に長い
            }
        )

        test_input = {"action": "analyze", "history": test_history}

        import io

        sys.stdin = io.StringIO(json.dumps(test_input))
        main()
    else:
        main()
