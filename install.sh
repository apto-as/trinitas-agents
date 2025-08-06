#!/bin/bash

# Project Trinitas v2.0 - Complete Installation Script
# Comprehensive installation for Claude Code Native Agents, Hooks, and Documentation

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRINITAS_ROOT="$SCRIPT_DIR"
REQUIRED_AGENTS=("trinitas-coordinator.md" "springfield-strategist.md" "krukai-optimizer.md" "vector-auditor.md" "trinitas-workflow.md" "trinitas-quality.md" "centaureissi-researcher.md")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

# Display Trinitas banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
🌸 ===================================================== 🌸
   
   TRINITAS v2.0 - Trinity Intelligence Installation
   
   Springfield: Strategic planning and team coordination
   Krukai: Technical excellence and optimization  
   Vector: Security analysis and risk management
   
🌸 ===================================================== 🌸
EOF
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Python is optional for enhanced features
    if ! command -v python3 &> /dev/null; then
        log_warning "Python 3 not found. Some enhanced features may be unavailable."
    fi
    
    # Check Claude Code CLI
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code CLI is required but not installed"
        echo -e "${YELLOW}Please install Claude Code CLI first: https://docs.anthropic.com/en/docs/claude-code${NC}"
        exit 1
    fi
    
    # Check if we're in the Trinitas project directory
    if [[ ! -f "$TRINITAS_ROOT/TRINITAS-AGENTS.md" ]]; then
        log_error "Please run this script from the trinitas-agents directory"
        exit 1
    fi
    
    # Check required hooks exist
    if [[ ! -d "$TRINITAS_ROOT/hooks" ]]; then
        log_error "Required hooks directory not found"
        exit 1
    fi
    
    # Check for existing installation
    if [[ -d "$HOME/.claude/agents" ]] || [[ -d ".claude/agents" ]]; then
        log_warning "Existing Trinitas installation detected!"
        echo -e "${YELLOW}"
        echo "⚠️  An existing installation was found."
        echo "   For upgrading from previous versions, please use:"
        echo "   ${BLUE}./upgrade.sh${YELLOW}"
        echo ""
        echo "   To force a fresh installation, use:"
        echo "   ${BLUE}./install.sh --force${NC}"
        echo -e "${NC}"
        
        if [[ "${1:-}" != "--force" ]] && [[ "${TRINITAS_FORCE_INSTALL:-}" != "true" ]]; then
            exit 0
        fi
        
        log_warning "Force installation requested. Proceeding..."
    fi
    
    log_success "Prerequisites check passed!"
}

# Installation mode selection
select_installation_scope() {
    echo -e "${BLUE}"
    echo "🎯 Choose installation scope:"
    echo "1) PROJECT - Install for current project only (.claude/)"
    echo "2) USER    - Install for all your projects (~/.claude/)"
    echo "3) BOTH    - Install for both user and project"
    echo -e "${NC}"
    
    if [[ "${TRINITAS_INSTALL_SCOPE:-}" ]]; then
        # Non-interactive mode
        INSTALL_SCOPE="$TRINITAS_INSTALL_SCOPE"
        log_info "Using scope: $INSTALL_SCOPE"
    else
        # Interactive mode
        read -p "Enter your choice (1-3) [1]: " INSTALL_CHOICE
        INSTALL_CHOICE=${INSTALL_CHOICE:-1}
        
        case $INSTALL_CHOICE in
            1)
                INSTALL_SCOPE="project"
                ;;
            2)
                INSTALL_SCOPE="user"
                ;;
            3)
                INSTALL_SCOPE="both"
                ;;
            *)
                log_warning "Invalid choice, defaulting to PROJECT installation"
                INSTALL_SCOPE="project"
                ;;
        esac
    fi
    
    log_success "Selected: $(echo "${INSTALL_SCOPE}" | tr 'a-z' 'A-Z') installation"
}

