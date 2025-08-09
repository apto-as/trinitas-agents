#!/usr/bin/env python3
"""
Krukai Technical Quality Gate
技術的卓越性・パフォーマンス・品質の厳格な評価

Krukai: "フン、この程度のコード品質では404の基準には達しないわね"
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List


class KrukaiQualityGate:
    """Krukai式完璧主義品質ゲート"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.quality_metrics = {}
        self.performance_metrics = {}
        self.strict_standards = {
            "code_quality_minimum": 85,
            "test_coverage_minimum": 90,
            "performance_grade_minimum": 80,
            "security_score_minimum": 95,
        }

    def analyze_code_quality(self) -> float:
        """コード品質の厳格な分析"""
        total_score = 0.0

        # Python code quality analysis
        python_files = list(self.project_root.rglob("*.py"))
        if python_files:
            score = self._analyze_python_quality(python_files)
            total_score += score * 0.4

        # JavaScript/TypeScript analysis
        js_files = list(self.project_root.rglob("*.js")) + list(
            self.project_root.rglob("*.ts")
        )
        if js_files:
            score = self._analyze_js_quality(js_files)
            total_score += score * 0.3

        # General code metrics
        general_score = self._analyze_general_quality()
        total_score += general_score * 0.3

        self.quality_metrics["code_quality"] = total_score
        return total_score

    def _analyze_python_quality(self, files: List[Path]) -> float:
        """Python専用品質分析"""
        score = 0.0

        try:
            # Run pylint for code quality
            pylint_result = subprocess.run(
                ["pylint", "--output-format=json"]
                + [str(f) for f in files[:10]],  # Limit files
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if pylint_result.returncode in [0, 4, 8, 16]:  # Various pylint exit codes
                try:
                    pylint_data = (
                        json.loads(pylint_result.stdout)
                        if pylint_result.stdout.strip()
                        else []
                    )
                    error_count = len(
                        [item for item in pylint_data if item.get("type") == "error"]
                    )
                    warning_count = len(
                        [item for item in pylint_data if item.get("type") == "warning"]
                    )

                    # Krukai's strict scoring
                    score = max(0, 100 - (error_count * 10) - (warning_count * 2))
                except json.JSONDecodeError:
                    score = 70  # Partial credit
            else:
                score = 50  # Execution issues

        except FileNotFoundError:
            print("⚡ Krukai: pylint not available, using alternative analysis")
            score = self._basic_python_analysis(files)

        return min(score, 100)

    def _analyze_js_quality(self, files: List[Path]) -> float:
        """JavaScript/TypeScript品質分析"""
        score = 80.0  # Default score if no specific tools available

        # Check for TypeScript usage (higher quality indicator)
        ts_files = [f for f in files if f.suffix == ".ts"]
        if ts_files:
            score += 10

        # Check for proper module structure
        has_modules = any(
            "import" in f.read_text(errors="ignore")
            or "require(" in f.read_text(errors="ignore")
            for f in files[:5]
        )
        if has_modules:
            score += 10

        return min(score, 100)

    def _basic_python_analysis(self, files: List[Path]) -> float:
        """基本的なPython分析（ツール不足時）"""
        score = 70.0

        for file_path in files[:10]:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Check for docstrings
                if '"""' in content or "'''" in content:
                    score += 2

                # Check for type hints
                if "typing" in content or "->" in content:
                    score += 3

                # Check for proper imports
                lines = content.split("\n")
                import_lines = [
                    l
                    for l in lines
                    if l.strip().startswith("import") or l.strip().startswith("from")
                ]
                if len(import_lines) > 0:
                    score += 1

            except Exception:
                score -= 5

        return min(score, 100)

    def _analyze_general_quality(self) -> float:
        """一般的なコード品質指標"""
        score = 0.0

        # Test files existence
        test_dirs = ["tests", "test", "__tests__"]
        has_tests = any((self.project_root / d).exists() for d in test_dirs)
        test_files = list(self.project_root.rglob("*test*.py")) + list(
            self.project_root.rglob("*.test.js")
        )

        if has_tests or test_files:
            score += 30

        # Configuration quality
        config_files = ["setup.py", "pyproject.toml", "package.json", "Cargo.toml"]
        config_score = sum(10 for f in config_files if (self.project_root / f).exists())
        score += min(config_score, 30)

        # Code organization
        if (self.project_root / "src").exists() or (self.project_root / "lib").exists():
            score += 20

        # Documentation
        if (self.project_root / "README.md").exists():
            score += 20

        return score

    def analyze_performance_indicators(self) -> float:
        """パフォーマンス指標の分析"""
        score = 70.0  # Base score

        # Check for performance-conscious patterns
        perf_indicators = {
            "async": 10,  # Async programming
            "cache": 5,  # Caching usage
            "optimize": 5,  # Optimization keywords
            "benchmark": 10,  # Benchmarking
        }

        code_files = list(self.project_root.rglob("*.py")) + list(
            self.project_root.rglob("*.js")
        )

        for file_path in code_files[:20]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
                for keyword, points in perf_indicators.items():
                    if keyword in content:
                        score += points
                        break  # Only count once per file
            except Exception:
                continue

        # Memory and resource consciousness
        resource_patterns = ["with open", "try:", "finally:", "context manager"]
        for file_path in code_files[:10]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if any(pattern in content for pattern in resource_patterns):
                    score += 5
            except Exception:
                continue

        self.performance_metrics["performance_indicators"] = score
        return min(score, 100)

    def run_security_quality_check(self) -> float:
        """セキュリティ品質チェック"""
        score = 75.0  # Base security score

        # Check for security best practices
        security_patterns = {
            "password": -10,  # Hardcoded passwords (bad)
            "api_key": -10,  # Hardcoded API keys (bad)
            "secret": -5,  # Hardcoded secrets (bad)
            "hash": 10,  # Hashing usage (good)
            "encrypt": 10,  # Encryption usage (good)
            "validate": 5,  # Input validation (good)
            "sanitize": 5,  # Data sanitization (good)
        }

        code_files = list(self.project_root.rglob("*.py")) + list(
            self.project_root.rglob("*.js")
        )

        for file_path in code_files[:15]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
                for pattern, points in security_patterns.items():
                    if pattern in content:
                        score += points
            except Exception:
                continue

        # Environment variable usage (good practice)
        env_usage = any(
            "os.environ" in file_path.read_text(errors="ignore")
            or "process.env" in file_path.read_text(errors="ignore")
            for file_path in code_files[:10]
            if file_path.stat().st_size < 100000
        )
        if env_usage:
            score += 15

        return max(min(score, 100), 0)

    def calculate_technical_debt(self) -> float:
        """技術的負債の計算"""
        debt_score = 100.0  # Start with perfect score

        # TODO/FIXME/HACK comments indicate debt
        debt_keywords = ["TODO", "FIXME", "HACK", "XXX", "BUG"]
        code_files = list(self.project_root.rglob("*.py")) + list(
            self.project_root.rglob("*.js")
        )

        total_debt_items = 0
        for file_path in code_files[:20]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for keyword in debt_keywords:
                    total_debt_items += content.upper().count(keyword)
            except Exception:
                continue

        # Penalize debt items
        debt_penalty = min(total_debt_items * 2, 30)
        debt_score -= debt_penalty

        # Large files indicate potential debt
        large_files = [f for f in code_files if f.stat().st_size > 10000]  # > 10KB
        debt_score -= min(len(large_files) * 1, 20)

        self.quality_metrics["technical_debt"] = 100 - debt_score
        return debt_score

    def generate_krukai_assessment(self) -> Dict:
        """Krukai式厳格な総合評価"""
        print("⚡ Krukai: 404品質基準による厳格な評価を開始するわ...")

        code_quality = self.analyze_code_quality()
        performance = self.analyze_performance_indicators()
        security = self.run_security_quality_check()
        tech_debt = self.calculate_technical_debt()

        # Krukai's weighted scoring (very strict)
        overall_score = (
            code_quality * 0.35
            + performance * 0.25
            + security * 0.25
            + tech_debt * 0.15
        )

        # Krukai's perfectionist recommendations
        recommendations = []
        if code_quality < self.strict_standards["code_quality_minimum"]:
            recommendations.append(
                "💻 コード品質が基準以下よ。リファクタリングと適切な設計パターンの適用が必要"
            )

        if performance < self.strict_standards["performance_grade_minimum"]:
            recommendations.append(
                "⚡ パフォーマンスが不十分。アルゴリズムの最適化と効率的な実装を行いなさい"
            )

        if security < self.strict_standards["security_score_minimum"]:
            recommendations.append(
                "🔒 セキュリティ実装が甘すぎる。適切な暗号化と入力検証を実装すること"
            )

        if tech_debt > 25:
            recommendations.append(
                "🗑️ 技術的負債が蓄積している。計画的なリファクタリングが急務よ"
            )

        # Krukai's final judgment
        grade = (
            "S"
            if overall_score >= 95
            else "A"
            if overall_score >= 85
            else "B"
            if overall_score >= 75
            else "C"
            if overall_score >= 65
            else "F"
        )

        status = "PASS" if overall_score >= 70 else "FAIL"

        krukai_message = {
            "S": "完璧よ。404の基準を満たす実装ね",
            "A": "悪くないわ。まだ改善の余地はあるけれど",
            "B": "平均的な実装ね。もっと効率化できるはず",
            "C": "基準ギリギリよ。大幅な改善が必要",
            "F": "これでは404の名が泣くわ。全面的な見直しが必要",
        }.get(grade, "評価不能")

        assessment_report = {
            "agent": "Krukai Quality Gate",
            "timestamp": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True
            ).stdout.strip(),
            "metrics": {
                "code_quality": code_quality,
                "performance_indicators": performance,
                "security_quality": security,
                "technical_debt": tech_debt,
                "overall_technical": overall_score,
            },
            "grade": grade,
            "recommendations": recommendations,
            "status": status,
            "message": f"Krukai: 「{krukai_message}」",
        }

        # Save results for CI pipeline
        with open("quality_score.txt", "w") as f:
            f.write(str(overall_score))

        with open("krukai_quality.json", "w") as f:
            json.dump(assessment_report, f, indent=2, ensure_ascii=False)

        print(f"⚡ Krukai: Grade {grade} - {krukai_message}")

        return assessment_report


def main():
    """メイン実行関数"""
    project_root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    quality_gate = KrukaiQualityGate(project_root)
    quality_gate.generate_krukai_assessment()


if __name__ == "__main__":
    main()
