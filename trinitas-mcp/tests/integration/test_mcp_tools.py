#!/usr/bin/env python3
"""
Test script for Trinitas v3.5 MCP Tools
Validates all tools and integration points
"""

import asyncio
import json
from typing import Dict, Any
import sys
from datetime import datetime

# Import our tools
from trinitas_mcp_tools import trinitas_tools, PersonaType, CollaborationMode
from component_wrapper import component_wrapper

# Test results collector
test_results = []


async def test_persona_execute():
    """Test individual persona execution"""
    print("\n" + "="*60)
    print("Testing: Persona Execute")
    print("="*60)
    
    personas_to_test = [
        ("springfield", "Design a microservice architecture"),
        ("krukai", "Optimize database queries"),
        ("vector", "Audit security vulnerabilities"),
        ("groza", "Plan deployment strategy"),
        ("littara", "Document API endpoints")
    ]
    
    for persona, task in personas_to_test:
        try:
            result = await trinitas_tools.persona_execute(
                persona=persona,
                task=task,
                context={"test": True}
            )
            
            success = result.success
            print(f"✓ {persona:12} - {task[:30]:30} {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"persona_execute_{persona}",
                "success": success,
                "error": result.error
            })
            
        except Exception as e:
            print(f"✗ {persona:12} - Error: {str(e)}")
            test_results.append({
                "test": f"persona_execute_{persona}",
                "success": False,
                "error": str(e)
            })


async def test_collaboration():
    """Test persona collaboration modes"""
    print("\n" + "="*60)
    print("Testing: Collaboration Modes")
    print("="*60)
    
    collaboration_tests = [
        (["springfield", "krukai"], "sequential", "Review code architecture"),
        (["groza", "littara"], "parallel", "Implement new feature"),
        (["springfield", "krukai", "vector"], "hierarchical", "Plan secure deployment"),
        (["springfield", "krukai", "vector"], "consensus", "Approve production release")
    ]
    
    for personas, mode, task in collaboration_tests:
        try:
            result = await trinitas_tools.collaborate_personas(
                personas=personas,
                task=task,
                mode=mode
            )
            
            success = result.success
            personas_str = "+".join(personas)
            print(f"✓ {mode:12} - {personas_str:25} {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"collaborate_{mode}",
                "success": success,
                "error": result.error
            })
            
        except Exception as e:
            print(f"✗ {mode:12} - Error: {str(e)}")
            test_results.append({
                "test": f"collaborate_{mode}",
                "success": False,
                "error": str(e)
            })


async def test_quality_check():
    """Test quality checking functionality"""
    print("\n" + "="*60)
    print("Testing: Quality Check")
    print("="*60)
    
    test_code = """
def authenticate(username, password):
    # Simple authentication function
    if username == "admin" and password == "password":
        return True
    return False
"""
    
    check_levels = ["basic", "standard", "comprehensive", "paranoid"]
    
    for level in check_levels:
        try:
            result = await trinitas_tools.quality_check(
                code=test_code,
                check_type=level
            )
            
            success = result.success
            score = result.data.get("overall_score", 0) if result.data else 0
            print(f"✓ {level:15} - Score: {score:.2f} {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"quality_check_{level}",
                "success": success,
                "score": score
            })
            
        except Exception as e:
            print(f"✗ {level:15} - Error: {str(e)}")
            test_results.append({
                "test": f"quality_check_{level}",
                "success": False,
                "error": str(e)
            })


async def test_optimization():
    """Test code optimization"""
    print("\n" + "="*60)
    print("Testing: Code Optimization")
    print("="*60)
    
    test_code = """
def slow_function(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
    
    targets = ["performance", "readability", "memory", "maintainability"]
    
    for target in targets:
        try:
            result = await trinitas_tools.optimize_code(
                code=test_code,
                target=target
            )
            
            success = result.success
            print(f"✓ {target:15} - {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"optimize_{target}",
                "success": success
            })
            
        except Exception as e:
            print(f"✗ {target:15} - Error: {str(e)}")
            test_results.append({
                "test": f"optimize_{target}",
                "success": False,
                "error": str(e)
            })


async def test_security_audit():
    """Test security auditing"""
    print("\n" + "="*60)
    print("Testing: Security Audit")
    print("="*60)
    
    vulnerable_code = """
