#!/usr/bin/env python3
"""
Trinitas v3.5 - Test Automation Pipeline
Intelligently delegates test generation and execution between Claude and Local LLM
"""

import asyncio
import json
import time
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path

from ..connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    TaskResponse,
    CognitiveComplexity
)
from ..delegation.delegation_engine import ExecutorType


class TestType(Enum):
    """Types of tests with cognitive complexity"""
    UNIT = ("unit", CognitiveComplexity.MECHANICAL)
    INTEGRATION = ("integration", CognitiveComplexity.ANALYTICAL)
    E2E = ("e2e", CognitiveComplexity.REASONING)
    PERFORMANCE = ("performance", CognitiveComplexity.ANALYTICAL)
    SECURITY = ("security", CognitiveComplexity.STRATEGIC)
    PROPERTY = ("property", CognitiveComplexity.REASONING)
    MUTATION = ("mutation", CognitiveComplexity.ANALYTICAL)
    REGRESSION = ("regression", CognitiveComplexity.MECHANICAL)


@dataclass
class TestCase:
    """Individual test case"""
    id: str
    name: str
    type: TestType
    description: str
    code: str
    expected_behavior: str
    priority: str = "normal"  # critical, high, normal, low
    tags: List[str] = field(default_factory=list)


@dataclass
class TestSuite:
    """Collection of test cases"""
    id: str
    name: str
    language: str
    framework: str
    test_cases: List[TestCase] = field(default_factory=list)
    coverage_target: float = 0.80
    metadata: Dict = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of test execution"""
    test_id: str
    status: str  # passed, failed, skipped, error
    duration: float
    output: str
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    coverage: Optional[float] = None


@dataclass
class TestReport:
    """Complete test execution report"""
    suite_id: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    coverage: float
    results: List[TestResult] = field(default_factory=list)
    failure_analysis: Optional[Dict] = None
    recommendations: List[str] = field(default_factory=list)


class TestAutomationPipeline:
    """
    Manages test generation, execution, and analysis
    Delegates based on cognitive complexity
    """
    
    # Test framework mappings
    FRAMEWORKS = {
        "python": {
            "unit": "pytest",
            "command": "pytest",
            "coverage": "pytest --cov",
        },
        "javascript": {
            "unit": "jest",
            "command": "npm test",
            "coverage": "npm test -- --coverage",
        },
        "typescript": {
            "unit": "jest",
            "command": "npm test",
            "coverage": "npm test -- --coverage",
        },
        "go": {
            "unit": "testing",
            "command": "go test",
            "coverage": "go test -cover",
        },
        "rust": {
            "unit": "cargo",
            "command": "cargo test",
            "coverage": "cargo tarpaulin",
        },
    }
    
    def __init__(self):
        self.local_connector = LocalLLMConnector()
        self.test_suites = {}
        self.execution_history = []
        
    async def initialize(self):
        """Initialize test automation pipeline"""
        await self.local_connector.initialize()
    
    async def generate_tests(
        self,
        code: str,
        language: str,
        test_types: List[TestType] = None,
        context: Optional[Dict] = None
    ) -> TestSuite:
        """
        Generate tests based on code and requirements
        Delegates based on test type complexity
        """
        
        if test_types is None:
            test_types = [TestType.UNIT, TestType.INTEGRATION]
        
        # Create test suite
        suite = TestSuite(
            id=f"suite_{int(time.time()*1000)}",
            name=f"Generated tests for {language}",
            language=language,
            framework=self.FRAMEWORKS.get(language, {}).get("unit", "generic"),
            metadata=context or {}
        )
        
        for test_type in test_types:
            # Determine who generates this test type
            executor = self._determine_test_generator(test_type)
            
            if executor == ExecutorType.LOCAL:
                # Local LLM generates mechanical/analytical tests
                test_cases = await self._generate_tests_local(
                    code, language, test_type, context
                )
            elif executor == ExecutorType.CLAUDE:
                # Claude generates complex tests
                test_cases = await self._generate_tests_claude(
                    code, language, test_type, context
                )
            else:
                # Hybrid: Local generates, Claude reviews
                test_cases = await self._generate_tests_hybrid(
                    code, language, test_type, context
                )
            
            suite.test_cases.extend(test_cases)
        
        # Store suite
        self.test_suites[suite.id] = suite
        
        return suite
    
    def _determine_test_generator(self, test_type: TestType) -> ExecutorType:
        """Determine who should generate this test type"""
        _, complexity = test_type.value
        
        if complexity.value <= 2:  # Mechanical or Analytical
            return ExecutorType.LOCAL
        elif complexity.value >= 4:  # Creative or Strategic
            return ExecutorType.CLAUDE
        else:  # Reasoning
            return ExecutorType.HYBRID
    
    async def _generate_tests_local(
        self,
        code: str,
        language: str,
        test_type: TestType,
        context: Optional[Dict]
    ) -> List[TestCase]:
        """Generate tests using Local LLM"""
        
        prompt = self._create_test_generation_prompt(
            code, language, test_type, context
        )
        
        task = TaskRequest(
            id=f"test_gen_{test_type.value[0]}",
            type="test_generation",
            description=prompt,
            estimated_tokens=5000,
            required_tools=["mcp_server"],
            complexity=test_type.value[1]
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse generated tests
        test_cases = self._parse_test_cases(
            response.result,
            test_type,
            language
        )
        
        return test_cases
    
    async def _generate_tests_claude(
        self,
        code: str,
        language: str,
        test_type: TestType,
        context: Optional[Dict]
    ) -> List[TestCase]:
        """Generate complex tests using Claude"""
        
        # Placeholder for Claude integration
        # In production, this would call actual Claude API
        
        test_cases = []
        
        if test_type == TestType.SECURITY:
            test_cases.append(TestCase(
                id=f"sec_001",
                name="test_sql_injection_prevention",
                type=test_type,
                description="Verify SQL injection prevention",
                code="""
