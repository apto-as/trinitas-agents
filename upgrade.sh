#!/bin/bash

# Trinitas v2.0 Upgrade Script
# 既存のTrinitasインストールを安全にアップグレード

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRINITAS_ROOT="$SCRIPT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
🌸 ===================================================== 🌸
   
   TRINITAS v2.0 - Upgrade Script
   
   Safely upgrade from previous versions
   
🌸 ===================================================== 🌸
EOF
    echo -e "${NC}"
}

# Check existing installation
check_existing_installation() {
    log_info "Checking existing Trinitas installation..."
    
    local has_user_install=false
    local has_project_install=false
    local old_version_detected=false
    
    # Check user installation
    if [[ -d "$HOME/.claude/agents" ]] || [[ -f "$HOME/.claude/CLAUDE.md" ]]; then
        has_user_install=true
        log_info "Found user installation in ~/.claude/"
    fi
    
    # Check for old Python-based hooks
    if [[ -d "$HOME/.claude/hooks" ]] && find "$HOME/.claude/hooks" -name "*.py" -type f | grep -q .; then
        old_version_detected=true
        log_warning "Detected old Python-based hooks"
    fi
    
    # Check for old SuperClaude artifacts
    if [[ -f "$HOME/.claude/scripts/hooks/setup_trinitas_hooks.py" ]]; then
        old_version_detected=true
        log_warning "Detected SuperClaude artifacts"
    fi
    
    # Check project installation
    if [[ -d ".claude/agents" ]] || [[ -f ".claude/CLAUDE.md" ]]; then
        has_project_install=true
        log_info "Found project installation in .claude/"
    fi
    
    echo
    echo "Installation Status:"
    echo "  User installation: $([ "$has_user_install" = true ] && echo "YES" || echo "NO")"
    echo "  Project installation: $([ "$has_project_install" = true ] && echo "YES" || echo "NO")"
    echo "  Old version detected: $([ "$old_version_detected" = true ] && echo "YES" || echo "NO")"
    echo
    
    return 0
}

# Backup existing installation
backup_existing() {
    local scope=$1
    local base_dir=""
    
    if [[ "$scope" == "user" ]]; then
        base_dir="$HOME/.claude"
    else
        base_dir=".claude"
    fi
    
    if [[ ! -d "$base_dir" ]]; then
        return 0
    fi
    
    local backup_dir="${base_dir}.backup.$(date +%Y%m%d_%H%M%S)"
    
    log_info "Creating backup of existing installation..."
    
    # Create backup
    cp -r "$base_dir" "$backup_dir"
    
    log_success "Backup created at: $backup_dir"
    
    # Save backup location for potential rollback
    echo "$backup_dir" > "/tmp/trinitas_last_backup_${scope}"
}

# Clean old artifacts
clean_old_artifacts() {
    local scope=$1
    local base_dir=""
    
    if [[ "$scope" == "user" ]]; then
        base_dir="$HOME/.claude"
    else
        base_dir=".claude"
    fi
    
    log_info "Cleaning old artifacts..."
    
    # Remove old Python hooks
    if [[ -d "$base_dir/hooks" ]]; then
        find "$base_dir/hooks" -name "*.py" -type f -delete 2>/dev/null || true
        log_info "Removed old Python hooks"
    fi
    
    # Remove old scripts directory if it contains SuperClaude stuff
    if [[ -d "$base_dir/scripts/hooks" ]]; then
        rm -rf "$base_dir/scripts/hooks"
        log_info "Removed old hooks scripts"
    fi
    
    # Clean up empty directories
    find "$base_dir" -type d -empty -delete 2>/dev/null || true
}

# Merge settings.json
merge_settings() {
    local scope=$1
    local settings_file=""
    
    if [[ "$scope" == "user" ]]; then
        settings_file="$HOME/.claude/settings.json"
    else
        settings_file=".claude/settings.json"
    fi
    
    if [[ ! -f "$settings_file" ]]; then
        return 0
    fi
    
    log_info "Updating settings.json..."
    
    # Backup current settings
    cp "$settings_file" "${settings_file}.upgrade_backup"
    
    # If jq is available, merge intelligently
    if command -v jq >/dev/null 2>&1; then
        # Create temporary file with new hooks configuration
        local new_hooks=$(cat << 'EOF'
{
  "SessionStart": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "~/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh"
    }]
  }],
  "PreCompact": [{
    "matcher": "*", 
    "hooks": [{
      "type": "command",
      "command": "~/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh pre_compact"
    }]
  }],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/pre-execution/01_safety_check.sh"
      }]
    },
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/pre-execution/02_file_safety_check.sh"
      }]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/post-execution/01_code_quality_check.sh"
      }]
    },
    {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/post-execution/02_test_runner.sh"
      }]
    }
  ]
}
EOF
        )
        
        # Merge with existing hooks
        echo "$new_hooks" > /tmp/trinitas_new_hooks.json
        
        # Update settings.json preserving existing configuration
        jq '.hooks = (.hooks // {}) * $newHooks[0]' "$settings_file" \
            --slurpfile newHooks /tmp/trinitas_new_hooks.json > /tmp/trinitas_merged_settings.json
        
        mv /tmp/trinitas_merged_settings.json "$settings_file"
        rm -f /tmp/trinitas_new_hooks.json
        
        log_success "Settings merged successfully"
    else
        log_warning "jq not found. Please manually update settings.json"
        log_info "Add SessionStart and PreCompact hooks from:"
        log_info "$TRINITAS_ROOT/hooks/examples/trinitas_protocol_settings.json"
    fi
}

