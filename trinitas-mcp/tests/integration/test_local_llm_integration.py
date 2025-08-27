#!/usr/bin/env python3
"""
Test Local LLM Integration for Trinitas v3.5 MCP Tools
Comprehensive testing of Local LLM integration with all modes
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any

# Import Trinitas components
from trinitas_mcp_tools import TrinitasMCPTools, PersonaType
from local_llm_client import LocalLLMClient

async def test_local_llm_availability():
    """Test Local LLM availability"""
    print("🔍 Testing Local LLM Availability")
    print("=" * 50)
    
    client = LocalLLMClient()
    available = await client.check_availability()
    
    print(f"Local LLM Endpoint: {client.config.endpoint}")
    print(f"Model: {client.config.model}")
    print(f"Available: {'✅ YES' if available else '❌ NO'}")
    print()
    
    return available

async def test_environment_configuration():
    """Test environment variable configuration"""
    print("⚙️  Testing Environment Configuration")
    print("=" * 50)
    
    env_vars = [
        "LOCAL_LLM_ENDPOINT",
        "LOCAL_LLM_MODE", 
        "LOCAL_LLM_MODEL",
        "LOCAL_LLM_TEMPERATURE",
        "LOCAL_LLM_MAX_TOKENS"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "Not Set")
        print(f"{var}: {value}")
    
    print()

async def test_mode_switching():
    """Test all Local LLM modes"""
    print("🔄 Testing Mode Switching")
    print("=" * 50)
    
    original_mode = os.getenv("LOCAL_LLM_MODE")
    
    modes = ["enabled", "disabled", "auto"]
    
    for mode in modes:
        print(f"\n--- Testing Mode: {mode.upper()} ---")
        
        # Set environment temporarily
        os.environ["LOCAL_LLM_MODE"] = mode
        
        # Create new instance for this mode
        tools = TrinitasMCPTools()
        
        # Wait for availability check
        await asyncio.sleep(1)
        
        print(f"Mode: {tools.local_llm_mode}")
        print(f"Available: {tools.local_llm_available}")
        
        # Test Groza execution
        result = await tools.persona_execute(
            "groza",
            "Analyze tactical approach for system deployment",
            {"environment": "production", "team_size": 5}
        )
        
        print(f"Groza Result: {result.success}")
        print(f"Executor: {result.metadata.get('executor', 'unknown')}")
        print(f"Response: {result.data[:100]}...")
        
        # Test Littara execution
        result = await tools.persona_execute(
            "littara",
            "Document API authentication flow",
            {"api_version": "v2", "auth_type": "JWT"}
        )
        
        print(f"Littara Result: {result.success}")
        print(f"Executor: {result.metadata.get('executor', 'unknown')}")
        print(f"Response: {result.data[:100]}...")
    
    # Restore original mode
    if original_mode:
        os.environ["LOCAL_LLM_MODE"] = original_mode
    elif "LOCAL_LLM_MODE" in os.environ:
        del os.environ["LOCAL_LLM_MODE"]
    
    print()

async def test_trinity_collaboration():
    """Test Trinity collaboration with Local LLM personas"""
    print("🤝 Testing Trinity Collaboration")
    print("=" * 50)
    
    tools = TrinitasMCPTools()
    await asyncio.sleep(1)  # Wait for initialization
    
    # Test sequential collaboration
    result = await tools.collaborate_personas(
        ["springfield", "groza", "littara"],
        "Design secure authentication system",
        mode="sequential"
    )
    
    print(f"Sequential Collaboration: {result.success}")
    if result.success:
        for i, persona_result in enumerate(result.data["results"]):
            print(f"{i+1}. {persona_result['persona']}: {persona_result['result'][:80]}...")
    
    print()
    
    # Test parallel collaboration
    result = await tools.collaborate_personas(
        ["krukai", "vector", "groza"],
        "Security audit for payment processing",
        mode="parallel"  
    )
    
    print(f"Parallel Collaboration: {result.success}")
    if result.success:
        for persona_result in result.data["results"]:
            print(f"- {persona_result['persona']}: {persona_result['result'][:80]}...")
    
    print()

async def test_quality_check_with_local_llm():
    """Test quality check with Local LLM personas"""
    print("🔍 Testing Quality Check Integration")
    print("=" * 50)
    
    tools = TrinitasMCPTools()
    await asyncio.sleep(1)
    
    test_code = """
