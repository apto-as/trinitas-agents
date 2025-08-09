#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Security Pre-Check Hook
Pre-execution security validation for file operations

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly security guidance and educational feedback
- Krukai: Efficient security pattern detection and validation algorithms
- Vector: Comprehensive security threat prevention (PRIMARY)
"""

import sys
import json
import re
from typing import Dict, List
from pathlib import Path


class TrinitasSecurityPreCheck:
    """Trinitas-powered pre-execution security validation"""

    def __init__(self):
        # Vector: Critical security patterns to prevent before execution
        self.critical_security_patterns = {
            "secrets_exposure": [
                r'(?i)password\s*=\s*["\'][^"\']{6,}["\']',
                r'(?i)api[_-]?key\s*=\s*["\'][^"\']{16,}["\']',
                r'(?i)secret\s*=\s*["\'][^"\']{12,}["\']',
                r'(?i)token\s*=\s*["\'][^"\']{20,}["\']',
                r"(?i)private[_-]?key\s*=",
                r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
            ],
            "dangerous_operations": [
                r"os\.system\s*\([^)]*[;\|&]",  # Command chaining
                r"subprocess\.call\s*\([^)]*shell\s*=\s*True",
                r"exec\s*\([^)]*input\s*\(",
                r"eval\s*\([^)]*request\.",
                r"__import__\s*\([^)]*input",
            ],
            "injection_vectors": [
                r"(?i)(?:select|insert|update|delete|drop)\s+.*\+.*%s",
                r"innerHTML\s*=\s*.*\+.*input",
                r"document\.write\s*\([^)]*\+",
                r'query\s*=\s*["\'].*\+.*["\']',
            ],
            "insecure_configurations": [
                r"verify\s*=\s*False",
                r"ssl\s*=\s*False",
                r"secure\s*=\s*False",
                r"debug\s*=\s*True.*production",
                r'cors\([^)]*origin\s*=\s*["\']?\*["\']?',
            ],
        }

        # Springfield: Security education and guidance
        self.security_education = {
            "secrets_exposure": {
                "risk": "Hardcoded secrets can be extracted from source code and repositories",
                "solution": "Use environment variables or secure vault systems",
                "example": 'Use os.environ.get("API_KEY") instead of hardcoding',
            },
            "dangerous_operations": {
                "risk": "Dynamic code execution can lead to arbitrary command execution",
                "solution": "Use safe alternatives and input validation",
                "example": "Use subprocess with argument lists instead of shell=True",
            },
            "injection_vectors": {
                "risk": "Injection vulnerabilities allow attackers to manipulate queries/output",
                "solution": "Use parameterized queries and proper escaping",
                "example": 'Use prepared statements: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))',
            },
            "insecure_configurations": {
                "risk": "Insecure configurations disable important security features",
                "solution": "Use secure defaults and enable security features",
                "example": "Enable SSL verification and use secure cookie settings",
            },
        }

        # Krukai: Performance-optimized file type security focus
        self.file_type_risks = {
            ".py": ["secrets_exposure", "dangerous_operations", "injection_vectors"],
            ".js": ["secrets_exposure", "injection_vectors", "insecure_configurations"],
            ".ts": ["secrets_exposure", "injection_vectors", "insecure_configurations"],
            ".php": ["secrets_exposure", "injection_vectors", "dangerous_operations"],
            ".java": ["secrets_exposure", "injection_vectors"],
            ".go": ["secrets_exposure", "dangerous_operations", "injection_vectors"],
            ".rb": ["secrets_exposure", "dangerous_operations", "injection_vectors"],
            ".config": ["secrets_exposure", "insecure_configurations"],
            ".yml": ["secrets_exposure", "insecure_configurations"],
            ".yaml": ["secrets_exposure", "insecure_configurations"],
            ".json": ["secrets_exposure", "insecure_configurations"],
        }

    def validate_content_security(self, content: str, file_path: str) -> Dict:
        """
        Validate content for security issues before execution
        Vector: This is our first line of defense against security vulnerabilities
        """

        file_ext = Path(file_path).suffix.lower()
        applicable_risks = self.file_type_risks.get(
            file_ext, list(self.critical_security_patterns.keys())
        )

        security_issues = []
        risk_level = "SAFE"

        # Check each applicable security pattern
        for risk_type in applicable_risks:
            if risk_type in self.critical_security_patterns:
                patterns = self.critical_security_patterns[risk_type]
                for pattern in patterns:
                    matches = self._find_security_issues(
                        content, pattern, risk_type, file_path
                    )
                    security_issues.extend(matches)

        # Determine overall risk level
        if any(issue["severity"] == "CRITICAL" for issue in security_issues):
            risk_level = "CRITICAL"
        elif any(issue["severity"] == "HIGH" for issue in security_issues):
            risk_level = "HIGH"
        elif security_issues:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "security_issues": security_issues,
            "file_path": file_path,
            "total_issues": len(security_issues),
            "critical_issues": len(
                [i for i in security_issues if i["severity"] == "CRITICAL"]
            ),
            "high_issues": len([i for i in security_issues if i["severity"] == "HIGH"]),
        }

    def _find_security_issues(
        self, content: str, pattern: str, risk_type: str, file_path: str
    ) -> List[Dict]:
        """Find security issues matching a specific pattern"""
        issues = []
        lines = content.split("\n")

        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

            for line_num, line in enumerate(lines, 1):
                if compiled_pattern.search(line):
                    severity = self._determine_severity(risk_type, line)
                    issues.append(
                        {
                            "type": risk_type,
                            "severity": severity,
                            "line": line_num,
                            "code": line.strip(),
                            "file": file_path,
                            "description": self._get_issue_description(risk_type),
                            "remediation": self._get_remediation_advice(risk_type),
                            "educational_content": self.security_education.get(
                                risk_type, {}
                            ),
                        }
                    )
        except re.error:
            # Pattern compilation failed, skip this pattern
            pass

        return issues

    def _determine_severity(self, risk_type: str, code_line: str) -> str:
        """Determine severity based on risk type and context"""
        severity_map = {
            "secrets_exposure": "CRITICAL",
            "dangerous_operations": "CRITICAL",
            "injection_vectors": "HIGH",
            "insecure_configurations": "MEDIUM",
        }

        base_severity = severity_map.get(risk_type, "MEDIUM")

        # Increase severity for production-related code
        if any(
            keyword in code_line.lower() for keyword in ["production", "prod", "live"]
        ):
            if base_severity == "MEDIUM":
                return "HIGH"
            elif base_severity == "HIGH":
                return "CRITICAL"

        return base_severity

    def _get_issue_description(self, risk_type: str) -> str:
        """Get human-readable description of the security issue"""
        descriptions = {
            "secrets_exposure": "Hardcoded credentials or secrets detected in source code",
            "dangerous_operations": "Potentially dangerous dynamic code execution detected",
            "injection_vectors": "Potential injection vulnerability in query or output construction",
            "insecure_configurations": "Insecure configuration setting that disables security features",
        }
        return descriptions.get(risk_type, "Security issue detected")

    def _get_remediation_advice(self, risk_type: str) -> str:
        """Get specific remediation advice"""
        advice = {
            "secrets_exposure": "Move secrets to environment variables or secure vault",
            "dangerous_operations": "Use safe alternatives with proper input validation",
            "injection_vectors": "Use parameterized queries and proper input escaping",
            "insecure_configurations": "Enable security features and use secure defaults",
        }
        return advice.get(risk_type, "Review and fix security configuration")

    def validate_file_operation_security(
        self, tool_name: str, tool_input: Dict
    ) -> Dict:
        """
        Main security validation for file operations
        """

        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            return {
                "security_validation": "SKIPPED",
                "reason": "Tool does not involve file content modification",
            }

        # Extract content and file path
        content = ""
        file_paths = []

        if tool_name in ["Write", "Edit"]:
            content = tool_input.get("content", "")
            file_path = tool_input.get("file_path", "")
            if file_path:
                file_paths.append(file_path)
        elif tool_name == "MultiEdit":
            # Handle MultiEdit operations
            edits = tool_input.get("edits", [])
            file_path = tool_input.get("file_path", "")
            if file_path:
                file_paths.append(file_path)
                # Combine all new_string content for analysis
                content = "\n".join(edit.get("new_string", "") for edit in edits)

        if not content or not file_paths:
            return {
                "security_validation": "SKIPPED",
                "reason": "No content or file path to validate",
            }

        # Validate security for the primary file
        file_path = file_paths[0]
        validation_result = self.validate_content_security(content, file_path)

        # Determine decision based on risk level
        risk_level = validation_result["risk_level"]
        if risk_level == "CRITICAL":
            decision = "BLOCK"
        elif risk_level == "HIGH":
            decision = "WARN"
        else:
            decision = "ALLOW"

        return {
            "security_validation": risk_level,
            "decision": decision,
            "validation_details": validation_result,
            "trinitas_analysis": {
                "springfield": f"Security pre-check completed for {Path(file_path).name}",
                "krukai": f"Efficient pattern matching - {validation_result['total_issues']} issues detected",
                "vector": f"Security validation: {validation_result['critical_issues']} critical issues found",
            },
        }


def main():
    """Main execution function for Claude Code hook integration"""

    try:
        # Parse input from Claude Code
        if len(sys.argv) < 2:
            print(
                json.dumps(
                    {
                        "allowed": True,
                        "message": "No command provided for security pre-check",
                    }
                )
            )
            sys.exit(0)

        command = sys.argv[1] if len(sys.argv) > 1 else ""
        context = {}

        if len(sys.argv) > 2:
            try:
                context = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                context = {"tool": sys.argv[2] if len(sys.argv) > 2 else "unknown"}

        # Extract tool information
        tool_name = context.get("tool_name", context.get("tool", ""))
        tool_input = context.get("tool_input", {})

        # Initialize security pre-checker
        pre_checker = TrinitasSecurityPreCheck()

        # Validate security
        security_result = pre_checker.validate_file_operation_security(
            tool_name, tool_input
        )

        # Generate response
        response = {
            "allowed": security_result.get("decision", "ALLOW") != "BLOCK",
            "security_pre_check": security_result,
            "command": command,
            "tool_context": tool_name,
        }

        # Add detailed security guidance for risky operations
        if security_result.get("decision") in ["BLOCK", "WARN"]:
            validation_details = security_result.get("validation_details", {})
            issues = validation_details.get("security_issues", [])

            if issues:
                response["security_guidance"] = f"""
🛡️ TRINITAS SECURITY PRE-CHECK ALERT

Risk Level: {validation_details.get("risk_level", "UNKNOWN")}
Issues Found: {len(issues)}
Critical: {validation_details.get("critical_issues", 0)}
High: {validation_details.get("high_issues", 0)}

Springfield's Education:
Security issues detected before code execution. Understanding these risks helps build secure coding habits.

Krukai's Analysis:
Efficient security pattern detection identified potential vulnerabilities that should be addressed.

Vector's Warning:
Security validation prevented potentially harmful code from being executed. Review and fix before proceeding.

Top Issues to Address:
{chr(10).join("- " + issue["description"] + f" (Line {issue['line']})" for issue in issues[:3])}

Remediation Guidance:
{chr(10).join("- " + issue["remediation"] for issue in issues[:3])}
"""

        print(json.dumps(response, indent=2))
        sys.exit(0 if response["allowed"] else 1)

    except Exception as e:
        error_response = {
            "allowed": False,
            "error": f"Trinitas security pre-check failed: {str(e)}",
            "trinitas_status": "SECURITY_PRE_CHECK_ERROR",
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
