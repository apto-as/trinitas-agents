#!/bin/bash
# Trinitas Health Check - System Stability Monitor
# Vector: "……システムの健全性を常に監視……異常を早期検出……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common library
source "$PROJECT_ROOT/hooks/core/common_lib.sh" 2>/dev/null || true

# Configuration
RESULTS_DIR="${TRINITAS_RESULTS_DIR:-$HOME/.claude/trinitas/parallel_results}"
LOG_DIR="$HOME/.claude/trinitas/logs"
HEALTH_REPORT="$LOG_DIR/health_report_$(date +%Y%m%d_%H%M%S).txt"

# =====================================================
# Health Check Functions
# =====================================================

check_directory_structure() {
    echo "=== Directory Structure Check ==="
    local issues=0
    
    # Required directories
    local required_dirs=(
        "$HOME/.claude/trinitas/hooks/core"
        "$HOME/.claude/trinitas/hooks/pre-execution"
        "$HOME/.claude/trinitas/hooks/post-execution"
        "$RESULTS_DIR/temp"
        "$RESULTS_DIR/completed"
        "$RESULTS_DIR/integrated"
        "$LOG_DIR"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            echo "❌ Missing directory: $dir"
            ((issues++))
        else
            echo "✅ Directory exists: $dir"
        fi
    done
    
    return $issues
}

check_hook_files() {
    echo -e "\n=== Hook Files Check ==="
    local issues=0
    
    # Critical hook files
    local hook_files=(
        "core/trinitas_protocol_injector.sh"
        "pre-execution/01_safety_check.sh"
        "pre-execution/02_file_safety_check.sh"
        "post-execution/01_code_quality_check.sh"
        "post-execution/capture_subagent_result.sh"
        "python/prepare_parallel_tasks.py"
        "python/integrate_parallel_results.py"
    )
    
    local hooks_dir="$HOME/.claude/trinitas/hooks"
    
    for hook in "${hook_files[@]}"; do
        local hook_path="$hooks_dir/$hook"
        if [[ ! -f "$hook_path" ]]; then
            echo "❌ Missing hook: $hook"
            ((issues++))
        elif [[ ! -x "$hook_path" ]]; then
            echo "⚠️  Hook not executable: $hook"
            ((issues++))
        else
            echo "✅ Hook OK: $hook"
        fi
    done
    
    return $issues
}

check_python_environment() {
    echo -e "\n=== Python Environment Check ==="
    local issues=0
    
    # Check Python availability
    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Python3 not found"
        ((issues++))
    else
        local python_version=$(python3 --version 2>&1)
        echo "✅ Python found: $python_version"
    fi
    
    # Check required Python modules
    local required_modules=("json" "pathlib" "datetime" "hashlib")
    
    for module in "${required_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            echo "✅ Python module available: $module"
        else
            echo "❌ Python module missing: $module"
            ((issues++))
        fi
    done
    
    return $issues
}

check_settings_json() {
    echo -e "\n=== Settings.json Check ==="
    local issues=0
    local settings_file="$HOME/.claude/settings.json"
    
    if [[ ! -f "$settings_file" ]]; then
        echo "❌ settings.json not found"
        return 1
    fi
    
    # Validate JSON syntax
    if jq empty "$settings_file" 2>/dev/null; then
        echo "✅ settings.json syntax is valid"
    else
        echo "❌ settings.json has invalid syntax"
        ((issues++))
    fi
    
    # Check for required hooks
    local has_session_start=$(jq -r '.hooks.SessionStart // empty' "$settings_file")
    local has_subagent_stop=$(jq -r '.hooks.SubagentStop // empty' "$settings_file")
    
    if [[ -n "$has_session_start" ]]; then
        echo "✅ SessionStart hook configured"
    else
        echo "⚠️  SessionStart hook not configured"
    fi
    
    if [[ -n "$has_subagent_stop" ]]; then
        echo "✅ SubagentStop hook configured"
    else
        echo "⚠️  SubagentStop hook not configured (parallel agents disabled)"
    fi
    
    return $issues
}

check_disk_space() {
    echo -e "\n=== Disk Space Check ==="
    local issues=0
    
    # Check available space in home directory
    local available_mb=$(df -m "$HOME" | awk 'NR==2 {print $4}')
    
    if [[ $available_mb -lt 100 ]]; then
        echo "❌ Low disk space: ${available_mb}MB available (minimum 100MB recommended)"
        ((issues++))
    else
        echo "✅ Disk space OK: ${available_mb}MB available"
    fi
    
    # Check results directory size
    if [[ -d "$RESULTS_DIR" ]]; then
        local results_size=$(du -sm "$RESULTS_DIR" 2>/dev/null | cut -f1)
        if [[ $results_size -gt 500 ]]; then
            echo "⚠️  Results directory is large: ${results_size}MB"
            echo "   Consider cleaning old results with: find $RESULTS_DIR -mtime +7 -delete"
        fi
    fi
    
    return $issues
}

check_recent_errors() {
    echo -e "\n=== Recent Errors Check ==="
    local issues=0
    
    # Check for recent errors in logs
    local error_log="$LOG_DIR/errors.log"
    if [[ -f "$error_log" ]]; then
        local recent_errors=$(find "$error_log" -mmin -60 -exec grep -c "ERROR" {} \; 2>/dev/null || echo "0")
        if [[ $recent_errors -gt 0 ]]; then
            echo "⚠️  Found $recent_errors errors in the last hour"
            echo "   Last 5 errors:"
            tail -5 "$error_log" | sed 's/^/   /'
            ((issues++))
        else
            echo "✅ No recent errors"
        fi
    else
        echo "✅ No error log found (good sign)"
    fi
    
    # Check for stale temp files
    local stale_temp=$(find "$RESULTS_DIR/temp" -name "*.json" -mmin +120 2>/dev/null | wc -l)
    if [[ $stale_temp -gt 0 ]]; then
        echo "⚠️  Found $stale_temp stale temporary files (>2 hours old)"
        echo "   Consider cleaning with: find $RESULTS_DIR/temp -name '*.json' -mmin +120 -delete"
    fi
    
    return $issues
}

perform_test_execution() {
    echo -e "\n=== Test Execution ==="
    local issues=0
    
    # Test basic hook execution
    echo "Testing protocol injector..."
    if TRINITAS_HOOK_TYPE="session_start" bash "$HOME/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh" >/dev/null 2>&1; then
        echo "✅ Protocol injector works"
    else
        echo "❌ Protocol injector failed"
        ((issues++))
    fi
    
    # Test Python script execution
    echo "Testing Python environment..."
    if echo "test prompt" | CLAUDE_USER_PROMPT="test" CLAUDE_TOOL_NAME="Task" \
        python3 "$HOME/.claude/trinitas/hooks/python/prepare_parallel_tasks.py" >/dev/null 2>&1; then
        echo "✅ Python hooks work"
    else
        echo "❌ Python hooks failed"
        ((issues++))
    fi
    
    return $issues
}

# =====================================================
# Report Generation
# =====================================================

generate_report() {
    local total_issues=$1
    
    {
        echo "Trinitas Health Check Report"
        echo "Generated: $(date)"
        echo "================================"
        echo ""
        echo "Total Issues Found: $total_issues"
        echo ""
        
        if [[ $total_issues -eq 0 ]]; then
            echo "✅ System Status: HEALTHY"
            echo ""
            echo "All checks passed. Trinitas is ready for production use."
        elif [[ $total_issues -le 3 ]]; then
            echo "⚠️  System Status: WARNING"
            echo ""
            echo "Minor issues detected. System is functional but should be monitored."
        else
            echo "❌ System Status: CRITICAL"
            echo ""
            echo "Multiple issues detected. Immediate attention required."
        fi
        
        echo ""
        echo "Recommendations:"
        if [[ $total_issues -gt 0 ]]; then
            echo "1. Review the detailed output above"
            echo "2. Run: ./install.sh --force to reinstall"
            echo "3. Check settings.json for conflicts"
            echo "4. Ensure all dependencies are installed"
        else
            echo "1. Regular monitoring recommended"
            echo "2. Clean old results periodically"
            echo "3. Update hooks as new versions are released"
        fi
    } > "$HEALTH_REPORT"
    
    echo -e "\n=== Health Report Saved ==="
    echo "Report saved to: $HEALTH_REPORT"
}

# =====================================================
# Main
# =====================================================

main() {
    echo "🏥 Trinitas Health Check v1.0"
    echo "================================"
    
    # Ensure log directory exists
    mkdir -p "$LOG_DIR"
    
    local total_issues=0
    
    # Run all checks
    check_directory_structure || ((total_issues+=$?))
    check_hook_files || ((total_issues+=$?))
    check_python_environment || ((total_issues+=$?))
    check_settings_json || ((total_issues+=$?))
    check_disk_space || ((total_issues+=$?))
    check_recent_errors || ((total_issues+=$?))
    perform_test_execution || ((total_issues+=$?))
    
    # Generate report
    generate_report $total_issues
    
    # Summary
    echo ""
    echo "================================"
    if [[ $total_issues -eq 0 ]]; then
        echo "✅ All checks passed!"
    else
        echo "⚠️  Found $total_issues issues"
    fi
    
    return $total_issues
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi