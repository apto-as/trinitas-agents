#!/usr/bin/env python3
"""
Springfield Strategic CI Analysis
プロジェクト戦略的評価・チーム協調性分析

Springfield: "CI/CDパイプラインも、チーム全体の持続可能性を考慮した設計にしましょうね"
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class SpringfieldStrategicAnalyzer:
    """Springfield式戦略的CI分析"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_results = {}
        
    def analyze_project_structure(self) -> float:
        """プロジェクト構造の戦略的健全性を評価"""
        score = 0.0
        
        # Documentation quality check
        docs_exist = any([
            (self.project_root / "README.md").exists(),
            (self.project_root / "docs").exists(),
            (self.project_root / "CLAUDE.md").exists(),
        ])
        if docs_exist:
            score += 30
            
        # Project organization
        standard_dirs = ["src", "lib", "tests", "scripts"]
        existing_dirs = sum(1 for d in standard_dirs if (self.project_root / d).exists())
        score += (existing_dirs / len(standard_dirs)) * 20
        
        # Configuration files
        config_files = ["package.json", "requirements.txt", "Cargo.toml", "go.mod"]
        has_config = any((self.project_root / f).exists() for f in config_files)
        if has_config:
            score += 25
            
        # Team coordination files
        team_files = [".gitignore", "CONTRIBUTING.md", "LICENSE"]
        team_score = sum(5 for f in team_files if (self.project_root / f).exists())
        score += min(team_score, 25)
        
        self.analysis_results["project_structure"] = score
        return score
        
    def evaluate_team_sustainability(self) -> float:
        """チーム持続可能性の評価"""
        score = 0.0
        
        try:
            # Git commit patterns analysis
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=30 days"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                commit_count = len([c for c in commits if c.strip()])
                
                # Healthy commit frequency
                if 10 <= commit_count <= 100:
                    score += 40
                elif commit_count > 0:
                    score += 20
                    
            # Check for team collaboration indicators
            if (self.project_root / ".github").exists():
                score += 20
                
            if (self.project_root / "CONTRIBUTING.md").exists():
                score += 20
                
            # Multi-contributor check
            contributors_result = subprocess.run(
                ["git", "shortlog", "-sn", "--since=30 days"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if contributors_result.returncode == 0:
                contributor_lines = [l for l in contributors_result.stdout.strip().split('\n') if l.strip()]
                if len(contributor_lines) > 1:
                    score += 20
                    
        except Exception as e:
            print(f"Springfield: Git analysis warning - {e}")
            score += 10  # Partial credit for attempt
            
        self.analysis_results["team_sustainability"] = score
        return score
        
    def assess_long_term_vision(self) -> float:
        """長期的ビジョンと計画性の評価"""
        score = 0.0
        
        # Version management
        version_files = ["VERSION", "version.txt", "package.json", "Cargo.toml"]
        has_versioning = any((self.project_root / f).exists() for f in version_files)
        if has_versioning:
            score += 25
            
        # Changelog presence
        changelog_files = ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"]
        has_changelog = any((self.project_root / f).exists() for f in changelog_files)
        if has_changelog:
            score += 25
            
        # Roadmap or planning
        planning_files = ["ROADMAP.md", "TODO.md", "BACKLOG.md"]
        has_planning = any((self.project_root / f).exists() for f in planning_files)
        if has_planning:
            score += 25
            
        # CI/CD configuration exists
        ci_configs = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".travis.yml"]
        has_ci = any((self.project_root / f).exists() for f in ci_configs)
        if has_ci:
            score += 25
            
        self.analysis_results["long_term_vision"] = score
        return score
        
    def generate_strategic_recommendations(self) -> List[str]:
        """Springfield式戦略的改善提案"""
        recommendations = []
        
        if self.analysis_results.get("project_structure", 0) < 70:
            recommendations.append(
                "📁 プロジェクト構造の改善をお勧めします。適切なディレクトリ構成と文書化により、"
                "新しいチームメンバーの参加がスムーズになりますよ"
            )
            
        if self.analysis_results.get("team_sustainability", 0) < 60:
            recommendations.append(
                "👥 チーム協調の仕組みを強化しましょう。CONTRIBUTING.md や適切なGitHub設定により、"
                "持続可能な開発体制を構築できます"
            )
            
        if self.analysis_results.get("long_term_vision", 0) < 70:
            recommendations.append(
                "🎯 長期的なビジョン管理の改善が必要です。バージョン管理とChangelog、"
                "ロードマップにより、プロジェクトの方向性を明確にしましょう"
            )
            
        return recommendations
        
    def run_complete_analysis(self) -> Dict:
        """完全な戦略的分析を実行"""
        print("🌸 Springfield: 戦略的CI分析を開始します...")
        
        structure_score = self.analyze_project_structure()
        sustainability_score = self.evaluate_team_sustainability()
        vision_score = self.assess_long_term_vision()
        
        total_score = (structure_score + sustainability_score + vision_score) / 3
        
        recommendations = self.generate_strategic_recommendations()
        
        analysis_report = {
            "agent": "Springfield Strategic Analyzer",
            "timestamp": subprocess.run(["date", "+%Y-%m-%d %H:%M:%S"], 
                                       capture_output=True, text=True).stdout.strip(),
            "scores": {
                "project_structure": structure_score,
                "team_sustainability": sustainability_score,
                "long_term_vision": vision_score,
                "overall_strategic": total_score
            },
            "recommendations": recommendations,
            "status": "PASS" if total_score >= 70 else "NEEDS_IMPROVEMENT",
            "message": f"Springfield: 「全体的な戦略スコアは {total_score:.1f}点です。" +
                      ("素晴らしい持続可能な構造ですね♪」" if total_score >= 70 else 
                       "改善の余地がありますが、一緒に素敵なプロジェクトにしてまいりましょう」")
        }
        
        # Save results for CI pipeline
        with open("strategic_score.txt", "w") as f:
            f.write(str(total_score))
            
        with open("springfield_analysis.json", "w") as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
            
        print(f"🌸 Springfield: {analysis_report['message']}")
        
        return analysis_report


def main():
    """メイン実行関数"""
    project_root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    analyzer = SpringfieldStrategicAnalyzer(project_root)
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()