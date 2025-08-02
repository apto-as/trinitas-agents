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
    
    # Determine target settings file
    local settings_file
    if [[ "$scope" == "user" ]]; then
        settings_file="$HOME/.claude/settings.json"
    else
        settings_file=".claude/settings.json"
    fi
    
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
    
    # Backup existing settings
    if [[ -f "$settings_file" ]]; then
        local backup_file="${settings_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$settings_file" "$backup_file"
        log_info "Backed up existing settings to: $backup_file"
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
          "command": "~/.claude/trinitas/hooks/pre-execution/01_safety_check.sh"
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
          "command": "~/.claude/trinitas/hooks/pre-execution/01_safety_check.sh"
        }
      ]
    },
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/trinitas/hooks/pre-execution/02_file_safety_check.sh"
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
          "command": "~/.claude/trinitas/hooks/post-execution/01_code_quality_check.sh"
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/trinitas/hooks/post-execution/02_test_runner.sh"
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
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/trinitas/hooks/pre-execution/01_safety_check.sh"
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
          "command": "~/.claude/trinitas/hooks/post-execution/01_code_quality_check.sh"
        }
      ]
    }
  ]
}
EOF
                )
                ;;
        esac
        
        # Update settings.json with hooks configuration
        echo "$hooks_config" > /tmp/trinitas_hooks_config.json
        
        # Merge hooks configuration into settings.json
        jq '.hooks = $hooks[0]' "$settings_file" --slurpfile hooks /tmp/trinitas_hooks_config.json > /tmp/trinitas_settings_updated.json
        
        # Replace original file
        mv /tmp/trinitas_settings_updated.json "$settings_file"
        rm -f /tmp/trinitas_hooks_config.json
        
        log_success "Hooks configuration added to settings.json"
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

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi