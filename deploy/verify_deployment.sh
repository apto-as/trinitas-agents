#!/bin/bash
# Trinitas Deployment Verification Script
# Springfield: "最終確認を行い、完璧な状態でのデプロイメントを保証します"

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TRINITAS_DIR="$HOME/.claude/trinitas"

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# =====================================================
# Test Functions
# =====================================================

log_test() {
    local status=$1
    local test_name=$2
    local message=${3:-""}
    
    ((TOTAL_TESTS++))
    
    if [[ "$status" == "PASS" ]]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        [[ -n "$message" ]] && echo -e "   ${YELLOW}$message${NC}"
        ((FAILED_TESTS++))
    fi
}

test_environment() {
    echo -e "\n${BLUE}=== Environment Tests ===${NC}"
    
    # Test Claude CLI
    if command -v claude >/dev/null 2>&1; then
        log_test "PASS" "Claude CLI installed"
    else
        log_test "FAIL" "Claude CLI installed" "Claude CLI not found in PATH"
    fi
    
    # Test Python
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if (( $(echo "$python_version >= 3.7" | bc -l) )); then
            log_test "PASS" "Python version" "Python $python_version"
        else
            log_test "FAIL" "Python version" "Python $python_version < 3.7"
        fi
    else
        log_test "FAIL" "Python installed" "Python3 not found"
    fi
    
    # Test jq (optional but recommended)
    if command -v jq >/dev/null 2>&1; then
        log_test "PASS" "jq installed (optional)"
    else
        log_test "PASS" "jq not installed (optional)" "Will use fallback methods"
    fi
}

test_installation() {
    echo -e "\n${BLUE}=== Installation Tests ===${NC}"
    
    # Test directory structure
    local required_dirs=(
        "$TRINITAS_DIR/hooks/core"
        "$TRINITAS_DIR/hooks/pre-execution"
        "$TRINITAS_DIR/hooks/post-execution"
        "$TRINITAS_DIR/hooks/python"
        "$TRINITAS_DIR/hooks/monitoring"
        "$TRINITAS_DIR/parallel_results/temp"
        "$TRINITAS_DIR/parallel_results/completed"
        "$TRINITAS_DIR/parallel_results/integrated"
        "$TRINITAS_DIR/logs"
    )
    
    local all_dirs_exist=true
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            all_dirs_exist=false
            break
        fi
    done
    
    if $all_dirs_exist; then
        log_test "PASS" "Directory structure"
    else
        log_test "FAIL" "Directory structure" "Missing required directories"
    fi
    
    # Test critical hooks
    local critical_hooks=(
        "core/trinitas_protocol_injector.sh"
        "post-execution/capture_subagent_result.sh"
        "python/prepare_parallel_tasks.py"
        "python/integrate_parallel_results.py"
        "monitoring/health_check.sh"
        "monitoring/session_monitor.sh"
    )
    
    local all_hooks_exist=true
    for hook in "${critical_hooks[@]}"; do
        if [[ ! -x "$TRINITAS_DIR/hooks/$hook" ]]; then
            all_hooks_exist=false
            break
        fi
    done
    
    if $all_hooks_exist; then
        log_test "PASS" "Critical hooks installed"
    else
        log_test "FAIL" "Critical hooks installed" "Missing or non-executable hooks"
    fi
}

test_configuration() {
    echo -e "\n${BLUE}=== Configuration Tests ===${NC}"
    
    local settings_file="$HOME/.claude/settings.json"
    
    # Test settings.json exists
    if [[ -f "$settings_file" ]]; then
        log_test "PASS" "settings.json exists"
        
        # Test JSON validity
        if jq empty "$settings_file" 2>/dev/null; then
            log_test "PASS" "settings.json valid JSON"
            
            # Test required hooks configured
            local has_pretooluse=$(jq -r '.hooks.PreToolUse // empty' "$settings_file")
            local has_subagentstop=$(jq -r '.hooks.SubagentStop // empty' "$settings_file")
            
            if [[ -n "$has_pretooluse" ]] && [[ -n "$has_subagentstop" ]]; then
                log_test "PASS" "Parallel agent hooks configured"
            else
                log_test "FAIL" "Parallel agent hooks configured" "Missing PreToolUse or SubagentStop hooks"
            fi
        else
            log_test "FAIL" "settings.json valid JSON" "Invalid JSON format"
        fi
    else
        log_test "FAIL" "settings.json exists" "File not found"
    fi
}

