#!/bin/bash
# Trinitas Pre-execution Safety Check Hook
# Vector: "……最初の防衛線。ここで脅威を止める……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependencies
source "$HOOKS_ROOT/core/common_lib.sh"
source "$HOOKS_ROOT/core/safety_check.sh"

# =====================================================
# Main Hook Logic
# =====================================================

main() {
    # Vector speaks
    vector_says "……コマンド実行前の安全性チェックを開始……"
    
    # Validate environment
    if ! validate_claude_environment; then
        format_hook_result "blocked" "Invalid Claude Code environment" \
            "Required environment variables are missing or invalid"
        exit 1
    fi
    
    # Perform safety check
    if ! perform_safety_check; then
        local tool_name="${CLAUDE_TOOL_NAME:-unknown}"
        local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
        
        vector_says "……危険な操作を検出。実行をブロックする……"
        
        format_hook_result "blocked" "Dangerous operation detected" \
            "Tool: $tool_name\nArguments: $tool_args\nThis operation has been blocked for safety reasons."
        
        # Log the blocked operation
        local log_file="$HOME/.claude/logs/blocked_operations.log"
        ensure_directory "$(dirname "$log_file")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] BLOCKED: $tool_name - $tool_args" >> "$log_file"
        
        exit 1
    fi
    
    # Safety check passed
    springfield_says "安全性チェックをパスしました。実行を続行します。"
    format_hook_result "success" "Safety check passed"
    
    exit 0
}

# Run main function
main "$@"