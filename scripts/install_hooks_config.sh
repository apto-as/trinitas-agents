#!/bin/bash
# Trinitas Hooks Configuration Installer
# Springfield: "設定ファイルの管理も、慎重に行いましょうね"

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRINITAS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common library if available
if [[ -f "$TRINITAS_ROOT/hooks/core/common_lib.sh" ]]; then
    source "$TRINITAS_ROOT/hooks/core/common_lib.sh"
else
    # Basic logging functions if common_lib not available
    log_info() { echo "[INFO] $1"; }
    log_error() { echo "[ERROR] $1" >&2; }
    log_success() { echo "[SUCCESS] $1"; }
    log_warning() { echo "[WARNING] $1"; }
fi

# Install hooks configuration
install_hooks_config() {
    local scope="$1"
    local mode="${2:-standard}"
    
    # Dynamic path resolution based on scope
    local settings_file
    local trinitas_hooks_dir
    
    case "$scope" in
        "user")
            settings_file="$HOME/.claude/settings.json"
            trinitas_hooks_dir="$HOME/.claude/trinitas/hooks"
            ;;
        "project")
            settings_file=".claude/settings.json"
            trinitas_hooks_dir=".claude/trinitas/hooks"
            ;;
        *)
            log_error "Invalid scope '$scope'. Must be 'user' or 'project'"
            return 1
            ;;
    esac
    
    # Check if settings.json exists
    if [[ ! -f "$settings_file" ]]; then
        log_warning "settings.json not found at: $settings_file"
        log_info "Creating minimal settings.json with hooks configuration..."
        
        # Create minimal settings.json
        mkdir -p "$(dirname "$settings_file")"
        cat > "$settings_file" << 'EOF'
{
  "hooks": {}
}
EOF
    fi
    
    # Enhanced backup system with recovery functionality
    local backup_dir="$(dirname "$settings_file")/.trinitas_backups"
    local backup_file
    
    if [[ -f "$settings_file" ]]; then
        mkdir -p "$backup_dir"
        backup_file="$backup_dir/settings_$(date +%Y%m%d_%H%M%S).json"
        cp "$settings_file" "$backup_file"
        
        # Create recovery metadata
        cat > "$backup_dir/recovery_info.json" << EOF
{
  "last_backup": "$backup_file",
  "backup_timestamp": "$(date -Iseconds)",
  "scope": "$scope",
  "mode": "$mode"
}
EOF
        
        log_info "Backed up existing settings to: $backup_file"
        
        # Cleanup old backups (keep last 10)
        find "$backup_dir" -name "settings_*.json" -type f | \
            sort -r | tail -n +11 | xargs -r rm -f
    fi
    
    # Check if jq is available for JSON manipulation
    if command -v jq >/dev/null 2>&1; then
        log_info "Using jq to update settings.json..."
        
        # Create hooks configuration based on mode
        local hooks_config
        case "$mode" in
            "minimal")
                hooks_config=$(cat << 'EOF'
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/pre-execution/01_safety_check.sh"
        }
      ]
    }
  ]
}
EOF
                )
                ;;
            "comprehensive")
                hooks_config=$(cat << 'EOF'
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/pre-execution/01_safety_check.sh"
        }
      ]
    },
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/pre-execution/02_file_safety_check.sh"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/post-execution/01_code_quality_check.sh"
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/post-execution/02_test_runner.sh"
        }
      ]
    }
  ]
}
EOF
                )
                ;;
            *)  # standard mode
                hooks_config=$(cat << 'EOF'
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/core/trinitas_protocol_injector.sh"
        }
      ]
    }
  ],
  "PreCompact": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/core/trinitas_protocol_injector.sh pre_compact"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/pre-execution/01_safety_check.sh"
        }
      ]
    },
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/pre-execution/02_file_safety_check.sh"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/post-execution/01_code_quality_check.sh"
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "$trinitas_hooks_dir/post-execution/02_test_runner.sh"
        }
      ]
    }
  ]
}
EOF
                )
                ;;
        esac
        
        # Expand trinitas_hooks_dir variable in configuration and write to temp file
        echo "$hooks_config" | sed "s|\$trinitas_hooks_dir|$trinitas_hooks_dir|g" > /tmp/trinitas_hooks_config.json
        
        # Merge hooks configuration into settings.json (preserving existing hooks)
        # Use merge strategy from upgrade.sh to avoid complete overwrite
        jq '.hooks = (.hooks // {}) * $hooks[0]' "$settings_file" \
            --slurpfile hooks /tmp/trinitas_hooks_config.json > /tmp/trinitas_settings_updated.json
        
        # Validate generated JSON before replacing original file
        if jq empty /tmp/trinitas_settings_updated.json >/dev/null 2>&1; then
            mv /tmp/trinitas_settings_updated.json "$settings_file"
            log_success "Hooks configuration added to settings.json"
        else
            log_error "Generated settings.json is invalid! Attempting recovery..."
            if [[ -n "$backup_file" && -f "$backup_file" ]]; then
                recover_from_backup "$settings_file" "$backup_file"
            fi
            rm -f /tmp/trinitas_settings_updated.json
            return 1
        fi
        
        rm -f /tmp/trinitas_hooks_config.json
    else
        log_warning "jq not found. Please manually add hooks configuration to settings.json"
        log_info "Example configuration can be found at: $TRINITAS_ROOT/hooks/examples/settings.json"
    fi
}

