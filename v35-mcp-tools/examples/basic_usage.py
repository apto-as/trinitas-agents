#!/usr/bin/env python3
"""
Trinitas v3.5 Basic Usage Examples
Demonstrates how to use Trinitas MCP Tools with Claude Code
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trinitas_mcp_tools import TrinitasMCPTools

async def example_single_persona():
    """Example: Using a single persona for a task"""
    print("\n🌸 Example 1: Single Persona Execution")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    # Springfield for strategic planning
    result = await tools.persona_execute(
        persona="springfield",
        task="Design a microservices architecture for an e-commerce platform",
        context={"requirements": ["scalability", "high availability", "security"]}
    )
    
    print(f"Springfield's Response:")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.data:
        print(f"Analysis: {result.data.get('analysis', '')[:200]}...")
    
    # Krukai for technical optimization
    result = await tools.persona_execute(
        persona="krukai",
        task="Optimize database query performance for product search",
        context={"current_latency": "500ms", "target": "50ms"}
    )
    
    print(f"\n⚡ Krukai's Response:")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    
    # Vector for security audit
    result = await tools.persona_execute(
        persona="vector",
        task="Identify security vulnerabilities in authentication system",
        context={"auth_type": "JWT", "framework": "Express.js"}
    )
    
    print(f"\n🛡️ Vector's Response:")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")

async def example_collaboration():
    """Example: Multiple personas collaborating"""
    print("\n🤝 Example 2: Trinity Collaboration")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    # Sequential collaboration
    result = await tools.collaborate_personas(
        personas=["springfield", "krukai", "vector"],
        task="Develop a secure, high-performance API endpoint for payment processing",
        mode="sequential",
        context={
            "framework": "Node.js",
            "database": "PostgreSQL",
            "requirements": ["PCI compliance", "sub-100ms latency", "99.99% uptime"]
        }
    )
    
    print("Trinity Collaboration Result:")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.data and "collaboration_results" in result.data:
        for persona, response in result.data["collaboration_results"].items():
            print(f"\n{persona.upper()}:")
            print(f"  - {response.get('analysis', '')[:150]}...")

async def example_quality_check():
    """Example: Code quality checking"""
    print("\n✅ Example 3: Quality Check")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate discounted price"""
    if discount_percent > 100:
        discount_percent = 100
    elif discount_percent < 0:
        discount_percent = 0
    
    discount_amount = price * (discount_percent / 100)
    final_price = price - discount_amount
    
    return final_price
'''
    
    # Basic quality check
    result = await tools.quality_check(sample_code, "basic")
    print("Basic Quality Check:")
    print(f"Success: {result.success}")
    print(f"Score: {result.data.get('score', 'N/A')}/10")
    
    # Comprehensive quality check
    result = await tools.quality_check(sample_code, "comprehensive")
    print("\nComprehensive Quality Check:")
    print(f"Success: {result.success}")
    if result.data:
        print(f"Issues found: {len(result.data.get('issues', []))}")
        print(f"Suggestions: {len(result.data.get('suggestions', []))}")

async def example_natural_request():
    """Example: Natural language request processing"""
    print("\n💬 Example 4: Natural Language Request")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    # Natural language request
    result = await tools.natural_request(
        "I need help optimizing my React application. It's running slowly and has performance issues with large lists."
    )
    
    print("Natural Request Processing:")
    print(f"Success: {result.success}")
    print(f"Suggested Persona: {result.data.get('persona', 'N/A')}")
    print(f"Action Taken: {result.data.get('action', 'N/A')}")
    print(f"Response: {result.message}")

async def example_code_optimization():
    """Example: Code optimization"""
    print("\n⚡ Example 5: Code Optimization")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    unoptimized_code = '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
'''
    
    result = await tools.optimize_code(
        unoptimized_code,
        focus_areas=["performance", "readability"]
    )
    
    print("Code Optimization Result:")
    print(f"Success: {result.success}")
    if result.data:
        print(f"Optimization Applied: {result.data.get('optimization_type', 'N/A')}")
        print(f"Performance Improvement: {result.data.get('improvement', 'N/A')}")
        print("\nOptimized Code:")
        print(result.data.get('optimized_code', 'N/A'))

async def example_security_audit():
    """Example: Security audit"""
    print("\n🔒 Example 6: Security Audit")
    print("-" * 40)
    
    tools = TrinitasMCPTools()
    
    vulnerable_code = '''
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Potential SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    return {'user': user}
'''
    
    result = await tools.security_audit(vulnerable_code)
    
    print("Security Audit Result:")
    print(f"Success: {result.success}")
    if result.data:
        vulnerabilities = result.data.get('vulnerabilities', [])
        print(f"Vulnerabilities Found: {len(vulnerabilities)}")
        for vuln in vulnerabilities:
            print(f"  - {vuln.get('type', 'Unknown')}: {vuln.get('description', '')}")
        
        print("\nRecommendations:")
        for rec in result.data.get('recommendations', []):
            print(f"  - {rec}")

async def main():
    """Run all examples"""
    print("=" * 60)
    print("🌸 Trinitas v3.5 MCP Tools - Basic Usage Examples")
    print("=" * 60)
    
    examples = [
        example_single_persona,
        example_collaboration,
        example_quality_check,
        example_natural_request,
        example_code_optimization,
        example_security_audit
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    print("These examples demonstrate how Trinitas MCP Tools can be used")
    print("directly from Claude Code or any Python application.")

if __name__ == "__main__":
    asyncio.run(main())