#!/usr/bin/env python3
"""
Test FULL_LOCAL mode specifically to diagnose why it's failing
"""

import asyncio
import logging
from trinitas_mcp_tools import TrinitasMCPTools
from trinitas_mode_manager import ExecutionMode

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def test_full_local():
    """Test FULL_LOCAL mode setup"""
    print("Testing FULL_LOCAL mode setup")
    print("=" * 60)
    
    tools = TrinitasMCPTools()
    
    # Ensure initialization
    print("\n1. Initializing system...")
    await tools.ensure_initialized()
    
    # Check availability
    print("\n2. Checking availability...")
    mode_info = tools.get_mode_info()
    print(f"   Local LLM: {mode_info['availability']['local_llm']}")
    print(f"   Claude: {mode_info['availability']['claude']}")
    
    # Manual update to ensure Local LLM is available
    print("\n3. Manually updating availability...")
    await tools.mode_manager.update_availability()
    
    # Check again
    mode_info = tools.get_mode_info()
    print(f"   Local LLM: {mode_info['availability']['local_llm']}")
    print(f"   Claude: {mode_info['availability']['claude']}")
    
    # Try to set FULL_LOCAL mode
    print("\n4. Attempting to set FULL_LOCAL mode...")
    result = await tools.set_mode("full_local")
    
    if result.success:
        print(f"   ✅ SUCCESS! Mode set to FULL_LOCAL")
        print(f"   Mode info: {result.data['mode_info']}")
        
        # Test Groza execution with Local LLM
        print("\n5. Testing Groza execution with Local LLM...")
        groza_result = await tools.persona_execute(
            "groza",
            "Provide tactical assessment of deployment strategy",
            {"test": True}
        )
        
        if groza_result.success:
            print(f"   ✅ Groza execution successful")
            print(f"   Executor: {groza_result.metadata.get('executor', 'unknown')}")
            print(f"   Response: {str(groza_result.data)[:200]}...")
        else:
            print(f"   ❌ Groza execution failed: {groza_result.error}")
    else:
        print(f"   ❌ FAILED: {result.error}")
        
        # Debug mode manager state
        print("\n   Debug info:")
        print(f"   - Current mode: {tools.mode_manager.current_mode}")
        print(f"   - Local LLM available in manager: {tools.mode_manager.local_llm_available}")
        print(f"   - Claude available in manager: {tools.mode_manager.claude_available}")
        
        # Try to check Local LLM directly
        print("\n   Checking Local LLM directly...")
        is_available = await tools.local_llm_client.check_availability()
        print(f"   - Direct check result: {is_available}")

if __name__ == "__main__":
    asyncio.run(test_full_local())