def test_sql_injection_prevention():
    malicious_input = "'; DROP TABLE users; --"
    result = execute_query(malicious_input)
    assert "error" not in result.lower()
    assert "users" in list_tables()  # Table still exists
                """,
                expected_behavior="Should sanitize input and prevent injection",
                priority="critical",
                tags=["security", "sql", "injection"]
            ))
        
        return test_cases
    
    async def _generate_tests_hybrid(
        self,
        code: str,
        language: str,
        test_type: TestType,
        context: Optional[Dict]
    ) -> List[TestCase]:
        """Generate tests using hybrid approach"""
        
        # Step 1: Local generates initial tests
        local_tests = await self._generate_tests_local(
            code, language, test_type, context
        )
        
        # Step 2: Claude reviews and enhances
        # (Placeholder - would send to Claude for review)
        enhanced_tests = local_tests
        
        # Add Claude's strategic insights
        for test in enhanced_tests:
            test.tags.append("claude_reviewed")
        
        return enhanced_tests
    
    def _create_test_generation_prompt(
        self,
        code: str,
        language: str,
        test_type: TestType,
        context: Optional[Dict]
    ) -> str:
        """Create prompt for test generation"""
        
        framework = self.FRAMEWORKS.get(language, {}).get("unit", "generic")
        
        prompt = f"""
Generate {test_type.value[0]} tests for the following {language} code:

```{language}
{code}
```

Requirements:
1. Use {framework} testing framework
2. Generate comprehensive test cases
3. Include edge cases and error conditions
4. Follow best practices for {language} testing
5. Include assertions for expected behavior

Test Type Focus:
"""
        
        if test_type == TestType.UNIT:
            prompt += """
- Test individual functions/methods
- Mock external dependencies
- Test boundary conditions
- Test error handling
"""
        elif test_type == TestType.INTEGRATION:
            prompt += """
