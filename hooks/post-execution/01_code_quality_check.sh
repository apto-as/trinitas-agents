#!/bin/bash
# Trinitas Post-execution Code Quality Check Hook
# Krukai: "フン、完璧なコードでなければ意味がないわ"
# Springfield: "品質チェックで、より良いコードを目指しましょう"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependencies
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# Language Detection
# =====================================================

detect_file_language() {
    local file="$1"
    local extension="${file##*.}"
    
    case "$extension" in
        js|jsx|ts|tsx)
            echo "javascript"
            ;;
        py)
            echo "python"
            ;;
        rb)
            echo "ruby"
            ;;
        go)
            echo "go"
            ;;
        rs)
            echo "rust"
            ;;
        java)
            echo "java"
            ;;
        c|h)
            echo "c"
            ;;
        cpp|cc|cxx|hpp)
            echo "cpp"
            ;;
        sh|bash)
            echo "shell"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# =====================================================
# Basic Quality Checks
# =====================================================

check_file_size() {
    local file="$1"
    local max_size_kb=500
    
    if [[ ! -f "$file" ]]; then
        return 0
    fi
    
    local size_kb=$(du -k "$file" | cut -f1)
    if [[ $size_kb -gt $max_size_kb ]]; then
        log_warning "File size warning: $file is ${size_kb}KB (max recommended: ${max_size_kb}KB)"
        return 1
    fi
    
    return 0
}

check_line_length() {
    local file="$1"
    local max_length=120
    local long_lines=0
    
    while IFS= read -r line; do
        if [[ ${#line} -gt $max_length ]]; then
            ((long_lines++))
        fi
    done < "$file"
    
    if [[ $long_lines -gt 0 ]]; then
        log_warning "Line length warning: $long_lines lines exceed $max_length characters"
        return 1
    fi
    
    return 0
}

check_trailing_whitespace() {
    local file="$1"
    
    if grep -q '[[:space:]]$' "$file"; then
        log_warning "Trailing whitespace detected in $file"
        krukai_says "空白文字の無駄は許さないわ。削除しなさい"
        return 1
    fi
    
    return 0
}

check_mixed_indentation() {
    local file="$1"
    
    local has_tabs=$(grep -l $'^\t' "$file" 2>/dev/null)
    local has_spaces=$(grep -l '^  ' "$file" 2>/dev/null)
    
    if [[ -n "$has_tabs" ]] && [[ -n "$has_spaces" ]]; then
        log_warning "Mixed indentation (tabs and spaces) detected in $file"
        krukai_says "インデントの混在は許容できないわ。統一しなさい"
        return 1
    fi
    
    return 0
}

# =====================================================
# Language-specific Checks
# =====================================================

check_javascript_quality() {
    local file="$1"
    local warnings=0
    
    # Check for console.log statements
    if grep -q 'console\.log' "$file"; then
        log_warning "console.log statements found (consider using proper logging)"
        ((warnings++))
    fi
    
    # Check for debugger statements
    if grep -q 'debugger' "$file"; then
        log_warning "debugger statements found (remove before production)"
        ((warnings++))
    fi
    
    # Check for TODO/FIXME comments
    if grep -qE '(TODO|FIXME|XXX)' "$file"; then
        log_warning "TODO/FIXME comments found"
        ((warnings++))
    fi
    
    return $warnings
}

check_python_quality() {
    local file="$1"
    local warnings=0
    
    # Check for print statements (Python 3)
    if grep -qE '^[^#]*print\(' "$file"; then
        log_warning "print() statements found (consider using logging module)"
        ((warnings++))
    fi
    
    # Check for bare except
    if grep -qE 'except\s*:' "$file"; then
        log_warning "Bare except clause found (specify exception type)"
        ((warnings++))
    fi
    
    # Check for TODO/FIXME comments
    if grep -qE '(TODO|FIXME|XXX)' "$file"; then
        log_warning "TODO/FIXME comments found"
        ((warnings++))
    fi
    
    return $warnings
}

check_shell_quality() {
    local file="$1"
    local warnings=0
    
    # Check for unquoted variables
    if grep -qE '\$[A-Za-z_][A-Za-z0-9_]*[^"]' "$file" | grep -v '^\s*#'; then
        log_warning "Potentially unquoted variables found"
        ((warnings++))
    fi
    
    # Check for backticks instead of $()
    if grep -q '`' "$file"; then
        log_warning "Backticks found (use \$() instead)"
        ((warnings++))
    fi
    
    return $warnings
}

# =====================================================
# Main Quality Check Function
# =====================================================

perform_quality_check() {
    local file_path="$1"
    local language="$2"
    local total_warnings=0
    
    krukai_says "コード品質チェックを開始するわ。妥協は許さない"
    
    # Basic checks for all files
    check_file_size "$file_path" || ((total_warnings++))
    check_line_length "$file_path" || ((total_warnings++))
    check_trailing_whitespace "$file_path" || ((total_warnings++))
    check_mixed_indentation "$file_path" || ((total_warnings++))
    
    # Language-specific checks
    case "$language" in
        javascript)
            check_javascript_quality "$file_path"
            ((total_warnings+=$?))
            ;;
        python)
            check_python_quality "$file_path"
            ((total_warnings+=$?))
            ;;
        shell)
            check_shell_quality "$file_path"
            ((total_warnings+=$?))
            ;;
    esac
    
    # Summary
    if [[ $total_warnings -eq 0 ]]; then
        springfield_says "素晴らしい！品質チェックをすべてパスしました"
    else
        krukai_says "フン、${total_warnings}個の品質問題を見つけたわ。改善の余地があるわね"
    fi
    
    return $total_warnings
}

# =====================================================
# Main Hook Logic
# =====================================================

main() {
    # Validate environment
    if ! validate_claude_environment; then
        cat << EOF
{
    "systemMessage": "Invalid Claude Code environment for quality check"
}
EOF
        return 0
    fi
    
    # Check which tool was used
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    # Only process file modification tools
    if [[ ! "$tool_name" =~ ^(Write|Edit|MultiEdit)$ ]]; then
        echo '{}'  # Return empty JSON for non-applicable tools
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
        log_warning "Could not extract file path from tool arguments"
        echo '{}'
        return 0
    fi
    
    # Detect language
    local language=$(detect_file_language "$file_path")
    
    if [[ "$language" == "unknown" ]]; then
        log_debug "Unknown file type, skipping quality check: $file_path"
        echo '{}'
        return 0
    fi
    
    # Perform quality check
    perform_quality_check "$file_path" "$language"
    local warnings=$?
    
    # Return JSON response
    if [[ $warnings -eq 0 ]]; then
        cat << EOF
{
    "systemMessage": "✅ Springfield: コード品質チェックをパスしました！素晴らしいコードです。"
}
EOF
    else
        cat << EOF
{
    "systemMessage": "⚠️ Krukai: ${warnings}個の品質問題を検出しました。\n詳細はログを確認してください。完璧を目指しましょう。"
}
EOF
    fi
    
    return 0
}

# Run main function
main "$@"