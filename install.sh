#!/bin/bash

# Project Trinitas v2.0 - Markdown Native Agents Installation Script
# Simple installation for Claude Code Native Agents

set -euo pipefail

# Configuration
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
BACKUP_DIR="$AGENTS_DIR/backup_$(date +%Y%m%d_%H%M%S)"
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
        echo "Visit: https://claude.ai/code"
        exit 1
    fi
    
    # Verify Claude Code version
    CLAUDE_VERSION=$(claude --version 2>/dev/null | head -n1 || echo "unknown")
    log_info "Claude Code version: $CLAUDE_VERSION"
    
    # Create agents directory if it doesn't exist
    if [ ! -d "$AGENTS_DIR" ]; then
        log_info "Creating agents directory: $AGENTS_DIR"
        mkdir -p "$AGENTS_DIR"
    fi
    
    log_success "Prerequisites check completed"
}

# Backup existing agents
backup_existing() {
    log_info "Creating backup of existing Trinitas agents..."
    
    local needs_backup=false
    for agent in "${REQUIRED_AGENTS[@]}"; do
        if [ -f "$AGENTS_DIR/$agent" ]; then
            needs_backup=true
            break
        fi
    done
    
    if $needs_backup; then
        mkdir -p "$BACKUP_DIR"
        for agent in "${REQUIRED_AGENTS[@]}"; do
            if [ -f "$AGENTS_DIR/$agent" ]; then
                cp "$AGENTS_DIR/$agent" "$BACKUP_DIR/" 2>/dev/null || true
            fi
        done
        log_success "Backup created at: $BACKUP_DIR"
    else
        log_info "No existing Trinitas agents to backup"
    fi
}

# Install Trinitas agents
install_agents() {
    log_info "Installing Trinitas Native Agents..."
    
    local install_dir="$(dirname "$0")"
    local agents_source="$install_dir/agents"
    
    if [ ! -d "$agents_source" ]; then
        log_error "Agents source directory not found: $agents_source"
        exit 1
    fi
    
    # Copy each agent with verification
    local installed_count=0
    for agent in "${REQUIRED_AGENTS[@]}"; do
        local source_file="$agents_source/$agent"
        local dest_file="$AGENTS_DIR/$agent"
        
        if [ -f "$source_file" ]; then
            cp "$source_file" "$dest_file"
            
            # Verify file was copied correctly
            if [ -f "$dest_file" ] && grep -q "MUST BE USED" "$dest_file"; then
                log_success "✓ $agent"
                ((installed_count++))
            else
                log_error "✗ Failed to install: $agent"
                exit 1
            fi
        else
            log_error "✗ Source file not found: $source_file"
            exit 1
        fi
    done
    
    log_success "Installed $installed_count Trinitas agents"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check all required agents are installed
    for agent in "${REQUIRED_AGENTS[@]}"; do
        local agent_file="$AGENTS_DIR/$agent"
        
        if [ -f "$agent_file" ]; then
            # Verify agent file structure
            if grep -q "MUST BE USED" "$agent_file" && grep -q "tools:" "$agent_file"; then
                continue
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
        log_warning "Trinitas agents not detected - you may need to restart Claude Code"
    fi
    
    log_info "Installation test completed"
}

# Rollback function
rollback_installation() {
    log_warning "Rolling back installation..."
    
    if [ -d "$BACKUP_DIR" ]; then
        for agent in "${REQUIRED_AGENTS[@]}"; do
            if [ -f "$BACKUP_DIR/$agent" ]; then
                cp "$BACKUP_DIR/$agent" "$AGENTS_DIR/"
            else
                rm -f "$AGENTS_DIR/$agent" 2>/dev/null || true
            fi
        done
        log_success "Rollback completed"
    else
        log_warning "No backup found for rollback"
        for agent in "${REQUIRED_AGENTS[@]}"; do
            rm -f "$AGENTS_DIR/$agent" 2>/dev/null || true
        done
    fi
}

# Main installation flow
main() {
    echo "========================================"
    echo "  Project Trinitas v2.0 Installation"
    echo "  Markdown Native Agents for Claude Code"
    echo "========================================"
    echo ""
    
    # Trap errors for rollback
    trap 'log_error "Installation failed"; rollback_installation; exit 1' ERR
    
    check_prerequisites
    backup_existing
    install_agents
    
    if verify_installation; then
        test_installation
        
        echo ""
        echo "========================================"
        log_success "Project Trinitas v2.0 installed successfully!"
        echo "========================================"
        echo ""
        echo "🌸 Trinity Intelligence System is ready!"
        echo ""
        echo "Available agents:"
        echo "  🎭 trinitas-coordinator  - Multi-perspective analysis"
        echo "  🌱 springfield-strategist - Strategic planning"
        echo "  ⚡ krukai-optimizer      - Technical optimization"
        echo "  🛡️ vector-auditor        - Security & risk analysis"
        echo "  🔄 trinitas-workflow     - Development automation"
        echo "  ✅ trinitas-quality      - Quality assurance"
        echo ""
        echo "Next steps:"
        echo "  1. Test: claude \"Analyze this project comprehensively\""
        echo "  2. Strategic: claude \"Help me plan our development roadmap\""
        echo "  3. Technical: claude \"Optimize this code for performance\""
        echo "  4. Security: claude \"Conduct a security audit\""
        echo ""
        echo "Documentation: README.md"
        echo "Support: https://github.com/apto-as/trinitas-agents"
        echo ""
        echo "Springfield の戦略、Krukai の技術、Vector の安全性"
        echo "三位一体の統合知性をお楽しみください 🌸"
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
            rm -f "$AGENTS_DIR/$agent"
            log_info "Removed: $agent"
        done
        log_success "Trinitas agents uninstalled"
        ;;
    "list")
        echo "Trinitas agents:"
        for agent in "${REQUIRED_AGENTS[@]}"; do
            if [ -f "$AGENTS_DIR/$agent" ]; then
                echo "  ✓ $agent"
            else
                echo "  ✗ $agent (not installed)"
            fi
        done
        ;;
    "help"|"--help")
        echo "Project Trinitas v2.0 - Installation Script"
        echo ""
        echo "Usage: $0 [install|uninstall|list|help]"
        echo ""
        echo "Commands:"
        echo "  install     Install Trinitas agents (default)"
        echo "  uninstall   Remove Trinitas agents"
        echo "  list        Show installation status"
        echo "  help        Show this help message"
        echo ""
        exit 0
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac