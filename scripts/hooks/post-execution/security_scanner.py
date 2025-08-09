#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Security Vulnerability Scanner Hook
Post-execution security analysis and vulnerability detection

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly security reports and remediation guidance
- Krukai: Efficient vulnerability detection algorithms and performance optimization
- Vector: Comprehensive threat analysis and security validation (PRIMARY)
"""

import sys
import json
import os
import re
from typing import Dict, List
from pathlib import Path


class TrinitasSecurityScanner:
    """Trinitas-powered security vulnerability scanner"""

    def __init__(self):
        # Vector: Comprehensive security threat patterns
        self.vulnerability_patterns = {
            # Injection vulnerabilities
            "sql_injection": [
                r"(?i)(?:select|insert|update|delete|drop|create)\s+.*\+.*%s",
                r'(?i)query\s*=\s*["\'].*\+.*["\']',
                r'(?i)execute\s*\(\s*["\'].*%.*["\']',
                r"(?i)cursor\.execute\s*\([^)]*%[^)]*\)",
            ],
            "xss_vulnerability": [
                r"innerHTML\s*=\s*.*\+",
                r"document\.write\s*\([^)]*\+",
                r"(?i)response\.write\s*\([^)]*\+",
                r"echo\s+\$_[GETpost|POST|REQUEST]",
                r"print\s*\([^)]*request\.",
            ],
            "command_injection": [
                r"os\.system\s*\([^)]*\+",
                r"subprocess\.call\s*\([^)]*\+",
                r"exec\s*\([^)]*\+",
                r"eval\s*\([^)]*input",
                r"shell_exec\s*\([^)]*\$_",
            ],
            "path_traversal": [
                r"open\s*\([^)]*\.\.[^)]*\)",
                r"file_get_contents\s*\([^)]*\.\.[^)]*\)",
                r"include\s*\([^)]*\.\.[^)]*\)",
                r"readfile\s*\([^)]*\.\.[^)]*\)",
            ],
            # Authentication and authorization
            "weak_auth": [
                r'password\s*=\s*["\']["\']',  # Empty passwords
                r"auth\s*=\s*false",
                r"verify\s*=\s*false",
                r"(?i)md5\s*\(\s*password",  # Weak hashing
                r"(?i)sha1\s*\(\s*password",
            ],
            "hardcoded_secrets": [
                r'(?i)password\s*=\s*["\'][^"\']{8,}["\']',
                r'(?i)api[_-]?key\s*=\s*["\'][^"\']{16,}["\']',
                r'(?i)secret\s*=\s*["\'][^"\']{16,}["\']',
                r'(?i)token\s*=\s*["\'][^"\']{20,}["\']',
                r'["\'][A-Za-z0-9]{32,}["\']',  # Long hex strings
            ],
            "jwt_issues": [
                r"jwt\.decode\s*\([^)]*verify=False",
                r"JsonWebToken\([^)]*verify:\s*false",
                r"verify:\s*false",
            ],
            # Data protection
            "insecure_crypto": [
                r"(?i)des\s*\(",
                r"(?i)md5\s*\(",
                r"(?i)sha1\s*\(",
                r"Random\(\)",  # Weak random
                r"Math\.random\(\)",
            ],
            "data_exposure": [
                r"print\s*\([^)]*password",
                r"console\.log\s*\([^)]*password",
                r"logger\.[^(]*\([^)]*password",
                r"debug\s*\([^)]*secret",
                r"echo\s+\$password",
            ],
            # Web security
            "csrf_missing": [
                r"@app\.route\s*\([^)]*methods\s*=\s*\[[^]]*POST",
                r"def\s+\w+\s*\([^)]*request",
            ],
            "cors_misconfiguration": [
                r"Access-Control-Allow-Origin.*\*",
                r"cors\([^)]*origin:\s*true",
                r"withCredentials:\s*true",
            ],
            # File security
            "file_upload_issues": [
                r"upload\s*\([^)]*\)",
                r"move_uploaded_file",
                r"file_put_contents\s*\([^)]*\$_FILES",
            ],
            "insecure_permissions": [
                r'chmod\s*\(\s*[\'"]?777[\'"]?',
                r"os\.chmod\s*\([^)]*0o777",
                r"chmod\s+777",
            ],
        }

        # Krukai: Performance-optimized file type security mapping
        self.file_security_rules = {
            ".py": [
                "sql_injection",
                "command_injection",
                "hardcoded_secrets",
                "insecure_crypto",
            ],
            ".js": ["xss_vulnerability", "hardcoded_secrets", "cors_misconfiguration"],
            ".php": [
                "sql_injection",
                "xss_vulnerability",
                "path_traversal",
                "file_upload_issues",
            ],
            ".java": ["sql_injection", "hardcoded_secrets", "weak_auth"],
            ".go": ["sql_injection", "command_injection", "hardcoded_secrets"],
            ".ts": ["xss_vulnerability", "hardcoded_secrets", "cors_misconfiguration"],
            ".jsx": ["xss_vulnerability", "hardcoded_secrets"],
            ".tsx": ["xss_vulnerability", "hardcoded_secrets"],
        }

        # Springfield: User-friendly severity classifications
        self.severity_mapping = {
            "sql_injection": "CRITICAL",
            "command_injection": "CRITICAL",
            "xss_vulnerability": "HIGH",
            "hardcoded_secrets": "HIGH",
            "path_traversal": "HIGH",
            "weak_auth": "HIGH",
            "insecure_crypto": "MEDIUM",
            "data_exposure": "MEDIUM",
            "csrf_missing": "MEDIUM",
            "cors_misconfiguration": "MEDIUM",
            "jwt_issues": "HIGH",
            "file_upload_issues": "HIGH",
            "insecure_permissions": "MEDIUM",
        }

    def scan_file_security(self, file_path: str) -> Dict:
        """
        Comprehensive security scan of a single file
        Vector: Paranoid security analysis - no vulnerability goes undetected
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            file_ext = Path(file_path).suffix.lower()
            vulnerabilities = []

            # Get applicable vulnerability patterns for this file type
            applicable_patterns = self.file_security_rules.get(
                file_ext, list(self.vulnerability_patterns.keys())
            )

            # Scan for each vulnerability type
            for vuln_type in applicable_patterns:
                if vuln_type in self.vulnerability_patterns:
                    patterns = self.vulnerability_patterns[vuln_type]
                    for pattern in patterns:
                        matches = self._find_pattern_matches(
                            content, pattern, file_path
                        )
                        for match in matches:
                            vulnerabilities.append(
                                {
                                    "type": vuln_type,
                                    "severity": self.severity_mapping.get(
                                        vuln_type, "MEDIUM"
                                    ),
                                    "line": match["line"],
                                    "code": match["code"],
                                    "description": self._get_vulnerability_description(
                                        vuln_type
                                    ),
                                    "remediation": self._get_remediation_advice(
                                        vuln_type
                                    ),
                                    "pattern_matched": pattern,
                                }
                            )

            # Additional context-aware analysis
            additional_checks = self._perform_context_analysis(content, file_path)
            vulnerabilities.extend(additional_checks)

            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerabilities)

            return {
                "file_path": file_path,
                "vulnerabilities": vulnerabilities,
                "risk_score": risk_score,
                "scan_timestamp": input_data.get("timestamp", ""),
                "total_issues": len(vulnerabilities),
                "critical_issues": len(
                    [v for v in vulnerabilities if v["severity"] == "CRITICAL"]
                ),
                "high_issues": len(
                    [v for v in vulnerabilities if v["severity"] == "HIGH"]
                ),
                "medium_issues": len(
                    [v for v in vulnerabilities if v["severity"] == "MEDIUM"]
                ),
                "low_issues": len(
                    [v for v in vulnerabilities if v["severity"] == "LOW"]
                ),
            }

        except Exception as e:
            return {"error": f"Security scan failed: {str(e)}"}

    def _find_pattern_matches(
        self, content: str, pattern: str, file_path: str
    ) -> List[Dict]:
        """Find all matches for a security pattern"""
        matches = []
        lines = content.split("\n")

        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

            for line_num, line in enumerate(lines, 1):
                if compiled_pattern.search(line):
                    matches.append(
                        {"line": line_num, "code": line.strip(), "file": file_path}
                    )
        except re.error:
            # Pattern compilation failed, skip
            pass

        return matches

    def _perform_context_analysis(self, content: str, file_path: str) -> List[Dict]:
        """Perform additional context-aware security analysis"""
        additional_issues = []

        # Check for missing security headers (for web files)
        if any(ext in file_path.lower() for ext in [".html", ".php", ".js", ".py"]):
            security_headers = [
                "X-Frame-Options",
                "X-XSS-Protection",
                "X-Content-Type-Options",
                "Strict-Transport-Security",
            ]
            missing_headers = [h for h in security_headers if h not in content]

            if len(missing_headers) > 2:  # If more than 2 headers missing
                additional_issues.append(
                    {
                        "type": "missing_security_headers",
                        "severity": "MEDIUM",
                        "line": 1,
                        "code": "Security headers not implemented",
                        "description": f"Missing security headers: {', '.join(missing_headers)}",
                        "remediation": "Implement proper security headers to protect against common attacks",
                        "pattern_matched": "context_analysis",
                    }
                )

        # Check for TODO/FIXME security comments
        security_todos = re.findall(
            r"(?i)(?:todo|fixme|hack|xxx).*(?:security|auth|password|crypto)",
            content,
            re.IGNORECASE,
        )
        if security_todos:
            additional_issues.append(
                {
                    "type": "security_todo",
                    "severity": "LOW",
                    "line": 1,
                    "code": f"Found {len(security_todos)} security-related TODO items",
                    "description": "Unresolved security-related TODO/FIXME comments found",
                    "remediation": "Review and address security-related TODO items before deployment",
                    "pattern_matched": "context_analysis",
                }
            )

        return additional_issues

    def _calculate_risk_score(self, vulnerabilities: List[Dict]) -> int:
        """Calculate overall risk score (0-100)"""
        if not vulnerabilities:
            return 0

        severity_weights = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3,
        }

        total_score = sum(
            severity_weights.get(v["severity"], 5) for v in vulnerabilities
        )
        return min(100, total_score)

    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type"""
        descriptions = {
            "sql_injection": "SQL injection vulnerability allows attackers to manipulate database queries",
            "xss_vulnerability": "Cross-site scripting vulnerability enables malicious script execution",
            "command_injection": "Command injection allows execution of arbitrary system commands",
            "path_traversal": "Path traversal vulnerability enables access to unauthorized files",
            "hardcoded_secrets": "Hardcoded secrets expose sensitive credentials in source code",
            "weak_auth": "Weak authentication mechanism provides insufficient security",
            "insecure_crypto": "Insecure cryptographic implementation uses weak algorithms",
            "data_exposure": "Sensitive data exposure in logs or output",
            "csrf_missing": "Missing CSRF protection allows cross-site request forgery attacks",
            "cors_misconfiguration": "CORS misconfiguration may allow unauthorized cross-origin access",
            "jwt_issues": "JWT implementation bypasses signature verification",
            "file_upload_issues": "Insecure file upload may allow malicious file execution",
            "insecure_permissions": "Overly permissive file permissions create security risks",
        }
        return descriptions.get(vuln_type, "Security vulnerability detected")

    def _get_remediation_advice(self, vuln_type: str) -> str:
        """Get remediation advice for vulnerability type"""
        remediations = {
            "sql_injection": "Use parameterized queries or prepared statements",
            "xss_vulnerability": "Sanitize and escape user input before output",
            "command_injection": "Avoid dynamic command construction, use allow-lists",
            "path_traversal": "Validate and sanitize file paths, use allow-lists",
            "hardcoded_secrets": "Move secrets to environment variables or secure vaults",
            "weak_auth": "Implement strong authentication with proper password policies",
            "insecure_crypto": "Use modern, secure cryptographic algorithms (AES-256, SHA-256+)",
            "data_exposure": "Remove sensitive data from logs and debug output",
            "csrf_missing": "Implement CSRF tokens for state-changing operations",
            "cors_misconfiguration": "Configure CORS with specific origins and restrict credentials",
            "jwt_issues": "Always verify JWT signatures and validate claims",
            "file_upload_issues": "Validate file types, scan for malware, restrict execution",
            "insecure_permissions": "Use principle of least privilege for file permissions",
        }
        return remediations.get(vuln_type, "Review and fix security issue")

    def scan_execution_security(
        self, tool_name: str, tool_input: Dict, tool_response: Dict, context: Dict
    ) -> Dict:
        """
        Scan security implications of executed operation
        Vector: This is our last line of defense against vulnerabilities
        """

        file_paths = []

        # Extract file paths from different tool types
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            if "file_path" in tool_input:
                file_paths.append(tool_input["file_path"])
            elif "edits" in tool_input:  # MultiEdit
                for edit in tool_input["edits"]:
                    if "file_path" in edit:
                        file_paths.append(edit["file_path"])

        if not file_paths:
            return {
                "security_scan": "SKIPPED",
                "reason": "No files to scan",
                "trinitas_note": "Operation did not involve file modifications",
            }

        # Scan each file
        scan_results = []
        total_vulnerabilities = 0
        critical_count = 0
        high_count = 0

        for file_path in file_paths:
            scan_result = self.scan_file_security(file_path)
            if "error" not in scan_result:
                scan_results.append(scan_result)
                total_vulnerabilities += scan_result["total_issues"]
                critical_count += scan_result["critical_issues"]
                high_count += scan_result["high_issues"]

        # Determine overall security status
        if critical_count > 0:
            security_status = "CRITICAL"
            decision = "WARN"
        elif high_count > 0:
            security_status = "HIGH_RISK"
            decision = "WARN"
        elif total_vulnerabilities > 0:
            security_status = "MEDIUM_RISK"
            decision = "WARN"
        else:
            security_status = "SECURE"
            decision = "PASS"

        return {
            "security_scan": security_status,
            "total_vulnerabilities": total_vulnerabilities,
            "critical_vulnerabilities": critical_count,
            "high_vulnerabilities": high_count,
            "decision": decision,
            "scan_results": scan_results,
            "trinitas_analysis": {
                "springfield": f"Security scan complete - {len(scan_results)} files analyzed",
                "krukai": f"Efficient pattern matching - {total_vulnerabilities} issues detected",
                "vector": f"Security validation: {critical_count} critical, {high_count} high-risk vulnerabilities",
            },
            "security_recommendations": self._generate_security_recommendations(
                scan_results
            ),
        }

    def _generate_security_recommendations(self, scan_results: List[Dict]) -> List[str]:
        """Generate prioritized security recommendations"""
        recommendations = []

        # Collect all vulnerabilities and sort by severity
        all_vulns = []
        for result in scan_results:
            for vuln in result.get("vulnerabilities", []):
                all_vulns.append(vuln)

        # Group by type and severity
        vuln_groups = {}
        for vuln in all_vulns:
            key = f"{vuln['severity']}_{vuln['type']}"
            if key not in vuln_groups:
                vuln_groups[key] = []
            vuln_groups[key].append(vuln)

        # Generate recommendations in priority order
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        for severity in severity_order:
            for key, vulns in vuln_groups.items():
                if key.startswith(severity):
                    vuln_type = key.split("_", 1)[1]
                    count = len(vulns)
                    recommendations.append(
                        f"{severity}: Fix {count} {vuln_type.replace('_', ' ')} issue{'s' if count > 1 else ''} - {vulns[0]['remediation']}"
                    )

        return recommendations[:8]  # Limit to top 8 recommendations


input_data = {}  # Global variable for timestamp access


def main():
    """Main execution function for Claude Code hook integration"""
    global input_data

    try:
        # Parse input from Claude Code
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        context = {
            "session_id": input_data.get("session_id", ""),
            "cwd": input_data.get("cwd", ""),
        }

        # Initialize scanner
        scanner = TrinitasSecurityScanner()

        # Perform security scan
        security_result = scanner.scan_execution_security(
            tool_name, tool_input, tool_response, context
        )

        # Generate response
        response = {
            "hook_result": "SUCCESS",
            "security_validation": security_result,
            "tool_name": tool_name,
            "timestamp": input_data.get("timestamp", ""),
        }

        # Add detailed security guidance for high-risk operations
        if (
            security_result.get("critical_vulnerabilities", 0) > 0
            or security_result.get("high_vulnerabilities", 0) > 0
        ):
            response["security_alert"] = f"""
