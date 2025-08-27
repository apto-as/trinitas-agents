#!/usr/bin/env python3
"""
Trinitas v3.5 Integration Tests
Tests the complete integration of all Phase 2 components
"""

import unittest
import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trinitas_mcp_tools import TrinitasMCPTools, ToolResult
from context_manager import AdvancedContextManager
from workflow_templates import WorkflowTemplatesEngine
from component_wrapper import ComponentWrapper

class TestPhase2Integration(unittest.TestCase):
    """Test Phase 2 integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tools = TrinitasMCPTools()
        self.context_manager = AdvancedContextManager()
        self.workflow_engine = WorkflowTemplatesEngine()
        self.wrapper = ComponentWrapper()
    
    def test_component_initialization(self):
        """Test that all components initialize correctly"""
        self.assertIsNotNone(self.tools)
        self.assertIsNotNone(self.context_manager)
        self.assertIsNotNone(self.workflow_engine)
        self.assertIsNotNone(self.wrapper)
        
        # Check personas are loaded
        self.assertIn("springfield", self.tools.personas)
        self.assertIn("krukai", self.tools.personas)
        self.assertIn("vector", self.tools.personas)
    
    def test_session_creation_and_management(self):
        """Test session creation and management"""
        # Create session
        session_id = self.context_manager.create_session("test_session")
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.context_manager.sessions)
        
        # Set and get context
        asyncio.run(self.context_manager.set_context(
            "test_key", "test_value", "session", session_id
        ))
        
        value = asyncio.run(self.context_manager.get_context(
            "test_key", "session", session_id
        ))
        self.assertEqual(value, "test_value")
        
        # Get session info
        info = asyncio.run(self.context_manager.get_session_info(session_id))
        self.assertIn("created_at", info)
        self.assertIn("context", info)
    
    def test_workflow_template_availability(self):
        """Test that workflow templates are available"""
        templates = self.workflow_engine.get_available_templates()
        
        expected_templates = [
            "secure_api_development",
            "rapid_prototyping",
            "code_review_refactor",
            "production_deployment",
            "bug_fix",
            "architecture_design"
        ]
        
        for template in expected_templates:
            self.assertIn(template, templates)
        
        # Test template details
        details = self.workflow_engine.get_template_details("secure_api_development")
        self.assertIn("name", details)
        self.assertIn("description", details)
        self.assertIn("steps", details)
    
    def test_persona_execution_with_context(self):
        """Test persona execution with context management"""
        async def run_test():
            # Create session
            session_id = self.context_manager.create_session("persona_test")
            
            # Execute with context
            result = await self.tools.persona_execute(
                "springfield",
                "Plan a project",
                {"project": "test"}
            )
            
            self.assertTrue(result.success)
            self.assertIsNotNone(result.data)
            
            # Store result in session
            await self.context_manager.set_context(
                "springfield_result",
                result.data,
                "session",
                session_id
            )
            
            # Retrieve from session
            stored_result = await self.context_manager.get_context(
                "springfield_result",
                "session",
                session_id
            )
            
            self.assertEqual(stored_result, result.data)
        
        asyncio.run(run_test())
    
    def test_workflow_execution(self):
        """Test workflow execution"""
        async def run_test():
            project_context = {
                "project_name": "Test Project",
                "requirements": ["feature1", "feature2"]
            }
            
            result = await self.workflow_engine.execute_workflow(
                "rapid_prototyping",
                project_context,
                parallel=False
            )
            
            self.assertIn("completed", result)
            self.assertIn("total_steps", result)
            self.assertIn("step_results", result)
            
            # Check that steps were executed
            self.assertGreater(result["total_steps"], 0)
        
        asyncio.run(run_test())
    
    def test_context_synchronization(self):
        """Test context synchronization between personas"""
        async def run_test():
            session_id = self.context_manager.create_session("sync_test")
            
            # Set context for Springfield
            await self.context_manager.set_context(
                "strategy",
                {"goal": "test", "timeline": "1 week"},
                "springfield",
                session_id
            )
            
            # Sync to Krukai
            await self.context_manager.sync_context_between_personas(
                session_id,
                "springfield",
                "krukai"
            )
            
            # Check Krukai received context
            krukai_context = await self.context_manager.get_context(
                "strategy",
                "krukai",
                session_id
            )
            
            self.assertIsNotNone(krukai_context)
            self.assertIn("goal", krukai_context)
        
        asyncio.run(run_test())
    
    def test_collaboration_modes(self):
        """Test different collaboration modes"""
        async def run_test():
            personas = ["springfield", "krukai", "vector"]
            task = "Test collaboration"
            
            # Test sequential mode
            result = await self.tools.collaborate_personas(
                personas, task, "sequential"
            )
            self.assertTrue(result.success)
            
            # Test parallel mode (simulated)
            result = await self.tools.collaborate_personas(
                personas, task, "parallel"
            )
            self.assertTrue(result.success)
            
            # Test consensus mode
            result = await self.tools.collaborate_personas(
                personas, task, "consensus"
            )
            self.assertTrue(result.success)
        
        asyncio.run(run_test())
    
    def test_quality_check_integration(self):
        """Test quality check with session tracking"""
        async def run_test():
            session_id = self.context_manager.create_session("quality_test")
            
            code = "def test(): return True"
            result = await self.tools.quality_check(code, "basic")
            
            self.assertTrue(result.success)
            self.assertIn("overall_score", result.data)
            
            # Store quality result in session
            await self.context_manager.set_context(
                "quality_result",
                result.data,
                "session",
                session_id
            )
            
            # Verify stored
            stored = await self.context_manager.get_context(
                "quality_result",
                "session",
                session_id
            )
            self.assertEqual(stored["overall_score"], result.data["overall_score"])
        
        asyncio.run(run_test())
    
    def test_workflow_with_session_persistence(self):
        """Test workflow execution with session persistence"""
        async def run_test():
            session_id = self.context_manager.create_session("workflow_persist_test")
            
            # Execute workflow
            project_context = {
                "project_name": "Persistent Test",
                "phase": "development"
            }
            
            workflow_result = await self.workflow_engine.execute_workflow(
                "rapid_prototyping",
                project_context
            )
            
            # Track in session
            await self.context_manager.track_workflow(
                session_id,
                "rapid_prototyping",
                project_context,
                workflow_result
            )
            
            # Get workflow history
            history = await self.context_manager.get_workflow_history(session_id)
            
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["template"], "rapid_prototyping")
        
        asyncio.run(run_test())
    
    def test_performance_tracking(self):
        """Test performance statistics tracking"""
        async def run_test():
            session_id = self.context_manager.create_session("performance_test")
            
            # Perform several operations
            for i in range(3):
                await self.context_manager.set_context(
                    f"key_{i}",
                    f"value_{i}",
                    "session",
                    session_id
                )
            
            # Get performance stats
            stats = await self.context_manager.get_performance_stats(session_id)
            
            self.assertIn("total_operations", stats)
            self.assertIn("context_operations", stats)
            self.assertEqual(stats["total_operations"], 3)
        
        asyncio.run(run_test())
    
    def test_natural_request_processing(self):
        """Test natural language request processing"""
        async def run_test():
            requests = [
                "Help me optimize my code",
                "I need to design a system architecture",
                "Find security vulnerabilities"
            ]
            
            for request in requests:
                result = await self.tools.natural_request(request)
                self.assertTrue(result.success)
                self.assertIn("persona", result.data)
                self.assertIn("action", result.data)
        
        asyncio.run(run_test())
    
    def test_error_handling(self):
        """Test error handling across components"""
        async def run_test():
            # Test invalid persona
            result = await self.tools.persona_execute(
                "invalid_persona",
                "test task"
            )
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
            
            # Test invalid workflow
            try:
                result = await self.workflow_engine.execute_workflow(
                    "non_existent_workflow",
                    {}
                )
                self.fail("Should have raised an exception")
            except Exception as e:
                self.assertIn("unknown", str(e).lower())
            
            # Test invalid session
            value = await self.context_manager.get_context(
                "key",
                "session",
                "invalid_session_id"
            )
            self.assertIsNone(value)
        
        asyncio.run(run_test())
    
    def test_full_integration_scenario(self):
        """Test a complete integration scenario"""
        async def run_test():
            # 1. Create session
            session_id = self.context_manager.create_session("full_integration")
            
            # 2. Natural request to determine persona
            nl_result = await self.tools.natural_request(
                "I need to build a secure API"
            )
            self.assertTrue(nl_result.success)
            
            # 3. Execute workflow
            workflow_result = await self.workflow_engine.execute_workflow(
                "secure_api_development",
                {"project_name": "Test API", "framework": "FastAPI"}
            )
            self.assertIn("completed", workflow_result)
            
            # 4. Trinity collaboration
            collab_result = await self.tools.collaborate_personas(
                ["springfield", "krukai", "vector"],
                "Review the API design",
                "sequential"
            )
            self.assertTrue(collab_result.success)
            
            # 5. Quality check
            sample_code = "def api_endpoint(): return {'status': 'ok'}"
            quality_result = await self.tools.quality_check(
                sample_code,
                "comprehensive"
            )
            self.assertTrue(quality_result.success)
            
            # 6. Track everything in session
            await self.context_manager.track_workflow(
                session_id,
                "secure_api_development",
                {"project_name": "Test API"},
                workflow_result
            )
            
            # 7. Get final stats
            stats = await self.context_manager.get_performance_stats(session_id)
            self.assertGreater(stats["total_operations"], 0)
            
            print(f"\n✅ Full integration test completed successfully!")
            print(f"   Session: {session_id}")
            print(f"   Operations: {stats['total_operations']}")
        
        asyncio.run(run_test())

class TestEnhancedMCPServer(unittest.TestCase):
    """Test the enhanced MCP server functionality"""
    
    def test_mcp_server_imports(self):
        """Test that MCP server can be imported"""
        try:
            import mcp_server_enhanced
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"MCP server dependencies not installed: {e}")
    
    def test_tool_definitions(self):
        """Test that all tools are properly defined"""
        # This would normally test the actual MCP server
        # but we'll check the implementation exists
        server_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "mcp_server_enhanced.py"
        )
        self.assertTrue(os.path.exists(server_file))
        
        # Check that required tools are defined
        with open(server_file, 'r') as f:
            content = f.read()
            
        required_tools = [
            "@mcp.tool()",
            "persona_execute",
            "collaborate_personas",
            "execute_workflow",
            "create_session",
            "get_session_context",
            "natural_request"
        ]
        
        for tool in required_tools:
            self.assertIn(tool, content)

def run_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("🧪 Trinitas v3.5 Phase 2 Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedMCPServer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        print(f"   Tests run: {result.testsRun}")
        print("🎉 Phase 2 implementation is complete and verified!")
    else:
        print("❌ Some tests failed")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)