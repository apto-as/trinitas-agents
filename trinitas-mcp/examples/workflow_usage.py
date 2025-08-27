#!/usr/bin/env python3
"""
Trinitas v3.5 Workflow Usage Examples
Demonstrates how to use workflow templates with context management
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_manager import AdvancedContextManager
from workflow_templates import WorkflowTemplatesEngine

async def example_api_development_workflow():
    """Example: Secure API Development Workflow"""
    print("\n🔐 Example 1: Secure API Development Workflow")
    print("-" * 50)
    
    workflow_engine = WorkflowTemplatesEngine()
    context_manager = AdvancedContextManager()
    
    # Create a session for the workflow
    session_id = context_manager.create_session("api_development_project")
    
    # Define project context
    project_context = {
        "project_name": "Payment Gateway API",
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "requirements": [
            "OAuth2 authentication",
            "Rate limiting",
            "PCI DSS compliance",
            "Webhook support"
        ],
        "team_size": 5,
        "timeline": "3 months"
    }
    
    # Store initial context
    await context_manager.update_session_context(session_id, project_context)
    
    # Execute workflow
    print(f"Starting workflow for: {project_context['project_name']}")
    result = await workflow_engine.execute_workflow(
        "secure_api_development",
        project_context,
        parallel=True  # Execute independent steps in parallel
    )
    
    print(f"\nWorkflow completed: {result['completed']}")
    print(f"Total steps: {result['total_steps']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    
    print("\nStep Results:")
    for step_name, step_result in result['step_results'].items():
        status = "✅" if step_result['success'] else "❌"
        print(f"  {status} {step_name}: {step_result.get('message', 'No message')}")
    
    # Track workflow in session
    await context_manager.track_workflow(
        session_id,
        "secure_api_development",
        project_context,
        result
    )
    
    # Get session summary
    session_info = await context_manager.get_session_info(session_id)
    print(f"\nSession Summary:")
    print(f"  Created: {session_info['created_at']}")
    print(f"  Workflows executed: {len(session_info['workflows'])}")

async def example_rapid_prototyping_workflow():
    """Example: Rapid Prototyping Workflow"""
    print("\n🚀 Example 2: Rapid Prototyping Workflow")
    print("-" * 50)
    
    workflow_engine = WorkflowTemplatesEngine()
    context_manager = AdvancedContextManager()
    
    # Create session
    session_id = context_manager.create_session("mvp_prototype")
    
    # Define MVP context
    project_context = {
        "project_name": "Social Media Analytics Dashboard",
        "tech_stack": {
            "frontend": "React + TypeScript",
            "backend": "Node.js + Express",
            "database": "MongoDB",
            "deployment": "Vercel + Railway"
        },
        "features": [
            "Twitter API integration",
            "Real-time analytics",
            "Sentiment analysis",
            "Export reports"
        ],
        "constraints": [
            "2-week deadline",
            "Single developer",
            "Limited budget"
        ]
    }
    
    # Execute rapid prototyping workflow
    print(f"Building MVP: {project_context['project_name']}")
    result = await workflow_engine.execute_workflow(
        "rapid_prototyping",
        project_context,
        parallel=False  # Sequential for MVP clarity
    )
    
    print(f"\nPrototype Status: {'Ready' if result['completed'] else 'Incomplete'}")
    
    # Analyze critical steps
    critical_steps = ["quick_design", "mvp_implementation", "user_testing"]
    print("\nCritical Steps:")
    for step in critical_steps:
        if step in result['step_results']:
            step_result = result['step_results'][step]
            print(f"  - {step}: {'✅ Success' if step_result['success'] else '❌ Failed'}")

async def example_bug_fix_workflow():
    """Example: Bug Fix Workflow"""
    print("\n🐛 Example 3: Bug Fix Workflow")
    print("-" * 50)
    
    workflow_engine = WorkflowTemplatesEngine()
    context_manager = AdvancedContextManager()
    
    # Create session for bug fix
    session_id = context_manager.create_session("critical_bug_fix")
    
    # Define bug context
    bug_context = {
        "bug_id": "BUG-2024-001",
        "severity": "critical",
        "description": "Memory leak in real-time data processing module",
        "affected_components": [
            "WebSocket handler",
            "Data transformation pipeline",
            "Cache manager"
        ],
        "reported_by": "production monitoring",
        "impact": "Server crashes after 24 hours of operation",
        "reproduction_steps": [
            "Start server with heavy load",
            "Monitor memory usage over 24 hours",
            "Observe gradual memory increase"
        ]
    }
    
    # Execute bug fix workflow
    print(f"Fixing: {bug_context['description']}")
    print(f"Severity: {bug_context['severity'].upper()}")
    
    result = await workflow_engine.execute_workflow(
        "bug_fix",
        bug_context,
        parallel=False  # Sequential for debugging
    )
    
    print(f"\nBug Fix Status: {'Resolved' if result['completed'] else 'Unresolved'}")
    
    # Show fix timeline
    print("\nFix Timeline:")
    for step_name, step_result in result['step_results'].items():
        if step_result['success']:
            print(f"  ✅ {step_name}: {step_result.get('duration', 0):.1f}s")

async def example_architecture_design_workflow():
    """Example: Architecture Design Workflow"""
    print("\n🏗️ Example 4: Architecture Design Workflow")
    print("-" * 50)
    
    workflow_engine = WorkflowTemplatesEngine()
    context_manager = AdvancedContextManager()
    
    # Create session
    session_id = context_manager.create_session("system_architecture")
    
    # Define architecture requirements
    architecture_context = {
        "system_name": "Global Content Delivery Network",
        "scale_requirements": {
            "users": "100M+ monthly active",
            "requests": "1B+ daily",
            "data_transfer": "10PB monthly",
            "regions": ["US", "EU", "APAC", "LATAM"]
        },
        "technical_requirements": [
            "Multi-region deployment",
            "Auto-scaling",
            "99.99% uptime SLA",
            "Sub-50ms latency globally",
            "DDoS protection"
        ],
        "constraints": [
            "AWS-based infrastructure",
            "GDPR compliance",
            "Cost optimization required"
        ]
    }
    
    # Execute architecture design workflow
    print(f"Designing: {architecture_context['system_name']}")
    result = await workflow_engine.execute_workflow(
        "architecture_design",
        architecture_context,
        parallel=True  # Parallel for independent design aspects
    )
    
    print(f"\nDesign Status: {'Complete' if result['completed'] else 'Incomplete'}")
    
    # Show design phases
    design_phases = [
        "requirements_analysis",
        "system_design",
        "component_design",
        "data_flow_design",
        "security_design"
    ]
    
    print("\nDesign Phases:")
    for phase in design_phases:
        if phase in result['step_results']:
            phase_result = result['step_results'][phase]
            status = "✅" if phase_result['success'] else "⚠️"
            print(f"  {status} {phase.replace('_', ' ').title()}")

async def example_context_synchronization():
    """Example: Context Synchronization Between Personas"""
    print("\n🔄 Example 5: Context Synchronization")
    print("-" * 50)
    
    context_manager = AdvancedContextManager()
    
    # Create a session
    session_id = context_manager.create_session("collaborative_development")
    
    # Springfield starts with strategic context
    await context_manager.set_context(
        "project_strategy",
        {
            "goal": "Build scalable e-commerce platform",
            "timeline": "6 months",
            "budget": "$500K",
            "team": 8
        },
        "springfield",
        session_id
    )
    
    print("Springfield's Strategic Context set")
    
    # Sync to Krukai with technical transformation
    await context_manager.sync_context_between_personas(
        session_id,
        "springfield",
        "krukai"
    )
    
    # Krukai adds technical details
    krukai_context = await context_manager.get_context(
        "project_strategy",
        "krukai",
        session_id
    )
    print(f"\nKrukai received context and adds technical perspective")
    
    await context_manager.set_context(
        "technical_specs",
        {
            "architecture": "microservices",
            "stack": ["Python", "React", "PostgreSQL", "Redis"],
            "deployment": "Kubernetes on AWS"
        },
        "krukai",
        session_id
    )
    
    # Sync to Vector for security analysis
    await context_manager.sync_context_between_personas(
        session_id,
        "krukai",
        "vector"
    )
    
    print("Vector analyzes security implications")
    
    await context_manager.set_context(
        "security_requirements",
        {
            "authentication": "OAuth2 + MFA",
            "encryption": "TLS 1.3 + AES-256",
            "compliance": ["PCI-DSS", "GDPR"],
            "vulnerabilities": ["SQL injection", "XSS", "CSRF"]
        },
        "vector",
        session_id
    )
    
    # Get unified context
    session_context = await context_manager.get_session_context(session_id)
    print("\nUnified Session Context:")
    print(f"  Total context items: {len(session_context)}")
    print(f"  Personas involved: Springfield, Krukai, Vector")

async def example_workflow_with_persistence():
    """Example: Workflow with Session Persistence"""
    print("\n💾 Example 6: Persistent Workflow Session")
    print("-" * 50)
    
    context_manager = AdvancedContextManager()
    workflow_engine = WorkflowTemplatesEngine()
    
    # Create persistent session
    session_id = context_manager.create_session("long_running_project")
    
    # Phase 1: Initial development
    print("Phase 1: Starting development workflow...")
    project_context_v1 = {
        "project_name": "Customer Portal",
        "phase": "development",
        "completed_features": []
    }
    
    result1 = await workflow_engine.execute_workflow(
        "rapid_prototyping",
        project_context_v1
    )
    
    # Save to persistent storage
    await context_manager.save_session(session_id)
    print("Session saved to disk")
    
    # Simulate resuming later...
    print("\n[Simulating session resume after break...]")
    
    # Load session
    await context_manager.load_session(session_id)
    print("Session restored from disk")
    
    # Phase 2: Bug fixes
    print("\nPhase 2: Running bug fix workflow...")
    project_context_v2 = {
        "project_name": "Customer Portal",
        "phase": "bug_fixing",
        "bugs_found": 5
    }
    
    result2 = await workflow_engine.execute_workflow(
        "bug_fix",
        project_context_v2
    )
    
    # Phase 3: Production deployment
    print("\nPhase 3: Production deployment workflow...")
    project_context_v3 = {
        "project_name": "Customer Portal",
        "phase": "deployment",
        "environment": "production"
    }
    
    result3 = await workflow_engine.execute_workflow(
        "production_deployment",
        project_context_v3
    )
    
    # Get complete history
    workflows = await context_manager.get_workflow_history(session_id)
    print(f"\nComplete Workflow History:")
    print(f"  Total workflows executed: {len(workflows)}")
    for i, wf in enumerate(workflows, 1):
        print(f"  {i}. {wf['template']} - {wf['timestamp']}")

async def main():
    """Run all workflow examples"""
    print("=" * 60)
    print("🌸 Trinitas v3.5 MCP Tools - Workflow Usage Examples")
    print("=" * 60)
    
    examples = [
        example_api_development_workflow,
        example_rapid_prototyping_workflow,
        example_bug_fix_workflow,
        example_architecture_design_workflow,
        example_context_synchronization,
        example_workflow_with_persistence
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✨ Workflow examples completed!")
    print("These examples show how to leverage Trinitas workflows")
    print("with advanced context management and session persistence.")

if __name__ == "__main__":
    asyncio.run(main())