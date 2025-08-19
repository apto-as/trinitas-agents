#!/usr/bin/env python3
"""
Trinitas v3.5 - Connector Unit Tests
Tests for Local LLM Connector component
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from ..connector.llm_connector import (
    LocalLLMConnector,
    TaskRequest,
    TaskResponse,
    CognitiveComplexity,
    ExecutorType
)


class TestLocalLLMConnector:
    """Unit tests for Local LLM Connector"""
    
    @pytest.fixture
    def connector(self):
        """Create connector instance"""
        with patch('builtins.open', Mock(return_value=Mock(
            __enter__=Mock(return_value=Mock(
                read=Mock(return_value="""
local_llm:
  model:
    name: "gpt-oss-120b"
  connection:
    endpoint: "http://localhost:8080/v1"
    timeout: 30
  optimization:
    primary_language: "english"
    temperature: 0.7
    max_tokens: 8000
    top_p: 0.95
""")
            )),
            __exit__=Mock(return_value=None)
        ))):
            return LocalLLMConnector()
    
    @pytest.mark.asyncio
    async def test_initialization(self, connector):
        """Test connector initialization"""
        connector.session = AsyncMock()
        connector.session.get = AsyncMock(return_value=AsyncMock(
            status=200,
            __aenter__=AsyncMock(return_value=AsyncMock(status=200)),
            __aexit__=AsyncMock()
        ))
        
        await connector.initialize()
        assert connector.health_status == "healthy"
        assert connector.session is not None
    
    @pytest.mark.asyncio
    async def test_health_check(self, connector):
        """Test health check functionality"""
        connector.session = AsyncMock()
        
        # Test successful health check
        response_mock = AsyncMock()
        response_mock.status = 200
        connector.session.get = AsyncMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=response_mock),
            __aexit__=AsyncMock()
        ))
        
        result = await connector.check_health()
        assert result is True
        assert connector.health_status == "healthy"
        
        # Test failed health check
        connector.session.get = AsyncMock(side_effect=Exception("Connection failed"))
        result = await connector.check_health()
        assert result is False
        assert "unhealthy" in connector.health_status
    
    def test_format_english_prompt(self, connector):
        """Test English-optimized prompt formatting"""
        task = TaskRequest(
            id="test-001",
            type="analysis",
            description="Analyze this code",
            estimated_tokens=1000,
            required_tools=["mcp_server", "bash"],
            priority="high",
            context={"module": "test"}
        )
        
        prompt = connector._format_english_prompt(task)
        
        # Check prompt structure
        assert "Task ID: test-001" in prompt
        assert "Task Type: analysis" in prompt
        assert "Priority: high" in prompt
        assert "Description:" in prompt
        assert "Analyze this code" in prompt
        assert "Required Tools:" in prompt
        assert "mcp_server" in prompt
        assert "bash" in prompt
        assert "Context:" in prompt
        assert '"module": "test"' in prompt
        assert "Instructions:" in prompt
    
    def test_prepare_tools(self, connector):
        """Test tool preparation for API calls"""
        required_tools = ["mcp_server", "file_operations", "bash"]
        
        tools = connector._prepare_tools(None, required_tools)
        
        # Check tool definitions
        tool_names = [t["function"]["name"] for t in tools]
        assert "mcp_server_call" in tool_names
        assert "read_file" in tool_names
        assert "search_files" in tool_names
        assert "execute_bash" in tool_names
        
        # Check MCP server tool
        mcp_tool = next(t for t in tools if t["function"]["name"] == "mcp_server_call")
        assert "tool" in mcp_tool["function"]["parameters"]["properties"]
        assert "params" in mcp_tool["function"]["parameters"]["properties"]
    
    def test_calculate_confidence(self, connector):
        """Test confidence calculation"""
        # Mechanical task - high confidence
        task1 = TaskRequest(
            id="test-1",
            type="file_search",
            description="Search files",
            estimated_tokens=1000,
            required_tools=[],
            complexity=CognitiveComplexity.MECHANICAL
        )
        result1 = {"content": "Results found", "tool_calls": []}
        confidence1 = connector._calculate_confidence(task1, result1)
        assert confidence1 >= 0.9
        
        # Strategic task - lower confidence
        task2 = TaskRequest(
            id="test-2",
            type="architecture",
            description="Design system",
            estimated_tokens=5000,
            required_tools=[],
            complexity=CognitiveComplexity.STRATEGIC
        )
        result2 = {"content": "Design proposal"}
        confidence2 = connector._calculate_confidence(task2, result2)
        assert confidence2 <= 0.6
        
        # Task with tool usage - higher confidence
        task3 = TaskRequest(
            id="test-3",
            type="analysis",
            description="Analyze",
            estimated_tokens=2000,
            required_tools=["mcp_server"],
            complexity=CognitiveComplexity.ANALYTICAL
        )
        result3 = {"content": "Analysis complete" * 20, "tool_calls": [{"function": "test"}]}
        confidence3 = connector._calculate_confidence(task3, result3)
        assert confidence3 >= 0.95  # Tool use + long content + analytical
    
    @pytest.mark.asyncio
    async def test_execute_success(self, connector):
        """Test successful task execution"""
        connector.session = AsyncMock()
        
        # Mock successful API response
        api_response = {
            "choices": [{
                "message": {
                    "content": "Task completed successfully",
                    "tool_calls": [{
                        "id": "call_001",
                        "function": {
                            "name": "search_files",
                            "arguments": '{"pattern": "test", "path": "/"}'
                        }
                    }]
                }
            }],
            "usage": {
                "total_tokens": 500
            }
        }
        
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.json = AsyncMock(return_value=api_response)
        
        connector.session.post = AsyncMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=response_mock),
            __aexit__=AsyncMock()
        ))
        
        task = TaskRequest(
            id="test-exec",
            type="search",
            description="Search for test files",
            estimated_tokens=1000,
            required_tools=["file_operations"]
        )
        
        response = await connector.execute(task)
        
        assert response.id == "test-exec"
        assert response.executor == "local"
        assert response.tokens_used == 500
        assert response.result["content"] == "Task completed successfully"
        assert len(response.result["tool_calls"]) == 1
        assert response.result["tool_calls"][0]["function"] == "search_files"
        assert response.confidence > 0.5
        assert response.errors == []
    
    @pytest.mark.asyncio
    async def test_execute_api_error(self, connector):
        """Test API error handling"""
        connector.session = AsyncMock()
        
        response_mock = AsyncMock()
        response_mock.status = 500
        response_mock.text = AsyncMock(return_value="Internal Server Error")
        
        connector.session.post = AsyncMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=response_mock),
            __aexit__=AsyncMock()
        ))
        
        task = TaskRequest(
            id="test-error",
            type="test",
            description="Test task",
            estimated_tokens=100,
            required_tools=[]
        )
        
        response = await connector.execute(task)
        
        assert response.executor == "local"
        assert response.result is None
        assert response.tokens_used == 0
        assert response.confidence == 0.0
        assert len(response.errors) > 0
        assert "API error: 500" in response.errors[0]
    
    @pytest.mark.asyncio
    async def test_execute_timeout(self, connector):
        """Test timeout handling"""
        connector.session = AsyncMock()
        connector.session.post = AsyncMock(side_effect=asyncio.TimeoutError())
        
        task = TaskRequest(
            id="test-timeout",
            type="test",
            description="Test task",
            estimated_tokens=100,
            required_tools=[]
        )
        
        response = await connector.execute(task)
        
        assert response.result is None
        assert response.confidence == 0.0
        assert "Request timeout" in response.errors[0]
    
    def test_parse_response(self, connector):
        """Test response parsing"""
        # Test normal response
        data = {
            "choices": [{
                "message": {
                    "content": "Response content",
                    "tool_calls": [{
                        "id": "call_001",
                        "function": {
                            "name": "test_tool",
                            "arguments": '{"param": "value"}'
                        }
                    }]
                }
            }]
        }
        
        result = connector._parse_response(data)
        assert result["content"] == "Response content"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"] == "test_tool"
        assert result["tool_calls"][0]["arguments"]["param"] == "value"
        
        # Test empty response
        empty_data = {"choices": []}
        empty_result = connector._parse_response(empty_data)
        assert "error" in empty_result
        
        # Test response without tool calls
        no_tools_data = {
            "choices": [{
                "message": {
                    "content": "Just content"
                }
            }]
        }
        
        no_tools_result = connector._parse_response(no_tools_data)
        assert no_tools_result["content"] == "Just content"
        assert no_tools_result["tool_calls"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])