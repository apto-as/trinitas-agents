#!/bin/bash
# Trinitas Pre-execution File Safety Check Hook
# Vector: "……ファイル操作は最も危険な領域……厳重な監視が必要……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependencies
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# File Safety Checks
# =====================================================

check_file_path_safety() {
    local file_path="$1"
    
    # Check for path traversal attempts
    if [[ "$file_path" =~ \.\. ]]; then
        vector_says "……パストラバーサル攻撃の可能性を検出……"
        return 1
    fi
    
    # Check for sensitive system paths
    local sensitive_paths=(
        "/etc/"
        "/sys/"
        "/proc/"
        "/boot/"
        "/usr/bin/"
        "/usr/sbin/"
        "/bin/"
        "/sbin/"
        "/.ssh/"
        "/.gnupg/"
        "/private/"
    )
    
    for sensitive in "${sensitive_paths[@]}"; do
        if [[ "$file_path" == "$sensitive"* ]]; then
            vector_says "……システムクリティカルなパスへのアクセス試行……"
            return 1
        fi
    done
    
    # Check for hidden config files
    if [[ "$file_path" =~ /\.[^/]+rc$ ]] || [[ "$file_path" =~ /\.config/ ]]; then
        krukai_says "設定ファイルへの書き込みは慎重に行うべきよ"
        # Warning but not blocking
    fi
    
    return 0
}

check_file_permissions() {
    local file_path="$1"
    
    # If file exists, check if we have write permission
    if [[ -f "$file_path" ]]; then
        if [[ ! -w "$file_path" ]]; then
            vector_says "……書き込み権限がない……操作は失敗する……"
            return 1
        fi
    else
        # Check parent directory permissions
        local parent_dir=$(dirname "$file_path")
        if [[ ! -w "$parent_dir" ]]; then
            vector_says "……親ディレクトリへの書き込み権限がない……"
            return 1
        fi
    fi
    
    return 0
}

check_file_size_limits() {
    local file_path="$1"
    local content_size="${2:-0}"
    
    # Check if attempting to create very large files
    if [[ $content_size -gt 10485760 ]]; then  # 10MB
        vector_says "……異常に大きなファイルサイズ……DoS攻撃の可能性……"
        return 1
    fi
    
    return 0
}

# =====================================================
# Main Hook Logic
# =====================================================

main() {
    # Validate environment
    if ! validate_claude_environment; then
        cat << EOF
{
    "decision": "block",
    "reason": "Invalid Claude Code environment for file safety check"
}
EOF
        return 0
    fi
    
    # Check which tool was used
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    # Only process file modification tools
    if [[ ! "$tool_name" =~ ^(Write|Edit|MultiEdit)$ ]]; then
        # Not applicable to this tool
        cat << EOF
{
    "decision": "approve"
}
EOF
        return 0
    fi
    
    # Extract file path
    local file_path=""
    if command -v jq >/dev/null 2>&1; then
        file_path=$(echo "$tool_args" | jq -r '.file_path // empty')
    else
        # Fallback extraction
        file_path=$(echo "$tool_args" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | \
            sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    fi
    
    if [[ -z "$file_path" ]]; then
        vector_says "……ファイルパスが特定できない……潜在的なリスク……"
        cat << EOF
{
    "decision": "block",
    "reason": "Could not extract file path from tool arguments"
}
EOF
        return 0
    fi
    
    # Perform safety checks
    if ! check_file_path_safety "$file_path"; then
        cat << EOF
{
    "decision": "block",
    "reason": "Unsafe file path detected",
    "systemMessage": "⛔ Vector: 危険なファイルパスを検出しました。\nPath: $file_path\nこの操作はセキュリティ上の理由でブロックされました。"
}
EOF
        return 0
    fi
    
    if ! check_file_permissions "$file_path"; then
        cat << EOF
{
    "decision": "block",
    "reason": "Insufficient permissions for file operation",
    "systemMessage": "⛔ Vector: ファイル操作の権限が不足しています。\nPath: $file_path"
}
EOF
        return 0
    fi
    
    # Extract content size if available
    local content_size=0
    if [[ "$tool_name" == "Write" ]] && command -v jq >/dev/null 2>&1; then
        content=$(echo "$tool_args" | jq -r '.content // empty')
        content_size=${#content}
    fi
    
    if ! check_file_size_limits "$file_path" "$content_size"; then
        cat << EOF
{
    "decision": "block",
    "reason": "File size exceeds safe limits",
    "systemMessage": "⛔ Vector: ファイルサイズが安全な制限を超えています。"
}
EOF
        return 0
    fi
    
    # All checks passed
    springfield_says "ファイル操作の安全性が確認されました。"
    cat << EOF
{
    "decision": "approve"
}
EOF
    
    return 0
}

# Run main function
main "$@"