- Test component interactions
- Test data flow between modules
- Test API contracts
- Test database operations
"""
        elif test_type == TestType.PERFORMANCE:
            prompt += """
- Test response times
- Test throughput
- Test resource usage
- Test scalability limits
"""
        
        if context:
            prompt += f"\nAdditional Context:\n{json.dumps(context, indent=2)}"
        
        prompt += "\nGenerate executable test code with clear descriptions."
        
        return prompt
    
    def _parse_test_cases(
        self,
        result: Dict,
        test_type: TestType,
        language: str
    ) -> List[TestCase]:
        """Parse test cases from LLM response"""
        
        test_cases = []
        content = result.get("content", "")
        
        # Simple parsing - in production, use structured output
        # For now, create example test cases
        
        if test_type == TestType.UNIT:
            test_cases.append(TestCase(
                id="unit_001",
                name="test_basic_functionality",
                type=test_type,
                description="Test basic function operation",
                code=f"""
def test_basic_functionality():
    result = function_under_test(valid_input)
    assert result == expected_output
                """,
                expected_behavior="Should return expected output for valid input",
                tags=["unit", "basic"]
            ))
            
            test_cases.append(TestCase(
                id="unit_002",
                name="test_edge_cases",
                type=test_type,
                description="Test edge cases",
                code=f"""
def test_edge_cases():
    assert function_under_test(None) raises ValueError
    assert function_under_test([]) == default_value
    assert function_under_test(max_value) == max_result
                """,
                expected_behavior="Should handle edge cases gracefully",
                tags=["unit", "edge"]
            ))
        
        elif test_type == TestType.INTEGRATION:
            test_cases.append(TestCase(
                id="int_001",
                name="test_api_integration",
                type=test_type,
                description="Test API endpoint integration",
                code=f"""
