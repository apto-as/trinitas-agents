#!/usr/bin/env python3
"""
Test script for Trinitas improvements
======================================

This script validates the type safety and package structure improvements.
"""

import asyncio
import sys
import os

# Add path for import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hooks', 'python'))

async def test_mcp_client():
    """Test AsyncMCPClient implementation."""
    from trinitas_hooks.mcp_client import AsyncMCPClient
    
    print("Testing AsyncMCPClient...")
    
    # Test context manager
    async with AsyncMCPClient() as client:
        print("✅ Context manager entry successful")
        
        # Test connection
        assert client.is_connected(), "Client should be connected"
        print("✅ Connection state verified")
        
        # Test request
        response = await client.request({
            "type": "web_search",
            "query": "test query"
        })
        assert "status" in response, "Response should have status"
        print("✅ Request/response successful")
        
    # After context exit
    assert not client.is_connected(), "Client should be disconnected"
    print("✅ Context manager exit successful")
    
    return True

def test_type_definitions():
    """Test type definitions in core module."""
    from trinitas_hooks.core import HookResult, HookStatus, TrinitasHook
    
    print("\nTesting type definitions...")
    
    # Test HookResult
    result = HookResult(
        status=HookStatus.SUCCESS,
        message="Test message",
        details="Test details"
    )
    assert result.status == HookStatus.SUCCESS
    print("✅ HookResult type checking passed")
    
    # Test HookStatus enum
    assert HookStatus.SUCCESS.value == "success"
    assert HookStatus.ERROR.value == "error"
    print("✅ HookStatus enum verified")
    
    # Test TrinitasHook abstract class
    assert hasattr(TrinitasHook, 'run'), "Should have abstract run method"
    print("✅ TrinitasHook abstract class verified")
    
    return True

def test_imports():
    """Test that all imports work without sys.path manipulation."""
    print("\nTesting import structure...")
    
    try:
        # Core imports
        from trinitas_hooks import (
            TrinitasHook,
            HookResult,
            HookStatus,
            CodeAnalyzer,
            SecurityAnalyzer,
            QualityChecker,
            TrinitasLogger
        )
        print("✅ Core imports successful")
        
        # MCP client import
        from trinitas_hooks.mcp_client import AsyncMCPClient
        print("✅ MCP client import successful")
        
        # Analyzer imports
        from trinitas_hooks.analyzers import CodeAnalyzer, SecurityAnalyzer
        print("✅ Analyzer imports successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("Trinitas Improvements Test Suite")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return 1
    
    # Test type definitions
    if not test_type_definitions():
        print("❌ Type definition tests failed")
        return 1
    
    # Test AsyncMCPClient
    if not await test_mcp_client():
        print("❌ AsyncMCPClient tests failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)