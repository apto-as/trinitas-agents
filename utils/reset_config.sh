#!/bin/bash

# Project Trinitas v2.0 - Configuration Reset Script
# Reset Trinitas configuration to default values

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration paths
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
TRINITAS_DIR="$AGENTS_DIR/trinitas"
CONFIG_FILE="$TRINITAS_DIR/config.yaml"
BACKUP_DIR="$TRINITAS_DIR/backup_$(date +%Y%m%d_%H%M%S)"

echo "========================================"
echo "  Project Trinitas Configuration Reset"
echo "========================================"
echo ""

# Check if Trinitas is installed
if [ ! -d "$TRINITAS_DIR" ]; then
    log_error "Trinitas installation not found at: $TRINITAS_DIR"
    log_info "Please install Trinitas first: ./install.sh"
    exit 1
fi

# Function to create backup
create_backup() {
    if [ -f "$CONFIG_FILE" ]; then
        log_info "Creating backup of current configuration..."
        mkdir -p "$BACKUP_DIR"
        cp "$CONFIG_FILE" "$BACKUP_DIR/config.yaml.backup"
        
        # Backup any other configuration files
        if [ -d "$TRINITAS_DIR/profiles" ]; then
            cp -r "$TRINITAS_DIR/profiles" "$BACKUP_DIR/"
        fi
        
        if [ -f "$TRINITAS_DIR/user_preferences.yaml" ]; then
            cp "$TRINITAS_DIR/user_preferences.yaml" "$BACKUP_DIR/"
        fi
        
        log_success "Backup created at: $BACKUP_DIR"
    else
        log_info "No existing configuration found to backup"
    fi
}

