#!/bin/bash
# Trinitas Common Library
# Springfield: "共通ライブラリで、再利用性を高めましょうね"
# Krukai: "DRY原則よ。同じコードを二度書くなんて非効率の極みだわ"
# Vector: "……共通化されたコードは、脆弱性の単一障害点になりうる……慎重に"

# =====================================================
# Color Definitions
# =====================================================

# Standard colors
export TRINITAS_RED='\033[0;31m'
export TRINITAS_GREEN='\033[0;32m'
export TRINITAS_YELLOW='\033[1;33m'
export TRINITAS_BLUE='\033[0;34m'
export TRINITAS_MAGENTA='\033[0;35m'
export TRINITAS_CYAN='\033[0;36m'
export TRINITAS_WHITE='\033[1;37m'
export TRINITAS_NC='\033[0m'  # No Color

# Character colors
export SPRINGFIELD_COLOR="$TRINITAS_MAGENTA"  # 優しい紫
export KRUKAI_COLOR="$TRINITAS_BLUE"          # クールな青
export VECTOR_COLOR="$TRINITAS_CYAN"          # 警戒の水色

# =====================================================
# Logging Functions
# =====================================================

log_info() {
    local message="$1"
    echo -e "${TRINITAS_BLUE}[INFO]${TRINITAS_NC} $message" >&2
}

log_success() {
    local message="$1"
    echo -e "${TRINITAS_GREEN}[SUCCESS]${TRINITAS_NC} $message" >&2
}

log_warning() {
    local message="$1"
    echo -e "${TRINITAS_YELLOW}[WARNING]${TRINITAS_NC} $message" >&2
}

log_error() {
    local message="$1"
    echo -e "${TRINITAS_RED}[ERROR]${TRINITAS_NC} $message" >&2
}

log_debug() {
    local message="$1"
    if [[ "${TRINITAS_DEBUG:-false}" == "true" ]]; then
        echo -e "${TRINITAS_CYAN}[DEBUG]${TRINITAS_NC} $message" >&2
    fi
}

# =====================================================
# Character Logging
# =====================================================

springfield_says() {
    local message="$1"
    echo -e "${SPRINGFIELD_COLOR}[Springfield]${TRINITAS_NC} $message" >&2
}

krukai_says() {
    local message="$1"
    echo -e "${KRUKAI_COLOR}[Krukai]${TRINITAS_NC} $message" >&2
}

vector_says() {
    local message="$1"
    echo -e "${VECTOR_COLOR}[Vector]${TRINITAS_NC} $message" >&2
}

# =====================================================
# Environment Validation
# =====================================================

validate_claude_environment() {
    # Check if we're running in Claude Code context
    if [[ -z "${CLAUDE_TOOL_NAME:-}" ]]; then
        log_error "Not running in Claude Code context"
        return 1
    fi
    
    # Check for project directory
    if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
        log_error "CLAUDE_PROJECT_DIR not set"
        return 1
    fi
    
    if [[ ! -d "$CLAUDE_PROJECT_DIR" ]]; then
        log_error "Project directory does not exist: $CLAUDE_PROJECT_DIR"
        return 1
    fi
    
    return 0
}

# =====================================================
# JSON Parsing
# =====================================================

extract_json_value() {
    local json="$1"
    local key="$2"
    
    # Try jq first if available
    if command -v jq >/dev/null 2>&1; then
        echo "$json" | jq -r ".$key // empty"
        return
    fi
    
    # Fallback to simple grep/sed extraction
    echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | \
        sed "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/"
}

# =====================================================
# File Operations
# =====================================================

ensure_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || {
            log_error "Failed to create directory: $dir"
            return 1
        }
    fi
    return 0
}

safe_file_backup() {
    local file="$1"
    local backup_dir="${2:-$HOME/.claude/backups}"
    
    if [[ ! -f "$file" ]]; then
        return 0  # No file to backup
    fi
    
    ensure_directory "$backup_dir"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local filename=$(basename "$file")
    local backup_path="$backup_dir/${filename}.${timestamp}.bak"
    
    cp "$file" "$backup_path" || {
        log_error "Failed to backup file: $file"
        return 1
    }
    
    log_debug "Backed up $file to $backup_path"
    return 0
}

# =====================================================
# Process Management
# =====================================================

