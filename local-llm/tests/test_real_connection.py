#!/usr/bin/env python3
"""
Trinitas v3.5 - Real Local LLM Connection Test
Tests actual connection to Local LLM server
"""

import asyncio
import aiohttp
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    CognitiveComplexity
)


async def test_real_connection():
    """Test actual connection to Local LLM server"""
    print("🔌 Testing Local LLM Server Connection...")
    print("=" * 50)
    
    # Initialize connector
    connector = LocalLLMConnector()
    
    # Check configuration
    print(f"📍 Endpoint: {connector.endpoint}")
    print(f"🔑 API Key Set: {'Yes' if connector.api_key else 'No'}")
    
    # Initialize and check health
    try:
        await connector.initialize()
        print("✅ Session initialized")
        
        # Check health
        health_result = await connector.check_health()
        if health_result:
            print(f"✅ Health check passed - Server is {'healthy' if connector.health_status == 'healthy' else connector.health_status}")
        else:
            print(f"❌ Health check failed - {connector.health_status}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Try a simple task
    print("\n📝 Testing simple task execution...")
    task = TaskRequest(
        id="test-real-001",
        type="simple_test",
        description="Say 'Hello from Local LLM' and nothing else",
        estimated_tokens=100,
        required_tools=[],
        complexity=CognitiveComplexity.MECHANICAL
    )
    
    try:
        response = await connector.execute(task)
        
        if response.errors:
            print(f"❌ Execution errors: {response.errors}")
            return False
        
        print(f"✅ Task executed successfully")
        print(f"📊 Tokens used: {response.tokens_used}")
        print(f"⏱️ Duration: {response.duration:.2f}s")
        print(f"🎯 Confidence: {response.confidence:.2%}")
        print(f"📤 Response: {response.result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False
    
    finally:
        await connector.cleanup()
        print("\n🧹 Cleanup completed")


async def test_server_availability():
    """Quick test to check if server is running"""
    print("🔍 Checking if Local LLM server is available...")
    
    # Get endpoint from config or use default
    connector = LocalLLMConnector()
    endpoint = connector.endpoint
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try to connect to the models endpoint
            async with session.get(f"{endpoint}/models", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server is running at {endpoint}")
                    print(f"📦 Available models: {data.get('data', [])}")
                    return True
                else:
                    print(f"⚠️ Server responded with status {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print(f"❌ Cannot connect to server at {endpoint}")
        print("   Make sure the Local LLM server is running:")
        print("   - Check if Qwen Code is running")
        print("   - Verify endpoint is correct")
        return False
        
    except asyncio.TimeoutError:
        print(f"⏱️ Connection timeout - server not responding")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def main():
    """Run all connection tests"""
    print("🧪 Trinitas v3.5 - Local LLM Connection Test")
    print("=" * 50)
    
    # First check if server is available
    server_available = await test_server_availability()
    
    if not server_available:
        print("\n⚠️ Local LLM server is not available")
        print("Please start the server and try again")
        print("\nExpected setup:")
        print("1. Start Qwen Code with GPT-OSS-120B model")
        print("2. Ensure it's listening on http://localhost:8080")
        print("3. Set LOCAL_LLM_API_KEY environment variable if required")
        return
    
    print("\n" + "=" * 50)
    
    # Test actual connection and execution
    success = await test_real_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All connection tests passed!")
        print("Local LLM is ready for use with Trinitas v3.5")
    else:
        print("❌ Connection tests failed")
        print("Please check the server configuration and logs")


if __name__ == "__main__":
    asyncio.run(main())