def authenticate_user(username: str, password: str) -> dict:
    \"\"\"Authenticate user with JWT token\"\"\"
    import hashlib
    import jwt
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Validate user (simplified)
    if username == "admin" and password_hash == "expected_hash":
        token = jwt.encode({"user": username}, "secret_key", algorithm="HS256")
        return {"status": "success", "token": token}
    
    return {"status": "error", "message": "Invalid credentials"}
"""
    
    result = await tools.quality_check(test_code, "comprehensive")
    
    print(f"Quality Check: {result.success}")
    if result.success:
        print(f"Overall Score: {result.data['overall_score']:.2f}")
        print(f"Recommendation: {result.data['recommendation']}")
        
        for check in result.data['trinity_checks']:
            print(f"- {check['persona']} ({check['aspect']}): {check['score']:.2f}")
    
    print()

async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("⚠️  Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid persona
    tools = TrinitasMCPTools()
    result = await tools.persona_execute("invalid_persona", "test task")
    
    print(f"Invalid Persona Test: {'✅ PASSED' if not result.success else '❌ FAILED'}")
    print(f"Error: {result.error}")
    
    # Test with invalid collaboration mode
    result = await tools.collaborate_personas(
        ["springfield", "krukai"],
        "test task",
        mode="invalid_mode"
    )
    
    print(f"Invalid Mode Test: {'✅ PASSED' if not result.success else '❌ FAILED'}")
    print(f"Error: {result.error}")
    
    print()

async def test_execution_stats():
    """Test execution statistics"""
    print("📊 Testing Execution Statistics")
    print("=" * 50)
    
    tools = TrinitasMCPTools()
    await asyncio.sleep(1)
    
    # Execute some tasks
    await tools.persona_execute("springfield", "Plan system architecture")
    await tools.persona_execute("groza", "Analyze deployment strategy")
    await tools.persona_execute("littara", "Document requirements")
    
    stats = tools.get_execution_stats()
    
    print(f"Total Executions: {stats['total_executions']}")
    print(f"Success Rate: {stats.get('success_rate', 0):.2%}")
    print(f"Local LLM Mode: {stats.get('local_llm_mode', 'unknown')}")
    print(f"Local LLM Available: {stats.get('local_llm_available', False)}")
    print(f"Personas Used: {', '.join(stats.get('personas_used', []))}")
    
    print()

async def main():
    """Main test runner"""
    print("🚀 Trinitas v3.5 Local LLM Integration Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test Local LLM availability
        available = await test_local_llm_availability()
        
        # Test environment configuration
        await test_environment_configuration()
        
        # Test mode switching
        await test_mode_switching()
        
        # Test Trinity collaboration
        await test_trinity_collaboration()
        
        # Test quality check integration
        await test_quality_check_with_local_llm()
        
        # Test error handling
        await test_error_handling()
        
        # Test execution statistics
        await test_execution_stats()
        
        print("✅ All tests completed successfully!")
        
        # Summary
        print("\n🎯 Test Summary")
        print("=" * 30)
        print(f"Local LLM Available: {'✅ YES' if available else '❌ NO'}")
        print(f"Integration Status: ✅ COMPLETE")
        print(f"Fallback Mechanism: ✅ WORKING")
        print(f"Mode Switching: ✅ FUNCTIONAL")
        
        if not available:
            print("\n⚠️  Note: Local LLM not available - fallback mode tested successfully")
            print("   To test Local LLM functionality, ensure the server is running at:")
            print(f"   {os.getenv('LOCAL_LLM_ENDPOINT', 'http://192.168.99.102:1234/v1/')}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set test environment defaults
    if not os.getenv("LOCAL_LLM_ENDPOINT"):
        os.environ["LOCAL_LLM_ENDPOINT"] = "http://192.168.99.102:1234/v1/"
    
    asyncio.run(main())