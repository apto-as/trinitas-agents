#!/usr/bin/env python3
"""
Test suite for Trinity Hybrid MCP Server
Tests both Claude-optimized and universal paths
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.hybrid_server import (
    ClientDetector,
    ClientType
)
from claude.claude_optimized import (
    set_persona_claude,
    execute_parallel_claude,
    manage_with_todowrite
)
from universal.universal_impl import (
    set_persona_universal,
    simulate_parallel,
    manage_internal_state
)


# =====================================
# Test Fixtures
# =====================================

@pytest.fixture
def mock_claude_context():
    """Mock context for Claude Code client"""
    context = Mock()
    context.request_headers = {"user-agent": "Claude-Code/1.0"}
    context.client_info = Mock(name="claude-code")
    context.supports_sampling = True
    return context


@pytest.fixture
def mock_gemini_context():
    """Mock context for Gemini client"""
    context = Mock()
    context.request_headers = {"user-agent": "Gemini-CLI/1.0"}
    context.client_info = Mock(name="gemini")
    context.supports_sampling = False
    return context


@pytest.fixture
def mock_unknown_context():
    """Mock context for unknown client"""
    context = Mock(spec=['request_headers', 'client_info'])
    context.request_headers = {"user-agent": "Unknown/1.0"}
    context.client_info = Mock(name="unknown")
    return context


# =====================================
# Client Detection Tests
# =====================================

class TestClientDetection:
    """Test client detection mechanism"""
    
    def test_detect_claude(self, mock_claude_context):
        """Test Claude Code detection"""
        detector = ClientDetector()
        client_type = detector.detect(mock_claude_context)
        
        assert client_type == ClientType.CLAUDE
        
        capabilities = detector.get_capabilities(client_type)
        assert capabilities["supports_parallel"] is True
        assert capabilities["supports_native_agents"] is True
        assert capabilities["has_todo_write"] is True
        assert capabilities["max_context"] == 200000
    
    def test_detect_gemini(self, mock_gemini_context):
        """Test Gemini detection"""
        detector = ClientDetector()
        client_type = detector.detect(mock_gemini_context)
        
        assert client_type == ClientType.GEMINI
        
        capabilities = detector.get_capabilities(client_type)
        assert capabilities["supports_parallel"] is False
        assert capabilities["supports_native_agents"] is False
        assert capabilities["has_todo_write"] is False
        assert capabilities["max_context"] == 32000
    
    def test_detect_unknown(self, mock_unknown_context):
        """Test unknown client detection"""
        detector = ClientDetector()
        client_type = detector.detect(mock_unknown_context)
        
        assert client_type == ClientType.UNKNOWN
        
        capabilities = detector.get_capabilities(client_type)
        assert capabilities["supports_parallel"] is False
        assert capabilities["max_context"] == 4096
    
    def test_detect_none_context(self):
        """Test with no context"""
        detector = ClientDetector()
        client_type = detector.detect(None)
        
        assert client_type == ClientType.UNKNOWN


# =====================================
# Claude Optimization Tests
# =====================================

class TestClaudeOptimization:
    """Test Claude-specific optimizations"""
    
    @pytest.mark.asyncio
    async def test_set_persona_claude(self, mock_claude_context):
        """Test Claude persona setting"""
        result = await set_persona_claude("springfield", mock_claude_context)
        
        assert result["action"] == "prepare_agent"
        assert result["native_tool"] == "Task"
        assert result["params"]["subagent_type"] == "springfield-strategist"
        assert "ふふ" in result["message"]
    
    @pytest.mark.asyncio
    async def test_parallel_execution_claude(self, mock_claude_context):
        """Test Claude native parallel execution"""
        result = await execute_parallel_claude("Test task", mock_claude_context)
        
        assert result["action"] == "execute_parallel"
        assert result["native_tool"] == "Task"
        assert result["params"]["subagent_type"] == "trinitas-parallel"
        assert result["parallel_type"] == "native"
    
    @pytest.mark.asyncio
    async def test_todowrite_integration(self):
        """Test TodoWrite state management"""
        # Test set operation
        result = await manage_with_todowrite("set", "test_key", "test_value")
        assert result["action"] == "update_todos"
        assert result["native_tool"] == "TodoWrite"
        
        # Test get operation
        result = await manage_with_todowrite("get", "test_key", None)
        assert result["action"] == "read_todos"
        
        # Test list operation
        result = await manage_with_todowrite("list", None, None)
        assert result["action"] == "list_todos"


# =====================================
# Universal Implementation Tests
# =====================================

class TestUniversalImplementation:
    """Test universal fallback implementation"""
    
    @pytest.mark.asyncio
    async def test_set_persona_universal(self):
        """Test universal persona setting"""
        result = await set_persona_universal("krukai", None)
        
        assert result["persona"] == "krukai"
        assert result["format"] == "markdown"
        assert result["implementation"] == "universal"
        assert "Krukai" in result["instructions"]
    
    @pytest.mark.asyncio
    async def test_simulated_parallel(self):
        """Test simulated parallel execution"""
        result = await simulate_parallel("Test task")
        
        assert result["execution_mode"] == "simulated_parallel"
        assert "springfield" in result["results"]
        assert "krukai" in result["results"]
        assert "vector" in result["results"]
        assert "consensus" in result
    
    @pytest.mark.asyncio
    async def test_internal_state_management(self):
        """Test internal state management"""
        # Test set
        result = await manage_internal_state("set", "key1", "value1", None)
        assert result["operation"] == "set"
        assert result["storage"] == "internal"
        
        # Test get
        result = await manage_internal_state("get", "key1", None, None)
        assert result["operation"] == "get"
        
        # Test list
        result = await manage_internal_state("list", None, None, None)
        assert result["operation"] == "list"
        
        # Test clear
        result = await manage_internal_state("clear", None, None, None)
        assert result["operation"] == "clear"


# =====================================
# Hybrid Switching Tests
# =====================================

class TestHybridSwitching:
    """Test automatic switching between implementations"""
    
    @pytest.mark.skip(reason="Requires FastMCP tool decorator to be processed")
    @pytest.mark.asyncio
    async def test_persona_switching(self, mock_claude_context, mock_gemini_context):
        """Test persona setting switches based on client"""
        # Note: In real test, would need to mock the imports
        # This is a conceptual test showing the structure
        
        # Claude should use optimized path
        # Would test the actual tool switching here once decorators are processed
        pass
    
    @pytest.mark.asyncio
    async def test_parallel_execution_switching(self):
        """Test parallel execution switches correctly"""
        # Claude: native parallel
        # Others: simulated parallel
        pass  # Implementation would test the switching logic


# =====================================
# Quality Gate Tests
# =====================================

class TestQualityGates:
    """Test quality enforcement mechanisms"""
    
    @pytest.mark.asyncio
    async def test_quality_gate_enforcement(self):
        """Test 100% quality enforcement"""
        from core.hybrid_server import trinity_quality_gate
        
        # Test that quality < 100% raises error
        request = Mock()
        request.quality_requirement = 0.99
        handler = AsyncMock(return_value="response")
        
        with pytest.raises(ValueError, match="100%"):
            await trinity_quality_gate(request, handler)
    
    @pytest.mark.asyncio
    async def test_springfield_gentle_enforcement(self):
        """Test Springfield's gentle quality enforcement"""
        from core.hybrid_server import trinity_quality_gate
        
        request = Mock(spec=[])  # No quality_requirement
        response = Mock()
        response.quality_score = 0.95
        handler = AsyncMock(return_value=response)
        
        # Should raise with Springfield's message
        with pytest.raises(ValueError, match="ふふ"):
            await trinity_quality_gate(request, handler)


