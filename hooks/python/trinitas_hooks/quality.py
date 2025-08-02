"""
Advanced code quality checks with language-specific rules.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .analyzers import CodeIssue


@dataclass
class QualityMetrics:
    """Code quality metrics for a file."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    code_duplication: float
    test_coverage: Optional[float] = None


class QualityChecker:
    """Advanced code quality analysis."""
    
    def __init__(self):
        """Initialize quality checker."""
        self.metrics: Dict[str, QualityMetrics] = {}
    
    def check_file(self, file_path: str) -> Tuple[List[CodeIssue], QualityMetrics]:
        """Perform comprehensive quality check on a file."""
        issues = []
        
        if not os.path.exists(file_path):
            return issues, None
        
        # Basic metrics
        metrics = self._calculate_metrics(file_path)
        
        # Language-specific checks
        ext = Path(file_path).suffix.lower()
        
        if ext == ".py":
            issues.extend(self._check_python_quality(file_path))
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            issues.extend(self._check_javascript_quality(file_path))
        elif ext in [".go"]:
            issues.extend(self._check_go_quality(file_path))
        
        # Universal checks
        issues.extend(self._check_universal_quality(file_path))
        
        return issues, metrics
    
    def _calculate_metrics(self, file_path: str) -> QualityMetrics:
        """Calculate basic code metrics."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Count actual lines of code (not empty or comments)
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith(("#", "//")))
            
            # Simple complexity calculation (very basic)
            complexity = self._calculate_cyclomatic_complexity(lines)
            
            # Simple maintainability index (based on LOC and complexity)
            maintainability = max(0, 100 - (complexity * 2) - (loc / 10))
            
            # Check for code duplication (very basic)
            duplication = self._check_duplication(lines)
            
            return QualityMetrics(
                file_path=file_path,
                lines_of_code=loc,
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                code_duplication=duplication
            )
        except Exception:
            return QualityMetrics(
                file_path=file_path,
                lines_of_code=0,
                cyclomatic_complexity=0,
                maintainability_index=0.0,
                code_duplication=0.0
            )
    
    def _calculate_cyclomatic_complexity(self, lines: List[str]) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = [
            r"\bif\b", r"\belif\b", r"\belse\b", r"\bfor\b", r"\bwhile\b",
            r"\bcase\b", r"\bcatch\b", r"\bexcept\b", r"\b\?\s*:", r"\b&&\b", r"\b\|\|\b"
        ]
        
        for line in lines:
            for keyword in decision_keywords:
                if re.search(keyword, line):
                    complexity += 1
        
        return complexity
    
    def _check_duplication(self, lines: List[str]) -> float:
        """Check for code duplication (simplified)."""
        # Very basic: count duplicate non-empty lines
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        unique_lines = set(non_empty_lines)
        duplication_ratio = 1.0 - (len(unique_lines) / len(non_empty_lines))
        
        return duplication_ratio * 100
    
    def _check_python_quality(self, file_path: str) -> List[CodeIssue]:
        """Python-specific quality checks."""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for missing docstrings on functions/classes
                if re.match(r"^(class|def)\s+\w+", line):
                    # Check if next non-empty line is a docstring
                    j = i
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines) and not lines[j].strip().startswith('"""'):
                        issues.append(CodeIssue(
                            file=file_path,
                            line=i,
                            column=0,
                            severity="info",
                            category="style",
                            message="Missing docstring",
                            suggestion="Add a docstring to document this function/class"
                        ))
                
                # Check for TODO/FIXME comments
                if re.search(r"\b(TODO|FIXME|XXX|HACK)\b", line):
                    issues.append(CodeIssue(
                        file=file_path,
                        line=i,
                        column=0,
                        severity="info",
                        category="quality",
                        message="TODO/FIXME comment found",
                        suggestion="Address this technical debt"
                    ))
                
                # Check for magic numbers
                if re.search(r"\b\d{2,}\b", line) and not re.search(r"(#|//|\"|\').*\d{2,}", line):
                    issues.append(CodeIssue(
                        file=file_path,
                        line=i,
                        column=0,
                        severity="info",
                        category="style",
                        message="Magic number detected",
                        suggestion="Consider using a named constant"
                    ))
                    
        except Exception:
            pass
        
        return issues
    
    def _check_javascript_quality(self, file_path: str) -> List[CodeIssue]:
        """JavaScript/TypeScript-specific quality checks."""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for var usage (prefer let/const)
                if re.search(r"\bvar\s+\w+", line):
                    issues.append(CodeIssue(
                        file=file_path,
                        line=i,
                        column=line.index("var"),
                        severity="warning",
                        category="style",
                        message="'var' declaration found",
                        suggestion="Use 'let' or 'const' instead"
                    ))
                
                # Check for == instead of ===
                if "==" in line and "===" not in line and "!==" not in line:
                    issues.append(CodeIssue(
                        file=file_path,
                        line=i,
                        column=line.index("=="),
                        severity="warning",
                        category="quality",
                        message="Loose equality comparison",
                        suggestion="Use === for strict equality"
                    ))
                
                # Check for missing semicolons (basic)
                if not line.strip().endswith((";", "{", "}", ",", ":", "//")) and line.strip():
                    if re.search(r"(const|let|var|return|break|continue)\s+", line):
                        issues.append(CodeIssue(
                            file=file_path,
                            line=i,
                            column=len(line.rstrip()),
                            severity="info",
                            category="style",
                            message="Missing semicolon",
                            suggestion="Add semicolon for consistency"
                        ))
                        
        except Exception:
            pass
        
        return issues
    
    def _check_go_quality(self, file_path: str) -> List[CodeIssue]:
        """Go-specific quality checks."""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for error handling
                if "err :=" in line:
                    # Check if error is handled in next few lines
                    handled = False
                    for j in range(i, min(i + 5, len(lines))):
                        if "if err != nil" in lines[j]:
                            handled = True
                            break
                    
                    if not handled:
                        issues.append(CodeIssue(
                            file=file_path,
                            line=i,
                            column=line.index("err :="),
                            severity="error",
                            category="quality",
                            message="Unhandled error",
                            suggestion="Check and handle the error"
                        ))
                
                # Check for exported functions without comments
                if re.match(r"^func\s+[A-Z]\w*", line):
                    # Check if previous line is a comment
                    if i > 1 and not lines[i-2].strip().startswith("//"):
                        issues.append(CodeIssue(
                            file=file_path,
                            line=i,
                            column=0,
                            severity="warning",
                            category="style",
                            message="Exported function without comment",
                            suggestion="Add a comment for exported functions"
                        ))
                        
        except Exception:
            pass
        
        return issues
    
    def _check_universal_quality(self, file_path: str) -> List[CodeIssue]:
        """Universal quality checks for all languages."""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
            
            # Check file size
            file_size_kb = len(content) / 1024
            if file_size_kb > 100:
                issues.append(CodeIssue(
                    file=file_path,
                    line=1,
                    column=0,
                    severity="warning",
                    category="quality",
                    message=f"Large file ({file_size_kb:.1f}KB)",
                    suggestion="Consider splitting into smaller modules"
                ))
            
            # Check for very long lines
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(CodeIssue(
                        file=file_path,
                        line=i,
                        column=120,
                        severity="info",
                        category="style",
                        message=f"Line too long ({len(line)} characters)",
                        suggestion="Break into multiple lines for readability"
                    ))
            
            # Check for deeply nested code
            max_indentation = 0
            for line in lines:
                if line.strip():
                    indentation = len(line) - len(line.lstrip())
                    max_indentation = max(max_indentation, indentation)
            
            if max_indentation > 20:  # 5 levels with 4-space indent
                issues.append(CodeIssue(
                    file=file_path,
                    line=1,
                    column=0,
                    severity="warning",
                    category="quality",
                    message="Deeply nested code detected",
                    suggestion="Refactor to reduce nesting levels"
                ))
                
        except Exception:
            pass
        
        return issues