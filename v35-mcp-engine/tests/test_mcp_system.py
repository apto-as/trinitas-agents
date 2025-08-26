#!/usr/bin/env python3
"""
Trinitas v3.5 TRUE - MCP System Test Script
Test the integrated MCP orchestration system
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List

# Service URLs
ORCHESTRATOR_URL = "http://localhost:8000"
CLAUDE_MCP_URL = "http://localhost:8001"
LOCAL_MCP_URL = "http://localhost:8002"

class MCPSystemTester:
    """Test the MCP system components"""
    
    def __init__(self):
        self.session = None
        self.results = []
        
    async def initialize(self):
        """Initialize test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def test_service_health(self, name: str, url: str) -> Dict:
        """Test if service is healthy"""
        try:
            async with self.session.get(
                f"{url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "service": name,
                        "status": "healthy",
                        "data": data
                    }
                else:
                    return {
                        "service": name,
                        "status": "unhealthy",
                        "code": response.status
                    }
        except Exception as e:
            return {
                "service": name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_persona_execution(self, persona: str, task: Dict) -> Dict:
        """Test execution with specific persona"""
        try:
            async with self.session.post(
                f"{ORCHESTRATOR_URL}/execute",
                json={
                    "description": task["description"],
                    "preferred_persona": persona,
                    "language": task.get("language", "auto")
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": f"Status {response.status}",
                        "text": await response.text()
                    }
        except Exception as e:
            return {"error": str(e)}
    
    async def test_collaboration(self, personas: List[str], task: Dict, mode: str) -> Dict:
        """Test collaborative execution"""
        try:
            async with self.session.post(
                f"{ORCHESTRATOR_URL}/collaborate",
                json={
                    "task": task,
                    "personas": personas,
                    "mode": mode
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": f"Status {response.status}",
                        "text": await response.text()
                    }
        except Exception as e:
            return {"error": str(e)}
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("Trinitas v3.5 TRUE - MCP System Test")
        print("=" * 60)
        
        # Test 1: Service Health
        print("\n[Test 1] Service Health Checks")
        print("-" * 40)
        
        services = [
            ("Orchestrator", ORCHESTRATOR_URL),
            ("Claude MCP", CLAUDE_MCP_URL),
            ("Local MCP", LOCAL_MCP_URL)
        ]
        
        for name, url in services:
            result = await self.test_service_health(name, url)
            status_icon = "✅" if result["status"] == "healthy" else "❌"
            print(f"{status_icon} {name}: {result['status']}")
            self.results.append(result)
        
        # Test 2: Individual Persona Execution
        print("\n[Test 2] Individual Persona Execution")
        print("-" * 40)
        
        test_tasks = [
            {
                "persona": "springfield",
                "task": {
                    "description": "Design a microservice architecture",
                    "language": "japanese"
                }
            },
            {
                "persona": "krukai",
                "task": {
                    "description": "Optimize database query performance",
                    "language": "japanese"
                }
            },
            {
                "persona": "vector",
                "task": {
                    "description": "Perform security audit on API endpoints",
                    "language": "japanese"
                }
            },
            {
                "persona": "groza",
                "task": {
                    "description": "Plan deployment strategy for production",
                    "language": "english"
                }
            },
            {
                "persona": "littara",
                "task": {
                    "description": "Implement caching layer for API",
                    "language": "english"
                }
            }
        ]
        
        for test in test_tasks:
            print(f"\nTesting {test['persona']}...")
            result = await self.test_persona_execution(test["persona"], test["task"])
            
            if "error" in result:
                print(f"❌ {test['persona']}: {result['error']}")
            else:
                print(f"✅ {test['persona']}: Success")
                print(f"   Executor: {result.get('executor', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0):.2%}")
                print(f"   Duration: {result.get('duration', 0):.2f}s")
        
        # Test 3: Collaborative Execution
        print("\n[Test 3] Collaborative Execution")
        print("-" * 40)
        
        collab_tests = [
            {
                "name": "Trinity Consensus",
                "personas": ["springfield", "krukai", "vector"],
                "mode": "consensus",
                "task": {
                    "description": "Evaluate new framework adoption"
                }
            },
            {
                "name": "Elmo Sequential",
                "personas": ["groza", "littara"],
                "mode": "sequential",
                "task": {
                    "description": "Design and implement REST API"
                }
            },
            {
                "name": "Cross-LLM Parallel",
                "personas": ["springfield", "groza"],
                "mode": "parallel",
                "task": {
                    "description": "Strategic planning for Q4"
                }
            }
        ]
        
        for test in collab_tests:
            print(f"\nTesting {test['name']}...")
            result = await self.test_collaboration(
                test["personas"],
                test["task"],
                test["mode"]
            )
            
            if "error" in result:
                print(f"❌ {test['name']}: {result['error']}")
            else:
                print(f"✅ {test['name']}: Success")
                print(f"   Mode: {result.get('mode', 'unknown')}")
                if test["mode"] == "consensus":
                    print(f"   Consensus: {result.get('consensus', 'unknown')}")
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        healthy_services = sum(1 for r in self.results[:3] if r.get("status") == "healthy")
        print(f"Services Online: {healthy_services}/3")
        
        if healthy_services == 3:
            print("✅ All systems operational - v3.5 TRUE ready!")
        else:
            print("⚠️  Some services unavailable - check Docker containers")

async def main():
    """Main test runner"""
    tester = MCPSystemTester()
    
    try:
        await tester.initialize()
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())