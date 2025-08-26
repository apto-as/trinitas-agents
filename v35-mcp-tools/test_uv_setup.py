#!/usr/bin/env python3
"""
Test script for UV setup
Verifies that all components are properly configured
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_uv_installation():
    """Test if uv is installed"""
    success, stdout, _ = run_command("uv --version")
    if success:
        print(f"✓ uv is installed: {stdout.strip()}")
        return True
    else:
        print("✗ uv is not installed")
        print("  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def test_pyproject():
    """Test if pyproject.toml exists"""
    if Path("pyproject.toml").exists():
        print("✓ pyproject.toml exists")
        return True
    else:
        print("✗ pyproject.toml not found")
        return False

def test_cli_import():
    """Test if CLI module can be imported"""
    try:
        import src.cli
        print("✓ CLI module can be imported")
        return True
    except ImportError as e:
        print(f"✗ Cannot import CLI module: {e}")
        return False

def test_mcp_server_import():
    """Test if MCP server can be imported"""
    try:
        import src.mcp_server
        print("✓ MCP server module can be imported")
        return True
    except ImportError as e:
        print(f"✗ Cannot import MCP server: {e}")
        return False

def test_uv_commands():
    """Test UV commands"""
    commands = [
        ("uv run trinitas-mcp --version", "CLI command"),
        ("uv run python -c 'from src.cli import main'", "CLI entry point"),
        ("uv run python -c 'from src.mcp_server import run_server'", "Server entry point"),
    ]
    
    all_success = True
    for cmd, description in commands:
        success, _, error = run_command(cmd)
        if success:
            print(f"✓ {description} works")
        else:
            print(f"✗ {description} failed: {error[:100]}")
            all_success = False
    
    return all_success

def main():
    """Run all tests"""
    print("🧪 Testing UV Setup for Trinitas MCP Tools")
    print("-" * 40)
    
    tests = [
        ("UV Installation", test_uv_installation),
        ("pyproject.toml", test_pyproject),
        ("CLI Import", test_cli_import),
        ("MCP Server Import", test_mcp_server_import),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results.append(test_func())
    
    # Only test UV commands if UV is installed
    if results[0]:  # UV is installed
        print("\nTesting UV Commands...")
        results.append(test_uv_commands())
    
    # Summary
    print("\n" + "=" * 40)
    if all(results):
        print("✨ All tests passed!")
        print("\nYou can now:")
        print("1. Run: uv run trinitas-setup --auto")
        print("2. Start server: uv run trinitas-server")
        print("3. Use CLI: uv run trinitas-mcp --help")
    else:
        print("⚠ Some tests failed")
        print("\nPlease:")
        print("1. Ensure uv is installed")
        print("2. Run: uv venv && uv pip install -e .")
        print("3. Try again")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())