import os
def execute_command(user_input):
    # Dangerous: Direct command execution
    result = os.system(user_input)
    return result
"""
    
    levels = ["basic", "standard", "comprehensive", "paranoid"]
    
    for level in levels:
        try:
            result = await trinitas_tools.security_audit(
                code=vulnerable_code,
                level=level
            )
            
            success = result.success
            score = result.data.get("security_score", 0) if result.data else 0
            print(f"✓ {level:15} - Score: {score:.2f} {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"security_audit_{level}",
                "success": success,
                "score": score
            })
            
        except Exception as e:
            print(f"✗ {level:15} - Error: {str(e)}")
            test_results.append({
                "test": f"security_audit_{level}",
                "success": False,
                "error": str(e)
            })


async def test_component_wrapper():
    """Test component wrapper integration"""
    print("\n" + "="*60)
    print("Testing: Component Wrapper")
    print("="*60)
    
    print(f"v35 Components Available: {component_wrapper.v35_available}")
    
    # Test wrapper functions
    tests = [
        ("execute_persona_task", {
            "persona": "springfield",
            "task": "Test task",
            "context": {}
        }),
        ("run_quality_check", {
            "code": "def test(): pass",
            "check_level": "basic"
        }),
        ("optimize_code", {
            "code": "def slow(): pass",
            "target": "performance"
        })
    ]
    
    for method_name, kwargs in tests:
        try:
            method = getattr(component_wrapper, method_name)
            result = await method(**kwargs)
            success = not isinstance(result, dict) or result.get("success", True)
            print(f"✓ {method_name:25} - {'SUCCESS' if success else 'FAILED'}")
            
            test_results.append({
                "test": f"wrapper_{method_name}",
                "success": success
            })
            
        except Exception as e:
            print(f"✗ {method_name:25} - Error: {str(e)}")
            test_results.append({
                "test": f"wrapper_{method_name}",
                "success": False,
                "error": str(e)
            })


async def test_execution_stats():
    """Test execution statistics"""
    print("\n" + "="*60)
    print("Testing: Execution Statistics")
    print("="*60)
    
    stats = trinitas_tools.get_execution_stats()
    
    print(f"Total Executions: {stats.get('total_executions', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.2%}")
    print(f"Personas Used: {', '.join(stats.get('personas_used', []))}")
    
    test_results.append({
        "test": "execution_stats",
        "success": True,
        "stats": stats
    })


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    successful_tests = sum(1 for t in test_results if t.get("success", False))
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    
    # List failed tests
    failed = [t for t in test_results if not t.get("success", False)]
    if failed:
        print("\nFailed Tests:")
        for test in failed:
            print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
    
    # Save results (convert non-serializable objects)
    serializable_results = []
    for result in test_results:
        clean_result = {}
        for key, value in result.items():
            if hasattr(value, 'isoformat'):  # datetime objects
                clean_result[key] = value.isoformat()
            elif hasattr(value, '__dict__'):  # custom objects
                clean_result[key] = str(value)
            else:
                clean_result[key] = value
        serializable_results.append(clean_result)
    
    with open("test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "successful": successful_tests,
                "failed": total_tests - successful_tests,
                "success_rate": successful_tests/total_tests
            },
            "results": serializable_results
        }, f, indent=2)
    
    print("\nResults saved to test_results.json")


async def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("TRINITAS v3.5 MCP TOOLS - TEST SUITE")
    print("="*60)
    print(f"Starting tests at {datetime.now().isoformat()}")
    
    # Run test suites
    await test_persona_execute()
    await test_collaboration()
    await test_quality_check()
    await test_optimization()
    await test_security_audit()
    await test_component_wrapper()
    await test_execution_stats()
    
    # Print summary
    print_summary()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_all_tests())