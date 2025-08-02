"""
Tests for Trinitas analyzers.
"""

import os
import tempfile
import pytest
from pathlib import Path

from trinitas_hooks.analyzers import CodeAnalyzer, SecurityAnalyzer, CodeIssue


class TestCodeAnalyzer:
    """Test code analyzer functionality."""
    
    def test_analyze_python_hardcoded_credentials(self):
        """Test detection of hardcoded credentials in Python."""
        analyzer = CodeAnalyzer()
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
# Test file
api_key = "sk-1234567890abcdef"
password = "super_secret_123"
username = "admin"
""")
            f.flush()
            
            issues = analyzer.analyze_file(f.name)
            
        os.unlink(f.name)
        
        # Check results
        assert len(issues) >= 2
        assert any("api_key" in issue.message for issue in issues)
        assert any("password" in issue.message for issue in issues)
        assert all(issue.category == "security" for issue in issues)
    
    def test_analyze_python_bare_except(self):
        """Test detection of bare except clauses."""
        analyzer = CodeAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
try:
    risky_operation()
except:
    pass
""")
            f.flush()
            
            issues = analyzer.analyze_file(f.name)
            
        os.unlink(f.name)
        
        assert len(issues) >= 1
        assert any("bare except" in issue.message.lower() for issue in issues)
    
    def test_analyze_javascript_eval(self):
        """Test detection of eval in JavaScript."""
        analyzer = CodeAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write("""
const userInput = getData();
eval(userInput);  // Dangerous!
""")
            f.flush()
            
            issues = analyzer.analyze_file(f.name)
            
        os.unlink(f.name)
        
        assert len(issues) >= 1
        assert any("eval" in issue.message for issue in issues)
        assert any(issue.severity == "error" for issue in issues)


class TestSecurityAnalyzer:
    """Test security analyzer functionality."""
    
    def test_scan_dangerous_functions(self):
        """Test detection of dangerous functions."""
        analyzer = SecurityAnalyzer()
        
        # Test Python
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import pickle
data = get_user_input()
obj = pickle.loads(data)  # Dangerous!
""")
            f.flush()
            
            issues = analyzer.scan_file(f.name)
            
        os.unlink(f.name)
        
        assert len(issues) >= 1
        assert any("pickle.loads" in issue.message for issue in issues)
    
    def test_scan_sql_injection(self):
        """Test SQL injection detection."""
        analyzer = SecurityAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
user_id = request.args.get('id')
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
db.execute(query)
""")
            f.flush()
            
            issues = analyzer.scan_file(f.name)
            
        os.unlink(f.name)
        
        assert len(issues) >= 1
        assert any("SQL injection" in issue.message for issue in issues)
    
    def test_scan_path_traversal(self):
        """Test path traversal detection."""
        analyzer = SecurityAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
filename = request.args.get('file')
path = "uploads/" + filename
# User could pass ../../etc/passwd
with open(path, 'r') as f:
    content = f.read()
""")
            f.flush()
            
            issues = analyzer.scan_file(f.name)
            
        os.unlink(f.name)
        
        # Should detect the comment about path traversal
        assert any("path traversal" in issue.message.lower() for issue in issues)