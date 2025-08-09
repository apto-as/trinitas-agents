#!/usr/bin/env python3
"""
Advanced security scanner using Python tools.
Vector: "……Pythonの深層解析で、隠れた脆弱性も見逃さない……"
"""

import os
import subprocess
import sys
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trinitas_hooks import (
    HookResult,
    HookStatus,
    SecurityAnalyzer,
    TrinitasHook,
    TrinitasLogger,
)


class SecurityScannerHook(TrinitasHook):
    """Advanced security scanning with Python tools."""

    def __init__(self):
        """Initialize hook."""
        super().__init__()
        self.logger = TrinitasLogger()
        self.analyzer = SecurityAnalyzer()
        self.has_bandit = self._check_tool("bandit")
        self.has_safety = self._check_tool("safety")

    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available."""
        try:
            # S607: Use of shlex to prevent command injection
            # S603: subprocess usage is controlled - using shell=False and quoted parameters
            safe_command = [tool_name, "--version"]  # No need to quote in list form
            subprocess.run(safe_command, capture_output=True, check=False, shell=False)  # nosec B603
            return True
        except (FileNotFoundError, OSError):
            return False

    def run(self) -> HookResult:
        """Execute security scan."""
        self.logger.vector(
            "……セキュリティスキャンを開始……すべての脅威を検出する……", "Security Scan"
        )

        vulnerabilities: List[Dict[str, Any]] = []

        # Scan based on tool type
        if self.tool_name == "Bash":
            # Check command for security issues
            command = self.tool_args.get("command", "")
            if command:
                vulnerabilities.extend(self._scan_command(command))

        elif self.tool_name in ["Write", "Edit", "MultiEdit"]:
            # Scan file for security issues
            file_path = self.tool_args.get("file_path", "")
            if file_path and os.path.exists(file_path):
                vulnerabilities.extend(self._scan_file(file_path))

        # Check for dependency vulnerabilities if applicable
        if self.tool_name == "Bash":
            command = self.tool_args.get("command", "")
            if any(
                cmd in command
                for cmd in ["pip install", "npm install", "gem install", "cargo add"]
            ):
                self.logger.warning(
                    "依存関係のインストールを検出。脆弱性チェックを推奨"
                )
                vulnerabilities.append(
                    {
                        "type": "dependency",
                        "severity": "warning",
                        "message": "Installing dependencies - consider security audit",
                    }
                )

        # Generate report
        if vulnerabilities:
            self._generate_security_report(vulnerabilities)

            # Check severity
            high_severity = sum(
                1 for v in vulnerabilities if v.get("severity") == "high"
            )

            if high_severity > 0:
                self.logger.vector(
                    f"……{high_severity}個の高リスク脆弱性を検出……即座の対応が必要……"
                )
                return HookResult(
                    status=HookStatus.BLOCKED,
                    message=f"High severity vulnerabilities detected: {high_severity}",
                    details=self._format_vulnerabilities(vulnerabilities),
                )
            else:
                self.logger.vector("……中程度のリスクを検出……注意して進めること……")
                return HookResult(
                    status=HookStatus.WARNING,
                    message=f"Security concerns found: {len(vulnerabilities)}",
                    details=self._format_vulnerabilities(vulnerabilities),
                )
        else:
            self.logger.springfield(
                "セキュリティチェック完了！問題は見つかりませんでした"
            )
            return HookResult(
                status=HookStatus.SUCCESS,
                message="No security vulnerabilities detected",
            )

    def _scan_command(self, command: str) -> List[Dict[str, Any]]:
        """Scan shell command for security issues."""
        vulnerabilities: List[Dict[str, Any]] = []

        # Check for dangerous patterns
        dangerous_patterns = [
            ("curl .* | bash", "high", "Piping to shell is extremely dangerous"),
            ("wget .* | sh", "high", "Piping to shell is extremely dangerous"),
            ("eval ", "high", "eval can execute arbitrary code"),
            ("sudo ", "medium", "Elevated privileges requested"),
            (r"\$\(.*\)", "low", "Command substitution detected"),
        ]

        for pattern, severity, message in dangerous_patterns:
            if pattern in command:
                vulnerabilities.append(
                    {
                        "type": "command",
                        "severity": severity,
                        "pattern": pattern,
                        "message": message,
                    }
                )

        return vulnerabilities

    def _scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan file for security vulnerabilities."""
        vulnerabilities: List[Dict[str, Any]] = []

        # Use built-in analyzer
        issues = self.analyzer.scan_file(file_path)
        for issue in issues:
            vulnerabilities.append(
                {
                    "type": "code",
                    "severity": "high" if issue.severity == "error" else "medium",
                    "line": issue.line,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
            )

        # Run Bandit for Python files if available
        if self.has_bandit and file_path.endswith(".py"):
            self.logger.progress_start("Running Bandit security linter")
            try:
                # S603: subprocess usage is controlled - using shell=False and safe parameters
                safe_command = ["bandit", "-f", "json", file_path]  # No need to quote in list form
                result = subprocess.run(  # nosec B603
                    safe_command,
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=False,
                )

                if result.stdout:
                    import json

                    bandit_results = json.loads(result.stdout)
                    for issue in bandit_results.get("results", []):
                        vulnerabilities.append(
                            {
                                "type": "bandit",
                                "severity": issue["issue_severity"].lower(),
                                "line": issue["line_number"],
                                "message": issue["issue_text"],
                                "confidence": issue["issue_confidence"],
                            }
                        )

                self.logger.progress_end(True)
            except Exception:
                self.logger.progress_end(False)

        return vulnerabilities

    def _generate_security_report(self, vulnerabilities: List[Dict[str, Any]]) -> None:
        """Generate detailed security report."""
        sections: Dict[str, Any] = {}

        # Group by type
        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "unknown")
            if vuln_type not in by_type:
                by_type[vuln_type] = []
            by_type[vuln_type].append(vuln)

        # Add sections
        for vuln_type, vulns in by_type.items():
            section_title = f"{vuln_type.title()} Vulnerabilities"
            sections[section_title] = [
                f"{v.get('severity', 'unknown').upper()}: {v['message']}"
                for v in vulns[:5]  # Show first 5
            ]
            if len(vulns) > 5:
                sections[section_title].append(f"... and {len(vulns) - 5} more")

        # Summary
        sections["Risk Summary"] = {
            "Total Issues": len(vulnerabilities),
            "High Severity": sum(
                1 for v in vulnerabilities if v.get("severity") == "high"
            ),
            "Medium Severity": sum(
                1 for v in vulnerabilities if v.get("severity") == "medium"
            ),
            "Low Severity": sum(
                1 for v in vulnerabilities if v.get("severity") == "low"
            ),
        }

        self.logger.report("Security Scan Report", sections)

    def _format_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Format vulnerabilities for shell output."""
        high = [v for v in vulnerabilities if v.get("severity") == "high"]
        medium = [v for v in vulnerabilities if v.get("severity") == "medium"]

        output: List[str] = []

        if high:
            output.append("High Severity:")
            for vuln in high[:3]:
                output.append(f"  • {vuln['message']}")
                if vuln.get("suggestion"):
                    output.append(f"    → {vuln['suggestion']}")

        if medium:
            output.append("\nMedium Severity:")
            for vuln in medium[:2]:
                output.append(f"  • {vuln['message']}")

        return "\n".join(output)


if __name__ == "__main__":
    hook = SecurityScannerHook()
    sys.exit(hook.execute())
