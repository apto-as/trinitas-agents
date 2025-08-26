#!/usr/bin/env python3
"""
Trinitas v3.5 Workflow Templates Engine - Fixed Version
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    description: str
    persona: str
    action: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    validation: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowTemplate:
    """Represents a workflow template"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    personas: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance"""
    id: str
    template_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)

class WorkflowTemplatesEngine:
    """Engine for managing and executing workflow templates"""
    
    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self._register_default_templates()
        logger.info("Workflow Templates Engine initialized")
    
    def _register_default_templates(self):
        """Register default workflow templates"""
        
        # 1. Secure API Development Workflow
        secure_api_template = WorkflowTemplate(
            id="secure_api_development",
            name="Secure API Development",
            description="Complete workflow for developing secure, scalable APIs",
            personas=["springfield", "krukai", "vector"],
            steps=[
                WorkflowStep(
                    name="requirements_analysis",
                    description="Analyze API requirements and constraints",
                    persona="springfield",
                    action="analyze_requirements",
                    parameters={"focus": "api_architecture"}
                ),
                WorkflowStep(
                    name="architecture_design",
                    description="Design API architecture",
                    persona="springfield",
                    action="design_architecture",
                    dependencies=["requirements_analysis"]
                ),
                WorkflowStep(
                    name="security_design",
                    description="Design security layers",
                    persona="vector",
                    action="design_security",
                    dependencies=["architecture_design"]
                ),
                WorkflowStep(
                    name="implementation",
                    description="Implement API endpoints",
                    persona="krukai",
                    action="implement_code",
                    dependencies=["security_design"]
                ),
                WorkflowStep(
                    name="optimization",
                    description="Optimize performance",
                    persona="krukai",
                    action="optimize_performance",
                    dependencies=["implementation"]
                ),
                WorkflowStep(
                    name="security_audit",
                    description="Audit security implementation",
                    persona="vector",
                    action="security_audit",
                    dependencies=["implementation"]
                ),
                WorkflowStep(
                    name="integration_testing",
                    description="Test API integration",
                    persona="springfield",
                    action="integration_test",
                    dependencies=["optimization", "security_audit"]
                )
            ]
        )
        self.register_template(secure_api_template)
        
        # 2. Rapid Prototyping Workflow
        rapid_proto_template = WorkflowTemplate(
            id="rapid_prototyping",
            name="Rapid Prototyping",
            description="Quick MVP development workflow",
            personas=["springfield", "krukai"],
            steps=[
                WorkflowStep(
                    name="concept_validation",
                    description="Validate concept feasibility",
                    persona="springfield",
                    action="validate_concept"
                ),
                WorkflowStep(
                    name="quick_design",
                    description="Create minimal design",
                    persona="springfield",
                    action="quick_design",
                    dependencies=["concept_validation"]
                ),
                WorkflowStep(
                    name="mvp_implementation",
                    description="Implement MVP",
                    persona="krukai",
                    action="implement_mvp",
                    dependencies=["quick_design"]
                ),
                WorkflowStep(
                    name="user_testing",
                    description="Conduct user testing",
                    persona="springfield",
                    action="user_test",
                    dependencies=["mvp_implementation"]
                )
            ]
        )
        self.register_template(rapid_proto_template)
        
        # 3. Code Review and Refactoring Workflow
        code_review_template = WorkflowTemplate(
            id="code_review_refactor",
            name="Code Review and Refactoring",
            description="Comprehensive code review and improvement",
            personas=["krukai", "vector", "springfield"],
            steps=[
                WorkflowStep(
                    name="code_analysis",
                    description="Analyze code structure",
                    persona="krukai",
                    action="analyze_code"
                ),
                WorkflowStep(
                    name="security_review",
                    description="Review security aspects",
                    persona="vector",
                    action="review_security"
                ),
                WorkflowStep(
                    name="architecture_review",
                    description="Review architecture patterns",
                    persona="springfield",
                    action="review_architecture"
                ),
                WorkflowStep(
                    name="refactoring",
                    description="Refactor code",
                    persona="krukai",
                    action="refactor_code",
                    dependencies=["code_analysis", "security_review", "architecture_review"]
                ),
                WorkflowStep(
                    name="validation",
                    description="Validate refactored code",
                    persona="krukai",
                    action="validate_code",
                    dependencies=["refactoring"]
                )
            ]
        )
        self.register_template(code_review_template)
        
        # 4. Production Deployment Workflow
        deployment_template = WorkflowTemplate(
            id="production_deployment",
            name="Production Deployment",
            description="Safe production deployment process",
            personas=["springfield", "vector", "krukai"],
            steps=[
                WorkflowStep(
                    name="pre_deployment_check",
                    description="Pre-deployment validation",
                    persona="springfield",
                    action="pre_deploy_check"
                ),
                WorkflowStep(
                    name="security_scan",
                    description="Final security scan",
                    persona="vector",
                    action="security_scan",
                    dependencies=["pre_deployment_check"]
                ),
                WorkflowStep(
                    name="performance_baseline",
                    description="Establish performance baseline",
                    persona="krukai",
                    action="performance_baseline",
                    dependencies=["pre_deployment_check"]
                ),
                WorkflowStep(
                    name="deployment",
                    description="Deploy to production",
                    persona="springfield",
                    action="deploy",
                    dependencies=["security_scan", "performance_baseline"]
                ),
                WorkflowStep(
                    name="post_deployment_monitoring",
                    description="Monitor deployment",
                    persona="vector",
                    action="monitor",
                    dependencies=["deployment"]
                )
            ]
        )
        self.register_template(deployment_template)
        
        # 5. Bug Fix Workflow
        bug_fix_template = WorkflowTemplate(
            id="bug_fix",
            name="Bug Fix",
            description="Systematic bug fixing process",
            personas=["krukai", "vector", "springfield"],
            steps=[
                WorkflowStep(
                    name="bug_reproduction",
                    description="Reproduce the bug",
                    persona="krukai",
                    action="reproduce_bug"
                ),
                WorkflowStep(
                    name="root_cause_analysis",
                    description="Analyze root cause",
                    persona="krukai",
                    action="analyze_root_cause",
                    dependencies=["bug_reproduction"]
                ),
                WorkflowStep(
                    name="fix_implementation",
                    description="Implement fix",
                    persona="krukai",
                    action="implement_fix",
                    dependencies=["root_cause_analysis"]
                ),
                WorkflowStep(
                    name="security_impact",
                    description="Assess security impact",
                    persona="vector",
                    action="assess_security",
                    dependencies=["fix_implementation"]
                ),
                WorkflowStep(
                    name="regression_testing",
                    description="Test for regressions",
                    persona="springfield",
                    action="regression_test",
                    dependencies=["fix_implementation"]
                ),
                WorkflowStep(
                    name="fix_validation",
                    description="Validate fix",
                    persona="krukai",
                    action="validate_fix",
                    dependencies=["security_impact", "regression_testing"]
                )
            ]
        )
        self.register_template(bug_fix_template)
        
        # 6. Architecture Design Workflow
        architecture_template = WorkflowTemplate(
            id="architecture_design",
            name="Architecture Design",
            description="System architecture design process",
            personas=["springfield", "krukai", "vector"],
            steps=[
                WorkflowStep(
                    name="requirements_gathering",
                    description="Gather system requirements",
                    persona="springfield",
                    action="gather_requirements"
                ),
                WorkflowStep(
                    name="system_design",
                    description="Design system architecture",
                    persona="springfield",
                    action="design_system",
                    dependencies=["requirements_gathering"]
                ),
                WorkflowStep(
                    name="component_design",
                    description="Design components",
                    persona="krukai",
                    action="design_components",
                    dependencies=["system_design"]
                ),
                WorkflowStep(
                    name="data_flow_design",
                    description="Design data flows",
                    persona="krukai",
                    action="design_data_flow",
                    dependencies=["component_design"]
                ),
                WorkflowStep(
                    name="security_architecture",
                    description="Design security architecture",
                    persona="vector",
                    action="design_security_arch",
                    dependencies=["component_design", "data_flow_design"]
                ),
                WorkflowStep(
                    name="scalability_review",
                    description="Review scalability",
                    persona="springfield",
                    action="review_scalability",
                    dependencies=["data_flow_design"]
                ),
                WorkflowStep(
                    name="architecture_validation",
                    description="Validate architecture",
                    persona="springfield",
                    action="validate_architecture",
                    dependencies=["security_architecture", "scalability_review"]
                )
            ]
        )
        self.register_template(architecture_template)
    
    def register_template(self, template: WorkflowTemplate):
        """Register a workflow template"""
        self.templates[template.id] = template
        logger.info(f"Registered workflow template: {template.name}")
    
    def get_available_templates(self) -> List[str]:
        """Get list of available workflow templates"""
        return list(self.templates.keys())
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """Get details about a workflow template"""
        if template_id not in self.templates:
            raise ValueError(f"Unknown workflow template: {template_id}")
        
        template = self.templates[template_id]
        return {
            "name": template.name,
            "description": template.description,
            "steps": [
                {
                    "name": step.name,
                    "description": step.description,
                    "persona": step.persona,
                    "dependencies": step.dependencies
                }
                for step in template.steps
            ],
            "personas": template.personas,
            "metadata": template.metadata
        }
    
    async def execute_workflow(
        self,
        template_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a workflow template
        
        Args:
            template_id: Template to execute
            parameters: Workflow parameters
            context: Optional initial context
            parallel: Whether to execute steps in parallel
            
        Returns:
            Workflow execution result dictionary
        """
        if template_id not in self.templates:
            raise ValueError(f"Unknown workflow template: {template_id}")
        
        template = self.templates[template_id]
        
        # Create execution
        execution = WorkflowExecution(
            id=f"exec_{datetime.now().timestamp()}",
            template_id=template_id,
            status=WorkflowStatus.PENDING,
            started_at=datetime.now(),
            context=context or {}
        )
        
        self.executions[execution.id] = execution
        
        # Track parallel execution flag
        execution.context["parallel"] = parallel
        
        try:
            # Execute workflow
            execution.status = WorkflowStatus.RUNNING
            result = await self._execute_template(template, execution, parameters, parallel=parallel)
            
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.results = result
            
            # Return result dictionary
            return {
                "completed": True,
                "total_steps": len(template.steps),
                "execution_time": (execution.completed_at - execution.started_at).total_seconds(),
                "step_results": result,
                "execution_id": execution.id
            }
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            execution.errors.append({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            # Return failure result
            return {
                "completed": False,
                "total_steps": len(template.steps),
                "execution_time": (execution.completed_at - execution.started_at).total_seconds() if execution.completed_at else 0,
                "error": str(e),
                "execution_id": execution.id
            }
    
    async def _execute_template(
        self,
        template: WorkflowTemplate,
        execution: WorkflowExecution,
        parameters: Dict[str, Any],
        parallel: bool = False
    ) -> Dict[str, Any]:
        """Execute workflow template steps"""
        
        results = {}
        completed_steps = set()
        
        # Check if we can execute in parallel
        if parallel:
            independent_steps = [
                step for step in template.steps
                if not step.dependencies
            ]
            
            if len(independent_steps) > 1:
                # Execute independent steps in parallel
                tasks = [
                    self._execute_step(step, execution, parameters)
                    for step in independent_steps
                ]
                parallel_results = await asyncio.gather(*tasks)
                
                for step, result in zip(independent_steps, parallel_results):
                    results[step.name] = result
                    completed_steps.add(step.name)
        
        # Execute remaining steps sequentially
        for step in template.steps:
            if step.name in completed_steps:
                continue
            
            # Check dependencies
            if all(dep in completed_steps for dep in step.dependencies):
                result = await self._execute_step(step, execution, parameters)
                results[step.name] = result
                completed_steps.add(step.name)
        
        return results
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        # Simulate step execution
        logger.info(f"Executing step: {step.name} with persona: {step.persona}")
        
        # In real implementation, this would call the actual persona
        await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "success": True,
            "step": step.name,
            "persona": step.persona,
            "action": step.action,
            "message": f"Step {step.name} completed successfully",
            "duration": 0.1
        }

# Global workflow engine instance
workflow_engine = WorkflowTemplatesEngine()

if __name__ == "__main__":
    # Test workflow engine
    async def test():
        print("Testing Workflow Templates Engine")
        print("=" * 60)
        
        # List templates
        templates = workflow_engine.get_available_templates()
        print(f"Available templates: {templates}")
        
        # Execute a workflow
        result = await workflow_engine.execute_workflow(
            "rapid_prototyping",
            {"project": "test"},
            parallel=True
        )
        
        print(f"\nWorkflow result: {result}")
    
    asyncio.run(test())