# Trinitas mode selection
select_trinitas_mode() {
    echo -e "${BLUE}"
    echo "⚙️ Choose Trinitas experience mode:"
    echo "1) MINIMAL      - Essential security and quality hooks only"
    echo "2) STANDARD     - Balanced functionality with core features (recommended)"
    echo "3) COMPREHENSIVE - Complete Trinitas experience with all features"
    echo -e "${NC}"
    
    if [[ "${TRINITAS_INSTALL_MODE:-}" ]]; then
        # Non-interactive mode
        TRINITAS_MODE="$TRINITAS_INSTALL_MODE"
        log_info "Using mode: $TRINITAS_MODE"
    else
        # Interactive mode
        read -p "Enter your choice (1-3) [2]: " MODE_CHOICE
        MODE_CHOICE=${MODE_CHOICE:-2}
        
        case $MODE_CHOICE in
            1)
                TRINITAS_MODE="minimal"
                ;;
            2)
                TRINITAS_MODE="standard"
                ;;
            3)
                TRINITAS_MODE="comprehensive"
                ;;
            *)
                log_warning "Invalid choice, defaulting to STANDARD mode"
                TRINITAS_MODE="standard"
                ;;
        esac
    fi
    
    log_success "Selected: $(echo "${TRINITAS_MODE}" | tr 'a-z' 'A-Z') mode"
}

# Install hooks scripts
install_hooks_scripts() {
    local target_dir=$1
    local scope_name=$2
    
    log_info "Installing Trinitas hooks scripts to ${scope_name}..."
    
    # Create trinitas hooks directory
    local trinitas_hooks_dir="${target_dir}/trinitas/hooks"
    mkdir -p "$trinitas_hooks_dir"
    
    # Create config directory and environment file
    mkdir -p "${target_dir}/trinitas/config"
    if [[ -f "templates/trinitas.env.template" ]]; then
        cp "templates/trinitas.env.template" "${target_dir}/trinitas/config/trinitas.env"
        log_success "Created environment configuration"
    else
        # Create minimal config if template not found
        cat > "${target_dir}/trinitas/config/trinitas.env" << 'ENVEOF'
# Trinitas Environment Configuration
TRINITAS_HOME="${HOME}/.claude/trinitas"
TRINITAS_MODE="production"
TRINITAS_CLAUDE_MODE="relaxed"
TRINITAS_DEFAULT_PROJECT_DIR="${HOME}/workspace"
TRINITAS_DEFAULT_TOOL_NAME="Bash"
TRINITAS_PARALLEL_ENABLED="true"
TRINITAS_LOG_LEVEL="INFO"
ENVEOF
        log_success "Created default environment configuration"
    fi
    
    # Copy all hook scripts with directory structure
    if [[ -d "$TRINITAS_ROOT/hooks/pre-execution" ]]; then
        cp -r "$TRINITAS_ROOT/hooks/pre-execution" "$trinitas_hooks_dir/"
    fi
    
    if [[ -d "$TRINITAS_ROOT/hooks/post-execution" ]]; then
        cp -r "$TRINITAS_ROOT/hooks/post-execution" "$trinitas_hooks_dir/"
    fi
    
    if [[ -d "$TRINITAS_ROOT/hooks/core" ]]; then
        cp -r "$TRINITAS_ROOT/hooks/core" "$trinitas_hooks_dir/"
    fi
    
    if [[ -d "$TRINITAS_ROOT/hooks/python" ]]; then
        cp -r "$TRINITAS_ROOT/hooks/python" "$trinitas_hooks_dir/"
    fi
    
    # Make all scripts executable
    find "$trinitas_hooks_dir" -name "*.sh" -exec chmod +x {} \;
    find "$trinitas_hooks_dir" -name "*.py" -exec chmod +x {} \;
    
    log_success "Hooks scripts installed to: $trinitas_hooks_dir"
    
    # Show example configuration
    log_info "To enable hooks, add the following to your settings.json:"
    log_info "See: $TRINITAS_ROOT/hooks/examples/settings.json"
}

