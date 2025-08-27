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
    # Vector speaks (to stderr)
    vector_says "……コマンド実行前の安全性チェックを開始……"
    
    # Validate environment
    if ! validate_claude_environment; then
        cat << EOF
{
    "continue": false,
    "error": "Invalid Claude Code environment: Required environment variables are missing or invalid"
}
EOF
        exit 0
    fi
    
    # Perform safety check
    if ! perform_safety_check; then
        local tool_name="${CLAUDE_TOOL_NAME:-unknown}"
        local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
        
        vector_says "……危険な操作を検出。実行をブロックする……"
        
        # Log the blocked operation
        local log_file="$HOME/.claude/logs/blocked_operations.log"
        ensure_directory "$(dirname "$log_file")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] BLOCKED: $tool_name - $tool_args" >> "$log_file"
        
        # Return JSON response for blocked operation (Claude Code spec compliant)
        cat << EOF
{
    "continue": false,
    "error": "Dangerous operation detected: This operation has been blocked for safety reasons.",
    "context": "Tool: $tool_name",
    "systemMessage": "⛔ Vector: 危険な操作を検出しました。\nTool: $tool_name\nこの操作は安全上の理由でブロックされました。"
}
EOF
        exit 0
    fi
    
    # Safety check passed - return continue decision (Claude Code spec compliant)
    springfield_says "安全性チェックをパスしました。実行を続行します。"
    cat << EOF
{
    "continue": true
}
EOF
    
    exit 0
}

# Run main function
main "$@"