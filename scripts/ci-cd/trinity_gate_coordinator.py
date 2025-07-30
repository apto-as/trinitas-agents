#!/usr/bin/env python3
"""
Trinity Gate Coordinator
三位一体統合判定システム - Springfield, Krukai, Vector の総合評価

Trinity System: "三つの視点が一つになり、最も適切な判断を下します"
"""

import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class TrinityGateCoordinator:
    """三位一体品質ゲート調整システム"""
    
    def __init__(self):
        self.project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
        self.trinity_threshold = {
            "excellent": 90,
            "good": 80, 
            "acceptable": 70,
            "needs_improvement": 60
        }
        
    def load_individual_assessments(self) -> Tuple[Dict, Dict, Dict]:
        """各エージェントの評価結果を読み込み"""
        
        # Springfield Strategic Analysis
        try:
            with open("springfield_analysis.json", "r", encoding='utf-8') as f:
                springfield_data = json.load(f)
        except FileNotFoundError:
            springfield_data = {"scores": {"overall_strategic": 70}, "status": "UNKNOWN"}
            
        # Krukai Quality Assessment
        try:
            with open("krukai_quality.json", "r", encoding='utf-8') as f:
                krukai_data = json.load(f)
        except FileNotFoundError:
            krukai_data = {"metrics": {"overall_technical": 70}, "status": "UNKNOWN"}
            
        # Vector Security Report
        try:
            with open("vector_security.json", "r", encoding='utf-8') as f:
                vector_data = json.load(f)
        except FileNotFoundError:
            vector_data = {"security_metrics": {"security_score": 70}, "status": "UNKNOWN"}
            
        return springfield_data, krukai_data, vector_data
        
    def calculate_trinity_score(self, strategic: float, technical: float, security: float) -> Dict:
        """三位一体統合スコア計算"""
        
        # Base weighted average
        trinity_base = (strategic * 0.35 + technical * 0.35 + security * 0.30)
        
        # Trinity synergy bonus/penalty system
        synergy_factor = self._calculate_synergy_factor(strategic, technical, security)
        trinity_final = trinity_base * synergy_factor
        
        # Ensure score stays within bounds
        trinity_final = max(0, min(100, trinity_final))
        
        return {
            "base_score": trinity_base,
            "synergy_factor": synergy_factor,
            "final_score": trinity_final,
            "individual_scores": {
                "springfield_strategic": strategic,
                "krukai_technical": technical,
                "vector_security": security
            }
        }
        
    def _calculate_synergy_factor(self, strategic: float, technical: float, security: float) -> float:
        """三位一体相乗効果係数計算"""
        scores = [strategic, technical, security]
        
        # Calculate balance factor (penalty for huge imbalances)
        max_score = max(scores)
        min_score = min(scores)
        imbalance = max_score - min_score
        
        if imbalance > 30:
            # Major imbalance penalty
            balance_penalty = 0.85
        elif imbalance > 20:
            # Moderate imbalance penalty
            balance_penalty = 0.90
        elif imbalance > 10:
            # Minor imbalance penalty
            balance_penalty = 0.95
        else:
            # Well balanced bonus
            balance_penalty = 1.05
            
        # Excellence synergy bonus
        excellence_count = sum(1 for score in scores if score >= 90)
        if excellence_count == 3:
            excellence_bonus = 1.10  # All three excellent
        elif excellence_count == 2:
            excellence_bonus = 1.05  # Two excellent
        else:
            excellence_bonus = 1.00
            
        # Critical failure penalty
        critical_failures = sum(1 for score in scores if score < 50)
        if critical_failures > 0:
            failure_penalty = 0.75  # Severe penalty for any critical failure
        else:
            failure_penalty = 1.00
            
        return balance_penalty * excellence_bonus * failure_penalty
        
    def generate_trinity_recommendations(self, trinity_scores: Dict, 
                                       springfield_data: Dict, 
                                       krukai_data: Dict, 
                                       vector_data: Dict) -> List[str]:
        """三位一体統合推奨事項生成"""
        recommendations = []
        scores = trinity_scores["individual_scores"]
        
        # Strategic (Springfield) recommendations
        if scores["springfield_strategic"] < 70:
            recommendations.append(
                "🌸 Springfield: プロジェクト戦略と長期的な持続可能性の改善が必要です。"
                "チーム協調とドキュメント整備に注力しましょう"
            )
            
        # Technical (Krukai) recommendations  
        if scores["krukai_technical"] < 70:
            recommendations.append(
                "⚡ Krukai: 技術的品質基準が不十分です。コード品質の向上と"
                "パフォーマンス最適化を実施してください"
            )
            
        # Security (Vector) recommendations
        if scores["vector_security"] < 70:
            recommendations.append(
                "🛡️ Vector: セキュリティリスクが検出されています。"
                "脆弱性の修正とセキュリティ対策の強化が急務です"
            )
            
        # Trinity integration recommendations
        synergy = trinity_scores["synergy_factor"]
        if synergy < 0.90:
            recommendations.append(
                "🎭 Trinity: 三つの評価領域のバランスが取れていません。"
                "全体的な品質向上のため、劣っている領域に重点的に取り組んでください"
            )
        elif synergy > 1.05:
            recommendations.append(
                "🎭 Trinity: 素晴らしいバランスです！三位一体の相乗効果が発揮されています。"
                "この品質水準を維持してください"
            )
            
        # Add specific recommendations from individual agents
        for agent_data in [springfield_data, krukai_data, vector_data]:
            agent_recommendations = agent_data.get("recommendations", [])
            recommendations.extend(agent_recommendations[:2])  # Limit to top recommendations
            
        return recommendations
        
    def determine_gate_decision(self, trinity_scores: Dict) -> Dict:
        """ゲート通過判定"""
        final_score = trinity_scores["final_score"]
        
        if final_score >= self.trinity_threshold["excellent"]:
            decision = "APPROVE_EXCELLENT"
            gate_message = "🎉 Trinity Gate: 卓越した品質です！自信を持ってデプロイしてください"
            color = "🟢"
        elif final_score >= self.trinity_threshold["good"]:
            decision = "APPROVE_GOOD"
            gate_message = "✅ Trinity Gate: 良好な品質です。デプロイを承認します"
            color = "🟢"
        elif final_score >= self.trinity_threshold["acceptable"]:
            decision = "APPROVE_WITH_CONDITIONS"
            gate_message = "🟡 Trinity Gate: 条件付き承認。推奨事項の実施をお願いします"
            color = "🟡"
        elif final_score >= self.trinity_threshold["needs_improvement"]:
            decision = "NEEDS_IMPROVEMENT"
            gate_message = "🟠 Trinity Gate: 改善が必要です。重要な問題を修正してから再評価してください"
            color = "🟠"
        else:
            decision = "REJECT"
            gate_message = "🔴 Trinity Gate: 品質基準を満たしていません。大幅な改善が必要です"
            color = "🔴"
            
        return {
            "decision": decision,
            "message": gate_message,
            "color": color,
            "deployable": decision in ["APPROVE_EXCELLENT", "APPROVE_GOOD", "APPROVE_WITH_CONDITIONS"]
        }
        
    def generate_trinity_summary(self, trinity_scores: Dict, gate_decision: Dict, 
                               recommendations: List[str]) -> str:
        """Trinity統合サマリー生成"""
        
        scores = trinity_scores["individual_scores"]
        final_score = trinity_scores["final_score"]
        
        summary = f"""# 🎭 Trinity Quality Gate Report
        
## 総合評価
{gate_decision['color']} **{gate_decision['decision']}** - Score: {final_score:.1f}/100

{gate_decision['message']}

## 個別評価
### 🌸 Springfield (Strategic): {scores['springfield_strategic']:.1f}/100
- プロジェクト構造、チーム協調、長期的持続可能性の評価

### ⚡ Krukai (Technical): {scores['krukai_technical']:.1f}/100  
- コード品質、パフォーマンス、技術的卓越性の評価

### 🛡️ Vector (Security): {scores['vector_security']:.1f}/100
- セキュリティ、リスク分析、脆弱性評価

## 三位一体相乗効果
- **Base Score**: {trinity_scores['base_score']:.1f}/100
- **Synergy Factor**: {trinity_scores['synergy_factor']:.2f}
- **Final Score**: {final_score:.1f}/100

## 推奨事項
"""
        
        for i, rec in enumerate(recommendations[:8], 1):  # Limit recommendations
            summary += f"{i}. {rec}\\n"
            
        summary += f"""
## 次のステップ
{"✅ **デプロイ可能**: 現在の品質水準でリリースできます" if gate_decision['deployable'] else "❌ **改善必要**: 推奨事項を実施してから再評価してください"}

---
*Generated by Trinity Gate Coordinator at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return summary
        
    def coordinate_trinity_gate(self, strategic_score: float, technical_score: float, 
                              security_score: float) -> Dict:
        """Trinity Gate メイン調整処理"""
        print("🎭 Trinity Coordinator: 三位一体統合評価を開始します...")
        
        # Load detailed assessments
        springfield_data, krukai_data, vector_data = self.load_individual_assessments()
        
        # Calculate Trinity integrated score
        trinity_scores = self.calculate_trinity_score(strategic_score, technical_score, security_score)
        
        # Generate integrated recommendations
        recommendations = self.generate_trinity_recommendations(
            trinity_scores, springfield_data, krukai_data, vector_data
        )
        
        # Make gate decision
        gate_decision = self.determine_gate_decision(trinity_scores)
        
        # Generate summary report
        trinity_summary = self.generate_trinity_summary(trinity_scores, gate_decision, recommendations)
        
        # Compile complete report
        complete_report = {
            "trinity_coordinator": "Trinity Gate System v2.0",
            "timestamp": datetime.now().isoformat(),
            "trinity_scores": trinity_scores,
            "gate_decision": gate_decision,
            "recommendations": recommendations,
            "individual_assessments": {
                "springfield": springfield_data,
                "krukai": krukai_data, 
                "vector": vector_data
            },
            "summary": trinity_summary
        }
        
        # Save results
        with open("trinity_gate_result.json", "w", encoding='utf-8') as f:
            json.dump(complete_report, f, indent=2, ensure_ascii=False)
            
        with open("trinity-summary.md", "w", encoding='utf-8') as f:
            f.write(trinity_summary)
            
        # Final Trinity messages
        print(f"🌸 Springfield: 戦略的評価完了 ({strategic_score:.1f}/100)")
        print(f"⚡ Krukai: 技術的評価完了 ({technical_score:.1f}/100)")
        print(f"🛡️ Vector: セキュリティ評価完了 ({security_score:.1f}/100)")
        print(f"🎭 Trinity: 統合評価完了 ({trinity_scores['final_score']:.1f}/100)")
        print(gate_decision['message'])
        
        # Set exit code based on gate decision
        if gate_decision['decision'] == "REJECT":
            exit(1)
        elif gate_decision['decision'] == "NEEDS_IMPROVEMENT":
            exit(2)
        else:
            exit(0)
            
        return complete_report


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="Trinity Gate Coordinator")
    parser.add_argument("--strategic", type=float, required=True, help="Springfield strategic score")
    parser.add_argument("--technical", type=float, required=True, help="Krukai technical score")
    parser.add_argument("--security", type=float, required=True, help="Vector security score")
    
    args = parser.parse_args()
    
    coordinator = TrinityGateCoordinator()
    coordinator.coordinate_trinity_gate(args.strategic, args.technical, args.security)


if __name__ == "__main__":
    main()