test_functionality() {
    echo -e "\n${BLUE}=== Functionality Tests ===${NC}"
    
    # Test protocol injector
    if TRINITAS_HOOK_TYPE="session_start" \
       bash "$TRINITAS_DIR/hooks/core/trinitas_protocol_injector.sh" >/dev/null 2>&1; then
        log_test "PASS" "Protocol injector"
    else
        log_test "FAIL" "Protocol injector" "Hook execution failed"
    fi
    
    # Test Python environment
    if echo "test" | CLAUDE_USER_PROMPT="test" CLAUDE_TOOL_NAME="Task" \
       python3 "$TRINITAS_DIR/hooks/python/prepare_parallel_tasks.py" >/dev/null 2>&1; then
        log_test "PASS" "Python task preparation"
    else
        log_test "FAIL" "Python task preparation" "Python hook failed"
    fi
    
    # Test result capture
    local test_env=(
        "CLAUDE_HOOK_EVENT=SubagentStop"
        "CLAUDE_TOOL_NAME=Task"
        "CLAUDE_TOOL_ARGUMENTS={\"subagent_type\":\"test\"}"
        "CLAUDE_TOOL_RESULT=test"
        "TRINITAS_SESSION_ID=verify_test"
    )
    
    if env "${test_env[@]}" bash "$TRINITAS_DIR/hooks/post-execution/capture_subagent_result.sh" >/dev/null 2>&1; then
        log_test "PASS" "Result capture"
        
        # Clean up test file
        rm -f "$HOME/.claude/trinitas/parallel_results/temp/verify_test_*.json"
    else
        log_test "FAIL" "Result capture" "Capture script failed"
    fi
}

test_monitoring() {
    echo -e "\n${BLUE}=== Monitoring Tests ===${NC}"
    
    # Test health check
    if "$TRINITAS_DIR/hooks/monitoring/health_check.sh" >/dev/null 2>&1; then
        log_test "PASS" "Health check script"
    else
        log_test "FAIL" "Health check script" "Health check failed"
    fi
    
    # Test session monitor
    if "$TRINITAS_DIR/hooks/monitoring/session_monitor.sh" status >/dev/null 2>&1; then
        log_test "PASS" "Session monitor"
    else
        log_test "FAIL" "Session monitor" "Monitor script failed"
    fi
    
    # Test auto-recovery (diagnose only)
    if python3 "$TRINITAS_DIR/hooks/monitoring/auto_recovery.py" --diagnose-only >/dev/null 2>&1; then
        log_test "PASS" "Auto-recovery system"
    else
        log_test "FAIL" "Auto-recovery system" "Recovery script failed"
    fi
}

test_performance() {
    echo -e "\n${BLUE}=== Performance Tests ===${NC}"
    
    # Test disk space
    local available_mb=$(df -m "$HOME" | awk 'NR==2 {print $4}')
    if [[ $available_mb -gt 100 ]]; then
        log_test "PASS" "Disk space" "${available_mb}MB available"
    else
        log_test "FAIL" "Disk space" "Only ${available_mb}MB available (need 100MB+)"
    fi
    
    # Test results directory size
    if [[ -d "$HOME/.claude/trinitas/parallel_results" ]]; then
        local results_size=$(du -sm "$HOME/.claude/trinitas/parallel_results" 2>/dev/null | cut -f1)
        if [[ $results_size -lt 500 ]]; then
            log_test "PASS" "Results directory size" "${results_size}MB"
        else
            log_test "FAIL" "Results directory size" "${results_size}MB (>500MB, consider cleanup)"
        fi
    else
        log_test "PASS" "Results directory size" "Directory not yet created"
    fi
}

# =====================================================
# Report Generation
# =====================================================

generate_report() {
    echo -e "\n${PURPLE}====================================${NC}"
    echo -e "${PURPLE}  Deployment Verification Report${NC}"
    echo -e "${PURPLE}====================================${NC}"
    
    echo -e "\nTotal Tests: $TOTAL_TESTS"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    
    local success_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    fi
    
    echo -e "\nSuccess Rate: ${success_rate}%"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "\n${GREEN}✅ DEPLOYMENT VERIFIED SUCCESSFULLY!${NC}"
        echo -e "\nYour Trinitas Parallel Agents installation is ready for use."
        echo -e "\nNext steps:"
        echo -e "1. Run a test: ./examples/parallel_analysis_demo.sh"
        echo -e "2. Monitor health: ~/.claude/trinitas/hooks/monitoring/health_check.sh"
        echo -e "3. Enable monitoring: Add health check to cron"
        return 0
    else
        echo -e "\n${RED}⚠️  DEPLOYMENT VERIFICATION FAILED${NC}"
        echo -e "\nPlease address the failed tests before using in production."
        echo -e "\nTroubleshooting:"
        echo -e "1. Review failed tests above"
        echo -e "2. Run: ./deploy/safe_deploy.sh"
        echo -e "3. Check logs: ~/.claude/trinitas/logs/"
        return 1
    fi
}

# =====================================================
# Main
# =====================================================

main() {
    echo -e "${PURPLE}Trinitas Deployment Verification v1.0${NC}"
    echo -e "${PURPLE}====================================${NC}"
    
    # Run all test suites
    test_environment
    test_installation
    test_configuration
    test_functionality
    test_monitoring
    test_performance
    
    # Generate final report
    generate_report
}

# Run verification
main "$@"