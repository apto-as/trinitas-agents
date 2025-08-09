#!/usr/bin/env python3
"""
conflict_resolver.py - ペルソナ間の対立解決メカニズム
異なる視点や判断の相違を建設的に解決
"""

import json
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConflictType(Enum):
    """対立のタイプ"""

    TECHNICAL = "technical"  # 技術的見解の相違
    STRATEGIC = "strategic"  # 戦略的方向性の相違
    PRIORITY = "priority"  # 優先順位の相違
    SECURITY = "security"  # セキュリティ懸念
    PERFORMANCE = "performance"  # パフォーマンス要求の相違
    COMPLEXITY = "complexity"  # 複雑性への対処法の相違


@dataclass
class Conflict:
    """対立の詳細"""

    conflict_id: str
    type: ConflictType
    personas: List[str]
    positions: Dict[str, Dict[str, Any]]  # 各ペルソナの立場
    severity: int  # 1-10の深刻度
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    """対立解決の結果"""

    resolution_id: str
    conflict_id: str
    method: str
    decision: str
    rationale: str
    compromises: Dict[str, str] = field(default_factory=dict)
    action_items: List[str] = field(default_factory=list)


class ConflictResolver:
    """対立解決エンジン"""

    def __init__(self):
        # 解決戦略
        self.resolution_strategies = {
            ConflictType.TECHNICAL: self._resolve_technical_conflict,
            ConflictType.STRATEGIC: self._resolve_strategic_conflict,
            ConflictType.PRIORITY: self._resolve_priority_conflict,
            ConflictType.SECURITY: self._resolve_security_conflict,
            ConflictType.PERFORMANCE: self._resolve_performance_conflict,
            ConflictType.COMPLEXITY: self._resolve_complexity_conflict,
        }

        # ペルソナの専門性重み
        self.expertise_weights = {
            "springfield": {
                ConflictType.STRATEGIC: 0.9,
                ConflictType.COMPLEXITY: 0.8,
                ConflictType.PRIORITY: 0.85,
            },
            "krukai": {
                ConflictType.TECHNICAL: 0.95,
                ConflictType.PERFORMANCE: 0.9,
                ConflictType.COMPLEXITY: 0.85,
            },
            "vector": {
                ConflictType.SECURITY: 0.98,
                ConflictType.TECHNICAL: 0.85,
                ConflictType.PRIORITY: 0.7,
            },
            "centaureissi": {
                ConflictType.TECHNICAL: 0.88,
                ConflictType.STRATEGIC: 0.85,
                ConflictType.COMPLEXITY: 0.9,
            },
        }

    def analyze_conflict(
        self, positions: Dict[str, Dict[str, Any]]
    ) -> Optional[Conflict]:
        """対立を分析して構造化"""
        if len(positions) < 2:
            return None

        # 意見の相違を検出
        decisions = {p: pos.get("decision", "neutral") for p, pos in positions.items()}
        unique_decisions = set(decisions.values())

        if len(unique_decisions) <= 1:
            return None  # 対立なし

        # 対立のタイプを判定
        conflict_type = self._determine_conflict_type(positions)

        # 深刻度を計算
        severity = self._calculate_severity(positions, conflict_type)

        return Conflict(
            conflict_id=f"conflict_{int(time.time())}",
            type=conflict_type,
            personas=list(positions.keys()),
            positions=positions,
            severity=severity,
            context=self._extract_context(positions),
        )

    def resolve_conflict(self, conflict: Conflict) -> Resolution:
        """対立を解決"""
        # 対立タイプに応じた解決戦略を選択
        strategy = self.resolution_strategies.get(
            conflict.type, self._default_resolution_strategy
        )

        # 解決を実行
        resolution = strategy(conflict)

        # 解決後の検証
        self._validate_resolution(resolution, conflict)

        return resolution

    def _determine_conflict_type(
        self, positions: Dict[str, Dict[str, Any]]
    ) -> ConflictType:
        """対立のタイプを判定"""
        # 各ポジションから対立の主要因を抽出
        concerns = []
        for _persona, position in positions.items():
            concerns.extend(position.get("concerns", []))

        # キーワードベースの判定
        if any("security" in c.lower() for c in concerns):
            return ConflictType.SECURITY
        elif any("performance" in c.lower() for c in concerns):
            return ConflictType.PERFORMANCE
        elif any(
            "technical" in c.lower() or "implementation" in c.lower() for c in concerns
        ):
            return ConflictType.TECHNICAL
        elif any(
            "strategy" in c.lower() or "architecture" in c.lower() for c in concerns
        ):
            return ConflictType.STRATEGIC
        elif any("priority" in c.lower() or "urgency" in c.lower() for c in concerns):
            return ConflictType.PRIORITY
        else:
            return ConflictType.COMPLEXITY

    def _calculate_severity(
        self, positions: Dict[str, Dict[str, Any]], conflict_type: ConflictType
    ) -> int:
        """対立の深刻度を計算"""
        base_severity = 5

        # Vectorがセキュリティで反対している場合は深刻
        if (
            conflict_type == ConflictType.SECURITY
            and positions.get("vector", {}).get("decision") == "reject"
        ):
            base_severity = 9

        # 全員が異なる意見の場合
        decisions = set(p.get("decision") for p in positions.values())
        if len(decisions) == len(positions):
            base_severity += 2

        # 重要度が高いと各ペルソナが判断している場合
        importance_sum = sum(p.get("importance", 5) for p in positions.values())
        avg_importance = importance_sum / len(positions)
        if avg_importance > 7:
            base_severity += 1

        return min(10, base_severity)

    def _extract_context(self, positions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """対立のコンテキストを抽出"""
        context = {"task_type": None, "urgency": "normal", "impact_scope": "moderate"}

        # 各ポジションからコンテキスト情報を集約
        for position in positions.values():
            if "task_type" in position and not context["task_type"]:
                context["task_type"] = position["task_type"]

            if position.get("urgency") == "high":
                context["urgency"] = "high"

            if position.get("impact") == "critical":
                context["impact_scope"] = "critical"

        return context

    def _resolve_technical_conflict(self, conflict: Conflict) -> Resolution:
        """技術的対立の解決"""
        # 技術的専門性の重みを考慮
        weighted_scores = {}

        for persona, position in conflict.positions.items():
            weight = self.expertise_weights.get(persona, {}).get(
                ConflictType.TECHNICAL, 0.5
            )

            # 技術的根拠の強さを評価
            technical_score = self._evaluate_technical_position(position)
            weighted_scores[persona] = technical_score * weight

        # 最も説得力のある技術的提案を選択
        winner = max(weighted_scores.items(), key=lambda x: x[1])[0]
        winning_position = conflict.positions[winner]

        # 他の視点も部分的に取り入れる
        compromises = {}
        action_items = []

        for persona, position in conflict.positions.items():
            if persona != winner:
                # 有効な懸念事項を抽出
                valid_concerns = self._extract_valid_concerns(position)
                if valid_concerns:
                    compromises[persona] = (
                        f"Address concerns: {', '.join(valid_concerns)}"
                    )
                    action_items.extend(
                        [
                            f"Implement safeguards for {concern}"
                            for concern in valid_concerns[:2]
                        ]
                    )

        return Resolution(
            resolution_id=f"res_{conflict.conflict_id}",
            conflict_id=conflict.conflict_id,
            method="weighted_technical_expertise",
            decision=winning_position.get("proposal", ""),
            rationale=f"Based on {winner}'s technical expertise and feasibility analysis",
            compromises=compromises,
            action_items=action_items,
        )

    def _resolve_strategic_conflict(self, conflict: Conflict) -> Resolution:
        """戦略的対立の解決"""
        # Springfieldの意見を重視しつつ、他の視点も統合
        springfield_position = conflict.positions.get("springfield", {})

        if springfield_position and springfield_position.get("decision") != "reject":
            base_decision = springfield_position.get("proposal", "")

            # 他のペルソナからの建設的な提案を統合
            enhancements = []
            for persona, position in conflict.positions.items():
                if persona != "springfield" and position.get("decision") != "reject":
                    if "enhancement" in position:
                        enhancements.append(position["enhancement"])

            return Resolution(
                resolution_id=f"res_{conflict.conflict_id}",
                conflict_id=conflict.conflict_id,
                method="strategic_leadership_with_consultation",
                decision=base_decision,
                rationale="Springfield's strategic vision enhanced by team insights",
                compromises={
                    p: "Concerns addressed in implementation phase"
                    for p in conflict.personas
                    if p != "springfield"
                },
                action_items=enhancements[:3],
            )
        else:
            # Springfieldが反対の場合は再検討
            return self._facilitate_discussion(conflict)

    def _resolve_security_conflict(self, conflict: Conflict) -> Resolution:
        """セキュリティ対立の解決"""
        vector_position = conflict.positions.get("vector", {})

        # Vectorがセキュリティ上の懸念を示した場合は最優先
        if vector_position.get("decision") == "reject":
            security_concerns = vector_position.get("security_issues", [])

            return Resolution(
                resolution_id=f"res_{conflict.conflict_id}",
                conflict_id=conflict.conflict_id,
                method="security_veto",
                decision="Postpone until security concerns are addressed",
                rationale="Vector identified critical security vulnerabilities",
                compromises={
                    p: "Must address security before proceeding"
                    for p in conflict.personas
                },
                action_items=[
                    f"Fix security issue: {issue}" for issue in security_concerns
                ],
            )
        else:
            # セキュリティは問題ないが、他の対立がある場合
            return self._balance_security_with_progress(conflict)

    def _resolve_priority_conflict(self, conflict: Conflict) -> Resolution:
        """優先順位の対立を解決"""
        # 各ペルソナの優先順位提案を収集
        priority_proposals = {}
        for persona, position in conflict.positions.items():
            if "priorities" in position:
                priority_proposals[persona] = position["priorities"]

        # 統合された優先順位リストを作成
        merged_priorities = self._merge_priorities(priority_proposals)

        return Resolution(
            resolution_id=f"res_{conflict.conflict_id}",
            conflict_id=conflict.conflict_id,
            method="priority_synthesis",
            decision=f"Merged priority list: {merged_priorities[:5]}",
            rationale="Balanced priorities based on impact and urgency",
            compromises={
                p: "Some priorities deferred to next phase" for p in conflict.personas
            },
            action_items=merged_priorities[:3],
        )

    def _resolve_performance_conflict(self, conflict: Conflict) -> Resolution:
        """パフォーマンス対立の解決"""
        # Krukaiの技術的判断を重視
        krukai_position = conflict.positions.get("krukai", {})

        if krukai_position:
            performance_target = krukai_position.get("performance_target", {})

            # 現実的な妥協点を見つける
            adjusted_targets = self._adjust_performance_targets(
                performance_target, conflict.positions
            )

            return Resolution(
                resolution_id=f"res_{conflict.conflict_id}",
                conflict_id=conflict.conflict_id,
                method="performance_optimization_balance",
                decision=f"Adjusted performance targets: {adjusted_targets}",
                rationale="Balance between ideal performance and practical constraints",
                compromises={
                    "krukai": "Slightly relaxed performance for maintainability",
                    "springfield": "Phased optimization approach",
                },
                action_items=[
                    "Implement core optimizations first",
                    "Monitor and iterate on performance",
                    "Consider future hardware improvements",
                ],
            )

        return self._default_resolution_strategy(conflict)

    def _resolve_complexity_conflict(self, conflict: Conflict) -> Resolution:
        """複雑性に関する対立の解決"""
        # Centaureissiの深い分析を活用
        centaureissi_position = conflict.positions.get("centaureissi", {})

        if centaureissi_position:
            complexity_analysis = centaureissi_position.get("complexity_analysis", {})

            # 段階的アプローチを提案
            phased_approach = self._create_phased_approach(
                complexity_analysis, conflict.positions
            )

            return Resolution(
                resolution_id=f"res_{conflict.conflict_id}",
                conflict_id=conflict.conflict_id,
                method="phased_complexity_management",
                decision=f"Phased approach: {phased_approach}",
                rationale="Manage complexity through incremental implementation",
                compromises={
                    p: "Complexity addressed in manageable phases"
                    for p in conflict.personas
                },
                action_items=phased_approach[:3],
            )

        return self._facilitate_discussion(conflict)

    def _default_resolution_strategy(self, conflict: Conflict) -> Resolution:
        """デフォルトの解決戦略"""
        return self._facilitate_discussion(conflict)

    def _facilitate_discussion(self, conflict: Conflict) -> Resolution:
        """話し合いによる解決"""
        # 共通点を見つける
        common_ground = self._find_common_ground(conflict.positions)

        # 妥協案を作成
        compromise_proposal = self._create_compromise(conflict.positions, common_ground)

        return Resolution(
            resolution_id=f"res_{conflict.conflict_id}",
            conflict_id=conflict.conflict_id,
            method="facilitated_discussion",
            decision=compromise_proposal,
            rationale="Consensus through structured discussion",
            compromises={
                p: "Partial implementation of proposal" for p in conflict.personas
            },
            action_items=[
                "Pilot implementation",
                "Regular review and adjustment",
                "Gather metrics for future decisions",
            ],
        )

    def _evaluate_technical_position(self, position: Dict[str, Any]) -> float:
        """技術的立場の評価"""
        score = 0.5  # ベーススコア

        # 技術的根拠の存在
        if "technical_rationale" in position:
            score += 0.2

        # 実装の詳細度
        if "implementation_details" in position:
            score += 0.15

        # テスト計画
        if "test_plan" in position:
            score += 0.1

        # 既存システムとの互換性
        if position.get("compatibility_checked", False):
            score += 0.05

        return min(1.0, score)

    def _extract_valid_concerns(self, position: Dict[str, Any]) -> List[str]:
        """有効な懸念事項を抽出"""
        concerns = position.get("concerns", [])

        # 具体的で実装可能な懸念のみを選択
        valid_concerns = []
        for concern in concerns:
            if isinstance(concern, str) and len(concern) > 10:
                # 単なる不満ではなく、具体的な懸念
                if any(
                    keyword in concern.lower()
                    for keyword in [
                        "security",
                        "performance",
                        "maintenance",
                        "compatibility",
                        "scalability",
                    ]
                ):
                    valid_concerns.append(concern)

        return valid_concerns[:3]  # 最大3つ

    def _balance_security_with_progress(self, conflict: Conflict) -> Resolution:
        """セキュリティと進捗のバランス"""
        # セキュリティを考慮しつつ前進する方法を見つける
        action_items = [
            "Implement security review at each milestone",
            "Add automated security testing",
            "Create security exception handling",
        ]

        return Resolution(
            resolution_id=f"res_{conflict.conflict_id}",
            conflict_id=conflict.conflict_id,
            method="security_aware_progression",
            decision="Proceed with enhanced security measures",
            rationale="Balance security with project progress",
            compromises={
                "vector": "Additional security checkpoints added",
                "others": "Slight delay for security implementation",
            },
            action_items=action_items,
        )

    def _merge_priorities(self, proposals: Dict[str, List[str]]) -> List[str]:
        """優先順位リストをマージ"""
        # 各提案での出現頻度と位置を考慮
        priority_scores = {}

        for _persona, priorities in proposals.items():
            weight = 1.0 / (len(proposals))  # 各ペルソナの重み

            for i, priority in enumerate(priorities):
                score = weight * (len(priorities) - i)  # 位置による重み

                if priority in priority_scores:
                    priority_scores[priority] += score
                else:
                    priority_scores[priority] = score

        # スコアでソート
        sorted_priorities = sorted(
            priority_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [p[0] for p in sorted_priorities]

    def _adjust_performance_targets(
        self, ideal_targets: Dict[str, Any], positions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """パフォーマンス目標を調整"""
        adjusted = ideal_targets.copy()

        # 各ペルソナの懸念を考慮
        for _persona, position in positions.items():
            if "performance_concerns" in position:
                for concern in position["performance_concerns"]:
                    # 懸念に基づいて目標を現実的に調整
                    if "latency" in concern and "latency" in adjusted:
                        adjusted["latency"] = adjusted["latency"] * 1.2
                    elif "memory" in concern and "memory" in adjusted:
                        adjusted["memory"] = adjusted["memory"] * 1.1

        return adjusted

    def _create_phased_approach(
        self, complexity_analysis: Dict[str, Any], positions: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """段階的アプローチを作成"""
        phases = []

        # Phase 1: 基本実装
        phases.append("Phase 1: Core functionality with simple architecture")

        # Phase 2: 最適化
        if any("optimization" in str(p) for p in positions.values()):
            phases.append("Phase 2: Performance optimization and refactoring")

        # Phase 3: 拡張
        phases.append("Phase 3: Advanced features and scalability")

        # Phase 4: 統合
        if len(positions) > 3:
            phases.append("Phase 4: Full integration and polish")

        return phases

    def _find_common_ground(self, positions: Dict[str, Dict[str, Any]]) -> List[str]:
        """共通点を見つける"""
        common_ground = []

        # 全員が同意している点を探す
        all_goals = []
        for position in positions.values():
            all_goals.extend(position.get("goals", []))

        # 複数回出現する目標は共通の関心事
        goal_counts = {}
        for goal in all_goals:
            goal_counts[goal] = goal_counts.get(goal, 0) + 1

        for goal, count in goal_counts.items():
            if count >= len(positions) * 0.6:  # 60%以上が言及
                common_ground.append(goal)

        return common_ground

    def _create_compromise(
        self, positions: Dict[str, Dict[str, Any]], common_ground: List[str]
    ) -> str:
        """妥協案を作成"""
        if common_ground:
            base = f"Focus on common goals: {', '.join(common_ground[:3])}"
        else:
            base = "Incremental approach with regular reviews"

        # 各ペルソナの主要な要求を部分的に含める
        additions = []
        for persona, position in positions.items():
            if "key_requirement" in position:
                additions.append(f"Include {persona}'s requirement partially")

        if additions:
            return f"{base}. {'. '.join(additions[:2])}"

        return base

    def _validate_resolution(self, resolution: Resolution, conflict: Conflict):
        """解決の妥当性を検証"""
        # セキュリティ対立でVectorの懸念が無視されていないか
        if conflict.type == ConflictType.SECURITY:
            if (
                "vector" in conflict.positions
                and conflict.positions["vector"].get("decision") == "reject"
            ):
                if "security" not in resolution.decision.lower():
                    # セキュリティ対策を追加
                    resolution.action_items.insert(
                        0, "Priority: Address Vector's security concerns"
                    )




def main():
    """Claude Code Hook として実行"""
    input_data = json.loads(sys.stdin.read())

    action = input_data.get("action", "resolve")

    try:
        resolver = ConflictResolver()

        if action == "analyze":
            # 対立を分析
            positions = input_data.get("positions", {})
            conflict = resolver.analyze_conflict(positions)

            if conflict:
                result = {
                    "decision": "approve",
                    "metadata": {
                        "conflict_detected": True,
                        "conflict": {
                            "id": conflict.conflict_id,
                            "type": conflict.type.value,
                            "severity": conflict.severity,
                            "personas": conflict.personas,
                        },
                    },
                }
            else:
                result = {
                    "decision": "approve",
                    "metadata": {
                        "conflict_detected": False,
                        "message": "No significant conflict detected",
                    },
                }

        elif action == "resolve":
            # 対立を解決
            positions = input_data.get("positions", {})
            conflict = resolver.analyze_conflict(positions)

            if conflict:
                resolution = resolver.resolve_conflict(conflict)

                result = {
                    "decision": "approve",
                    "metadata": {
                        "conflict": {
                            "type": conflict.type.value,
                            "severity": conflict.severity,
                        },
                        "resolution": {
                            "method": resolution.method,
                            "decision": resolution.decision,
                            "rationale": resolution.rationale,
                            "compromises": resolution.compromises,
                            "action_items": resolution.action_items,
                        },
                    },
                }
            else:
                result = {
                    "decision": "approve",
                    "metadata": {"message": "No conflict to resolve"},
                }

        else:
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        result = {
            "decision": "reject",
            "message": f"Conflict resolution error: {str(e)}",
            "metadata": {"error": str(e)},
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
