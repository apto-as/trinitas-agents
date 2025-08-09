"""
Advanced code analyzers using tree-sitter and AST parsing.
"""

import ast
import importlib.util
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None

if HAS_TREE_SITTER:
    pass


@dataclass
class CodeIssue:
    """Represents a code quality or security issue."""

    file: str
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    category: str  # "security", "quality", "style"
    message: str
    suggestion: Optional[str] = None


class CodeAnalyzer:
    """Advanced code analysis using AST and tree-sitter."""

    def __init__(self, use_tree_sitter: bool = True):
        """Initialize analyzer."""
        self.use_tree_sitter = use_tree_sitter and HAS_TREE_SITTER
        self.issues: List[CodeIssue] = []

    def analyze_file(self, file_path: str) -> List[CodeIssue]:
        """Analyze a single file."""
        self.issues = []

        if not os.path.exists(file_path):
            return self.issues

        # Detect language
        ext = Path(file_path).suffix.lower()

        if ext == ".py":
            self._analyze_python(file_path)
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            self._analyze_javascript(file_path)
        elif ext in [".sh", ".bash"]:
            self._analyze_shell(file_path)

        return self.issues

    def _analyze_python(self, file_path: str):
        """Analyze Python code using AST."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            # Check for various patterns
            for node in ast.walk(tree):
                # Hardcoded credentials
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id.lower()
                            if any(
                                secret in name
                                for secret in ["password", "token", "key", "secret"]
                            ):
                                if isinstance(node.value, ast.Constant):
                                    self.issues.append(
                                        CodeIssue(
                                            file=file_path,
                                            line=node.lineno,
                                            column=node.col_offset,
                                            severity="error",
                                            category="security",
                                            message=f"Hardcoded credential found: {target.id}",
                                            suggestion="Use environment variables or secure credential storage",
                                        )
                                    )

                # Broad exception handling
                elif isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        self.issues.append(
                            CodeIssue(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                severity="warning",
                                category="quality",
                                message="Bare except clause found",
                                suggestion="Specify the exception type to catch",
                            )
                        )

                # eval() usage
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "eval":
                        self.issues.append(
                            CodeIssue(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                severity="error",
                                category="security",
                                message="eval() usage detected",
                                suggestion="Avoid eval() as it can execute arbitrary code",
                            )
                        )

                    # exec() usage
                    elif isinstance(node.func, ast.Name) and node.func.id == "exec":
                        self.issues.append(
                            CodeIssue(
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                severity="error",
                                category="security",
                                message="exec() usage detected",
                                suggestion="Avoid exec() as it can execute arbitrary code",
                            )
                        )

        except Exception as e:
            # If parsing fails, log the error for debugging
            logging.warning(f"Failed to parse Python file {file_path}: {e}")
            return

    def _analyze_javascript(self, file_path: str):
        """Analyze JavaScript/TypeScript code."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Simple pattern matching for now
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # eval() usage
                if "eval(" in line and not line.strip().startswith("//"):
                    self.issues.append(
                        CodeIssue(
                            file=file_path,
                            line=i,
                            column=line.index("eval("),
                            severity="error",
                            category="security",
                            message="eval() usage detected",
                            suggestion="Avoid eval() as it can execute arbitrary code",
                        )
                    )

                # Hardcoded tokens
                if any(
                    pattern in line.lower()
                    for pattern in ["api_key", "apikey", "token", "secret"]
                ):
                    if "=" in line and ('"' in line or "'" in line):
                        if not line.strip().startswith("//"):
                            self.issues.append(
                                CodeIssue(
                                    file=file_path,
                                    line=i,
                                    column=0,
                                    severity="warning",
                                    category="security",
                                    message="Possible hardcoded credential",
                                    suggestion="Use environment variables or config files",
                                )
                            )

                # console.log in production
                if "console.log(" in line and not line.strip().startswith("//"):
                    self.issues.append(
                        CodeIssue(
                            file=file_path,
                            line=i,
                            column=line.index("console.log("),
                            severity="info",
                            category="quality",
                            message="console.log() found",
                            suggestion="Use proper logging library for production",
                        )
                    )

        except Exception as e:
            # Log JavaScript analysis failures for debugging
            logging.warning(f"Failed to analyze JavaScript file {file_path}: {e}")
            return

    def _analyze_shell(self, file_path: str):
        """Analyze shell scripts."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # eval usage
                if "eval " in line and not line.strip().startswith("#"):
                    self.issues.append(
                        CodeIssue(
                            file=file_path,
                            line=i,
                            column=line.index("eval "),
                            severity="warning",
                            category="security",
                            message="eval usage in shell script",
                            suggestion="Consider safer alternatives",
                        )
                    )

                # Unquoted variables
                if "$" in line and not line.strip().startswith("#"):
                    # Simple check for unquoted variables after common commands
                    for cmd in ["rm", "mv", "cp", "mkdir"]:
                        if f"{cmd} $" in line and '"$' not in line:
                            self.issues.append(
                                CodeIssue(
                                    file=file_path,
                                    line=i,
                                    column=line.index(f"{cmd} $"),
                                    severity="warning",
                                    category="quality",
                                    message="Possibly unquoted variable",
                                    suggestion="Quote variables to prevent word splitting",
                                )
                            )

        except Exception as e:
            # Log shell script analysis failures for debugging
            logging.warning(f"Failed to analyze shell file {file_path}: {e}")
            return


class SecurityAnalyzer:
    """Security-focused code analysis."""

    # Common patterns for various security issues
    DANGEROUS_FUNCTIONS = {
        "python": ["eval", "exec", "compile", "__import__", "pickle.loads"],
        "javascript": ["eval", "Function", "setTimeout", "setInterval", "innerHTML"],
        "php": ["eval", "exec", "system", "shell_exec", "passthru"],
    }

    SQL_INJECTION_PATTERNS = [
        r"SELECT.*FROM.*WHERE.*['\"]?\s*\+",
        r"INSERT.*VALUES.*['\"]?\s*\+",
        r"UPDATE.*SET.*['\"]?\s*\+",
        r"DELETE.*FROM.*WHERE.*['\"]?\s*\+",
    ]

    def __init__(self):
        """Initialize security analyzer."""
        self.vulnerabilities: List[CodeIssue] = []

    def scan_file(self, file_path: str) -> List[CodeIssue]:
        """Scan file for security vulnerabilities."""
        self.vulnerabilities = []

        if not os.path.exists(file_path):
            return self.vulnerabilities

        # Detect language
        ext = Path(file_path).suffix.lower()
        language = self._detect_language(ext)

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check for dangerous functions
            if language in self.DANGEROUS_FUNCTIONS:
                for func in self.DANGEROUS_FUNCTIONS[language]:
                    for i, line in enumerate(lines, 1):
                        if func in line and not line.strip().startswith(("#", "//")):
                            self.vulnerabilities.append(
                                CodeIssue(
                                    file=file_path,
                                    line=i,
                                    column=line.index(func),
                                    severity="error",
                                    category="security",
                                    message=f"Dangerous function '{func}' detected",
                                    suggestion="This function can execute arbitrary code",
                                )
                            )

            # Check for SQL injection patterns
            self._check_sql_injection(file_path, lines)

            # Check for path traversal
            self._check_path_traversal(file_path, lines)

        except Exception as e:
            # Log security scan failures for debugging
            logging.warning(f"Failed to scan file {file_path}: {e}")

        return self.vulnerabilities

    def _detect_language(self, ext: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript",
            ".php": "php",
        }
        return ext_map.get(ext, "unknown")

    def _check_sql_injection(self, file_path: str, lines: List[str]):
        """Check for potential SQL injection vulnerabilities."""
        import re

        for pattern in self.SQL_INJECTION_PATTERNS:
            regex = re.compile(pattern, re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    self.vulnerabilities.append(
                        CodeIssue(
                            file=file_path,
                            line=i,
                            column=0,
                            severity="error",
                            category="security",
                            message="Potential SQL injection vulnerability",
                            suggestion="Use parameterized queries or prepared statements",
                        )
                    )

    def _check_path_traversal(self, file_path: str, lines: List[str]):
        """Check for path traversal vulnerabilities."""
        patterns = ["../", "..\\", ".." + os.sep]

        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if pattern in line and not line.strip().startswith(("#", "//")):
                    # Check if it's in a string context
                    if any(q in line for q in ['"', "'"]):
                        self.vulnerabilities.append(
                            CodeIssue(
                                file=file_path,
                                line=i,
                                column=line.index(pattern),
                                severity="warning",
                                category="security",
                                message="Potential path traversal pattern detected",
                                suggestion="Validate and sanitize file paths",
                            )
                        )
