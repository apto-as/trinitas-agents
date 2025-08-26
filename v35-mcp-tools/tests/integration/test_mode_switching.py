#!/usr/bin/env python3
"""
Trinitas v3.5 Mode Switching Test Suite
Comprehensive testing for all execution modes and persona combinations
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# Import our modules
from trinitas_mcp_tools import TrinitasMCPTools, PersonaType
from trinitas_mode_manager import ExecutionMode, TrinitasModeManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    error: str = None

class ModeTestSuite:
    """Comprehensive test suite for mode switching system"""
    
    def __init__(self):
        """Initialize test suite"""
        self.results: List[TestResult] = []
        self.tools = TrinitasMCPTools()
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🌸 Trinitas v3.5 Mode Switching Test Suite")
        print("=" * 70)
        print("指揮官、全モードの包括的テストを開始いたします。\n")
        
        # Test categories
        test_categories = [
            ("Basic Functionality", self._test_basic_functionality),
            ("Mode Switching", self._test_mode_switching),
            ("Persona Execution", self._test_persona_execution),
            ("Collaboration", self._test_collaboration_modes),
            ("Error Handling", self._test_error_handling),
            ("Performance", self._test_performance)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n📋 Testing: {category_name}")
            print("-" * 50)
            
            try:
                await test_function()
            except Exception as e:
                logger.error(f"Test category {category_name} failed: {e}")
                self.results.append(TestResult(
                    test_name=f"{category_name}_CATEGORY_ERROR",
                    success=False,
                    duration=0.0,
                    details={},
                    error=str(e)
                ))
        
        # Generate summary report
        return self._generate_test_report()
    
    async def _test_basic_functionality(self):
        """Test basic functionality"""
        
        # Test 1: Initialization
        start_time = datetime.now()
        try:
            tools = TrinitasMCPTools()
            await tools.ensure_initialized()
            
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="initialization",
                success=True,
                duration=duration,
                details={"mode": tools.mode_manager.current_mode.value}
            ))
            print("✓ Initialization test passed")
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="initialization",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            ))
            print(f"✗ Initialization test failed: {e}")
        
        # Test 2: Mode information retrieval
        start_time = datetime.now()
        try:
            mode_info = self.tools.get_mode_info()
            available_modes = self.tools.get_available_modes()
            
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="mode_info_retrieval",
                success=True,
                duration=duration,
                details={
                    "current_mode": mode_info["mode"],
                    "available_modes": list(available_modes.keys())
                }
            ))
            print("✓ Mode information retrieval passed")
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="mode_info_retrieval",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            ))
            print(f"✗ Mode information retrieval failed: {e}")
    
    async def _test_mode_switching(self):
        """Test mode switching functionality"""
        
        modes_to_test = [
            ExecutionMode.SIMULATION,
            ExecutionMode.CLAUDE_ONLY,
            ExecutionMode.HYBRID,
            ExecutionMode.AUTO
        ]
        
        for mode in modes_to_test:
            start_time = datetime.now()
            test_name = f"mode_switch_{mode.value}"
            
            try:
                # Switch to mode
                result = await self.tools.set_mode(mode.value)
                
                if result.success:
                    # Verify mode change
                    current_mode_info = self.tools.get_mode_info()
                    success = current_mode_info["mode"] == mode.value
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    self.results.append(TestResult(
                        test_name=test_name,
                        success=success,
                        duration=duration,
                        details={
                            "target_mode": mode.value,
                            "actual_mode": current_mode_info["mode"],
                            "executors": current_mode_info["executors"]
                        }
                    ))
                    
                    if success:
                        print(f"✓ Mode switch to {mode.value} passed")
                    else:
                        print(f"✗ Mode switch to {mode.value} failed: mode mismatch")
                else:
                    duration = (datetime.now() - start_time).total_seconds()
                    self.results.append(TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        details={},
                        error=result.error or "Mode switch returned failure"
                    ))
                    print(f"✗ Mode switch to {mode.value} failed: {result.error}")
                    
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.results.append(TestResult(
                    test_name=test_name,
                    success=False,
                    duration=duration,
                    details={},
                    error=str(e)
                ))
                print(f"✗ Mode switch to {mode.value} failed: {e}")
    
    async def _test_persona_execution(self):
        """Test persona execution in different modes"""
        
        personas_to_test = [
            PersonaType.SPRINGFIELD,
            PersonaType.KRUKAI,
            PersonaType.VECTOR,
            PersonaType.GROZA,
            PersonaType.LITTARA
        ]
        
        modes_to_test = [
            ExecutionMode.SIMULATION,
            ExecutionMode.CLAUDE_ONLY,
            ExecutionMode.HYBRID
        ]
        
        test_task = "Analyze system architecture for scalability improvements"
        
        for mode in modes_to_test:
            # Switch to mode first
            await self.tools.set_mode(mode.value)
            
            for persona in personas_to_test:
                start_time = datetime.now()
                test_name = f"persona_execution_{mode.value}_{persona.value}"
                
                try:
                    result = await self.tools.persona_execute(
                        persona.value,
                        test_task,
                        {"test_mode": mode.value}
                    )
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    self.results.append(TestResult(
                        test_name=test_name,
                        success=result.success,
                        duration=duration,
                        details={
                            "persona": persona.value,
                            "mode": mode.value,
                            "executor": result.metadata.get("executor", "unknown"),
                            "response_length": len(str(result.data)) if result.data else 0
                        },
                        error=result.error if not result.success else None
                    ))
                    
                    if result.success:
                        print(f"✓ {persona.value} execution in {mode.value} mode passed")
                    else:
                        print(f"✗ {persona.value} execution in {mode.value} mode failed: {result.error}")
                        
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    self.results.append(TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        details={},
                        error=str(e)
                    ))
                    print(f"✗ {persona.value} execution in {mode.value} mode failed: {e}")
    
    async def _test_collaboration_modes(self):
        """Test collaboration between personas"""
        
        collaboration_tests = [
            {
                "name": "trinity_sequential",
                "personas": ["springfield", "krukai", "vector"],
                "mode": "sequential",
                "task": "Review security architecture"
            },
            {
                "name": "trinity_parallel",
                "personas": ["springfield", "krukai", "vector"],
                "mode": "parallel",
                "task": "Analyze performance bottlenecks"
            },
            {
                "name": "full_team_hierarchical",
                "personas": ["springfield", "krukai", "vector", "groza", "littara"],
                "mode": "hierarchical",
                "task": "Plan system deployment"
            }
        ]
        
        for test_config in collaboration_tests:
            start_time = datetime.now()
            test_name = f"collaboration_{test_config['name']}"
            
            try:
                result = await self.tools.collaborate_personas(
                    test_config["personas"],
                    test_config["task"],
                    test_config["mode"]
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                self.results.append(TestResult(
                    test_name=test_name,
                    success=result.success,
                    duration=duration,
                    details={
                        "personas": test_config["personas"],
                        "collaboration_mode": test_config["mode"],
                        "result_count": len(result.data.get("results", [])) if result.data else 0
                    },
                    error=result.error if not result.success else None
                ))
                
                if result.success:
                    print(f"✓ Collaboration test {test_config['name']} passed")
                else:
                    print(f"✗ Collaboration test {test_config['name']} failed: {result.error}")
                    
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.results.append(TestResult(
                    test_name=test_name,
                    success=False,
                    duration=duration,
                    details={},
                    error=str(e)
                ))
                print(f"✗ Collaboration test {test_config['name']} failed: {e}")
    
    async def _test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        
        error_tests = [
            {
                "name": "invalid_persona",
                "test": lambda: self.tools.persona_execute("invalid_persona", "test task"),
                "expect_failure": True
            },
            {
                "name": "invalid_mode_switch",
                "test": lambda: self.tools.set_mode("invalid_mode"),
                "expect_failure": True
            },
            {
                "name": "invalid_collaboration_mode",
                "test": lambda: self.tools.collaborate_personas(
                    ["springfield"], "test", "invalid_mode"
                ),
                "expect_failure": True
            }
        ]
        
        for test_config in error_tests:
            start_time = datetime.now()
            test_name = f"error_handling_{test_config['name']}"
            
            try:
                result = await test_config["test"]()
                duration = (datetime.now() - start_time).total_seconds()
                
                # Check if result matches expectation
                success = (not result.success) == test_config["expect_failure"]
                
                self.results.append(TestResult(
                    test_name=test_name,
                    success=success,
                    duration=duration,
                    details={
                        "expected_failure": test_config["expect_failure"],
                        "actual_success": result.success,
                        "error_message": result.error
                    }
                ))
                
                if success:
                    print(f"✓ Error handling test {test_config['name']} passed")
                else:
                    print(f"✗ Error handling test {test_config['name']} failed")
                    
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                # For error handling tests, exceptions might be expected
                success = test_config["expect_failure"]
                
                self.results.append(TestResult(
                    test_name=test_name,
                    success=success,
                    duration=duration,
                    details={},
                    error=str(e) if not success else None
                ))
                
                if success:
                    print(f"✓ Error handling test {test_config['name']} passed (exception expected)")
                else:
                    print(f"✗ Error handling test {test_config['name']} failed: {e}")
    
    async def _test_performance(self):
        """Test performance characteristics"""
        
        # Performance test: rapid mode switching
        start_time = datetime.now()
        mode_switches = 0
        try:
            modes = [ExecutionMode.SIMULATION, ExecutionMode.CLAUDE_ONLY, ExecutionMode.HYBRID]
            
            for i in range(3):  # 3 cycles
                for mode in modes:
                    await self.tools.set_mode(mode.value)
                    mode_switches += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            avg_switch_time = duration / mode_switches
            
            self.results.append(TestResult(
                test_name="performance_mode_switching",
                success=True,
                duration=duration,
                details={
                    "mode_switches": mode_switches,
                    "avg_switch_time": avg_switch_time,
                    "switches_per_second": mode_switches / duration
                }
            ))
            print(f"✓ Performance test (mode switching): {mode_switches} switches in {duration:.2f}s")
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="performance_mode_switching",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            ))
            print(f"✗ Performance test (mode switching) failed: {e}")
        
        # Performance test: rapid persona execution
        start_time = datetime.now()
        executions = 0
        try:
            await self.tools.set_mode("simulation")  # Use simulation for speed
            
            for i in range(5):  # 5 executions per persona
                for persona in ["springfield", "krukai", "vector"]:
                    await self.tools.persona_execute(persona, f"Quick test {i}")
                    executions += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            avg_execution_time = duration / executions
            
            self.results.append(TestResult(
                test_name="performance_persona_execution",
                success=True,
                duration=duration,
                details={
                    "executions": executions,
                    "avg_execution_time": avg_execution_time,
                    "executions_per_second": executions / duration
                }
            ))
            print(f"✓ Performance test (persona execution): {executions} executions in {duration:.2f}s")
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.results.append(TestResult(
                test_name="performance_persona_execution",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            ))
            print(f"✗ Performance test (persona execution) failed: {e}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # Categorize results
        categories = {}
        for result in self.results:
            category = result.test_name.split('_')[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Performance metrics
        performance_results = [r for r in self.results if r.test_name.startswith("performance")]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_test_duration": avg_duration
            },
            "categories": categories,
            "performance": {
                result.test_name: result.details for result in performance_results
            },
            "failures": [
                {
                    "test": r.test_name,
                    "error": r.error,
                    "duration": r.duration
                }
                for r in self.results if not r.success
            ],
            "mode_system_status": self.tools.get_mode_info(),
            "timestamp": datetime.now().isoformat()
        }
        
        return report

async def main():
    """Run the test suite"""
    suite = ModeTestSuite()
    report = await suite.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎯 Test Summary")
    print("=" * 70)
    
    summary = report["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Average Test Duration: {summary['average_test_duration']:.3f}s")
    
    # Category breakdown
    print("\n📊 Category Breakdown:")
    for category, stats in report["categories"].items():
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"  {category.capitalize()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Performance metrics
    if report["performance"]:
        print("\n⚡ Performance Metrics:")
        for test_name, metrics in report["performance"].items():
            print(f"  {test_name}: {json.dumps(metrics, indent=4)}")
    
    # Failures
    if report["failures"]:
        print("\n❌ Failed Tests:")
        for failure in report["failures"]:
            print(f"  {failure['test']}: {failure['error']}")
    
    # Mode system status
    print(f"\n🔧 Final Mode Status: {report['mode_system_status']['mode']}")
    
    # Save detailed report
    with open("test_results_mode_switching.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: test_results_mode_switching.json")
    
    # Final message
    if summary["success_rate"] == 100:
        print("\n🌸 Springfield: 「ふふ、全てのテストが完璧に成功いたしました！」")
        print("⚡ Krukai: 「フン、404の基準でも合格レベルね。」")
        print("🛡️ Vector: 「……全システム正常……安全確認済み……」")
    elif summary["success_rate"] >= 90:
        print("\n🌸 Springfield: 「概ね良好な結果ですが、改善の余地がありますね。」")
        print("⚡ Krukai: 「まだ最適化が必要な部分があるわ。」")
        print("🛡️ Vector: 「……いくつかリスクが残っている……注意が必要……」")
    else:
        print("\n🌸 Springfield: 「システムの修正が必要な状況です。」")
        print("⚡ Krukai: 「この品質では404の基準に達していない。」")
        print("🛡️ Vector: 「……危険レベル……即座の対応が必要……」")

if __name__ == "__main__":
    asyncio.run(main())