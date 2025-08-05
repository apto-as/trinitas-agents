#!/bin/bash
# Trinitas Safe Deployment Script
# Vector: "……慎重な段階的デプロイ……各ステップでの検証が必須……"
# Springfield: "ユーザーの作業を中断させない、スムーズな移行を実現します"

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOYMENT_LOG="$HOME/.claude/trinitas/logs/deployment_$(date +%Y%m%d_%H%M%S).log"
ROLLBACK_POINT=""

# =====================================================
# Logging
# =====================================================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)  echo -e "${BLUE}[INFO]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$DEPLOYMENT_LOG"
}

# =====================================================
# Pre-deployment Checks
# =====================================================

create_deployment_checkpoint() {
    log INFO "Creating deployment checkpoint..."
    
    local checkpoint_dir="$HOME/.claude/trinitas/checkpoints/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$checkpoint_dir"
    
    # Backup current state
    if [[ -f "$HOME/.claude/settings.json" ]]; then
        cp "$HOME/.claude/settings.json" "$checkpoint_dir/"
    fi
    
    if [[ -d "$HOME/.claude/trinitas" ]]; then
        tar -czf "$checkpoint_dir/trinitas_backup.tar.gz" -C "$HOME/.claude" trinitas/
    fi
    
    ROLLBACK_POINT="$checkpoint_dir"
    log SUCCESS "Checkpoint created: $checkpoint_dir"
}

verify_prerequisites() {
    log INFO "Verifying prerequisites..."
    
    local errors=0
    
    # Check Claude CLI
    if ! command -v claude >/dev/null 2>&1; then
        log ERROR "Claude CLI not found"
        ((errors++))
    fi
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        log ERROR "Python3 not found"
        ((errors++))
    fi
    
    # Check disk space
    local available_mb=$(df -m "$HOME" | awk 'NR==2 {print $4}')
    if [[ $available_mb -lt 100 ]]; then
        log ERROR "Insufficient disk space: ${available_mb}MB (need 100MB)"
        ((errors++))
    fi
    
    # Check for running Claude sessions
    if pgrep -f "claude" >/dev/null 2>&1; then
        log WARNING "Claude processes are running. They may need to be restarted after deployment."
    fi
    
    if [[ $errors -gt 0 ]]; then
        log ERROR "Prerequisites check failed. Please resolve issues before proceeding."
        return 1
    fi
    
    log SUCCESS "Prerequisites verified"
    return 0
}

# =====================================================
# Deployment Steps
# =====================================================

