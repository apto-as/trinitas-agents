#!/usr/bin/env python3
"""
Enhanced code quality check using Python analysis tools.
Krukai: "Pythonの力で、さらに完璧な品質チェックを実現するわ"
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trinitas_hooks import (
    TrinitasHook, HookResult, HookStatus,
    CodeAnalyzer, SecurityAnalyzer, QualityChecker,
    TrinitasLogger
)


class EnhancedQualityCheckHook(TrinitasHook):
    """Enhanced code quality check with advanced Python analysis."""
    
    def __init__(self):
        """Initialize hook."""
        super().__init__()
        self.logger = TrinitasLogger()
        self.code_analyzer = CodeAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.quality_checker = QualityChecker()
    
    def run(self) -> HookResult:
        """Execute enhanced quality check."""
        # Only process file modification tools
        if self.tool_name not in ["Write", "Edit", "MultiEdit"]:
            return HookResult(
                status=HookStatus.SUCCESS,
                message="Not applicable to this tool"
            )
        
        # Extract file path
        file_path = self.tool_args.get("file_path", "")
        if not file_path:
            return HookResult(
                status=HookStatus.WARNING,
                message="Could not extract file path"
            )
        
        # Check if file exists
        if not os.path.exists(file_path):
            return HookResult(
                status=HookStatus.WARNING,
                message=f"File not found: {file_path}"
            )
        
        self.logger.krukai("Python強化版の品質チェックを開始するわ。妥協は許さない", "Quality Check")
        
        # Perform analyses
        all_issues = []
        
        # Code analysis
        self.logger.progress_start("Analyzing code structure")
        code_issues = self.code_analyzer.analyze_file(file_path)
        all_issues.extend(code_issues)
        self.logger.progress_end(True)
        
        # Security analysis
        self.logger.progress_start("Scanning for security vulnerabilities")
        security_issues = self.security_analyzer.scan_file(file_path)
        all_issues.extend(security_issues)
        self.logger.progress_end(True)
        
        # Quality analysis
        self.logger.progress_start("Checking code quality metrics")
        quality_issues, metrics = self.quality_checker.check_file(file_path)
        all_issues.extend(quality_issues)
        self.logger.progress_end(True)
        
        # Generate report
        self._generate_report(file_path, all_issues, metrics)
        
        # Determine overall status
        error_count = sum(1 for issue in all_issues if issue.severity == "error")
        warning_count = sum(1 for issue in all_issues if issue.severity == "warning")
        info_count = sum(1 for issue in all_issues if issue.severity == "info")
        
        if error_count > 0:
            self.logger.vector(f"……{error_count}個の重大な問題を検出。即座に修正が必要……")
            return HookResult(
                status=HookStatus.ERROR,
                message=f"Found {error_count} errors, {warning_count} warnings",
                details=self._format_issues_summary(all_issues)
            )
        elif warning_count > 0:
            self.logger.krukai(f"フン、{warning_count}個の警告があるわね。改善の余地があるわ")
            return HookResult(
                status=HookStatus.WARNING,
                message=f"Found {warning_count} warnings, {info_count} suggestions",
                details=self._format_issues_summary(all_issues)
            )
        elif info_count > 0:
            self.logger.springfield("いくつか改善提案がありますが、全体的に良いコードですね")
            return HookResult(
                status=HookStatus.SUCCESS,
                message=f"Code looks good with {info_count} suggestions"
            )
        else:
            self.logger.springfield("素晴らしい！完璧な品質です", "Perfect Score")
            return HookResult(
                status=HookStatus.SUCCESS,
                message="Excellent code quality - no issues found!"
            )
    
    def _generate_report(self, file_path: str, issues: list, metrics):
        """Generate detailed quality report."""
        sections = {}
        
        # File info
        sections["File Information"] = {
            "Path": file_path,
            "Language": Path(file_path).suffix,
            "Size": f"{os.path.getsize(file_path) / 1024:.1f} KB"
        }
        
        # Metrics
        if metrics:
            sections["Code Metrics"] = {
                "Lines of Code": metrics.lines_of_code,
                "Cyclomatic Complexity": metrics.cyclomatic_complexity,
                "Maintainability Index": f"{metrics.maintainability_index:.1f}/100",
                "Code Duplication": f"{metrics.code_duplication:.1f}%"
            }
        
        # Issues by category
        security_issues = [i for i in issues if i.category == "security"]
        quality_issues = [i for i in issues if i.category == "quality"]
        style_issues = [i for i in issues if i.category == "style"]
        
        if security_issues:
            sections["Security Issues"] = [
                f"Line {i.line}: {i.message}" for i in security_issues[:5]
            ]
        
        if quality_issues:
            sections["Quality Issues"] = [
                f"Line {i.line}: {i.message}" for i in quality_issues[:5]
            ]
        
        if style_issues:
            sections["Style Issues"] = [
                f"Line {i.line}: {i.message}" for i in style_issues[:5]
            ]
        
        # Issue summary
        sections["Summary"] = {
            "Total Issues": len(issues),
            "Errors": sum(1 for i in issues if i.severity == "error"),
            "Warnings": sum(1 for i in issues if i.severity == "warning"),
            "Info": sum(1 for i in issues if i.severity == "info")
        }
        
        self.logger.report("Enhanced Code Quality Report", sections)
    
    def _format_issues_summary(self, issues: list) -> str:
        """Format issues for shell output."""
        if not issues:
            return ""
        
        # Group by severity
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        summary = []
        
        if errors:
            summary.append("Errors:")
            for issue in errors[:3]:  # Show first 3
                summary.append(f"  • Line {issue.line}: {issue.message}")
            if len(errors) > 3:
                summary.append(f"  • ... and {len(errors) - 3} more errors")
        
        if warnings:
            summary.append("\nWarnings:")
            for issue in warnings[:3]:  # Show first 3
                summary.append(f"  • Line {issue.line}: {issue.message}")
            if len(warnings) > 3:
                summary.append(f"  • ... and {len(warnings) - 3} more warnings")
        
        return "\n".join(summary)


if __name__ == "__main__":
    hook = EnhancedQualityCheckHook()
    sys.exit(hook.execute())