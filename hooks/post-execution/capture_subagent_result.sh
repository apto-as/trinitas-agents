#!/bin/bash
# Trinitas Capture Subagent Result Hook
# Springfield: "複数の視点を統合して、最高の成果を導き出しましょう"
# Krukai: "並列処理の結果を効率的に収集するわ"
# Vector: "……各エージェントの出力を慎重に検証する……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependencies
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# Configuration
# =====================================================

# Results directory
RESULTS_DIR="${TRINITAS_RESULTS_DIR:-$HOME/.claude/trinitas/parallel_results}"
TEMP_DIR="${RESULTS_DIR}/temp"
COMPLETED_DIR="${RESULTS_DIR}/completed"

# =====================================================
# Result Capture Functions
# =====================================================

initialize_directories() {
    ensure_directory "$RESULTS_DIR"
    ensure_directory "$TEMP_DIR"
    ensure_directory "$COMPLETED_DIR"
}

extract_subagent_info() {
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    # Extract subagent_type and session_id
    local subagent_type=""
    local session_id=""
    local task_id=""
    
    if command -v jq >/dev/null 2>&1; then
        subagent_type=$(echo "$tool_args" | jq -r '.subagent_type // empty')
        # Try to extract session/task ID from environment or generate one
        session_id="${TRINITAS_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
        task_id="${TRINITAS_TASK_ID:-${subagent_type}_$(date +%s)}"
    else
        # Fallback parsing
        log_warning "jq not available, using fallback parsing"
        session_id="${TRINITAS_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
        task_id="task_$(date +%s)"
    fi
    
    echo "${session_id}|${task_id}|${subagent_type}"
}

capture_subagent_result() {
    local tool_result="${CLAUDE_TOOL_RESULT:-}"
    local tool_error="${CLAUDE_TOOL_ERROR:-}"
    local execution_time="${CLAUDE_EXECUTION_TIME:-0}"
    
    # Extract agent information
    local agent_info=$(extract_subagent_info)
    IFS='|' read -r session_id task_id subagent_type <<< "$agent_info"
    
    if [[ -z "$subagent_type" ]]; then
        log_debug "Not a subagent task, skipping capture"
        return 0
    fi
    
    springfield_says "サブエージェント ${subagent_type} の結果をキャプチャします"
    
    # Create result file
    local timestamp=$(date +%Y%m%d_%H%M%S_%N)
    local result_file="${TEMP_DIR}/${session_id}_${task_id}_${timestamp}.json"
    
    # Build result JSON
    cat > "$result_file" << EOF
{
    "session_id": "${session_id}",
    "task_id": "${task_id}",
    "subagent_type": "${subagent_type}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
    "execution_time_ms": ${execution_time},
    "status": $([ -n "$tool_error" ] && echo '"error"' || echo '"success"'),
    "result": $(echo "$tool_result" | jq -Rs . 2>/dev/null || echo '""'),
    "error": $(echo "$tool_error" | jq -Rs . 2>/dev/null || echo 'null'),
    "metadata": {
        "tool_name": "${CLAUDE_TOOL_NAME:-}",
        "claude_request_id": "${CLAUDE_REQUEST_ID:-}",
        "project_dir": "${CLAUDE_PROJECT_DIR:-}"
    }
}
EOF
    
    krukai_says "結果を ${result_file} に保存しました"
    
    # Check if all parallel tasks are complete
    check_parallel_completion "$session_id"
    
    return 0
}

check_parallel_completion() {
    local session_id="$1"
    
    # Count results for this session
    local result_count=$(find "$TEMP_DIR" -name "${session_id}_*.json" -type f | wc -l)
    
    # Check if we have expected number of results (from environment variable)
    local expected_count="${TRINITAS_PARALLEL_COUNT:-0}"
    
    if [[ $expected_count -gt 0 ]] && [[ $result_count -ge $expected_count ]]; then
        vector_says "……全ての並列タスクが完了……結果を統合する時……"
        
        # Move all results to completed directory
        local completed_dir="${COMPLETED_DIR}/${session_id}"
        ensure_directory "$completed_dir"
        
        find "$TEMP_DIR" -name "${session_id}_*.json" -type f -exec mv {} "$completed_dir/" \;
        
        # Trigger integration if hook is available
        if [[ -x "$HOOKS_ROOT/python/integrate_parallel_results.py" ]]; then
            log_info "Triggering result integration for session: $session_id"
            # Set environment variable for integration script
            export TRINITAS_INTEGRATION_SESSION="$session_id"
        fi
    else
        log_debug "Waiting for more results: $result_count/$expected_count"
    fi
}

# =====================================================
# Main Hook Logic
# =====================================================

main() {
    # Initialize directories
    initialize_directories
    
    # Validate environment
    if ! validate_claude_environment; then
        log_error "Invalid Claude Code environment"
        echo '{}'
        return 0
    fi
    
    # Check if this is a SubagentStop event
    local hook_event="${CLAUDE_HOOK_EVENT:-}"
    if [[ "$hook_event" != "SubagentStop" ]]; then
        log_debug "Not a SubagentStop event, skipping"
        echo '{}'
        return 0
    fi
    
    # Check if this is a Task tool result
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    if [[ "$tool_name" != "Task" ]]; then
        log_debug "Not a Task tool result, skipping"
        echo '{}'
        return 0
    fi
    
    # Capture the subagent result
    if capture_subagent_result; then
        # Return success message
        cat << EOF
{
    "systemMessage": "✅ Trinitas: サブエージェントの結果を正常にキャプチャしました"
}
EOF
    else
        # Return error message
        cat << EOF
{
    "systemMessage": "⚠️ Trinitas: サブエージェントの結果キャプチャ中にエラーが発生しました"
}
EOF
    fi
    
    return 0
}

# Run main function
main "$@"