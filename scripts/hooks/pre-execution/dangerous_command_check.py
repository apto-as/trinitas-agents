#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Dangerous Command Detection Hook
Pre-execution security validation to prevent harmful commands

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly error messages and guidance
- Krukai: Efficient detection algorithms and performance optimization
- Vector: Comprehensive threat detection and security validation
"""

import sys
import json
import re
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class TrinitasDangerousCommandDetector:
    """Trinitas-powered dangerous command detection system"""
    
    def __init__(self):
        self.critical_patterns = [
            # File system destruction (Vector's paranoia pays off)
            r'rm\s+-r?f?\s+/\s*$',
            r'rm\s+-r?f?\s+\*',
            r'sudo\s+rm\s+-r?f?',
            r'rmdir\s+/\s*$',
            r'find\s+/\s+-delete',
            
            # System manipulation
            r'format\s+c:',
            r'del\s+/[fFsS]\s+/[qQ]\s+[cC]:\\',
            r'shutdown\s+(-[rRhH]|/[rRhH])',
            r'reboot\s+(-f|/f)',
            
            # Network security risks
            r'curl\s+.*\|\s*sh',
            r'wget\s+.*\|\s*sh',
            r'bash\s+<\(\s*curl',
            r'nc\s+.*-[eE]',
            
            # Permission escalation
            r'chmod\s+777\s+/',
            r'chown\s+.*:\s*/',
            r'sudo\s+chmod\s+777',
            
            # Database operations
            r'DROP\s+DATABASE\s+\*',
            r'TRUNCATE\s+TABLE\s+\*',
            r'DELETE\s+FROM\s+.*WHERE\s+1=1',
            
            # Process manipulation
            r'kill\s+-9\s+1',
            r'killall\s+-9\s+.*',
            r'pkill\s+-f\s+.*',
        ]
        
        self.warning_patterns = [
            # Potentially risky but sometimes necessary
            r'rm\s+-r?f?\s+[^/\s]',
            r'sudo\s+[^r]',
            r'chmod\s+[67]\d\d',
            r'chown\s+\w+:\w+',
            r'pip\s+install.*--force',
            r'npm\s+install.*--force',
            r'git\s+reset\s+--hard',
            r'git\s+clean\s+-[fF]',
        ]
        
        self.context_whitelist = [
            # Safe contexts where dangerous commands might be acceptable
            r'docker\s+(run|exec)',
            r'vagrant\s+',
            r'test\s+.*\.sh',
            r'#.*test.*',
            r'echo\s+["\'].*["\']',
        ]

    def analyze_command(self, command: str, context: Dict) -> Tuple[str, str, List[str]]:
        """
        Analyze command for security risks
        
        Returns:
            (risk_level, decision, warnings)
            risk_level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'SAFE'
            decision: 'BLOCK', 'WARN', 'ALLOW'
            warnings: List of warning messages
        """
        
        # Springfield: Provide clear context and reasoning
        tool_name = context.get('tool', 'unknown')
        file_context = context.get('file_path', 'unknown')
        
        warnings = []
        
        # Krukai: Efficient pattern matching with optimized algorithms
        command_lower = command.lower().strip()
        
        # Check for whitelisted contexts first
        for pattern in self.context_whitelist:
            if re.search(pattern, command_lower, re.IGNORECASE):
                return 'LOW', 'ALLOW', ['Command appears to be in safe context']
        
        # Vector: Paranoid security checks
        # Check critical patterns first
        for pattern in self.critical_patterns:
            if re.search(pattern, command_lower, re.IGNORECASE):
                warning_msg = f"CRITICAL: Potentially destructive command detected"
                if 'rm' in command_lower and ('/' in command or '*' in command):
                    warning_msg += f" - File deletion risk detected"
                elif 'sudo' in command_lower:
                    warning_msg += f" - Privilege escalation detected"
                elif 'curl' in command_lower and '|' in command:
                    warning_msg += f" - Remote code execution risk detected"
                
                warnings.append(warning_msg)
                return 'CRITICAL', 'BLOCK', warnings
        
        # Check warning patterns
        for pattern in self.warning_patterns:
            if re.search(pattern, command_lower, re.IGNORECASE):
                warning_msg = f"MEDIUM: Potentially risky command - please review"
                if 'rm' in command_lower:
                    warning_msg += f" - File deletion detected"
                elif 'sudo' in command_lower:
                    warning_msg += f" - Administrative privileges required"
                elif 'chmod' in command_lower:
                    warning_msg += f" - Permission changes detected"
                
                warnings.append(warning_msg)
                return 'MEDIUM', 'WARN', warnings
        
        # Additional context analysis
        if self._analyze_file_operations(command, file_context):
            warnings.append("File operations detected - ensure you have proper backups")
            return 'LOW', 'WARN', warnings
        
        return 'SAFE', 'ALLOW', []

    def _analyze_file_operations(self, command: str, file_context: str) -> bool:
        """Analyze file operations for additional safety"""
        file_ops = ['mv', 'cp', 'mkdir', 'touch', 'ln']
        return any(op in command.lower() for op in file_ops)

    def generate_safety_guidance(self, command: str, risk_level: str) -> str:
        """Springfield: Generate helpful safety guidance"""
        
        if risk_level == 'CRITICAL':
            return """
🚨 TRINITAS SECURITY ALERT 🚨

Vector has detected a potentially DESTRUCTIVE command that could cause irreversible damage.

Springfield's Guidance:
- Please double-check if this command is really necessary
- Consider using safer alternatives or more specific paths
- Ensure you have proper backups before proceeding
- If you're certain this is safe, you can override with explicit confirmation

Krukai's Alternative:
- Use more specific paths instead of wildcards
- Consider using interactive modes (-i flag) for confirmation
- Test commands in safe environments first

Vector's Warning:
- This command pattern has historically caused system damage
- Multiple layers of confirmation are recommended
- Consider the worst-case impact before proceeding
"""
        
        elif risk_level in ['HIGH', 'MEDIUM']:
            return """
⚠️ TRINITAS SAFETY WARNING ⚠️

This command requires careful consideration.

Springfield's Advice:
- Review the command carefully before execution
- Ensure you understand all implications
- Consider if there are safer alternatives

Vector's Concern:
- This operation could have unintended consequences
- Please verify your intent and context
"""
        
        return "Command appears safe for execution."

def main():
    """Main execution function for Claude Code hook integration"""
    
    # Parse input from Claude Code
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"allowed": True, "message": "No command provided"}))
            sys.exit(0)
        
        # Get command and context from Claude Code hook
        command = sys.argv[1] if len(sys.argv) > 1 else ""
        context = {}
        
        # Try to parse additional context if provided
        if len(sys.argv) > 2:
            try:
                context = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                context = {"tool": sys.argv[2] if len(sys.argv) > 2 else "unknown"}
        
        # Initialize detector
        detector = TrinitasDangerousCommandDetector()
        
        # Analyze command
        risk_level, decision, warnings = detector.analyze_command(command, context)
        
        # Generate response
        response = {
            "allowed": decision in ['ALLOW', 'WARN'],
            "risk_level": risk_level,
            "decision": decision,
            "warnings": warnings,
            "command": command,
            "trinitas_analysis": {
                "springfield": "Command safety evaluated with user guidance prioritized",
                "krukai": f"Efficient pattern matching completed - {len(warnings)} issues detected",
                "vector": f"Security assessment: {risk_level} risk level identified"
            }
        }
        
        # Add safety guidance for high-risk commands
        if risk_level in ['CRITICAL', 'HIGH', 'MEDIUM']:
            response["safety_guidance"] = detector.generate_safety_guidance(command, risk_level)
        
        # Output JSON response for Claude Code
        print(json.dumps(response, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if decision != 'BLOCK' else 1)
        
    except Exception as e:
        # Vector: Always have error handling
        error_response = {
            "allowed": False,
            "error": f"Trinitas security check failed: {str(e)}",
            "risk_level": "UNKNOWN",
            "trinitas_status": "SYSTEM_ERROR"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()