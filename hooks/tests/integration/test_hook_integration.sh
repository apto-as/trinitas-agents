#!/bin/bash
# Integration tests for Trinitas hooks
# Springfield: "統合テストで、システム全体の動作を確認しましょう"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_ROOT="$(cd "$TEST_ROOT/.." && pwd)"

# Source test framework
source "$TEST_ROOT/test_framework.sh"

# =====================================================
# Test Setup
# =====================================================

setup() {
    # Create temporary test directory
    export TEST_TEMP_DIR="/tmp/trinitas_integration_test_$$"
    mkdir -p "$TEST_TEMP_DIR"
    
    # Set up Claude environment
    export CLAUDE_PROJECT_DIR="$TEST_TEMP_DIR"
    export CLAUDE_TOOL_NAME="Bash"
}

teardown() {
    # Clean up test directory
    rm -rf "$TEST_TEMP_DIR"
}

# =====================================================
# Pre-execution Hook Tests
# =====================================================

test_pre_execution_safety_hook_blocks_dangerous_commands() {
    describe "Pre-execution Safety Hook"
    
    it "should block dangerous rm -rf commands"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"rm -rf /"}'
    
    # Run the hook and capture exit code
    local exit_code=0
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || exit_code=$?
    
    assert_equals 1 "$exit_code" "Hook blocks dangerous command"
}

test_pre_execution_safety_hook_allows_safe_commands() {
    it "should allow safe commands"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"ls -la"}'
    
    # Run the hook and capture exit code
    local exit_code=0
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || exit_code=$?
    
    assert_equals 0 "$exit_code" "Hook allows safe command"
}

test_pre_execution_safety_hook_blocks_sudo() {
    it "should block sudo commands"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"sudo apt-get update"}'
    
    # Run the hook and capture exit code
    local exit_code=0
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || exit_code=$?
    
    assert_equals 1 "$exit_code" "Hook blocks sudo command"
}

test_pre_execution_safety_hook_blocks_dangerous_git() {
    it "should block dangerous git operations"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"git push --force origin master"}'
    
    # Run the hook and capture exit code
    local exit_code=0
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || exit_code=$?
    
    assert_equals 1 "$exit_code" "Hook blocks force push to master"
}

test_pre_execution_safety_hook_validates_environment() {
    it "should validate Claude environment"
    # Save current environment
    local saved_project_dir="$CLAUDE_PROJECT_DIR"
    
    # Unset required environment variable
    unset CLAUDE_PROJECT_DIR
    
    # Run the hook and capture exit code
    local exit_code=0
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || exit_code=$?
    
    assert_equals 1 "$exit_code" "Hook fails without proper environment"
    
    # Restore environment
    export CLAUDE_PROJECT_DIR="$saved_project_dir"
}

test_pre_execution_safety_hook_logs_blocked_operations() {
    it "should log blocked operations"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"rm -rf /*"}'
    
    # Clear any existing log
    local log_file="$HOME/.claude/logs/blocked_operations.log"
    rm -f "$log_file"
    
    # Run the hook
    "$HOOKS_ROOT/pre-execution/01_safety_check.sh" >/dev/null 2>&1 || true
    
    # Check if log was created
    assert_file_exists "$log_file" "Creates blocked operations log"
    
    # Check log content
    if [[ -f "$log_file" ]]; then
        local log_content=$(cat "$log_file")
        assert_contains "$log_content" "BLOCKED: Bash" "Logs blocked tool name"
        assert_contains "$log_content" "rm -rf" "Logs blocked command"
    fi
}

test_hook_output_formatting() {
    describe "Hook Output Formatting"
    
    it "should produce formatted output for blocked commands"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"sudo rm -rf /"}'
    
    # Run the hook and capture output
    local output=$("$HOOKS_ROOT/pre-execution/01_safety_check.sh" 2>&1 || true)
    
    assert_contains "$output" "Hook Blocked" "Shows blocked status"
    assert_contains "$output" "危険な操作を検出" "Shows danger detection message"
}

# =====================================================
# Common Library Tests
# =====================================================

test_common_library_functions() {
    describe "Common Library Functions"
    
    it "should provide logging functions"
    source "$HOOKS_ROOT/core/common_lib.sh"
    
    # Test that functions exist
    assert_true "type -t log_info >/dev/null" "log_info function exists"
    assert_true "type -t log_error >/dev/null" "log_error function exists"
    assert_true "type -t springfield_says >/dev/null" "springfield_says function exists"
    assert_true "type -t krukai_says >/dev/null" "krukai_says function exists"
    assert_true "type -t vector_says >/dev/null" "vector_says function exists"
}

test_json_extraction() {
    it "should extract JSON values"
    source "$HOOKS_ROOT/core/common_lib.sh"
    
    local json='{"command":"ls -la","timeout":5000}'
    local command=$(extract_json_value "$json" "command")
    local timeout=$(extract_json_value "$json" "timeout")
    
    assert_equals "ls -la" "$command" "Extracts command value"
    assert_equals "5000" "$timeout" "Extracts timeout value"
}

# =====================================================
# Run all tests
# =====================================================

# Only run tests if this script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Run all test functions
    for func in $(declare -F | awk '{print $3}' | grep '^test_'); do
        $func
    done
    
    # Print summary
    print_summary
fi