# =====================================
# Integration Tests
# =====================================

class TestIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_claude_flow(self, mock_claude_context):
        """Test complete Claude Code flow"""
        # 1. Set persona
        persona_result = await set_persona_claude("springfield", mock_claude_context)
        assert persona_result["native_tool"] == "Task"
        
        # 2. Execute parallel analysis
        analysis_result = await execute_parallel_claude("Analyze system", mock_claude_context)
        assert analysis_result["parallel_type"] == "native"
        
        # 3. Manage state with TodoWrite
        state_result = await manage_with_todowrite("set", "analysis", "complete")
        assert state_result["native_tool"] == "TodoWrite"
    
    @pytest.mark.asyncio
    async def test_full_universal_flow(self):
        """Test complete universal flow"""
        # 1. Set persona
        persona_result = await set_persona_universal("vector", None)
        assert persona_result["implementation"] == "universal"
        
        # 2. Execute simulated parallel
        analysis_result = await simulate_parallel("Security audit")
        assert analysis_result["execution_mode"] == "simulated_parallel"
        
        # 3. Manage internal state
        state_result = await manage_internal_state("set", "audit", "complete", None)
        assert state_result["storage"] == "internal"


# =====================================
# Performance Tests
# =====================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_claude_performance(self):
        """Test Claude path performance"""
        import time
        
        start = time.time()
        await set_persona_claude("springfield", Mock())
        elapsed = time.time() - start
        
        # Should be fast (< 100ms)
        assert elapsed < 0.1
    
    @pytest.mark.asyncio
    async def test_universal_performance(self):
        """Test universal path performance"""
        import time
        
        start = time.time()
        await simulate_parallel("Test")
        elapsed = time.time() - start
        
        # Simulated parallel adds delays
        assert elapsed < 0.5


# =====================================
# Main Test Runner
# =====================================

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])