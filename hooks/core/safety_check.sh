#!/bin/bash
# Trinitas Safety Check Module
# Vector: "……すべての脅威を、事前に検知し、排除する……"
# Krukai: "セキュリティは妥協できないわ。完璧な防御が必要よ"
# Springfield: "安全第一で、確実な保護を提供しましょう"

# =====================================================
# Dangerous Command Detection
# =====================================================

is_dangerous_command() {
    local cmd="$1"
    
    # Dangerous patterns to detect
    local dangerous_patterns=(
        # Destructive file operations
        "rm -rf /"
        "rm -rf /\*"
        "rm -rf ~/\*"
        "rm -rf \.\./\*"
        "rm -rf \$HOME"
        
        # Disk operations
        "dd .*of=/dev/"
        "mkfs"
        "format"
        
        # Fork bombs
        ":\(\){\s*:\|:&\s*};"
        
        # Sudo operations
        "^sudo "
        "sudo -"
        
        # System modifications
        "chmod -R 777"
        "chmod 777 /"
        "chown -R"
        
        # Package managers (without permission)
        "apt-get install"
        "yum install"
        "brew install"
        "npm install -g"
        "pip install"
        "gem install"
    )
    
    # Check each pattern
    for pattern in "${dangerous_patterns[@]}"; do
        if echo "$cmd" | grep -qE "$pattern"; then
            return 0  # Command is dangerous
        fi
    done
    
    return 1  # Command is safe
}

# =====================================================
# Path Safety Validation
# =====================================================