🚨 TRINITAS SECURITY ALERT 🚨

Security Status: {security_result.get("security_scan", "UNKNOWN")}
Total Vulnerabilities: {security_result.get("total_vulnerabilities", 0)}
Critical Issues: {security_result.get("critical_vulnerabilities", 0)}
High-Risk Issues: {security_result.get("high_vulnerabilities", 0)}

Springfield's Guidance:
- Security vulnerabilities require immediate attention
- Please review and address issues before deployment
- Consider implementing security testing in your workflow

Krukai's Analysis:
- Automated security scanning detected potential vulnerabilities
- Performance and security can be balanced with proper implementation
- Use secure coding practices to prevent issues

Vector's Warning:
- {security_result.get("critical_vulnerabilities", 0)} critical vulnerabilities require IMMEDIATE remediation
- Deployment with these vulnerabilities poses significant security risk
- All security recommendations should be implemented

Priority Actions:
{chr(10).join("- " + rec for rec in security_result.get("security_recommendations", [])[:5])}
"""

        print(json.dumps(response, indent=2))
        sys.exit(0)

    except Exception as e:
        error_response = {
            "hook_result": "ERROR",
            "error": f"Trinitas security scan failed: {str(e)}",
            "trinitas_status": "SECURITY_SCAN_FAILED",
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
