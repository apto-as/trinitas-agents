#!/usr/bin/env python3
"""
collaboration_patterns.py - ペルソナ間の協調パターン定義
各ペルソナの協調関係と相互作用を管理
"""

import json
import sys
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class CollaborationType(Enum):
    """協調タイプ"""
    SEQUENTIAL = "sequential"      # 順次実行
    PARALLEL = "parallel"          # 並列実行
    HIERARCHICAL = "hierarchical"  # 階層的実行
    CONSENSUS = "consensus"        # 合意形成
    SYNTHESIS = "synthesis"        # 統合・融合

@dataclass
class CollaborationPattern:
    """協調パターン"""
    pattern_id: str
    name: str
    type: CollaborationType
    personas: List[str]
    description: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)

class CollaborationEngine:
    """ペルソナ協調エンジン"""
    
    def __init__(self):
        # 事前定義された協調パターン
        self.patterns = {
            "trinity_consensus": CollaborationPattern(
                pattern_id="trinity_consensus",
                name="三位一体合意形成",
                type=CollaborationType.CONSENSUS,
                personas=["springfield", "krukai", "vector"],
                description="三つの視点から総合的に判断",
                constraints={
                    "min_agreement": 2,  # 最低2人の合意が必要
                    "veto_power": ["vector"]  # Vectorは拒否権を持つ
                },
                success_criteria=[
                    "戦略的妥当性（Springfield）",
                    "技術的実現可能性（Krukai）",
                    "セキュリティ確保（Vector）"
                ]
            ),
            
            "deep_research_flow": CollaborationPattern(
                pattern_id="deep_research_flow",
                name="深層研究フロー",
                type=CollaborationType.SEQUENTIAL,
                personas=["centaureissi", "springfield", "krukai", "vector"],
                description="研究から実装までの完全フロー",
                constraints={
                    "order": ["centaureissi", "springfield", "krukai", "vector"],
                    "dependency": True
                },
                success_criteria=[
                    "包括的研究完了（Centaureissi）",
                    "アーキテクチャ設計（Springfield）",
                    "実装完了（Krukai）",
                    "セキュリティ検証（Vector）"
                ]
            ),
            
            "parallel_analysis": CollaborationPattern(
                pattern_id="parallel_analysis",
                name="並列分析",
                type=CollaborationType.PARALLEL,
                personas=["springfield", "krukai", "vector", "centaureissi"],
                description="全ペルソナが並列で分析",
                constraints={
                    "max_time": 300,  # 5分以内
                    "sync_points": ["start", "mid", "end"]
                },
                success_criteria=[
                    "全ペルソナの分析完了",
                    "結果の統合成功"
                ]
            ),
            
            "quality_gate": CollaborationPattern(
                pattern_id="quality_gate",
                name="品質ゲート",
                type=CollaborationType.HIERARCHICAL,
                personas=["krukai", "vector"],
                description="品質とセキュリティの二重チェック",
                constraints={
                    "order": ["krukai", "vector"],
                    "fail_fast": True  # 一つでも失敗したら中断
                },
                success_criteria=[
                    "コード品質基準達成（Krukai）",
                    "セキュリティ基準達成（Vector）"
                ]
            ),
            
            "knowledge_synthesis": CollaborationPattern(
                pattern_id="knowledge_synthesis",
                name="知識統合",
                type=CollaborationType.SYNTHESIS,
                personas=["centaureissi", "springfield"],
                description="研究結果と戦略的視点の統合",
                constraints={
                    "integration_method": "weighted_merge",
                    "weights": {
                        "centaureissi": 0.6,  # 研究重視
                        "springfield": 0.4    # 実用性重視
                    }
                },
                success_criteria=[
                    "研究の深さと実用性のバランス",
                    "実装可能な提案の生成"
                ]
            )
        }
        
        # ペルソナ間の相性マトリックス
        self.compatibility_matrix = {
            ("springfield", "krukai"): 0.85,      # 良好な協力関係
            ("springfield", "vector"): 0.90,      # 信頼関係
            ("springfield", "centaureissi"): 0.88, # 知的な協調
            ("krukai", "vector"): 0.75,           # 時に対立するが補完的
            ("krukai", "centaureissi"): 0.80,     # 技術的な理解
            ("vector", "centaureissi"): 0.78      # 慎重な協力
        }
        
    def select_pattern(self, context: Dict[str, Any]) -> Optional[CollaborationPattern]:
        """コンテキストに基づいて最適な協調パターンを選択"""
        task_type = context.get("task_type", "")
        complexity = context.get("complexity", "normal")
        urgency = context.get("urgency", "normal")
        
        # タスクタイプに基づく選択
        if task_type == "research":
            if complexity == "complex":
                return self.patterns["deep_research_flow"]
            else:
                return self.patterns["knowledge_synthesis"]
        
        elif task_type == "implementation":
            if urgency == "high":
                return self.patterns["parallel_analysis"]
            else:
                return self.patterns["trinity_consensus"]
        
        elif task_type == "validation":
            return self.patterns["quality_gate"]
        
        # デフォルトは三位一体合意形成
        return self.patterns["trinity_consensus"]
    
    def calculate_synergy(self, personas: List[str]) -> float:
        """ペルソナ間のシナジー効果を計算"""
        if len(personas) < 2:
            return 1.0
        
        total_compatibility = 0.0
        pair_count = 0
        
        for i in range(len(personas)):
            for j in range(i + 1, len(personas)):
                pair = tuple(sorted([personas[i], personas[j]]))
                compatibility = self.compatibility_matrix.get(pair, 0.7)
                total_compatibility += compatibility
                pair_count += 1
        
        # 平均相性スコア
        avg_compatibility = total_compatibility / pair_count if pair_count > 0 else 0.7
        
        # チームサイズによるボーナス（3-4人が最適）
        size_bonus = 1.0
        if len(personas) == 3:
            size_bonus = 1.1
        elif len(personas) == 4:
            size_bonus = 1.15
        elif len(personas) > 4:
            size_bonus = 0.9  # 多すぎると効率が下がる
        
        return avg_compatibility * size_bonus
    
    def resolve_conflicts(self, opinions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """ペルソナ間の意見の相違を解決"""
        # 各ペルソナの意見を集計
        decisions = {}
        for persona, opinion in opinions.items():
            decision = opinion.get("decision", "neutral")
            decisions[persona] = decision
        
        # 多数決の基本結果
        decision_counts = {}
        for decision in decisions.values():
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        # Vectorの拒否権チェック
        if decisions.get("vector") == "reject":
            return {
                "final_decision": "reject",
                "reason": "Security concerns raised by Vector",
                "details": opinions.get("vector", {})
            }
        
        # 最も多い決定を選択
        final_decision = max(decision_counts.items(), key=lambda x: x[1])[0]
        
        # 合意形成の詳細
        return {
            "final_decision": final_decision,
            "consensus_level": decision_counts.get(final_decision, 0) / len(decisions),
            "individual_decisions": decisions,
            "resolution_method": "weighted_consensus"
        }
    
    def generate_collaboration_plan(self, pattern: CollaborationPattern, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """協調実行計画を生成"""
        plan = {
            "pattern": pattern.pattern_id,
            "type": pattern.type.value,
            "steps": []
        }
        
        if pattern.type == CollaborationType.SEQUENTIAL:
            # 順次実行計画
            order = pattern.constraints.get("order", pattern.personas)
            for i, persona in enumerate(order):
                step = {
                    "step": i + 1,
                    "persona": persona,
                    "action": self._get_persona_action(persona, context),
                    "dependencies": [order[i-1]] if i > 0 else []
                }
                plan["steps"].append(step)
        
        elif pattern.type == CollaborationType.PARALLEL:
            # 並列実行計画
            sync_points = pattern.constraints.get("sync_points", [])
            for persona in pattern.personas:
                step = {
                    "step": 1,  # 全て同じステップ
                    "persona": persona,
                    "action": self._get_persona_action(persona, context),
                    "sync_points": sync_points
                }
                plan["steps"].append(step)
        
        elif pattern.type == CollaborationType.CONSENSUS:
            # 合意形成計画
            # 1. 各ペルソナが分析
            for i, persona in enumerate(pattern.personas):
                step = {
                    "step": 1,
                    "persona": persona,
                    "action": "analyze",
                    "output": "opinion"
                }
                plan["steps"].append(step)
            
            # 2. 合意形成
            plan["steps"].append({
                "step": 2,
                "action": "consensus_building",
                "participants": pattern.personas,
                "method": "weighted_voting"
            })
        
        return plan
    
    def _get_persona_action(self, persona: str, context: Dict[str, Any]) -> str:
        """ペルソナに応じたアクションを決定"""
        task_type = context.get("task_type", "")
        
        action_map = {
            "springfield": {
                "research": "strategic_analysis",
                "implementation": "architecture_design",
                "validation": "holistic_review"
            },
            "krukai": {
                "research": "technical_analysis",
                "implementation": "code_implementation",
                "validation": "quality_check"
            },
            "vector": {
                "research": "risk_analysis",
                "implementation": "security_review",
                "validation": "vulnerability_scan"
            },
            "centaureissi": {
                "research": "deep_investigation",
                "implementation": "knowledge_integration",
                "validation": "comprehensive_analysis"
            }
        }
        
        return action_map.get(persona, {}).get(task_type, "analyze")

def main():
    """Claude Code Hook として実行"""
    input_data = json.loads(sys.stdin.read())
    
    action = input_data.get("action", "select_pattern")
    
    try:
        engine = CollaborationEngine()
        
        if action == "select_pattern":
            # 最適な協調パターンを選択
            context = input_data.get("context", {})
            pattern = engine.select_pattern(context)
            
            if pattern:
                result = {
                    "decision": "approve",
                    "metadata": {
                        "selected_pattern": {
                            "id": pattern.pattern_id,
                            "name": pattern.name,
                            "type": pattern.type.value,
                            "personas": pattern.personas
                        },
                        "collaboration_plan": engine.generate_collaboration_plan(pattern, context)
                    }
                }
            else:
                result = {
                    "decision": "reject",
                    "message": "No suitable collaboration pattern found"
                }
        
        elif action == "calculate_synergy":
            # シナジー効果を計算
            personas = input_data.get("personas", [])
            synergy = engine.calculate_synergy(personas)
            
            result = {
                "decision": "approve",
                "metadata": {
                    "synergy_score": synergy,
                    "team_effectiveness": "high" if synergy > 0.9 else "medium" if synergy > 0.7 else "low"
                }
            }
        
        elif action == "resolve_conflicts":
            # 意見の相違を解決
            opinions = input_data.get("opinions", {})
            resolution = engine.resolve_conflicts(opinions)
            
            result = {
                "decision": "approve",
                "metadata": {
                    "conflict_resolution": resolution
                }
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    except Exception as e:
        result = {
            "decision": "reject",
            "message": f"Collaboration pattern error: {str(e)}",
            "metadata": {
                "error": str(e)
            }
        }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()