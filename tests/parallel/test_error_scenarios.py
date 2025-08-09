#!/usr/bin/env python3
"""
Trinitas Parallel Execution Error Scenario Tests
Vector: "……全ての失敗パターンを想定し、システムの堅牢性を確保する……"
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import modules to test
from hooks.python.integrate_parallel_results import ParallelResultIntegrator
from hooks.python.prepare_parallel_tasks import ParallelTaskPreparer


class TestErrorScenarios(unittest.TestCase):
    """Test various error scenarios in parallel execution"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.results_dir = Path(self.test_dir) / "results"
        self.results_dir.mkdir(parents=True)

        # Mock environment
        os.environ["TRINITAS_RESULTS_DIR"] = str(self.results_dir)
        os.environ["CLAUDE_TOOL_NAME"] = "Task"

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.test_dir)

    # =====================================================
    # Task Preparation Error Tests
    # =====================================================

    def test_empty_prompt_handling(self):
        """Test handling of empty user prompt"""
        preparer = ParallelTaskPreparer("", {})
        tasks = preparer.prepare_parallel_tasks()
        self.assertEqual(len(tasks), 0, "Empty prompt should not create tasks")

    def test_malformed_prompt_handling(self):
        """Test handling of malformed prompts"""
        # Test with special characters
        preparer = ParallelTaskPreparer("@#$%^&*()", {})
        analysis = preparer.analyze_prompt()
        self.assertFalse(
            analysis["parallelizable"], "Special chars should not trigger parallel"
        )

        # Test with very long prompt
        long_prompt = "a" * 10000
        preparer = ParallelTaskPreparer(long_prompt, {})
        tasks = preparer.prepare_parallel_tasks()
        self.assertLessEqual(len(tasks), 6, "Should limit number of parallel tasks")

    def test_agent_selection_edge_cases(self):
        """Test agent selection with edge cases"""
        # Test with no matching keywords
        preparer = ParallelTaskPreparer("The weather is nice today", {})
        suitable = preparer._identify_suitable_agents()
        self.assertEqual(len(suitable), 0, "Unrelated prompt should match no agents")

        # Test with all keywords
        all_keywords_prompt = (
            "analyze security optimize performance test workflow quality"
        )
        preparer = ParallelTaskPreparer(all_keywords_prompt, {})
        suitable = preparer._identify_suitable_agents()
        self.assertGreaterEqual(len(suitable), 4, "Should match multiple agents")

    # =====================================================
    # Result Capture Error Tests
    # =====================================================

    def test_missing_environment_variables(self):
        """Test capture with missing environment variables"""
        # Run capture script without required env vars
        script_path = (
            PROJECT_ROOT / "hooks" / "post-execution" / "capture_subagent_result.sh"
        )
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            env={},  # Empty environment
        )

        output = result.stdout.strip()
        self.assertEqual(output, "{}", "Should return empty JSON on missing env")

    def test_invalid_json_in_arguments(self):
        """Test handling of invalid JSON in tool arguments"""
        env = os.environ.copy()
        env.update(
            {
                "CLAUDE_HOOK_EVENT": "SubagentStop",
                "CLAUDE_TOOL_NAME": "Task",
                "CLAUDE_TOOL_ARGUMENTS": "{invalid json}",
                "CLAUDE_TOOL_RESULT": "test result",
            }
        )

        script_path = (
            PROJECT_ROOT / "hooks" / "post-execution" / "capture_subagent_result.sh"
        )
        result = subprocess.run(
            ["bash", str(script_path)], capture_output=True, text=True, env=env
        )

        # Should still produce valid JSON output
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("Output should be valid JSON even with invalid input")

    def test_filesystem_errors(self):
        """Test handling of filesystem errors"""
        # Make results directory read-only
        os.chmod(self.results_dir, 0o444)

        try:
            env = os.environ.copy()
            env.update(
                {
                    "CLAUDE_HOOK_EVENT": "SubagentStop",
                    "CLAUDE_TOOL_NAME": "Task",
                    "CLAUDE_TOOL_ARGUMENTS": '{"subagent_type":"test-agent"}',
                    "CLAUDE_TOOL_RESULT": "test",
                    "TRINITAS_RESULTS_DIR": str(self.results_dir),
                }
            )

            script_path = (
                PROJECT_ROOT / "hooks" / "post-execution" / "capture_subagent_result.sh"
            )
            result = subprocess.run(
                ["bash", str(script_path)], capture_output=True, text=True, env=env
            )

            # Should handle permission error gracefully
            self.assertIn("systemMessage", result.stdout)
        finally:
            # Restore permissions
            os.chmod(self.results_dir, 0o755)

    # =====================================================
    # Integration Error Tests
    # =====================================================

    def test_missing_session_directory(self):
        """Test integration with missing session directory"""
        integrator = ParallelResultIntegrator("nonexistent_session")
        success = integrator.load_results()
        self.assertFalse(success, "Should fail gracefully with missing directory")

    def test_corrupted_result_files(self):
        """Test handling of corrupted JSON files"""
        session_id = "test_corrupted"
        session_dir = self.results_dir / "completed" / session_id
        session_dir.mkdir(parents=True)

        # Create corrupted JSON file
        corrupted_file = session_dir / "result_1.json"
        corrupted_file.write_text("{invalid json content")

        # Create valid JSON file
        valid_file = session_dir / "result_2.json"
        valid_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "subagent_type": "test-agent",
                    "result": "valid result",
                    "status": "success",
                }
            )
        )

        integrator = ParallelResultIntegrator(session_id)
        integrator.session_dir = session_dir
        success = integrator.load_results()

        self.assertTrue(success, "Should load valid results despite corrupted files")
        self.assertEqual(len(integrator.results), 1, "Should load only valid results")

    def test_timeout_handling(self):
        """Test handling of agent timeouts"""
        results = [
            {
                "subagent_type": "slow-agent",
                "status": "timeout",
                "result": "",
                "error": "Operation timed out after 30 seconds",
                "execution_time_ms": 30000,
            },
            {
                "subagent_type": "fast-agent",
                "status": "success",
                "result": "Completed successfully",
                "error": None,
                "execution_time_ms": 500,
            },
        ]

        integrator = ParallelResultIntegrator("test_timeout")
        integrator.results = results
        integrator.integrate_results()

        # Should handle mixed success/timeout results
        self.assertEqual(
            integrator.integrated_result["agent_results"]["slow-agent"]["status"],
            "partial_failure",
        )
        self.assertEqual(
            integrator.integrated_result["synthesis"]["consensus_level"], "medium"
        )

    def test_partial_completion(self):
        """Test handling when only some agents complete"""
        session_id = "test_partial"

        # Set expected count higher than actual results
        os.environ["TRINITAS_PARALLEL_COUNT"] = "3"

        # Create only 2 results
        for i in range(2):
            env = os.environ.copy()
            env.update(
                {
                    "CLAUDE_HOOK_EVENT": "SubagentStop",
                    "CLAUDE_TOOL_NAME": "Task",
                    "CLAUDE_TOOL_ARGUMENTS": f'{{"subagent_type":"agent-{i}"}}',
                    "CLAUDE_TOOL_RESULT": f"Result {i}",
                    "TRINITAS_SESSION_ID": session_id,
                    "TRINITAS_PARALLEL_COUNT": "3",
                }
            )

            script_path = (
                PROJECT_ROOT / "hooks" / "post-execution" / "capture_subagent_result.sh"
            )
            subprocess.run(["bash", str(script_path)], env=env)

        # Check that results are still in temp, not completed
        temp_files = list((self.results_dir / "temp").glob(f"{session_id}_*.json"))
        self.assertEqual(len(temp_files), 2, "Should have 2 results in temp")

        completed_dir = self.results_dir / "completed" / session_id
        self.assertFalse(completed_dir.exists(), "Should not move to completed yet")

    # =====================================================
    # Stress Tests
    # =====================================================

    def test_concurrent_writes(self):
        """Test handling of concurrent result writes"""
        import threading

        session_id = "test_concurrent"
        errors = []

        def write_result(agent_id):
            try:
                env = os.environ.copy()
                env.update(
                    {
                        "CLAUDE_HOOK_EVENT": "SubagentStop",
                        "CLAUDE_TOOL_NAME": "Task",
                        "CLAUDE_TOOL_ARGUMENTS": f'{{"subagent_type":"agent-{agent_id}"}}',
                        "CLAUDE_TOOL_RESULT": f"Result {agent_id}",
                        "TRINITAS_SESSION_ID": session_id,
                        "TRINITAS_TASK_ID": f"task_{agent_id}",
                    }
                )

                script_path = (
                    PROJECT_ROOT
                    / "hooks"
                    / "post-execution"
                    / "capture_subagent_result.sh"
                )
                result = subprocess.run(
                    ["bash", str(script_path)], env=env, capture_output=True
                )

                if result.returncode != 0:
                    errors.append(f"Agent {agent_id} failed")
            except Exception as e:
                errors.append(f"Agent {agent_id}: {e}")

        # Launch concurrent writes
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_result, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent writes failed: {errors}")

        # Verify all results were captured
        result_files = list((self.results_dir / "temp").glob(f"{session_id}_*.json"))
        self.assertEqual(
            len(result_files), 10, "All concurrent results should be captured"
        )

    def test_memory_pressure(self):
        """Test handling under memory pressure"""
        # Create a large result that might cause memory issues
        large_result = "x" * (10 * 1024 * 1024)  # 10MB

        env = os.environ.copy()
        env.update(
            {
                "CLAUDE_HOOK_EVENT": "SubagentStop",
                "CLAUDE_TOOL_NAME": "Task",
                "CLAUDE_TOOL_ARGUMENTS": '{"subagent_type":"memory-test"}',
                "CLAUDE_TOOL_RESULT": large_result,
                "TRINITAS_SESSION_ID": "memory_test",
            }
        )

        script_path = (
            PROJECT_ROOT / "hooks" / "post-execution" / "capture_subagent_result.sh"
        )
        result = subprocess.run(
            ["bash", str(script_path)], env=env, capture_output=True, text=True
        )

        # Should handle large results without crashing
        self.assertEqual(result.returncode, 0, "Should handle large results")


