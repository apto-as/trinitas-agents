#!/bin/bash
# Trinitas Post-execution Test Runner Hook
# Springfield: "テストを実行して、品質を確保しましょうね"
# Vector: "……テストなしでは、未知の脆弱性が潜んでいる可能性がある……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependencies
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# Test Detection
# =====================================================

detect_test_framework() {
    local project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    
    # Node.js/JavaScript
    if [[ -f "$project_dir/package.json" ]]; then
        if grep -q '"test"' "$project_dir/package.json"; then
            echo "npm"
            return
        fi
    fi
    
    # Python
    if [[ -f "$project_dir/pyproject.toml" ]] || [[ -f "$project_dir/setup.py" ]]; then
        if [[ -d "$project_dir/tests" ]] || [[ -d "$project_dir/test" ]]; then
            echo "python"
            return
        fi
    fi
    
    # Go
    if [[ -f "$project_dir/go.mod" ]]; then
        if find "$project_dir" -name "*_test.go" -type f | grep -q .; then
            echo "go"
            return
        fi
    fi
    
    # Rust
    if [[ -f "$project_dir/Cargo.toml" ]]; then
        echo "cargo"
        return
    fi
    
    # Ruby
    if [[ -f "$project_dir/Gemfile" ]]; then
        if [[ -d "$project_dir/spec" ]] || [[ -d "$project_dir/test" ]]; then
            echo "ruby"
            return
        fi
    fi
    
    # Shell scripts (our own tests)
    if [[ -d "$project_dir/hooks/tests" ]]; then
        echo "shell"
        return
    fi
    
    echo "none"
}

# =====================================================
# Test Runners
# =====================================================

run_npm_tests() {
    local project_dir="$1"
    
    springfield_says "npm testを実行します"
    
    cd "$project_dir" || return 1
    
    # Check if test script exists
    if ! grep -q '"test"' package.json; then
        log_info "No test script defined in package.json"
        return 0
    fi
    
    # Run tests with timeout
    if timeout_command 60 npm test; then
        format_hook_result "success" "npm tests passed"
        return 0
    else
        format_hook_result "warning" "npm tests failed" \
            "Some tests failed. Please check the test output above."
        return 1
    fi
}

run_python_tests() {
    local project_dir="$1"
    
    springfield_says "Pythonテストを実行します"
    
    cd "$project_dir" || return 1
    
    # Try pytest first
    if command -v pytest >/dev/null 2>&1; then
        if timeout_command 60 pytest -v; then
            format_hook_result "success" "Python tests passed"
            return 0
        else
            format_hook_result "warning" "Python tests failed"
            return 1
        fi
    fi
    
    # Fallback to unittest
    if timeout_command 60 python -m pytest discover; then
        format_hook_result "success" "Python tests passed"
        return 0
    else
        format_hook_result "warning" "Python tests failed"
        return 1
    fi
}

run_go_tests() {
    local project_dir="$1"
    
    springfield_says "Goテストを実行します"
    
    cd "$project_dir" || return 1
    
    if timeout_command 60 go test ./...; then
        format_hook_result "success" "Go tests passed"
        return 0
    else
        format_hook_result "warning" "Go tests failed"
        return 1
    fi
}

run_cargo_tests() {
    local project_dir="$1"
    
    springfield_says "Cargoテストを実行します"
    
    cd "$project_dir" || return 1
    
    if timeout_command 120 cargo test; then
        format_hook_result "success" "Rust tests passed"
        return 0
    else
        format_hook_result "warning" "Rust tests failed"
        return 1
    fi
}

run_shell_tests() {
    local project_dir="$1"
    
    springfield_says "Shellテストを実行します"
    
    # Run our own test framework
    if [[ -f "$project_dir/hooks/tests/test_framework.sh" ]]; then
        local test_files=$(find "$project_dir/hooks/tests" -name "test_*.sh" -type f)
        
        if [[ -z "$test_files" ]]; then
            log_info "No test files found"
            return 0
        fi
        
        local failed=0
        for test_file in $test_files; do
            if ! "$test_file"; then
                ((failed++))
            fi
        done
        
        if [[ $failed -eq 0 ]]; then
            format_hook_result "success" "Shell tests passed"
            return 0
        else
            format_hook_result "warning" "$failed Shell test files failed"
            return 1
        fi
    fi
}

# =====================================================
# Test Relevance Detection
# =====================================================

should_run_tests() {
    local tool_name="$1"
    local tool_args="$2"
    
    # Only run tests after code changes
    if [[ ! "$tool_name" =~ ^(Write|Edit|MultiEdit|Bash)$ ]]; then
        return 1
    fi
    
    # For Bash commands, check if it's a test-related command
    if [[ "$tool_name" == "Bash" ]]; then
        local cmd=""
        if command -v jq >/dev/null 2>&1; then
            cmd=$(echo "$tool_args" | jq -r '.command // empty')
        else
            cmd=$(echo "$tool_args" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | \
                sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
        fi
        
        # Skip if command is already running tests
        if echo "$cmd" | grep -qE '(test|spec|pytest|cargo test|go test)'; then
            return 1
        fi
        
        # Skip for simple commands
        if echo "$cmd" | grep -qE '^(ls|pwd|cd|echo|cat|grep|find)'; then
            return 1
        fi
    fi
    
    return 0
}

# =====================================================
# Main Hook Logic
# =====================================================

main() {
    # Validate environment
    if ! validate_claude_environment; then
        format_hook_result "error" "Invalid Claude Code environment"
        return 1
    fi
    
    # Check if we should run tests
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    if ! should_run_tests "$tool_name" "$tool_args"; then
        log_debug "Test runner skipped - not relevant for this operation"
        return 0
    fi
    
    # Detect test framework
    local framework=$(detect_test_framework)
    
    if [[ "$framework" == "none" ]]; then
        log_debug "No test framework detected"
        return 0
    fi
    
    vector_says "……テストを実行する。失敗は許されない……"
    
    # Run appropriate tests
    case "$framework" in
        npm)
            run_npm_tests "$CLAUDE_PROJECT_DIR"
            ;;
        python)
            run_python_tests "$CLAUDE_PROJECT_DIR"
            ;;
        go)
            run_go_tests "$CLAUDE_PROJECT_DIR"
            ;;
        cargo)
            run_cargo_tests "$CLAUDE_PROJECT_DIR"
            ;;
        shell)
            run_shell_tests "$CLAUDE_PROJECT_DIR"
            ;;
        *)
            log_info "Unknown test framework: $framework"
            ;;
    esac
    
    return 0  # Don't fail the operation even if tests fail
}

# Run main function
main "$@"