# Install agents
install_agents() {
    local target_dir=$1
    local scope_name=$2
    
    log_info "Installing Trinitas agents to ${scope_name}..."
    
    # Create agents directory
    mkdir -p "$target_dir"
    
    # Backup existing agents if they exist
    local backup_dir="${target_dir}/backup_$(date +%Y%m%d_%H%M%S)"
    local needs_backup=false
    
    for agent in "${REQUIRED_AGENTS[@]}"; do
        if [[ -f "$target_dir/$agent" ]]; then
            needs_backup=true
            break
        fi
    done
    
    if $needs_backup; then
        mkdir -p "$backup_dir"
        for agent in "${REQUIRED_AGENTS[@]}"; do
            if [[ -f "$target_dir/$agent" ]]; then
                cp "$target_dir/$agent" "$backup_dir/" 2>/dev/null || true
            fi
        done
        log_info "Backup created at: $backup_dir"
    fi
    
    # Copy all agent files
    local installed_count=0
    for agent in "${REQUIRED_AGENTS[@]}"; do
        local source_file="$TRINITAS_ROOT/agents/$agent"
        local dest_file="$target_dir/$agent"
        
        if [[ -f "$source_file" ]]; then
            cp "$source_file" "$dest_file"
            
            # Verify file was copied correctly
            if [[ -f "$dest_file" ]] && grep -q "MUST BE USED" "$dest_file"; then
                ((installed_count++))
            else
                log_error "Failed to install: $agent"
                return 1
            fi
        else
            log_error "Source file not found: $source_file"
            return 1
        fi
    done
    
    log_success "Installed $installed_count agents to: $target_dir"
}

# Run Shell-based hooks and documentation installer
install_hooks_and_docs() {
    local scope=$1
    local mode=$2
    
    log_info "Installing hooks and documentation for ${scope}..."
    
    # Use the Shell-based installer
    if "$TRINITAS_ROOT/scripts/install_hooks_config.sh" "$scope" "$mode"; then
        log_success "Hooks and documentation installed for ${scope}"
        return 0
    else
        log_error "Failed to install hooks for ${scope}"
        return 1
    fi
}

# Verify complete installation
verify_installation() {
    local scope=$1
    
    log_info "Verifying ${scope} installation..."
    
    if [[ "$scope" == "user" ]]; then
        SETTINGS_FILE="$HOME/.claude/settings.json"
        AGENTS_DIR="$HOME/.claude/agents"
        DOCS_FILE="$HOME/.claude/CLAUDE.md"
    else
        SETTINGS_FILE=".claude/settings.json"
        AGENTS_DIR=".claude/agents"
        DOCS_FILE=".claude/CLAUDE.md"
    fi
    
    local errors=0
    
    # Check Claude Code settings
    if [[ -f "$SETTINGS_FILE" ]] && grep -q "trinitas" "$SETTINGS_FILE"; then
        log_success "  ✓ Claude Code settings configured"
    else
        log_warning "  ⚠ Claude Code settings not found or incomplete"
        ((errors++))
    fi
    
    # Check agents installation
    if [[ -d "$AGENTS_DIR" ]]; then
        local agent_count=0
        for agent in "${REQUIRED_AGENTS[@]}"; do
            if [[ -f "$AGENTS_DIR/$agent" ]] && grep -q "MUST BE USED" "$AGENTS_DIR/$agent"; then
                ((agent_count++))
            fi
        done
        
        if [[ $agent_count -eq ${#REQUIRED_AGENTS[@]} ]]; then
            log_success "  ✓ All $agent_count Trinitas agents installed"
        else
            log_warning "  ⚠ Only $agent_count/${#REQUIRED_AGENTS[@]} agents installed correctly"
            ((errors++))
        fi
    else
        log_warning "  ⚠ Agents directory not found"
        ((errors++))
    fi
    
    # Check documentation
    if [[ -f "$DOCS_FILE" ]]; then
        log_success "  ✓ Documentation installed"
    else
        log_warning "  ⚠ Documentation not found"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "${scope} installation verified successfully!"
        return 0
    else
        log_warning "${scope} installation has $errors issues"
        return 1
    fi
}

# Generate test command based on mode
generate_test_command() {
    local mode=$1
    
    case $mode in
        "minimal")
            echo "echo 'console.log(\"Hello, Trinitas!\");' > test-trinitas.js"
            ;;
        "standard")
            echo "echo '# Trinitas Test File\nprint(\"Hello, Trinitas!\")' > test-trinitas.py"
            ;;
        "comprehensive")
            echo "echo '// Trinitas Comprehensive Test\nconsole.log(\"Trinitas hooks active!\");' > test-trinitas.js"
            ;;
    esac
}

# Main installation process
main_install() {
    show_banner
    
    log_info "Starting Trinitas installation..."
    
    check_prerequisites "$@"
    select_installation_scope
    select_trinitas_mode
    
    # Install based on scope selection
    if [[ "$INSTALL_SCOPE" == "user" ]] || [[ "$INSTALL_SCOPE" == "both" ]]; then
        echo -e "\n${BLUE}=== USER INSTALLATION ===${NC}"
        
        # Install hooks scripts first
        if ! install_hooks_scripts "$HOME/.claude" "user settings"; then
            log_error "User hooks scripts installation failed"
            exit 1
        fi
        
        # Install agents
        if ! install_agents "$HOME/.claude/agents" "user settings"; then
            log_error "User agent installation failed"
            exit 1
        fi
        
        # Install hooks and documentation  
        if ! install_hooks_and_docs "user" "$TRINITAS_MODE"; then
            log_error "User hooks installation failed"
            exit 1
        fi
        
        # Verify installation
        verify_installation "user"
    fi
    
    if [[ "$INSTALL_SCOPE" == "project" ]] || [[ "$INSTALL_SCOPE" == "both" ]]; then
        echo -e "\n${BLUE}=== PROJECT INSTALLATION ===${NC}"
        
        # Install hooks scripts first
        if ! install_hooks_scripts ".claude" "project settings"; then
            log_error "Project hooks scripts installation failed"
            exit 1
        fi
        
        # Install agents
        if ! install_agents ".claude/agents" "project settings"; then
            log_error "Project agent installation failed"
            exit 1
        fi
        
        # Install hooks and documentation
        if ! install_hooks_and_docs "project" "$TRINITAS_MODE"; then
            log_error "Project hooks installation failed"
            exit 1
        fi
        
        # Verify installation
        verify_installation "project"
    fi
    
    # Generate test command
    TEST_COMMAND=$(generate_test_command "$TRINITAS_MODE")
    
    # Success message
    echo -e "\n${GREEN}"
    cat << "EOF"
🎉 ============================================== 🎉
   
   TRINITAS INSTALLATION COMPLETED SUCCESSFULLY!
   
🎉 ============================================== 🎉
EOF
    echo -e "${NC}"
    
    echo -e "${CYAN}📋 Installation Summary:${NC}"
    echo -e "  • Scope: $(echo "${INSTALL_SCOPE}" | tr 'a-z' 'A-Z')"
    echo -e "  • Mode: $(echo "${TRINITAS_MODE}" | tr 'a-z' 'A-Z')"
    echo -e "  • Agents: ${#REQUIRED_AGENTS[@]} agents installed"
    echo -e "  • Hooks: Configured for Claude Code"
    echo -e "  • Documentation: Available as CLAUDE.md"
    
    echo -e "\n${BLUE}🧪 Test Your Installation:${NC}"
    echo -e "Run this command to test Trinitas:"
    echo -e "${YELLOW}claude bash \"$TEST_COMMAND\"${NC}"
    
    echo -e "\n${PURPLE}🌸 Welcome to Café Zuccaro! 🌸${NC}"
    echo -e "${GREEN}Springfield:${NC} \"指揮官、ようこそ！美味しいコーヒーと共に、素晴らしいコードを作りましょうね\""
    echo -e "${BLUE}Krukai:${NC} \"フン、完璧なシステムを構築する準備はできているわね\""
    echo -e "${RED}Vector:${NC} \"……あなたのプロジェクトを、あらゆる脅威から守ります……\""
    
    echo -e "\n${CYAN}📚 Documentation Locations:${NC}"
    if [[ "$INSTALL_SCOPE" == "user" ]]; then
        echo -e "  • User: ~/.claude/CLAUDE.md"
    elif [[ "$INSTALL_SCOPE" == "project" ]]; then
        echo -e "  • Project: .claude/CLAUDE.md"
    else
        echo -e "  • User: ~/.claude/CLAUDE.md"
        echo -e "  • Project: .claude/CLAUDE.md"
    fi
    
    echo -e "\n${CYAN}🔗 Resources:${NC}"
    echo -e "  • GitHub: https://github.com/apto-as/trinitas-agents"
    echo -e "  • Issues: https://github.com/apto-as/trinitas-agents/issues"
    
    echo -e "\n${GREEN}Happy coding with Trinitas! 🌸${NC}"
}

# Uninstall function
uninstall_trinitas() {
    log_warning "Uninstalling Trinitas..."
    
    # Remove user installation
    if [[ -d "$HOME/.claude/agents" ]]; then
        for agent in "${REQUIRED_AGENTS[@]}"; do
            rm -f "$HOME/.claude/agents/$agent"
        done
        rm -f "$HOME/.claude/CLAUDE.md"
        log_info "Removed user installation"
    fi
    
    # Remove project installation
    if [[ -d ".claude/agents" ]]; then
        for agent in "${REQUIRED_AGENTS[@]}"; do
            rm -f ".claude/agents/$agent"
        done
        rm -f ".claude/CLAUDE.md"
        log_info "Removed project installation"
    fi
    
    log_success "Trinitas uninstalled"
}

# List installation status
list_installation() {
    echo "Trinitas Installation Status:"
    echo ""
    
    # Check user installation
    echo "User installation (~/.claude/):"
    for agent in "${REQUIRED_AGENTS[@]}"; do
        if [[ -f "$HOME/.claude/agents/$agent" ]]; then
            echo "  ✓ $agent"
        else
            echo "  ✗ $agent (not installed)"
        fi
    done
    
    if [[ -f "$HOME/.claude/CLAUDE.md" ]]; then
        echo "  ✓ CLAUDE.md"
    else
        echo "  ✗ CLAUDE.md (not installed)"
    fi
    
    echo ""
    
    # Check project installation
    echo "Project installation (.claude/):"
    for agent in "${REQUIRED_AGENTS[@]}"; do
        if [[ -f ".claude/agents/$agent" ]]; then
            echo "  ✓ $agent"
        else
            echo "  ✗ $agent (not installed)"
        fi
    done
    
    if [[ -f ".claude/CLAUDE.md" ]]; then
        echo "  ✓ CLAUDE.md"
    else
        echo "  ✗ CLAUDE.md (not installed)"
    fi
}

# Handle command line arguments
case "${1:-install}" in
    "install"|"--force")
        main_install "$@"
        ;;
    "uninstall")
        uninstall_trinitas
        ;;
    "list")
        list_installation
        ;;
    "help"|"--help")
        echo "Project Trinitas v2.0 - Complete Installation Script"
        echo ""
        echo "Usage: $0 [install|uninstall|list|help] [options]"
        echo ""
        echo "Commands:"
        echo "  install     Install Trinitas agents, hooks, and documentation (default)"
        echo "  uninstall   Remove all Trinitas components"
        echo "  list        Show installation status"
        echo "  help        Show this help message"
        echo ""
        echo "Options:"
        echo "  --force     Force installation even if existing installation is detected"
        echo ""
        echo "Environment Variables:"
        echo "  TRINITAS_INSTALL_SCOPE  Set installation scope (user|project|both)"
        echo "  TRINITAS_INSTALL_MODE   Set installation mode (minimal|standard|comprehensive)"
        echo ""
        echo "Examples:"
        echo "  ./install.sh                                    # Interactive installation"
        echo "  ./install.sh --force                            # Force fresh installation"
        echo "  ./upgrade.sh                                    # Upgrade existing installation"
        echo "  TRINITAS_INSTALL_SCOPE=user ./install.sh       # Non-interactive user install"
        echo "  TRINITAS_INSTALL_MODE=comprehensive ./install.sh  # Comprehensive mode"
        echo ""
        exit 0
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac