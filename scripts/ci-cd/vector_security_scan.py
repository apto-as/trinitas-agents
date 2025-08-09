#!/usr/bin/env python3
"""
Vector Paranoid Security Scanner
超悲観的セキュリティ脆弱性検査・リスク分析

Vector: "……きっとどこかに脆弱性が隠れてる……でも、あたしが見つけて守る……"
"""

import os
import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add parent directory to path for common modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.project_path_resolver import resolver


class VectorSecurityScanner:
    """Vector式超悲観的セキュリティスキャナー"""

    def __init__(self, project_root: str = None):
        # Springfield式思いやり設計: 統一パス解決システムを使用
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = resolver.project_root
        self.security_findings = []
        self.risk_score = 0.0
        self.paranoia_level = "maximum"

        # Vector's security categories (worst-case scenarios)
        self.threat_categories = {
            "CRITICAL": {
                "weight": 50,
                "description": "即座にシステムが危険にさらされる",
            },
            "HIGH": {"weight": 30, "description": "重大なセキュリティリスク"},
            "MEDIUM": {"weight": 15, "description": "潜在的な脆弱性"},
            "LOW": {"weight": 5, "description": "軽微だが注意が必要"},
            "INFO": {"weight": 1, "description": "セキュリティ強化の余地"},
        }

    def scan_hardcoded_secrets(self) -> List[Dict]:
        """ハードコードされた秘密情報の検出"""
        findings = []

        # Vector's paranoid secret patterns
        secret_patterns = {
            "password": r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{3,}["\']',
            "api_key": r'(?i)(api_key|apikey|api-key)\s*[=:]\s*["\'][^"\']{10,}["\']',
            "token": r'(?i)(token|access_token)\s*[=:]\s*["\'][^"\']{10,}["\']',
            "secret": r'(?i)(secret|secret_key)\s*[=:]\s*["\'][^"\']{8,}["\']',
            "private_key": r"-----BEGIN.*PRIVATE KEY-----",
            "connection_string": r'(?i)(connection_string|conn_str|database_url).*[=:]\s*["\'][^"\']*://[^"\']*["\']',
        }

        code_files = (
            list(self.project_root.rglob("*.py"))
            + list(self.project_root.rglob("*.js"))
            + list(self.project_root.rglob("*.ts"))
            + list(self.project_root.rglob("*.json"))
            + list(self.project_root.rglob("*.yml"))
            + list(self.project_root.rglob("*.yaml"))
        )

        for file_path in code_files:
            if file_path.name.startswith(".") and file_path.name != ".env.example":
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                for secret_type, pattern in secret_patterns.items():
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[: match.start()].count("\\n") + 1
                        findings.append(
                            {
                                "type": "hardcoded_secret",
                                "severity": "CRITICAL",
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": line_num,
                                "secret_type": secret_type,
                                "message": f"ハードコードされた{secret_type}を検出: {match.group(0)[:20]}...",
                                "recommendation": "環境変数または安全な設定ファイルに移動してください",
                            }
                        )

            except Exception as e:
                # Vector doesn't give up easily
                findings.append(
                    {
                        "type": "scan_error",
                        "severity": "MEDIUM",
                        "file": str(file_path.relative_to(self.project_root)),
                        "message": f"ファイル読み込みエラー: {e}",
                        "recommendation": "ファイルの権限とエンコーディングを確認",
                    }
                )

        return findings

    def analyze_dependency_vulnerabilities(self) -> List[Dict]:
        """依存関係の脆弱性分析"""
        findings = []

        # Python dependencies
        requirements_files = ["requirements.txt", "Pipfile", "pyproject.toml"]
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                findings.extend(self._scan_python_dependencies(req_path))

        # JavaScript dependencies
        package_json = self.project_root / "package.json"
        if package_json.exists():
            findings.extend(self._scan_npm_dependencies(package_json))

        return findings

    def _scan_python_dependencies(self, req_file: Path) -> List[Dict]:
        """Python依存関係のスキャン"""
        findings = []

        try:
            # Try using safety for vulnerability scanning
            result = subprocess.run(
                ["safety", "check", "--file", str(req_file), "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        findings.append(
                            {
                                "type": "dependency_vulnerability",
                                "severity": "HIGH",
                                "file": str(req_file.relative_to(self.project_root)),
                                "package": vuln.get("package", "unknown"),
                                "vulnerability_id": vuln.get("id", ""),
                                "message": vuln.get(
                                    "advisory", "依存関係に脆弱性があります"
                                ),
                                "recommendation": "パッケージを最新バージョンにアップデートしてください",
                            }
                        )
                except json.JSONDecodeError:
                    pass

        except FileNotFoundError:
            # Fallback: manual basic checks
            findings.extend(self._basic_python_dep_check(req_file))

        return findings

    def _basic_python_dep_check(self, req_file: Path) -> List[Dict]:
        """基本的なPython依存関係チェック"""
        findings = []

        # Known vulnerable patterns (basic check)
        risky_packages = {
            "flask": "古いバージョンのFlaskには脆弱性があります",
            "django": "Djangoのバージョンを確認してください",
            "requests": "古いrequestsは脆弱性があります",
            "pyyaml": "PyYAMLの古いバージョンは危険です",
        }

        try:
            content = req_file.read_text()
            for line in content.split("\\n"):
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue

                for pkg, warning in risky_packages.items():
                    if pkg in line:
                        findings.append(
                            {
                                "type": "dependency_check",
                                "severity": "MEDIUM",
                                "file": str(req_file.relative_to(self.project_root)),
                                "package": pkg,
                                "message": warning,
                                "recommendation": "最新バージョンを確認してください",
                            }
                        )

        except Exception:
            pass

        return findings

    def _scan_npm_dependencies(self, package_json: Path) -> List[Dict]:
        """npm依存関係のスキャン"""
        findings = []

        try:
            # Try npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.stdout.strip():
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})

                    for pkg_name, vuln_info in vulnerabilities.items():
                        severity = vuln_info.get("severity", "unknown").upper()
                        if severity not in self.threat_categories:
                            severity = "MEDIUM"

                        findings.append(
                            {
                                "type": "npm_vulnerability",
                                "severity": severity,
                                "file": "package.json",
                                "package": pkg_name,
                                "message": f"npm audit: {pkg_name}に脆弱性があります",
                                "recommendation": "npm updateまたはnpm auditを実行してください",
                            }
                        )

                except json.JSONDecodeError:
                    pass

        except FileNotFoundError:
            # npm not available
            pass

        return findings

    def scan_insecure_patterns(self) -> List[Dict]:
        """危険なコードパターンの検出"""
        findings = []

        # Vector's paranoid code patterns
        dangerous_patterns = {
            "sql_injection": {
                "pattern": r'(?i)(execute|query|select|insert|update|delete).*["\'][^"\']*\+.*["\']',
                "severity": "CRITICAL",
                "message": "SQL Injection の可能性があります",
            },
            "command_injection": {
                "pattern": r"(?i)(os\.system|subprocess\.call|exec|eval)\s*\([^)]*\+",
                "severity": "CRITICAL",
                "message": "Command Injection の可能性があります",
            },
            "xss_vulnerable": {
                "pattern": r"(?i)(innerHTML|document\.write).*\+",
                "severity": "HIGH",
                "message": "XSS脆弱性の可能性があります",
            },
            "weak_crypto": {
                "pattern": r"(?i)(md5|sha1)\\(",
                "severity": "MEDIUM",
                "message": "弱い暗号化アルゴリズムが使用されています",
            },
            "debug_info": {
                "pattern": r"(?i)(print|console\.log|debug|trace).*(?:password|secret|token|key)",
                "severity": "HIGH",
                "message": "機密情報がログに出力される可能性があります",
            },
        }

        code_files = (
            list(self.project_root.rglob("*.py"))
            + list(self.project_root.rglob("*.js"))
            + list(self.project_root.rglob("*.ts"))
        )

        for file_path in code_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                for pattern_name, pattern_info in dangerous_patterns.items():
                    matches = re.finditer(
                        pattern_info["pattern"], content, re.MULTILINE
                    )
                    for match in matches:
                        line_num = content[: match.start()].count("\\n") + 1
                        findings.append(
                            {
                                "type": "insecure_pattern",
                                "severity": pattern_info["severity"],
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": line_num,
                                "pattern": pattern_name,
                                "message": pattern_info["message"],
                                "code_snippet": match.group(0)[:50] + "...",
                                "recommendation": "セキュアなコーディング手法を使用してください",
                            }
                        )

            except Exception:
                continue

        return findings

    def check_file_permissions(self) -> List[Dict]:
        """ファイル権限の危険性チェック"""
        findings = []

        # Check for overly permissive files
        sensitive_files = [".env", "config.json", "secrets.yaml", "private.key"]

        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                try:
                    stat_info = file_path.stat()
                    mode = oct(stat_info.st_mode)[-3:]

                    # Check if file is readable by others
                    if mode[2] in ["4", "5", "6", "7"]:  # Others can read
                        findings.append(
                            {
                                "type": "file_permission",
                                "severity": "HIGH",
                                "file": str(file_path.relative_to(self.project_root)),
                                "permission": mode,
                                "message": "機密ファイルが他のユーザーから読み取り可能です",
                                "recommendation": "ファイル権限を600または700に変更してください",
                            }
                        )

                except Exception:
                    continue

        return findings

    def calculate_overall_risk(self, all_findings: List[Dict]) -> float:
        """総合リスクスコアの計算"""
        total_risk = 0.0

        for finding in all_findings:
            severity = finding.get("severity", "LOW")
            weight = self.threat_categories.get(severity, {"weight": 1})["weight"]
            total_risk += weight

        # Vector's pessimistic scaling
        max_possible_risk = len(all_findings) * 50  # Assuming all CRITICAL
        if max_possible_risk > 0:
            risk_percentage = (total_risk / max_possible_risk) * 100
        else:
            risk_percentage = 0

        # Vector always assumes the worst case
        return min(100, risk_percentage * 1.5)  # Amplify risk

    def generate_vector_report(self) -> Dict:
        """Vector式セキュリティレポート生成"""
        print("🛡️ Vector: ……セキュリティスキャンを開始……最悪のケースを想定中……")

        # Comprehensive security scanning
        secret_findings = self.scan_hardcoded_secrets()
        dependency_findings = self.analyze_dependency_vulnerabilities()
        pattern_findings = self.scan_insecure_patterns()
        permission_findings = self.check_file_permissions()

        all_findings = (
            secret_findings
            + dependency_findings
            + pattern_findings
            + permission_findings
        )

        # Calculate risk metrics
        risk_score = self.calculate_overall_risk(all_findings)
        security_score = max(0, 100 - risk_score)

        # Vector's categorized analysis
        critical_findings = [f for f in all_findings if f.get("severity") == "CRITICAL"]
        high_findings = [f for f in all_findings if f.get("severity") == "HIGH"]

        # Vector's pessimistic recommendations
        recommendations = []
        if critical_findings:
            recommendations.append(
                "🚨 CRITICAL: 即座に対応が必要な重大な脆弱性があります。すぐに修正してください"
            )
        if high_findings:
            recommendations.append(
                "⚠️ HIGH: 重要なセキュリティ問題があります。早急な対応が必要です"
            )
        if len(all_findings) > 10:
            recommendations.append(
                "📊 多数のセキュリティ問題が検出されました。包括的なセキュリティレビューを実施してください"
            )
        if not all_findings:
            recommendations.append(
                "……今回は大きな問題は見つからなかった……でも、きっとまだ隠れてる……継続的な監視が必要"
            )

        # Vector's final judgment
        if len(critical_findings) > 0:
            status = "CRITICAL_FAIL"
            vector_message = "……最悪の予感が的中した……重大な脆弱性がある……"
        elif len(high_findings) > 3:
            status = "FAIL"
            vector_message = "……やっぱり問題があった……高リスクの脆弱性が複数……"
        elif len(all_findings) > 5:
            status = "WARNING"
            vector_message = "……いくつか問題がある……注意深く対応して……"
        elif len(all_findings) > 0:
            status = "PASS_WITH_WARNINGS"
            vector_message = "……小さな問題はある……でも、許容範囲内……"
        else:
            status = "PASS"
            vector_message = "……今回は大丈夫そう……でも、油断は禁物……"

        security_report = {
            "agent": "Vector Security Scanner",
            "timestamp": datetime.now().isoformat(),
            "security_metrics": {
                "total_findings": len(all_findings),
                "critical_findings": len(critical_findings),
                "high_findings": len(high_findings),
                "risk_score": risk_score,
                "security_score": security_score,
            },
            "findings_by_category": {
                "hardcoded_secrets": len(secret_findings),
                "dependency_vulnerabilities": len(dependency_findings),
                "insecure_patterns": len(pattern_findings),
                "file_permissions": len(permission_findings),
            },
            "detailed_findings": all_findings,
            "recommendations": recommendations,
            "status": status,
            "message": f"Vector: {vector_message}",
        }

        # Save results for CI pipeline
        with open("security_score.txt", "w") as f:
            f.write(str(security_score))

        with open("vector_security.json", "w") as f:
            json.dump(security_report, f, indent=2, ensure_ascii=False)

        print(f"🛡️ Vector: {vector_message}")
        print(f"🛡️ Vector: セキュリティスコア: {security_score:.1f}/100")

        return security_report


def main():
    """メイン実行関数 - 統一パス解決システム使用"""
    # Springfield式統一パス解決: 引数なしで自動解決
    scanner = VectorSecurityScanner()

    # デバッグ情報出力（必要に応じて）
    if os.environ.get("DEBUG_TRINITAS"):
        from common.project_path_resolver import print_resolution_info

        print_resolution_info()

    scanner.generate_vector_report()


if __name__ == "__main__":
    main()