is_safe_path() {
    local path="$1"
    local operation="${2:-read}"
    
    # Normalize path
    local abs_path
    if [[ "$path" == /* ]]; then
        abs_path="$path"
    else
        abs_path="$(pwd)/$path"
    fi
    
    # System directories that should not be modified
    local protected_paths=(
        "/etc"
        "/usr"
        "/bin"
        "/sbin"
        "/System"
        "/Library"
        "/var"
        "/boot"
        "/proc"
        "/sys"
        "/dev"
    )
    
    # Check write operations to protected paths
    if [[ "$operation" == "write" ]]; then
        for protected in "${protected_paths[@]}"; do
            if [[ "$abs_path" == "$protected"/* ]] || [[ "$abs_path" == "$protected" ]]; then
                return 1  # Not safe
            fi
        done
    fi
    
    return 0  # Safe
}

# =====================================================
# Resource Limit Checks
# =====================================================

check_memory_available() {
    local requested_mb="$1"
    local max_allowed_mb=10240  # 10GB max
    
    if [[ "$requested_mb" -gt "$max_allowed_mb" ]]; then
        return 1  # Too much memory requested
    fi
    
    # Check actual available memory (platform specific)
    if command -v free >/dev/null 2>&1; then
        # Linux
        local available_mb=$(free -m | awk 'NR==2{print $7}')
        if [[ "$requested_mb" -gt "$available_mb" ]]; then
            return 1
        fi
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS
        local page_size=$(pagesize)
        local free_pages=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
        local available_mb=$((free_pages * page_size / 1024 / 1024))
        if [[ "$requested_mb" -gt "$available_mb" ]]; then
            return 1
        fi
    fi
    
    return 0
}

# =====================================================
# Network Safety Validation
# =====================================================

is_safe_network_operation() {
    local cmd="$1"
    
    # Dangerous network patterns
    local dangerous_patterns=(
        # Piping to shell
        "curl.*\|.*bash"
        "curl.*\|.*sh"
        "wget.*\|.*bash"
        "wget.*\|.*sh"
        "fetch.*\|.*bash"
        "fetch.*\|.*sh"
        
        # Executing remote scripts
        "bash <\(curl"
        "sh <\(wget"
        
        # Suspicious downloads
        "curl.*-o.*/etc/"
        "wget.*-O.*/etc/"
    )
    
    for pattern in "${dangerous_patterns[@]}"; do
        if echo "$cmd" | grep -qE "$pattern"; then
            return 1  # Not safe
        fi
    done
    
    return 0  # Safe
}

# =====================================================
# Git Operation Validation
# =====================================================

is_safe_git_operation() {
    local cmd="$1"
    
    # Dangerous git operations
    local dangerous_patterns=(
        # Force push to main branches
        "git push.*--force.*master"
        "git push.*--force.*main"
        "git push.*-f.*master"
        "git push.*-f.*main"
        
        # Hard reset with significant history loss
        "git reset --hard HEAD~[0-9][0-9]"
        "git reset --hard HEAD\^[0-9][0-9]"
        
        # Dangerous config changes
        "git config.*user.email.*<.*@anthropic"
        "git config.*--global"
    )
    
    for pattern in "${dangerous_patterns[@]}"; do
        if echo "$cmd" | grep -qE "$pattern"; then
            return 1  # Not safe
        fi
    done
    
    return 0  # Safe
}

# =====================================================
# Hook Environment Validation
# =====================================================

validate_hook_environment() {
    # Required environment variables
    local required_vars=(
        "CLAUDE_PROJECT_DIR"
        "CLAUDE_TOOL_NAME"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            echo "Error: Required environment variable $var is not set" >&2
            return 1
        fi
    done
    
    # Validate project directory exists
    if [[ ! -d "$CLAUDE_PROJECT_DIR" ]]; then
        echo "Error: Project directory does not exist: $CLAUDE_PROJECT_DIR" >&2
        return 1
    fi
    
    return 0
}

# =====================================================
# Main Safety Check Function
# =====================================================

perform_safety_check() {
    # Validate environment first
    if ! validate_hook_environment; then
        return 1
    fi
    
    # Extract command from tool arguments
    local tool_name="${CLAUDE_TOOL_NAME:-}"
    local tool_args="${CLAUDE_TOOL_ARGUMENTS:-}"
    
    # Handle Bash tool specifically
    if [[ "$tool_name" == "Bash" ]]; then
        # Extract command from JSON arguments
        local cmd=""
        if command -v jq >/dev/null 2>&1; then
            cmd=$(echo "$tool_args" | jq -r '.command // empty')
        else
            # Fallback: simple extraction
            cmd=$(echo "$tool_args" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
        fi
        
        if [[ -z "$cmd" ]]; then
            echo "Error: Could not extract command from arguments" >&2
            return 1
        fi
        
        # Check for dangerous commands
        if is_dangerous_command "$cmd"; then
            echo "Error: Dangerous command detected: $cmd" >&2
            return 1
        fi
        
        # Check network safety
        if ! is_safe_network_operation "$cmd"; then
            echo "Error: Unsafe network operation detected: $cmd" >&2
            return 1
        fi
        
        # Check git safety
        if echo "$cmd" | grep -q "^git "; then
            if ! is_safe_git_operation "$cmd"; then
                echo "Error: Unsafe git operation detected: $cmd" >&2
                return 1
            fi
        fi
    fi
    
    # Handle file operations
    if [[ "$tool_name" =~ ^(Write|Edit|MultiEdit)$ ]]; then
        local file_path=""
        if command -v jq >/dev/null 2>&1; then
            file_path=$(echo "$tool_args" | jq -r '.file_path // empty')
        else
            # Fallback: simple extraction
            file_path=$(echo "$tool_args" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
        fi
        
        if [[ -n "$file_path" ]]; then
            if ! is_safe_path "$file_path" "write"; then
                echo "Error: Unsafe file path for write operation: $file_path" >&2
                return 1
            fi
        fi
    fi
    
    return 0  # All checks passed
}

# Export functions for use in other scripts
export -f is_dangerous_command
export -f is_safe_path
export -f check_memory_available
export -f is_safe_network_operation
export -f is_safe_git_operation
export -f validate_hook_environment
export -f perform_safety_check