deploy_hooks() {
    log INFO "Deploying hook scripts..."
    
    # Create directories
    local hooks_dir="$HOME/.claude/trinitas/hooks"
    mkdir -p "$hooks_dir"/{core,pre-execution,post-execution,python,monitoring}
    
    # Copy hook files
    local hook_categories=(core pre-execution post-execution python monitoring)
    
    for category in "${hook_categories[@]}"; do
        if [[ -d "$PROJECT_ROOT/hooks/$category" ]]; then
            log INFO "Installing $category hooks..."
            cp -r "$PROJECT_ROOT/hooks/$category"/* "$hooks_dir/$category/" 2>/dev/null || true
            
            # Make scripts executable
            find "$hooks_dir/$category" -name "*.sh" -exec chmod +x {} \;
            find "$hooks_dir/$category" -name "*.py" -exec chmod +x {} \;
        fi
    done
    
    log SUCCESS "Hook scripts deployed"
}

deploy_settings() {
    log INFO "Updating settings.json..."
    
    local settings_file="$HOME/.claude/settings.json"
    
    # Use settings merger for safe integration
    if [[ -f "$settings_file" ]]; then
        log INFO "Merging with existing settings..."
        
        if python3 "$PROJECT_ROOT/hooks/migration/settings_merger.py" \
            "$settings_file" \
            --output "$settings_file.new" \
            --force; then
            
            # Validate new settings
            if jq empty "$settings_file.new" 2>/dev/null; then
                mv "$settings_file.new" "$settings_file"
                log SUCCESS "Settings updated successfully"
            else
                log ERROR "Invalid JSON in new settings"
                rm -f "$settings_file.new"
                return 1
            fi
        else
            log ERROR "Settings merge failed"
            return 1
        fi
    else
        log INFO "Creating new settings.json..."
        cp "$PROJECT_ROOT/hooks/examples/parallel_agents_settings.json" "$settings_file"
    fi
    
    return 0
}

test_deployment() {
    log INFO "Running deployment tests..."
    
    # Test 1: Health check
    log INFO "Test 1: System health check"
    if "$HOME/.claude/trinitas/hooks/monitoring/health_check.sh" > /dev/null 2>&1; then
        log SUCCESS "Health check passed"
    else
        log WARNING "Health check reported issues (non-critical)"
    fi
    
    # Test 2: Hook execution
    log INFO "Test 2: Basic hook execution"
    if TRINITAS_HOOK_TYPE="session_start" \
       bash "$HOME/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh" > /dev/null 2>&1; then
        log SUCCESS "Hook execution test passed"
    else
        log ERROR "Hook execution test failed"
        return 1
    fi
    
    # Test 3: Python environment
    log INFO "Test 3: Python environment"
    if echo "test" | CLAUDE_USER_PROMPT="test" CLAUDE_TOOL_NAME="Task" \
       python3 "$HOME/.claude/trinitas/hooks/python/prepare_parallel_tasks.py" > /dev/null 2>&1; then
        log SUCCESS "Python environment test passed"
    else
        log WARNING "Python environment test failed (parallel agents may not work)"
    fi
    
    return 0
}

# =====================================================
# Rollback
# =====================================================

rollback_deployment() {
    log WARNING "Initiating rollback..."
    
    if [[ -z "$ROLLBACK_POINT" ]] || [[ ! -d "$ROLLBACK_POINT" ]]; then
        log ERROR "No rollback point available"
        return 1
    fi
    
    # Restore settings.json
    if [[ -f "$ROLLBACK_POINT/settings.json" ]]; then
        cp "$ROLLBACK_POINT/settings.json" "$HOME/.claude/settings.json"
        log INFO "Restored settings.json"
    fi
    
    # Restore trinitas directory
    if [[ -f "$ROLLBACK_POINT/trinitas_backup.tar.gz" ]]; then
        rm -rf "$HOME/.claude/trinitas"
        tar -xzf "$ROLLBACK_POINT/trinitas_backup.tar.gz" -C "$HOME/.claude"
        log INFO "Restored trinitas directory"
    fi
    
    log SUCCESS "Rollback completed"
    return 0
}

# =====================================================
# Main Deployment Flow
# =====================================================

main() {
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${PURPLE}  Trinitas Safe Deployment v1.0${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    echo ""
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$DEPLOYMENT_LOG")"
    log INFO "Deployment started"
    
    # Phase 1: Pre-deployment
    echo -e "${BLUE}Phase 1: Pre-deployment Checks${NC}"
    
    if ! verify_prerequisites; then
        log ERROR "Deployment aborted due to failed prerequisites"
        exit 1
    fi
    
    create_deployment_checkpoint
    
    # Confirmation
    echo ""
    echo -e "${YELLOW}⚠️  This will deploy Trinitas parallel agents to your system.${NC}"
    echo -e "${YELLOW}   A checkpoint has been created for rollback if needed.${NC}"
    echo ""
    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log INFO "Deployment cancelled by user"
        exit 0
    fi
    
    # Phase 2: Deployment
    echo -e "\n${BLUE}Phase 2: Deployment${NC}"
    
    if ! deploy_hooks; then
        log ERROR "Hook deployment failed"
        rollback_deployment
        exit 1
    fi
    
    if ! deploy_settings; then
        log ERROR "Settings deployment failed"
        rollback_deployment
        exit 1
    fi
    
    # Phase 3: Verification
    echo -e "\n${BLUE}Phase 3: Verification${NC}"
    
    if ! test_deployment; then
        log ERROR "Deployment tests failed"
        echo ""
        echo -e "${YELLOW}Some tests failed. Would you like to rollback? (y/N)${NC}"
        read -p "" -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback_deployment
            exit 1
        else
            log WARNING "Proceeding despite test failures"
        fi
    fi
    
    # Phase 4: Completion
    echo -e "\n${BLUE}Phase 4: Completion${NC}"
    
    log SUCCESS "Deployment completed successfully"
    
    # Final instructions
    echo ""
    echo -e "${GREEN}✅ Deployment Successful!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart any running Claude sessions"
    echo "2. Run a test: ./examples/parallel_analysis_demo.sh"
    echo "3. Monitor health: ./hooks/monitoring/health_check.sh"
    echo ""
    echo "Checkpoint saved at: $ROLLBACK_POINT"
    echo "Deployment log: $DEPLOYMENT_LOG"
    echo ""
    echo -e "${PURPLE}Welcome to Trinitas Parallel Agents!${NC}"
}

# =====================================================
# Script Entry Point
# =====================================================

case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        if [[ -n "${2:-}" ]] && [[ -d "$2" ]]; then
            ROLLBACK_POINT="$2"
            rollback_deployment
        else
            echo "Usage: $0 rollback <checkpoint_directory>"
            exit 1
        fi
        ;;
    test)
        test_deployment
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|test]"
        exit 1
        ;;
esac