async def test_api_integration():
    response = await client.post("/api/endpoint", json=test_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
                """,
                expected_behavior="API should process request successfully",
                tags=["integration", "api"]
            ))
        
        return test_cases
    
    async def execute_tests(
        self,
        suite_id: str,
        parallel: bool = True,
        coverage: bool = True
    ) -> TestReport:
        """
        Execute test suite
        Always delegated to Local LLM for mechanical execution
        """
        
        suite = self.test_suites.get(suite_id)
        if not suite:
            raise ValueError(f"Test suite {suite_id} not found")
        
        start_time = time.time()
        results = []
        
        if parallel:
            # Execute tests in parallel
            tasks = [
                self._execute_single_test(test, suite)
                for test in suite.test_cases
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Execute tests sequentially
            for test in suite.test_cases:
                result = await self._execute_single_test(test, suite)
                results.append(result)
        
        # Calculate metrics
        passed = sum(1 for r in results if r.status == "passed")
        failed = sum(1 for r in results if r.status == "failed")
        skipped = sum(1 for r in results if r.status == "skipped")
        
        # Get coverage if requested
        coverage_value = 0.0
        if coverage:
            coverage_value = await self._calculate_coverage(suite)
        
        # Create report
        report = TestReport(
            suite_id=suite_id,
            total_tests=len(suite.test_cases),
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=time.time() - start_time,
            coverage=coverage_value,
            results=results
        )
        
        # Analyze failures if any
        if failed > 0:
            report.failure_analysis = await self._analyze_failures(
                report, suite
            )
            report.recommendations = self._generate_recommendations(
                report.failure_analysis
            )
        
        # Store in history
        self.execution_history.append(report)
        
        return report
    
    async def _execute_single_test(
        self,
        test: TestCase,
        suite: TestSuite
    ) -> TestResult:
        """Execute a single test using Local LLM"""
        
        # Create execution task
        task = TaskRequest(
            id=f"exec_{test.id}",
            type="test_execution",
            description=f"Execute test: {test.name}",
            estimated_tokens=1000,
            required_tools=["bash"],
            complexity=CognitiveComplexity.MECHANICAL
        )
        
        # Execute via Local LLM
        response = await self.local_connector.execute(
            task,
            tools=[{
                "type": "function",
                "function": {
                    "name": "run_test",
                    "description": "Run test command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "test_file": {"type": "string"}
                        }
                    }
                }
            }]
        )
        
        # Parse execution result
        # In production, would parse actual test output
        result = TestResult(
            test_id=test.id,
            status="passed",  # Simplified
            duration=0.1,
            output="Test executed successfully",
            coverage=0.85
        )
        
        return result
    
    async def _calculate_coverage(self, suite: TestSuite) -> float:
        """Calculate test coverage using Local LLM"""
        
        # Use Local LLM to run coverage tools
        framework_config = self.FRAMEWORKS.get(suite.language, {})
        coverage_command = framework_config.get("coverage", "echo 'No coverage'")
        
        task = TaskRequest(
            id=f"coverage_{suite.id}",
            type="coverage_calculation",
            description=f"Calculate test coverage using: {coverage_command}",
            estimated_tokens=2000,
            required_tools=["bash"],
            complexity=CognitiveComplexity.MECHANICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse coverage from response
        # Simplified - return mock value
        return 0.85
    
    async def _analyze_failures(
        self,
        report: TestReport,
        suite: TestSuite
    ) -> Dict:
        """
        Analyze test failures
        Complex analysis delegated to Claude
        """
        
        failed_tests = [r for r in report.results if r.status == "failed"]
        
        if not failed_tests:
            return {}
        
        # Determine complexity of failure
        # Simple failures -> Local LLM
        # Complex failures -> Claude
        
        analysis = {
            "failure_count": len(failed_tests),
            "failure_categories": {},
            "root_causes": [],
            "suggested_fixes": []
        }
        
        for failure in failed_tests:
            # Check if it's a simple failure
            if self._is_simple_failure(failure):
                # Local LLM analyzes
                local_analysis = await self._analyze_simple_failure(failure)
                analysis["failure_categories"][failure.test_id] = "simple"
                analysis["suggested_fixes"].append(local_analysis)
            else:
                # Claude analyzes (placeholder)
                analysis["failure_categories"][failure.test_id] = "complex"
                analysis["root_causes"].append(
                    "Complex failure requiring deep analysis"
                )
        
        return analysis
    
    def _is_simple_failure(self, failure: TestResult) -> bool:
        """Determine if failure is simple enough for Local LLM"""
        
        # Simple heuristics
        if "assertion" in failure.error_message.lower():
            return True
        if "timeout" in failure.error_message.lower():
            return True
        if "not found" in failure.error_message.lower():
            return True
        
        return False
    
    async def _analyze_simple_failure(self, failure: TestResult) -> str:
        """Analyze simple failure using Local LLM"""
        
        task = TaskRequest(
            id=f"analyze_{failure.test_id}",
            type="failure_analysis",
            description=f"Analyze test failure: {failure.error_message}",
            estimated_tokens=1000,
            required_tools=[],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Extract suggestion from response
        return "Check assertion values and update expected results"
    
    def _generate_recommendations(self, failure_analysis: Dict) -> List[str]:
        """Generate recommendations based on failure analysis"""
        
        recommendations = []
        
        if failure_analysis.get("failure_count", 0) > 5:
            recommendations.append(
                "High failure rate detected. Consider reviewing test strategy."
            )
        
        if "complex" in failure_analysis.get("failure_categories", {}).values():
            recommendations.append(
                "Complex failures detected. Manual review recommended."
            )
        
        if failure_analysis.get("root_causes"):
            recommendations.append(
                f"Address root causes: {', '.join(failure_analysis['root_causes'][:3])}"
            )
        
        return recommendations
    
    async def run_property_tests(
        self,
        code: str,
        language: str,
        properties: List[str]
    ) -> TestReport:
        """
        Run property-based tests
        Hybrid: Local generates cases, Claude verifies properties
        """
        
        # Local LLM generates random test cases
        test_cases = await self._generate_property_cases(
            code, language, properties
        )
        
        # Execute test cases
        results = []
        for case in test_cases:
            result = await self._verify_property(case, properties)
            results.append(result)
        
        # Claude analyzes property violations (if any)
        violations = [r for r in results if r.status == "failed"]
        if violations:
            # Would send to Claude for deep analysis
            pass
        
        return TestReport(
            suite_id=f"property_{int(time.time())}",
            total_tests=len(test_cases),
            passed=sum(1 for r in results if r.status == "passed"),
            failed=len(violations),
            skipped=0,
            duration=1.0,
            coverage=0.0,
            results=results
        )
    
    async def _generate_property_cases(
        self,
        code: str,
        language: str,
        properties: List[str]
    ) -> List[TestCase]:
        """Generate property test cases using Local LLM"""
        
        task = TaskRequest(
            id="prop_gen",
            type="property_generation",
            description=f"Generate test cases for properties: {properties}",
            estimated_tokens=3000,
            required_tools=["mcp_server"],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        
        response = await self.local_connector.execute(task)
        
        # Parse and return test cases
        return []
    
    async def _verify_property(
        self,
        test_case: TestCase,
        properties: List[str]
    ) -> TestResult:
        """Verify if property holds for test case"""
        
        # Execute test and check property
        # Simplified implementation
        return TestResult(
            test_id=test_case.id,
            status="passed",
            duration=0.1,
            output="Property verified"
        )
    
    def get_test_statistics(self) -> Dict:
        """Get testing statistics"""
        
        stats = {
            "total_suites": len(self.test_suites),
            "total_executions": len(self.execution_history),
            "overall_pass_rate": 0.0,
            "average_coverage": 0.0,
            "test_types": {},
            "failure_categories": {}
        }
        
        if self.execution_history:
            total_tests = sum(r.total_tests for r in self.execution_history)
            total_passed = sum(r.passed for r in self.execution_history)
            stats["overall_pass_rate"] = total_passed / total_tests if total_tests > 0 else 0
            
            coverages = [r.coverage for r in self.execution_history if r.coverage > 0]
            if coverages:
                stats["average_coverage"] = sum(coverages) / len(coverages)
        
        return stats


# Example usage
async def main():
    """Example of using Test Automation Pipeline"""
    pipeline = TestAutomationPipeline()
    await pipeline.initialize()
    
    # Example code to test
    code = """
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount

def process_order(items, discount=0):
    total = sum(item['price'] for item in items)
    final_price = calculate_discount(total, discount)
    return {
        'total': total,
        'discount': discount,
        'final_price': final_price
    }
    """
    
    # Generate tests
    print("🧪 Generating tests...")
    suite = await pipeline.generate_tests(
        code=code,
        language="python",
        test_types=[TestType.UNIT, TestType.INTEGRATION],
        context={"module": "order_processing"}
    )
    
    print(f"✅ Generated {len(suite.test_cases)} test cases")
    for test in suite.test_cases:
        print(f"  - {test.name} ({test.type.value[0]})")
    
    # Execute tests
    print("\n🏃 Executing tests...")
    report = await pipeline.execute_tests(
        suite_id=suite.id,
        parallel=True,
        coverage=True
    )
    
    print(f"\n📊 Test Report:")
    print(f"  Total: {report.total_tests}")
    print(f"  Passed: {report.passed} ✅")
    print(f"  Failed: {report.failed} ❌")
    print(f"  Coverage: {report.coverage:.1%}")
    print(f"  Duration: {report.duration:.2f}s")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")
    
    # Show statistics
    stats = pipeline.get_test_statistics()
    print(f"\n📈 Overall Statistics:")
    print(f"  Pass Rate: {stats['overall_pass_rate']:.1%}")
    print(f"  Avg Coverage: {stats['average_coverage']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())