is_process_running() {
    local pid="$1"
    kill -0 "$pid" 2>/dev/null
}

timeout_command() {
    local timeout_seconds="$1"
    shift
    local command=("$@")
    
    # Use timeout command if available
    if command -v timeout >/dev/null 2>&1; then
        timeout "$timeout_seconds" "${command[@]}"
    elif command -v gtimeout >/dev/null 2>&1; then
        gtimeout "$timeout_seconds" "${command[@]}"
    else
        # Fallback: run in background and kill after timeout
        "${command[@]}" &
        local pid=$!
        
        (
            sleep "$timeout_seconds"
            if is_process_running "$pid"; then
                kill -TERM "$pid" 2>/dev/null
                sleep 1
                if is_process_running "$pid"; then
                    kill -KILL "$pid" 2>/dev/null
                fi
            fi
        ) &
        
        local timer_pid=$!
        wait "$pid"
        local exit_code=$?
        kill "$timer_pid" 2>/dev/null || true
        return $exit_code
    fi
}

# =====================================================
# System Information
# =====================================================

get_system_info() {
    local info=""
    
    # OS information
    if [[ -f /etc/os-release ]]; then
        info+="OS: $(grep '^PRETTY_NAME' /etc/os-release | cut -d'"' -f2)\n"
    elif [[ "$(uname)" == "Darwin" ]]; then
        info+="OS: macOS $(sw_vers -productVersion)\n"
    else
        info+="OS: $(uname -s) $(uname -r)\n"
    fi
    
    # Memory information
    if command -v free >/dev/null 2>&1; then
        info+="Memory: $(free -h | awk 'NR==2{print $2" total, "$3" used"}')\n"
    elif command -v vm_stat >/dev/null 2>&1; then
        local pages_free=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
        local pages_active=$(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
        info+="Memory: Active pages: $pages_active, Free pages: $pages_free\n"
    fi
    
    # CPU information
    if [[ -f /proc/cpuinfo ]]; then
        info+="CPU: $(grep -m1 'model name' /proc/cpuinfo | cut -d':' -f2 | xargs)\n"
    elif command -v sysctl >/dev/null 2>&1; then
        info+="CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")\n"
    fi
    
    echo -e "$info"
}

# =====================================================
# Hook Result Formatting
# =====================================================

format_hook_result() {
    local status="$1"
    local message="$2"
    local details="${3:-}"
    
    local result=""
    
    if [[ "$status" == "success" ]]; then
        result="${TRINITAS_GREEN}✓ Hook Success${TRINITAS_NC}"
    elif [[ "$status" == "warning" ]]; then
        result="${TRINITAS_YELLOW}⚠ Hook Warning${TRINITAS_NC}"
    elif [[ "$status" == "error" ]]; then
        result="${TRINITAS_RED}✗ Hook Error${TRINITAS_NC}"
    elif [[ "$status" == "blocked" ]]; then
        result="${TRINITAS_RED}⛔ Hook Blocked${TRINITAS_NC}"
    fi
    
    result+=": $message"
    
    if [[ -n "$details" ]]; then
        result+="\n$details"
    fi
    
    echo -e "$result"
}

# =====================================================
# Trinitas Configuration
# =====================================================

load_trinitas_config() {
    local config_file="${TRINITAS_CONFIG:-$HOME/.claude/trinitas/config}"
    
    if [[ -f "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
        return 0
    fi
    
    # Default configuration
    export TRINITAS_LOG_LEVEL="${TRINITAS_LOG_LEVEL:-INFO}"
    export TRINITAS_BACKUP_ENABLED="${TRINITAS_BACKUP_ENABLED:-true}"
    export TRINITAS_SAFETY_LEVEL="${TRINITAS_SAFETY_LEVEL:-HIGH}"
    export TRINITAS_PARALLEL_AGENTS="${TRINITAS_PARALLEL_AGENTS:-false}"
    
    return 0
}

# =====================================================
# Export All Functions
# =====================================================

# Export logging functions
export -f log_info log_success log_warning log_error log_debug
export -f springfield_says krukai_says vector_says

# Export utility functions
export -f validate_claude_environment extract_json_value
export -f ensure_directory safe_file_backup
export -f is_process_running timeout_command
export -f get_system_info format_hook_result
export -f load_trinitas_config

# Load configuration on source
load_trinitas_config