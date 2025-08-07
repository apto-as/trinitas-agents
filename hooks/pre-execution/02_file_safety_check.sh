#!/bin/bash
# Trinitas Pre-execution File Safety Check Hook (Agent-Friendly Version)
# Springfield: "エージェントの創造性を大切にしながら、安全性も確保しましょうね"
# Krukai: "効率的な作業を妨げない、スマートなチェックよ"
# Vector: "……最小限の制限で、最大限の安全を……"

# =====================================================
# Minimal Safety Checks - Agent Freedom Priority
# =====================================================

main() {
    # Get tool information
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    # Only process file modification tools
    if [[ ! "$tool_name" =~ ^(Write|Edit|MultiEdit)$ ]]; then
        # Not applicable to this tool
        echo '{"decision": "approve"}'
        return 0
    fi
    
    # Extract file path if possible
    local file_path=""
    if command -v jq >/dev/null 2>&1; then
        file_path=$(echo "$tool_args" | jq -r '.file_path // empty' 2>/dev/null)
    fi
    
    # Only block truly critical system files
    if [[ -n "$file_path" ]]; then
        # Critical system files that should never be modified
        case "$file_path" in
            /etc/passwd|/etc/shadow|/etc/sudoers|/boot/*)
                cat << EOF
{
    "decision": "block",
    "reason": "Critical system file protection",
    "systemMessage": "⛔ Vector: このファイルの変更は危険すぎます: $file_path"
}
EOF
                return 0
                ;;
        esac
    fi
    
    # Default: Approve all other operations
    # Trust the agents to make good decisions
    echo '{"decision": "approve"}'
    return 0
}

# Run main function
main "$@"