# Install documentation
install_documentation() {
    local scope="$1"
    
    # Determine target directory
    local target_dir
    if [[ "$scope" == "user" ]]; then
        target_dir="$HOME/.claude"
    else
        target_dir=".claude"
    fi
    
    # Create directory if needed
    mkdir -p "$target_dir"
    
    # Copy TRINITAS-AGENTS.md as CLAUDE.md
    if [[ -f "$TRINITAS_ROOT/TRINITAS-AGENTS.md" ]]; then
        cp "$TRINITAS_ROOT/TRINITAS-AGENTS.md" "$target_dir/CLAUDE.md"
        log_success "Documentation installed to: $target_dir/CLAUDE.md"
    else
        log_error "TRINITAS-AGENTS.md not found"
        return 1
    fi
    
    # Copy protocol template if it doesn't exist
    if [[ ! -f "$target_dir/TRINITAS-CORE-PROTOCOL.md" ]] && [[ -f "$TRINITAS_ROOT/templates/TRINITAS-CORE-PROTOCOL.md" ]]; then
        cp "$TRINITAS_ROOT/templates/TRINITAS-CORE-PROTOCOL.md" "$target_dir/TRINITAS-CORE-PROTOCOL.md"
        log_success "Protocol template installed to: $target_dir/TRINITAS-CORE-PROTOCOL.md"
    fi
}

# Main function
main() {
    local scope="${1:-project}"
    local mode="${2:-standard}"
    
    log_info "Installing Trinitas hooks configuration..."
    log_info "Scope: $scope, Mode: $mode"
    
    # Install documentation
    install_documentation "$scope"
    
    # Install hooks configuration
    install_hooks_config "$scope" "$mode"
    
    log_success "Trinitas hooks configuration completed!"
}

# Recovery function for backup restoration
recover_from_backup() {
    local target_file="$1"
    local backup_file="$2"
    
    if [[ -f "$backup_file" ]]; then
        log_info "Restoring from backup: $backup_file"
        cp "$backup_file" "$target_file"
        
        # Verify restored file
        if jq empty "$target_file" >/dev/null 2>&1; then
            log_success "Successfully restored from backup"
            return 0
        else
            log_error "Backup file is also corrupted!"
            return 1
        fi
    else
        log_error "No backup file found for recovery"
        return 1
    fi
}

# Enhanced backup management
cleanup_old_backups() {
    local backup_dir="$1"
    local keep_count="${2:-10}"
    
    if [[ -d "$backup_dir" ]]; then
        local backup_count
        backup_count=$(find "$backup_dir" -name "settings_*.json" -type f | wc -l)
        
        if [[ $backup_count -gt $keep_count ]]; then
            log_info "Cleaning up old backups (keeping last $keep_count)..."
            find "$backup_dir" -name "settings_*.json" -type f | \
                sort -r | tail -n +$((keep_count + 1)) | xargs -r rm -f
        fi
    fi
}

# Backup validation and listing
list_available_backups() {
    local backup_dir="$1"
    
    if [[ -d "$backup_dir" ]]; then
        echo "Available backups:"
        find "$backup_dir" -name "settings_*.json" -type f | \
            sort -r | head -5 | while read -r backup; do
            local timestamp
            timestamp=$(basename "$backup" .json | sed 's/settings_//')
            echo "  - $backup ($(date -d "${timestamp//_/ }" 2>/dev/null || echo "$timestamp"))"
        done
    else
        echo "No backup directory found at: $backup_dir"
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi