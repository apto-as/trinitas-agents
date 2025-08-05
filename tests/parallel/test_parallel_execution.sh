#!/bin/bash
# Trinitas Parallel Execution End-to-End Test
# Springfield: "統合テストで、全ての要素が調和して動作することを確認します"
# Krukai: "パフォーマンスと正確性の両方を検証するわ"
# Vector: "……あらゆる失敗パターンをテストする……"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source test framework
source "$PROJECT_ROOT/hooks/tests/test_framework.sh"

# Test configuration
TEST_RESULTS_DIR="${TRINITAS_RESULTS_DIR:-$HOME/.claude/trinitas/parallel_results}"
TEST_SESSION_ID="test_$(date +%Y%m%d_%H%M%S)"

# =====================================================
# Setup and Teardown
# =====================================================

setup_test_environment() {
    echo -e "${BLUE}[SETUP]${NC} Preparing test environment..."
    
    # Create test directories
    mkdir -p "$TEST_RESULTS_DIR/temp"
    mkdir -p "$TEST_RESULTS_DIR/completed"
    mkdir -p "$TEST_RESULTS_DIR/integrated"
    
    # Set environment variables
    export TRINITAS_SESSION_ID="$TEST_SESSION_ID"
    export TRINITAS_PARALLEL_ENABLED="true"
    export TRINITAS_DEBUG="true"
    
    # Install Python dependencies if needed
    if [[ -f "$PROJECT_ROOT/hooks/python/requirements.txt" ]]; then
        pip install -q -r "$PROJECT_ROOT/hooks/python/requirements.txt"
    fi
}

cleanup_test_environment() {
    echo -e "${BLUE}[CLEANUP]${NC} Cleaning up test environment..."
    
    # Remove test results
    rm -rf "$TEST_RESULTS_DIR/temp/${TEST_SESSION_ID}_*"
    rm -rf "$TEST_RESULTS_DIR/completed/${TEST_SESSION_ID}"
    rm -rf "$TEST_RESULTS_DIR/integrated/${TEST_SESSION_ID}_*"
}

# =====================================================
# Test: Prompt Analysis
# =====================================================

test_prompt_analysis() {
    echo -e "\n${YELLOW}=== Test: Prompt Analysis ===${NC}"
    
    # Test simple prompt (should not trigger parallel)
    local simple_prompt="What is 2+2?"
    local result=$(echo "$simple_prompt" | \
        CLAUDE_USER_PROMPT="$simple_prompt" \
        CLAUDE_TOOL_NAME="Task" \
        python3 "$PROJECT_ROOT/hooks/pre-execution/prepare_parallel_tasks.py")
    
    assert_equals "{}" "$result" "Simple prompt should not trigger parallel execution"
    
    # Test complex prompt (should trigger parallel)
    local complex_prompt="Analyze the security vulnerabilities, optimize the performance, and create a comprehensive test plan for this codebase"
    local result=$(echo "$complex_prompt" | \
        CLAUDE_USER_PROMPT="$complex_prompt" \
        CLAUDE_TOOL_NAME="Task" \
        python3 "$PROJECT_ROOT/hooks/pre-execution/prepare_parallel_tasks.py")
    
    assert_not_equals "{}" "$result" "Complex prompt should trigger parallel execution"
    
    # Verify task structure
    local task_count=$(echo "$result" | jq -r '.hookSpecificOutput.parallel_tasks | length')
    assert_true "[ $task_count -ge 2 ]" "Should create at least 2 parallel tasks"
}

# =====================================================
# Test: Result Capture
# =====================================================

test_result_capture() {
    echo -e "\n${YELLOW}=== Test: Result Capture ===${NC}"
    
    # Simulate subagent result
    local test_result="Test agent result content"
    local test_error=""
    
    CLAUDE_HOOK_EVENT="SubagentStop" \
    CLAUDE_TOOL_NAME="Task" \
    CLAUDE_TOOL_ARGUMENTS='{"subagent_type":"krukai-optimizer"}' \
    CLAUDE_TOOL_RESULT="$test_result" \
    CLAUDE_TOOL_ERROR="$test_error" \
    CLAUDE_EXECUTION_TIME="1234" \
    TRINITAS_SESSION_ID="$TEST_SESSION_ID" \
    TRINITAS_TASK_ID="test_task_001" \
    bash "$PROJECT_ROOT/hooks/post-execution/capture_subagent_result.sh"
    
    # Check if result was captured
    local captured_files=$(find "$TEST_RESULTS_DIR/temp" -name "${TEST_SESSION_ID}_test_task_001_*.json" | wc -l)
    assert_true "[ $captured_files -eq 1 ]" "Result should be captured to temp directory"
    
    # Verify result content
    local result_file=$(find "$TEST_RESULTS_DIR/temp" -name "${TEST_SESSION_ID}_test_task_001_*.json" | head -1)
    if [[ -f "$result_file" ]]; then
        local agent_type=$(jq -r '.subagent_type' "$result_file")
        assert_equals "krukai-optimizer" "$agent_type" "Agent type should be preserved"
        
        local status=$(jq -r '.status' "$result_file")
        assert_equals "success" "$status" "Status should be success"
    fi
}

# =====================================================
# Test: Parallel Integration
# =====================================================

test_parallel_integration() {
    echo -e "\n${YELLOW}=== Test: Parallel Integration ===${NC}"
    
    # Create multiple test results
    local agents=("krukai-optimizer" "vector-auditor" "springfield-strategist")
    local session_id="integration_test_$(date +%s)"
    
    mkdir -p "$TEST_RESULTS_DIR/completed/$session_id"
    
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local result_file="$TEST_RESULTS_DIR/completed/$session_id/${session_id}_task_${i}_test.json"
        
        cat > "$result_file" << EOF
{
    "session_id": "$session_id",
    "task_id": "task_${i}",
    "subagent_type": "$agent",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
    "execution_time_ms": $((1000 + i * 500)),
    "status": "success",
    "result": "Result from $agent agent",
    "error": null
}
EOF
    done
    
    # Run integration
    TRINITAS_INTEGRATION_SESSION="$session_id" \
    python3 "$PROJECT_ROOT/hooks/python/integrate_parallel_results.py"
    
    # Verify integrated result
    local integrated_file="$TEST_RESULTS_DIR/integrated/${session_id}_integrated.json"
    assert_true "[ -f '$integrated_file' ]" "Integrated result file should exist"
    
    if [[ -f "$integrated_file" ]]; then
        local agent_count=$(jq -r '.metadata.total_agents' "$integrated_file")
        assert_equals "3" "$agent_count" "Should integrate results from 3 agents"
        
        local total_time=$(jq -r '.metadata.total_execution_time_ms' "$integrated_file")
        assert_true "[ $total_time -eq 4500 ]" "Total execution time should be sum of all agents"
    fi
    
    # Verify summary file
    local summary_file="$TEST_RESULTS_DIR/integrated/${session_id}_summary.md"
    assert_true "[ -f '$summary_file' ]" "Summary markdown file should exist"
    
    # Cleanup
    rm -rf "$TEST_RESULTS_DIR/completed/$session_id"
    rm -f "$TEST_RESULTS_DIR/integrated/${session_id}_*"
}

# =====================================================
# Test: Error Handling
# =====================================================

test_error_handling() {
    echo -e "\n${YELLOW}=== Test: Error Handling ===${NC}"
    
    # Test with invalid JSON in tool arguments
    local result=$(
        CLAUDE_HOOK_EVENT="SubagentStop" \
        CLAUDE_TOOL_NAME="Task" \
        CLAUDE_TOOL_ARGUMENTS='invalid json}' \
        CLAUDE_TOOL_RESULT="test" \
        bash "$PROJECT_ROOT/hooks/post-execution/capture_subagent_result.sh" 2>&1
    )
    
    assert_contains "$result" "{}" "Should return empty JSON on invalid input"
    
    # Test missing required environment variables
    local result=$(
        CLAUDE_TOOL_NAME="Task" \
        bash "$PROJECT_ROOT/hooks/post-execution/capture_subagent_result.sh" 2>&1
    )
    
    assert_contains "$result" "{}" "Should handle missing environment gracefully"
}

# =====================================================
# Test: Performance Measurement
# =====================================================

test_performance() {
    echo -e "\n${YELLOW}=== Test: Performance Measurement ===${NC}"
    
    # Measure prompt analysis performance
    local start_time=$(date +%s%N)
    
    for i in {1..10}; do
        CLAUDE_USER_PROMPT="Complex analysis task $i" \
        CLAUDE_TOOL_NAME="Task" \
        python3 "$PROJECT_ROOT/hooks/pre-execution/prepare_parallel_tasks.py" > /dev/null
    done
    
    local end_time=$(date +%s%N)
    local elapsed_ms=$(( (end_time - start_time) / 1000000 ))
    local avg_ms=$((elapsed_ms / 10))
    
    echo -e "${BLUE}[PERF]${NC} Average prompt analysis time: ${avg_ms}ms"
    assert_true "[ $avg_ms -lt 100 ]" "Prompt analysis should be fast (<100ms)"
}

# =====================================================
# Main Test Runner
# =====================================================

main() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  Trinitas Parallel Execution Tests${NC}"
    echo -e "${PURPLE}========================================${NC}"
    
    setup_test_environment
    
    # Run all tests
    test_prompt_analysis
    test_result_capture
    test_parallel_integration
    test_error_handling
    test_performance
    
    # Show results
    show_test_summary
    
    cleanup_test_environment
    
    # Return appropriate exit code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}✅ All tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ Some tests failed!${NC}"
        return 1
    fi
}

# Run tests if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi