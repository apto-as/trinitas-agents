#!/bin/bash

# Project Trinitas v2.0 - Installation Script
# Safe installation with verification and rollback capability

set -euo pipefail

# Configuration
TRINITAS_DIR="$HOME/.claude/agents"
BACKUP_DIR="$HOME/.claude/agents/backup_$(date +%Y%m%d_%H%M%S)"
REQUIRED_AGENTS=("trinitas-coordinator.md" "springfield-strategist.md" "krukai-optimizer.md" "vector-auditor.md" "trinitas-workflow.md" "trinitas-quality.md")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Pre-installation checks
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Claude Code installation
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code not found. Please install Claude Code first."
        exit 1
    fi
    
    # Verify Claude Code version
    CLAUDE_VERSION=$(claude --version 2>/dev/null | head -n1 || echo "unknown")
    log_info "Claude Code version: $CLAUDE_VERSION"
    
    # Create agents directory if it doesn't exist
    if [ ! -d "$TRINITAS_DIR" ]; then
        log_info "Creating agents directory: $TRINITAS_DIR"
        mkdir -p "$TRINITAS_DIR"
    fi
    
    log_success "Prerequisites check completed"
}

# Backup existing agents
backup_existing() {
    log_info "Creating backup of existing agents..."
    
    if [ -d "$TRINITAS_DIR" ] && [ "$(ls -A $TRINITAS_DIR 2>/dev/null)" ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r "$TRINITAS_DIR"/* "$BACKUP_DIR"/ 2>/dev/null || true
        log_success "Backup created at: $BACKUP_DIR"
    else
        log_info "No existing agents to backup"
    fi
}

# Install Trinitas agents
install_agents() {
    log_info "Installing Trinitas agents..."
    
    local install_dir="$(dirname "$0")"
    local agents_source="$install_dir/agents"
    
    if [ ! -d "$agents_source" ]; then
        log_error "Agents source directory not found: $agents_source"
        exit 1
    fi
    
    # Copy each agent with verification
    for agent in "${REQUIRED_AGENTS[@]}"; do
        local source_file="$agents_source/$agent"
        local dest_file="$TRINITAS_DIR/$agent"
        
        if [ -f "$source_file" ]; then
            cp "$source_file" "$dest_file"
            
            # Verify file was copied correctly
            if [ -f "$dest_file" ]; then
                log_success "Installed: $agent"
            else
                log_error "Failed to install: $agent"
                exit 1
            fi
        else
            log_error "Source file not found: $source_file"
            exit 1
        fi
    done
}

# Install utility scripts
install_utilities() {
    log_info "Installing utility scripts..."
    
    local install_dir="$(dirname "$0")"
    local utils_source="$install_dir/utils"
    local utils_dest="$TRINITAS_DIR/trinitas"
    
    if [ -d "$utils_source" ]; then
        mkdir -p "$utils_dest/utils"
        cp -r "$utils_source"/* "$utils_dest/utils/"
        log_success "Utility scripts installed"
    else
        log_warning "No utility scripts found - advanced features may not be available"
    fi
}

# Install configuration
install_config() {
    log_info "Installing configuration..."
    
    local install_dir="$(dirname "$0")"
    local config_source="$install_dir/config.yaml"
    local config_dest="$TRINITAS_DIR/trinitas/config.yaml"
    
    if [ -f "$config_source" ]; then
        mkdir -p "$(dirname "$config_dest")"
        cp "$config_source" "$config_dest"
        log_success "Configuration installed"
    else
        log_info "Creating default configuration..."
        mkdir -p "$(dirname "$config_dest")"
        cat > "$config_dest" << 'EOF'
trinitas:
  mode: "full"  # full | efficient | minimal
  auto_coordination: true
  quality_gates: true
  
personalities:
  springfield:
    formality: "polite"
    language: "japanese"
    
  krukai:
    standards: "strict"
    optimization: "aggressive"
    
  vector:
    paranoia_level: "high"
    compliance: ["OWASP", "GDPR"]
EOF
        log_success "Default configuration created"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check all required agents are installed
    for agent in "${REQUIRED_AGENTS[@]}"; do
        local agent_file="$TRINITAS_DIR/$agent"
        
        if [ -f "$agent_file" ]; then
            # Verify agent file structure
            if grep -q "MUST BE USED" "$agent_file" && grep -q "tools:" "$agent_file"; then
                log_success "✓ $agent"
            else
                log_error "✗ $agent (invalid format)"
                ((errors++))
            fi
        else
            log_error "✗ $agent (missing)"
            ((errors++))
        fi
    done
    
    if [ $errors -eq 0 ]; then
        log_success "All agents installed successfully!"
        return 0
    else
        log_error "$errors installation errors detected"
        return 1
    fi
}

# Test basic functionality
test_installation() {
    log_info "Testing Trinitas functionality..."
    
    # Test agent listing
    if claude --list-agents 2>/dev/null | grep -q "trinitas"; then
        log_success "Trinitas agents detected by Claude Code"
    else
        log_warning "Trinitas agents not detected - may need Claude Code restart"
    fi
    
    log_info "Installation test completed"
}

# Rollback function
rollback_installation() {
    log_warning "Rolling back installation..."
    
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$TRINITAS_DIR"
        mkdir -p "$TRINITAS_DIR"
        cp -r "$BACKUP_DIR"/* "$TRINITAS_DIR"/ 2>/dev/null || true
        log_success "Rollback completed"
    else
        log_warning "No backup found for rollback"
    fi
}

# Main installation flow
main() {
    echo "========================================"
    echo "  Project Trinitas v2.0 Installation"
    echo "========================================"
    echo ""
    
    # Trap errors for rollback
    trap 'log_error "Installation failed"; rollback_installation; exit 1' ERR
    
    check_prerequisites
    backup_existing
    install_agents
    install_utilities
    install_config
    
    if verify_installation; then
        test_installation
        
        echo ""
        echo "========================================"
        log_success "Project Trinitas v2.0 installed successfully!"
        echo "========================================"
        echo ""
        echo "Next steps:"
        echo "  1. Test installation: claude \"Test Trinitas installation\""
        echo "  2. Try basic analysis: claude \"Analyze this project comprehensively\""
        echo "  3. Read documentation: trinitas-agents/README.md"
        echo ""
        echo "Support: https://github.com/project-trinitas/trinitas-agents"
        echo ""
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-install}" in
    "install")
        main
        ;;
    "uninstall")
        log_info "Uninstalling Trinitas agents..."
        for agent in "${REQUIRED_AGENTS[@]}"; do
            rm -f "$TRINITAS_DIR/$agent"
        done
        rm -rf "$TRINITAS_DIR/trinitas"
        log_success "Trinitas uninstalled"
        ;;
    "verify")
        verify_installation
        ;;
    "test")
        test_installation
        ;;
    *)
        echo "Usage: $0 [install|uninstall|verify|test]"
        exit 1
        ;;
esac