# Main upgrade process
upgrade_installation() {
    local scope=$1
    
    echo -e "\n${BLUE}=== UPGRADING $(echo "${scope}" | tr 'a-z' 'A-Z') INSTALLATION ===${NC}"
    
    # Backup
    backup_existing "$scope"
    
    # Clean old artifacts
    clean_old_artifacts "$scope"
    
    # Run standard installation
    log_info "Running standard installation..."
    if [[ "$scope" == "user" ]]; then
        TRINITAS_INSTALL_SCOPE="user" TRINITAS_FORCE_INSTALL="true" "$TRINITAS_ROOT/install.sh"
    else
        TRINITAS_INSTALL_SCOPE="project" TRINITAS_FORCE_INSTALL="true" "$TRINITAS_ROOT/install.sh"
    fi
    
    # Merge settings
    merge_settings "$scope"
    
    log_success "$(echo "${scope:0:1}" | tr 'a-z' 'A-Z')${scope:1} upgrade completed!"
}

# Rollback function
rollback() {
    local scope=$1
    local backup_location_file="/tmp/trinitas_last_backup_${scope}"
    
    if [[ ! -f "$backup_location_file" ]]; then
        log_error "No backup found for ${scope} installation"
        return 1
    fi
    
    local backup_dir=$(cat "$backup_location_file")
    
    if [[ ! -d "$backup_dir" ]]; then
        log_error "Backup directory not found: $backup_dir"
        return 1
    fi
    
    local target_dir=""
    if [[ "$scope" == "user" ]]; then
        target_dir="$HOME/.claude"
    else
        target_dir=".claude"
    fi
    
    log_info "Rolling back to: $backup_dir"
    
    # Remove current installation
    rm -rf "$target_dir"
    
    # Restore backup
    cp -r "$backup_dir" "$target_dir"
    
    log_success "Rollback completed for ${scope} installation"
}

# Main
main() {
    show_banner
    
    # Check prerequisites
    if ! command -v claude >/dev/null 2>&1; then
        log_error "Claude Code CLI not found"
        exit 1
    fi
    
    # Check existing installation
    check_existing_installation
    
    echo -e "${YELLOW}"
    echo "⚠️  IMPORTANT: This will upgrade your existing Trinitas installation."
    echo "   - Your current installation will be backed up"
    echo "   - Old Python-based hooks will be removed"
    echo "   - Settings will be updated to include new hooks"
    echo -e "${NC}"
    
    read -p "Continue with upgrade? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Upgrade cancelled"
        exit 0
    fi
    
    # Determine what to upgrade
    echo -e "\n${BLUE}Select upgrade scope:${NC}"
    echo "1) User installation only (~/.claude/)"
    echo "2) Project installation only (.claude/)"
    echo "3) Both installations"
    echo "4) Cancel"
    
    read -p "Enter choice (1-4) [1]: " UPGRADE_CHOICE
    UPGRADE_CHOICE=${UPGRADE_CHOICE:-1}
    
    case $UPGRADE_CHOICE in
        1)
            upgrade_installation "user"
            ;;
        2)
            upgrade_installation "project"
            ;;
        3)
            upgrade_installation "user"
            upgrade_installation "project"
            ;;
        4)
            log_info "Upgrade cancelled"
            exit 0
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
    
    # Success message
    echo -e "\n${GREEN}"
    cat << "EOF"
🎉 ============================================== 🎉
   
   TRINITAS UPGRADE COMPLETED SUCCESSFULLY!
   
🎉 ============================================== 🎉
EOF
    echo -e "${NC}"
    
    echo -e "${CYAN}📋 Upgrade Summary:${NC}"
    echo "  • Old artifacts cleaned"
    echo "  • New hooks system installed" 
    echo "  • Protocol injection configured"
    echo "  • Settings updated"
    
    echo -e "\n${CYAN}🔄 Rollback Option:${NC}"
    echo "If you encounter issues, you can rollback:"
    echo "  ./upgrade.sh --rollback user    # Rollback user installation"
    echo "  ./upgrade.sh --rollback project # Rollback project installation"
    
    echo -e "\n${GREEN}Your Trinitas installation is now up to date!${NC}"
}

# Handle command line arguments
case "${1:-}" in
    "--rollback")
        if [[ -z "${2:-}" ]]; then
            log_error "Please specify scope: user or project"
            exit 1
        fi
        rollback "$2"
        ;;
    "--help"|"-h")
        echo "Trinitas Upgrade Script"
        echo ""
        echo "Usage:"
        echo "  ./upgrade.sh           # Interactive upgrade"
        echo "  ./upgrade.sh --rollback user    # Rollback user installation"
        echo "  ./upgrade.sh --rollback project # Rollback project installation"
        echo ""
        exit 0
        ;;
    *)
        main
        ;;
esac