# Function to generate default configuration
generate_default_config() {
    log_info "Generating default configuration..."
    
    mkdir -p "$TRINITAS_DIR"
    
    cat > "$CONFIG_FILE" << 'EOF'
# Project Trinitas v2.0 - Default Configuration
# Auto-generated on $(date)

# Core Trinitas Configuration
trinitas:
  # Operation mode: full (complete analysis), efficient (balanced), minimal (basic)
  mode: "full"
  
  # Enable automatic coordination between agents
  auto_coordination: true
  
  # Enable quality gates and validation
  quality_gates: true
  
  # Coordination threshold (0.0-1.0) - higher values require more explicit triggers
  coordination_threshold: 0.8

# Individual Persona Configuration
personalities:
  
  # Springfield - Strategic Coordinator
  springfield:
    # Communication formality: casual, polite, formal
    formality: "polite"
    
    # Primary language: english, japanese, mixed
    language: "japanese"
    
    # Strategic focus areas
    focus_areas:
      - "long_term_planning"
      - "team_coordination" 
      - "stakeholder_management"
      - "risk_communication"
    
  # Krukai - Technical Optimizer
  krukai:
    # Quality standards: relaxed, standard, strict
    standards: "strict"
    
    # Optimization level: disabled, enabled, aggressive
    optimization: "aggressive"
    
    # Performance focus areas
    focus_areas:
      - "code_quality"
      - "performance_optimization"
      - "technical_excellence"
      - "implementation_efficiency"
    
  # Vector - Security Auditor
  vector:
    # Paranoia level for risk assessment: low, medium, high
    paranoia_level: "high"
    
    # Compliance frameworks to consider
    compliance:
      - "OWASP"
      - "GDPR"
      - "SOX"
      - "NIST"
    
    # Security focus areas
    focus_areas:
      - "vulnerability_assessment"
      - "threat_modeling"
      - "risk_analysis"
      - "compliance_validation"

# Agent Auto-Detection Configuration
agent_config:
  
  trinitas_coordinator:
    # Threshold for automatic activation (0.0-1.0)
    auto_trigger_threshold: 0.8
    
    # Keywords that trigger this agent
    keywords:
      - "comprehensive"
      - "trinitas"
      - "three perspectives"
      - "multi-perspective"
      - "strategic technical security"
    
    # Required context patterns
    context_patterns:
      - "analysis"
      - "evaluation"
      - "assessment"
      - "review"
  
  springfield_strategist:
    auto_trigger_threshold: 0.7
    keywords:
      - "strategy"
      - "planning"
      - "roadmap"
      - "long-term"
      - "vision"
      - "architecture"
      - "stakeholder"
    context_patterns:
      - "plan"
      - "strategy"
      - "future"
      - "goal"
  
  krukai_optimizer:
    auto_trigger_threshold: 0.7
    keywords:
      - "performance"
      - "optimization"
      - "quality"
      - "technical"
      - "efficiency"
      - "code review"
      - "implementation"
    context_patterns:
      - "optimize"
      - "improve"
      - "enhance"
      - "refactor"
  
  vector_auditor:
    auto_trigger_threshold: 0.9
    keywords:
      - "security"
      - "audit"
      - "risk"
      - "vulnerability"
      - "threat"
      - "compliance"
      - "safety"
    context_patterns:
      - "secure"
      - "protect"
      - "validate"
      - "verify"
  
  trinitas_workflow:
    auto_trigger_threshold: 0.6
    keywords:
      - "workflow"
      - "pipeline"
      - "automation"
      - "process"
      - "lifecycle"
      - "CI/CD"
      - "deployment"
    context_patterns:
      - "automate"
      - "streamline"
      - "manage"
      - "coordinate"
  
  trinitas_quality:
    auto_trigger_threshold: 0.7
    keywords:
      - "quality"
      - "testing"
      - "validation"
      - "QA"
      - "assurance"
      - "verification"
      - "standards"
    context_patterns:
      - "test"
      - "validate"
      - "check"
      - "verify"

# Quality Gates Configuration
quality_gates:
  # Enable individual quality gate steps
  enabled_gates:
    syntax_validation: true
    type_safety: true
    code_quality: true
    security_validation: true
    testing_validation: true
    performance_validation: true
    integration_testing: true
    documentation_validation: true
  
  # Quality thresholds
  thresholds:
    code_quality_score: 0.80
    test_coverage_unit: 0.90
    test_coverage_integration: 0.70
    security_score: 0.90
    performance_score: 0.85
  
  # Failure handling
  on_failure:
    action: "report"  # report, block, warn
    notification: true
    retry_attempts: 2

# Automation Configuration
automation:
  # Pre-execution hooks
  pre_execution:
    dangerous_command_check: true
    resource_validation: true
    security_clearance: true
    context_preparation: true
  
  # Post-execution hooks
  post_execution:
    quality_validation: true
    knowledge_persistence: true
    progress_notification: true
    cleanup: true
  
  # Notification settings
  notifications:
    enabled: true
    channels: ["console"]  # console, file, webhook
    verbosity: "normal"  # minimal, normal, verbose

# Integration Configuration
integrations:
  # Version control
  git:
    enabled: true
    auto_commit: false
    commit_message_template: "feat: {description}\n\nTrinitas automated commit\n\nCo-authored-by: Springfield <strategy@trinitas.dev>\nCo-authored-by: Krukai <technical@trinitas.dev>\nCo-authored-by: Vector <security@trinitas.dev>"
  
  # CI/CD systems
  cicd:
    enabled: false
    systems: []  # github_actions, gitlab_ci, jenkins
  
  # Project management
  project_management:
    enabled: false
    systems: []  # jira, github_issues, linear

# Logging Configuration
logging:
  # Log level: DEBUG, INFO, WARNING, ERROR
  level: "INFO"
  
  # Log destinations
  destinations:
    console: true
    file: true
    file_path: "~/.claude/agents/trinitas/logs/trinitas.log"
  
  # Log rotation
  rotation:
    enabled: true
    max_size: "10MB"
    backup_count: 5

# Performance Configuration
performance:
  # Enable caching
  cache_enabled: true
  cache_ttl: 3600  # seconds
  
  # Parallel processing
  parallel_operations: true
  max_workers: 3
  
  # Timeout settings
  timeouts:
    agent_response: 30  # seconds
    coordination: 60    # seconds
    quality_gates: 120  # seconds

# Security Configuration
security:
  # Validation settings
  validate_inputs: true
  sanitize_outputs: true
  
  # Audit logging
  audit_logging: true
  audit_log_path: "~/.claude/agents/trinitas/logs/audit.log"
  
  # Dangerous command protection
  dangerous_commands:
    enabled: true
    block_list:
      - "rm -rf /"
      - "sudo rm -rf"
      - "format c:"
      - "del /f /s /q C:\\"
    
    # Action on dangerous command: block, warn, log
    action: "block"

# Development Configuration (for Trinitas development)
development:
  # Debug mode
  debug: false
  
  # Test mode (reduces thresholds, increases verbosity)
  test_mode: false
  
  # Development logging
  dev_logging: false
EOF

    # Substitute the actual date
    sed -i.bak "s/\$(date)/$(date)/" "$CONFIG_FILE" && rm "$CONFIG_FILE.bak"
    
    log_success "Default configuration generated"
}

# Function to create default directories
create_default_directories() {
    log_info "Creating default directory structure..."
    
    mkdir -p "$TRINITAS_DIR/logs"
    mkdir -p "$TRINITAS_DIR/cache"
    mkdir -p "$TRINITAS_DIR/profiles"
    mkdir -p "$TRINITAS_DIR/utils"
    
    log_success "Directory structure created"
}

# Function to reset permissions
reset_permissions() {
    log_info "Resetting file permissions..."
    
    find "$TRINITAS_DIR" -type f -name "*.yaml" -exec chmod 644 {} \;
    find "$TRINITAS_DIR" -type f -name "*.sh" -exec chmod 755 {} \;
    find "$TRINITAS_DIR" -type f -name "*.py" -exec chmod 755 {} \;
    find "$TRINITAS_DIR" -type d -exec chmod 755 {} \;
    
    log_success "Permissions reset"
}

# Function to validate configuration
validate_configuration() {
    log_info "Validating configuration..."
    
    if [ -f "$CONFIG_FILE" ]; then
        # Basic YAML syntax check
        if command -v python3 &> /dev/null; then
            if python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
                log_success "Configuration validation passed"
                return 0
            else
                log_error "Configuration validation failed - invalid YAML syntax"
                return 1
            fi
        else
            log_info "Python not available - skipping YAML validation"
            return 0
        fi
    else
        log_error "Configuration file not found"
        return 1
    fi
}

# Main reset process
main() {
    # Confirm with user unless --force flag is provided
    if [[ "${1:-}" != "--force" ]]; then
        echo "This will reset your Trinitas configuration to default values."
        echo "Your current configuration will be backed up."
        echo ""
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Configuration reset cancelled"
            exit 0
        fi
    fi
    
    # Execute reset steps
    create_backup
    generate_default_config
    create_default_directories
    reset_permissions
    
    if validate_configuration; then
        echo ""
        log_success "Configuration reset completed successfully!"
        echo ""
        echo "What was reset:"
        echo "  ✓ Configuration file restored to defaults"
        echo "  ✓ Directory structure recreated"
        echo "  ✓ File permissions reset"
        echo ""
        echo "Backup location: $BACKUP_DIR"
        echo ""
        echo "Next steps:"
        echo "  1. Test configuration: python3 utils/test_utilities.py"
        echo "  2. Customize as needed: edit $CONFIG_FILE"
        echo "  3. Restart Claude Code if needed"
        echo ""
    else
        log_error "Configuration reset failed validation"
        echo "Please check the error messages above and try again"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-reset}" in
    "reset"|"--force")
        main "$@"
        ;;
    "backup-only")
        create_backup
        log_success "Backup completed without reset"
        ;;
    "validate")
        validate_configuration
        ;;
    "help"|"--help")
        echo "Usage: $0 [reset|--force|backup-only|validate|help]"
        echo ""
        echo "Commands:"
        echo "  reset      Reset configuration with confirmation (default)"
        echo "  --force    Reset configuration without confirmation"
        echo "  backup-only Create backup without reset"
        echo "  validate   Validate current configuration"
        echo "  help       Show this help message"
        echo ""
        exit 0
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac