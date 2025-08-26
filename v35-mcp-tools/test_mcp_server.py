#!/usr/bin/env python3
"""
Test script for v35-mcp-tools MCP server
"""

import json
import subprocess
import sys
import os
import time

# Set environment
os.environ["MCP_ENGINE_URL"] = "http://localhost:8000"
os.environ["MCP_ENGINE_MODE"] = "hybrid"
os.environ["PYTHONPATH"] = "."

def send_request(request):
    """Send request to MCP server via subprocess"""
    cmd = [sys.executable, "-m", "src.mcp_server"]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/Users/apto-as/workspace/github.com/apto-as/trinitas-agents/v35-mcp-tools"
    )
    
    stdout, stderr = process.communicate(input=json.dumps(request) + "\n", timeout=10)
    
    if stderr:
        print(f"Error: {stderr}")
    
    if stdout:
        try:
            return json.loads(stdout.split('\n')[0])
        except:
            print(f"Raw output: {stdout}")
            return None
    return None

def test_mcp_server():
    """Test MCP server functionality"""
    
    print("=" * 60)
    print("Testing v35-mcp-tools MCP Server")
    print("=" * 60)
    
    # Test 1: Initialize
    print("\n1. Testing initialize...")
    response = send_request({
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": 1,
        "params": {}
    })
    
    if response:
        print(f"✓ Initialize response: {json.dumps(response, indent=2)}")
    else:
        print("✗ Initialize failed")
    
    # Test 2: List tools
    print("\n2. Testing tools/list...")
    response = send_request({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 2,
        "params": {}
    })
    
    if response:
        print(f"✓ Tools available: {len(response.get('result', {}).get('tools', []))} tools")
        for tool in response.get('result', {}).get('tools', []):
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        print("✗ Tools list failed")
    
    # Test 3: Get status
    print("\n3. Testing trinitas_status...")
    response = send_request({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 3,
        "params": {
            "name": "trinitas_status",
            "arguments": {}
        }
    })
    
    if response:
        result = response.get('result', {})
        print(f"✓ Status: Engine={result.get('engine', 'unknown')}, Mode={result.get('mode', 'unknown')}")
    else:
        print("✗ Status check failed")
    
    # Test 4: Execute task (will likely fail without proper backend)
    print("\n4. Testing trinitas_execute...")
    response = send_request({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 4,
        "params": {
            "name": "trinitas_execute",
            "arguments": {
                "persona": "springfield",
                "task": "Test task: Analyze system architecture",
                "context": {"test": True}
            }
        }
    })
    
    if response:
        if 'error' in response:
            print(f"⚠ Execute returned error: {response['error']['message']}")
        else:
            print(f"✓ Execute response received")
    else:
        print("✗ Execute failed")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_mcp_server()