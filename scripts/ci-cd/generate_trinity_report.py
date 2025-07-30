#!/usr/bin/env python3
"""
Trinity Report Generator
三位一体品質レポート生成システム

HTML形式の詳細な分析レポートを生成
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class TrinityReportGenerator:
    """Trinity統合レポート生成器"""
    
    def __init__(self):
        self.project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
        self.template = self._get_html_template()
        
    def _get_html_template(self) -> str:
        """HTMLレポートテンプレート"""
        return """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trinity Quality Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .trinity-logo {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .content {
            padding: 30px;
        }
        .agent-section {
            margin: 30px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .springfield { background: linear-gradient(135deg, #a8e6cf, #88d8a3); }
        .krukai { background: linear-gradient(135deg, #ffd93d, #ffcd3c); }
        .vector { background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; }
        .trinity { background: linear-gradient(135deg, #4ecdc4, #44a08d); color: white; }
        
        .score-circle {
            display: inline-block;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            text-align: center;
            line-height: 80px;
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px;
        }
        .recommendations {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .recommendation-item {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-excellent { background: #28a745; color: white; }
        .status-good { background: #17a2b8; color: white; }
        .status-warning { background: #ffc107; color: black; }
        .status-danger { background: #dc3545; color: white; }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="trinity-logo">🎭 🌸 ⚡ 🛡️</div>
            <h1>Trinity Quality Analysis Report</h1>
            <p>Three Minds, One Purpose, Infinite Quality</p>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="content">
            <!-- Trinity Overall Status -->
            <div class="agent-section trinity">
                <h2>🎭 Trinity Gate Decision</h2>
                <div style="text-align: center;">
                    <div class="score-circle">{trinity_score}</div>
                    <div class="status-badge {status_class}">{gate_decision}</div>
                </div>
                <p style="font-size: 1.2em; text-align: center; margin: 20px 0;">
                    {gate_message}
                </p>
            </div>
            
            <!-- Individual Agent Results -->
            <div class="metrics-grid">
                <div class="agent-section springfield">
                    <h3>🌸 Springfield - Strategic Analysis</h3>
                    <div class="score-circle">{springfield_score}</div>
                    <p><strong>Focus:</strong> Project architecture, team coordination, long-term sustainability</p>
                    <p><strong>Status:</strong> {springfield_status}</p>
                </div>
                
                <div class="agent-section krukai">
                    <h3>⚡ Krukai - Technical Excellence</h3>
                    <div class="score-circle">{krukai_score}</div>
                    <p><strong>Focus:</strong> Code quality, performance optimization, technical standards</p>
                    <p><strong>Status:</strong> {krukai_status}</p>
                </div>
                
                <div class="agent-section vector">
                    <h3>🛡️ Vector - Security Analysis</h3>
                    <div class="score-circle">{vector_score}</div>
                    <p><strong>Focus:</strong> Security vulnerabilities, risk assessment, compliance</p>
                    <p><strong>Status:</strong> {vector_status}</p>
                </div>
            </div>
            
            <!-- Detailed Metrics -->
            <div class="recommendations">
                <h3>📊 Detailed Quality Metrics</h3>
                <div class="metrics-grid">
                    {detailed_metrics}
                </div>
            </div>
            
            <!-- Recommendations -->
            <div class="recommendations">
                <h3>💡 Trinity Recommendations</h3>
                {recommendations_html}
            </div>
            
            <!-- Project Summary -->
            <div class="recommendations">
                <h3>📈 Project Health Summary</h3>
                <p><strong>Overall Assessment:</strong> {overall_assessment}</p>
                <p><strong>Deployment Readiness:</strong> {deployment_readiness}</p>
                <p><strong>Next Steps:</strong> {next_steps}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>🎭 Generated by Trinity Analysis System v2.0</p>
            <p>Springfield の戦略 • Krukai の技術 • Vector の安全性</p>
            <p>Project: {project_name} | Repository: {repository}</p>
        </div>
    </div>
</body>
</html>"""
    
    def load_trinity_data(self) -> Dict:
        """Trinity評価データの読み込み"""
        try:
            with open("trinity_gate_result.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_data()
            
    def _create_default_data(self) -> Dict:
        """デフォルトデータ作成（ファイルが見つからない場合）"""
        return {
            "trinity_scores": {
                "final_score": 75.0,
                "individual_scores": {
                    "springfield_strategic": 75.0,
                    "krukai_technical": 75.0,
                    "vector_security": 75.0
                }
            },
            "gate_decision": {
                "decision": "UNKNOWN",
                "message": "データが不完全です",
                "deployable": False
            },
            "recommendations": ["データの再生成が必要です"],
            "individual_assessments": {
                "springfield": {"status": "UNKNOWN"},
                "krukai": {"status": "UNKNOWN"},
                "vector": {"status": "UNKNOWN"}
            }
        }
        
    def generate_detailed_metrics(self, trinity_data: Dict) -> str:
        """詳細メトリクスHTML生成"""
        metrics_html = ""
        
        # Springfield metrics
        springfield = trinity_data.get("individual_assessments", {}).get("springfield", {})
        springfield_scores = springfield.get("scores", {})
        
        for metric, value in springfield_scores.items():
            if metric != "overall_strategic":
                metrics_html += f"""
                <div class="metric-card">
                    <div class="metric-value">{value:.1f}</div>
                    <p>{metric.replace('_', ' ').title()}</p>
                </div>
                """
                
        # Krukai metrics  
        krukai = trinity_data.get("individual_assessments", {}).get("krukai", {})
        krukai_metrics = krukai.get("metrics", {})
        
        for metric, value in krukai_metrics.items():
            if metric != "overall_technical":
                metrics_html += f"""
                <div class="metric-card">
                    <div class="metric-value">{value:.1f}</div>
                    <p>{metric.replace('_', ' ').title()}</p>
                </div>
                """
                
        # Vector metrics
        vector = trinity_data.get("individual_assessments", {}).get("vector", {})
        vector_metrics = vector.get("security_metrics", {})
        
        for metric, value in vector_metrics.items():
            if isinstance(value, (int, float)) and metric != "security_score":
                metrics_html += f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <p>{metric.replace('_', ' ').title()}</p>
                </div>
                """
                
        return metrics_html or '<p>詳細メトリクスは利用できません</p>'
        
    def generate_recommendations_html(self, recommendations: List[str]) -> str:
        """推奨事項HTML生成"""
        if not recommendations:
            return '<p>推奨事項はありません</p>'
            
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation-item">{rec}</div>'
            
        return html
        
    def get_status_class(self, decision: str) -> str:
        """ステータスクラス取得"""
        if decision in ["APPROVE_EXCELLENT"]:
            return "status-excellent"
        elif decision in ["APPROVE_GOOD"]:
            return "status-good"
        elif decision in ["APPROVE_WITH_CONDITIONS", "NEEDS_IMPROVEMENT"]:
            return "status-warning"
        else:
            return "status-danger"
            
    def generate_html_report(self) -> str:
        """HTMLレポート生成"""
        trinity_data = self.load_trinity_data()
        
        # Extract data
        trinity_scores = trinity_data.get("trinity_scores", {})
        gate_decision = trinity_data.get("gate_decision", {})
        recommendations = trinity_data.get("recommendations", [])
        individual_scores = trinity_scores.get("individual_scores", {})
        individual_assessments = trinity_data.get("individual_assessments", {})
        
        # Generate components
        detailed_metrics = self.generate_detailed_metrics(trinity_data)
        recommendations_html = self.generate_recommendations_html(recommendations)
        
        # Project info
        project_name = os.path.basename(self.project_root)
        repository = os.environ.get("GITHUB_REPOSITORY", "Unknown Repository")
        
        # Fill template
        html_content = self.template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trinity_score=f"{trinity_scores.get('final_score', 0):.1f}",
            gate_decision=gate_decision.get("decision", "UNKNOWN"),
            gate_message=gate_decision.get("message", "評価中..."),
            status_class=self.get_status_class(gate_decision.get("decision", "")),
            
            springfield_score=f"{individual_scores.get('springfield_strategic', 0):.1f}",
            krukai_score=f"{individual_scores.get('krukai_technical', 0):.1f}",
            vector_score=f"{individual_scores.get('vector_security', 0):.1f}",
            
            springfield_status=individual_assessments.get("springfield", {}).get("status", "UNKNOWN"),
            krukai_status=individual_assessments.get("krukai", {}).get("status", "UNKNOWN"),
            vector_status=individual_assessments.get("vector", {}).get("status", "UNKNOWN"),
            
            detailed_metrics=detailed_metrics,
            recommendations_html=recommendations_html,
            
            overall_assessment=self._get_overall_assessment(trinity_scores.get('final_score', 0)),
            deployment_readiness="Ready" if gate_decision.get("deployable", False) else "Needs Improvement",
            next_steps=self._get_next_steps(gate_decision.get("decision", "")),
            
            project_name=project_name,
            repository=repository
        )
        
        return html_content
        
    def _get_overall_assessment(self, score: float) -> str:
        """総合評価メッセージ取得"""
        if score >= 90:
            return "🌟 Excellent - 卓越した品質水準"
        elif score >= 80:
            return "✅ Good - 良好な品質水準"
        elif score >= 70:
            return "🟡 Acceptable - 許容可能な品質水準"
        elif score >= 60:
            return "🟠 Needs Improvement - 改善が必要"
        else:
            return "🔴 Poor - 大幅な改善が必要"
            
    def _get_next_steps(self, decision: str) -> str:
        """次のステップメッセージ取得"""
        steps = {
            "APPROVE_EXCELLENT": "継続的な品質維持とベストプラクティスの共有",
            "APPROVE_GOOD": "現在の品質水準を維持し、継続的改善を実施",
            "APPROVE_WITH_CONDITIONS": "推奨事項を実施してから本格デプロイ",
            "NEEDS_IMPROVEMENT": "重要な問題を修正してから再評価",
            "REJECT": "品質基準を満たすまで大幅な改善が必要"
        }
        return steps.get(decision, "評価を完了してから判断")
        
    def save_report(self) -> str:
        """レポート保存"""
        html_content = self.generate_html_report()
        
        report_path = "trinity-report.html"
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"🎭 Trinity Report: HTMLレポートを生成しました - {report_path}")
        return report_path


def main():
    """メイン実行関数"""
    generator = TrinityReportGenerator()
    generator.save_report()


if __name__ == "__main__":
    main()