# =====================================================
# Performance Tests
# =====================================================


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""

    def test_prompt_analysis_speed(self):
        """Test speed of prompt analysis"""
        prompts = [
            "Simple task",
            "Analyze the security vulnerabilities in this code",
            "Optimize performance and create comprehensive test plan with security review",
            "Complex multi-part request with architecture design, security audit, performance optimization, quality assurance, and workflow automation",
        ]

        for prompt in prompts:
            start = time.time()
            preparer = ParallelTaskPreparer(prompt, {})
            tasks = preparer.prepare_parallel_tasks()
            elapsed = time.time() - start

            self.assertLess(
                elapsed, 0.1, f"Analysis should be fast (<100ms): {elapsed:.3f}s"
            )
            print(
                f"Analyzed '{prompt[:30]}...': {elapsed * 1000:.1f}ms, {len(tasks)} tasks"
            )

    def test_integration_speed(self):
        """Test speed of result integration"""
        # Create test data
        session_id = "perf_test"
        session_dir = Path(tempfile.mkdtemp()) / session_id
        session_dir.mkdir(parents=True)

        # Create multiple result files
        for i in range(50):
            result = {
                "session_id": session_id,
                "task_id": f"task_{i}",
                "subagent_type": f"agent-{i % 5}",
                "result": f"Result content {i}" * 100,
                "status": "success",
                "execution_time_ms": 100 + i * 10,
            }

            result_file = session_dir / f"result_{i}.json"
            result_file.write_text(json.dumps(result))

        # Time integration
        start = time.time()
        integrator = ParallelResultIntegrator(session_id)
        integrator.session_dir = session_dir
        integrator.load_results()
        integrator.integrate_results()
        elapsed = time.time() - start

        self.assertLess(
            elapsed, 1.0, f"Integration should be fast (<1s): {elapsed:.3f}s"
        )
        print(f"Integrated 50 results in {elapsed * 1000:.1f}ms")

        # Cleanup
        import shutil

        shutil.rmtree(session_dir.parent)


if __name__ == "__main__":
    unittest.main(verbosity=2)
