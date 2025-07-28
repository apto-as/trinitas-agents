#!/bin/bash

# Project Trinitas v2.0 - Compatibility Check Script
# Comprehensive system compatibility validation

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

# Compatibility requirements
MIN_CLAUDE_VERSION="1.0.0"
MIN_BASH_VERSION="4.0"
MIN_PYTHON_VERSION="3.8"

echo "========================================"
echo "  Project Trinitas Compatibility Check"
echo "========================================"
echo ""

compatibility_score=0
total_checks=0

# Function to compare versions
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($1) ver2=($2)
    
    # Fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    
    return 0
}

check_os_compatibility() {
    log_info "Checking operating system compatibility..."
    ((total_checks++))
    
    case "$(uname -s)" in
        Darwin*)
            log_success "✓ macOS detected - fully supported"
            ((compatibility_score++))
            ;;
        Linux*)
            log_success "✓ Linux detected - fully supported"
            ((compatibility_score++))
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            log_success "✓ Windows (WSL/Git Bash) detected - supported"
            ((compatibility_score++))
            ;;
        *)
            log_warning "! Unknown OS detected - may have compatibility issues"
            ;;
    esac
}

check_claude_code() {
    log_info "Checking Claude Code installation..."
    ((total_checks++))
    
    if command -v claude &> /dev/null; then
        CLAUDE_VERSION=$(claude --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "unknown")
        
        if [[ "$CLAUDE_VERSION" == "unknown" ]]; then
            log_warning "! Claude Code found but version could not be determined"
        else
            version_compare "$CLAUDE_VERSION" "$MIN_CLAUDE_VERSION"
            case $? in
                0|1)
                    log_success "✓ Claude Code v$CLAUDE_VERSION (meets minimum v$MIN_CLAUDE_VERSION)"
                    ((compatibility_score++))
                    ;;
                2)
                    log_error "✗ Claude Code v$CLAUDE_VERSION is below minimum v$MIN_CLAUDE_VERSION"
                    ;;
            esac
        fi
    else
        log_error "✗ Claude Code not found in PATH"
        echo "    Please install Claude Code: https://claude.ai/code"
    fi
}

check_bash_version() {
    log_info "Checking Bash version..."
    ((total_checks++))
    
    BASH_VERSION="${BASH_VERSION:-unknown}"
    
    if [[ "$BASH_VERSION" == "unknown" ]]; then
        log_warning "! Bash version could not be determined"
    else
        BASH_MAJOR=$(echo "$BASH_VERSION" | cut -d. -f1)
        
        if (( BASH_MAJOR >= 4 )); then
            log_success "✓ Bash $BASH_VERSION (meets minimum v$MIN_BASH_VERSION)"
            ((compatibility_score++))
        else
            log_warning "! Bash $BASH_VERSION is below recommended v$MIN_BASH_VERSION"
            echo "    Some advanced features may not work properly"
        fi
    fi
}

check_python_availability() {
    log_info "Checking Python availability (optional)..."
    ((total_checks++))
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -n1)
        
        version_compare "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"
        case $? in
            0|1)
                log_success "✓ Python $PYTHON_VERSION (meets minimum v$MIN_PYTHON_VERSION)"
                log_info "    Advanced utility features will be available"
                ((compatibility_score++))
                ;;
            2)
                log_warning "! Python $PYTHON_VERSION is below recommended v$MIN_PYTHON_VERSION"
                echo "    Some utility features may not work properly"
                ;;
        esac
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -n1)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        
        if (( PYTHON_MAJOR >= 3 )); then
            log_success "✓ Python $PYTHON_VERSION found"
            ((compatibility_score++))
        else
            log_warning "! Python $PYTHON_VERSION is Python 2 - Python 3 recommended"
        fi
    else
        log_warning "! Python not found - utility features will be limited"
        echo "    Basic Trinitas functionality will still work"
    fi
}

check_git_availability() {
    log_info "Checking Git availability (optional)..."
    ((total_checks++))
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
        log_success "✓ Git $GIT_VERSION available"
        log_info "    Version control integration will be available"
        ((compatibility_score++))
    else
        log_warning "! Git not found - version control features will be limited"
        echo "    Manual installation method required"
    fi
}

check_curl_availability() {
    log_info "Checking curl availability..."
    ((total_checks++))
    
    if command -v curl &> /dev/null; then
        CURL_VERSION=$(curl --version | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
        log_success "✓ curl $CURL_VERSION available"
        log_info "    One-command installation will be available"
        ((compatibility_score++))
    else
        log_warning "! curl not found - manual installation required"
        echo "    wget or manual download method needed"
    fi
}

check_directory_permissions() {
    log_info "Checking directory permissions..."
    ((total_checks++))
    
    CLAUDE_DIR="$HOME/.claude"
    AGENTS_DIR="$CLAUDE_DIR/agents"
    
    # Test write permissions
    if mkdir -p "$AGENTS_DIR" 2>/dev/null; then
        if touch "$AGENTS_DIR/.trinitas_test" 2>/dev/null; then
            rm -f "$AGENTS_DIR/.trinitas_test"
            log_success "✓ Write permissions available for $AGENTS_DIR"
            ((compatibility_score++))
        else
            log_error "✗ No write permission for $AGENTS_DIR"
        fi
    else
        log_error "✗ Cannot create directory $AGENTS_DIR"
    fi
}

check_disk_space() {
    log_info "Checking available disk space..."
    ((total_checks++))
    
    CLAUDE_DIR="$HOME/.claude"
    
    if command -v df &> /dev/null; then
        # Get available space in KB
        AVAILABLE_KB=$(df "$HOME" | tail -1 | awk '{print $4}')
        AVAILABLE_MB=$((AVAILABLE_KB / 1024))
        
        if (( AVAILABLE_MB >= 50 )); then
            log_success "✓ Sufficient disk space: ${AVAILABLE_MB}MB available (50MB required)"
            ((compatibility_score++))
        else
            log_warning "! Limited disk space: ${AVAILABLE_MB}MB available (50MB required)"
        fi
    else
        log_info "    Disk space check unavailable - assuming sufficient"
        ((compatibility_score++))
    fi
}

# Run all compatibility checks
check_os_compatibility
check_claude_code
check_bash_version
check_python_availability
check_git_availability
check_curl_availability
check_directory_permissions
check_disk_space

# Calculate compatibility percentage
compatibility_percentage=$((compatibility_score * 100 / total_checks))

echo ""
echo "========================================"
echo "  Compatibility Summary"
echo "========================================"
echo ""

if (( compatibility_percentage >= 90 )); then
    log_success "Excellent compatibility: $compatibility_score/$total_checks checks passed ($compatibility_percentage%)"
    echo "✓ Your system is fully compatible with Project Trinitas"
    echo "✓ All features will be available"
elif (( compatibility_percentage >= 75 )); then
    log_success "Good compatibility: $compatibility_score/$total_checks checks passed ($compatibility_percentage%)"
    echo "✓ Your system is compatible with Project Trinitas"
    echo "! Some optional features may be limited"
elif (( compatibility_percentage >= 50 )); then
    log_warning "Partial compatibility: $compatibility_score/$total_checks checks passed ($compatibility_percentage%)"
    echo "! Your system has partial compatibility"
    echo "! Core features should work, but some functionality may be limited"
else
    log_error "Poor compatibility: $compatibility_score/$total_checks checks passed ($compatibility_percentage%)"
    echo "✗ Your system may have significant compatibility issues"
    echo "✗ Installation may fail or have limited functionality"
fi

echo ""
echo "Next steps:"
if (( compatibility_percentage >= 75 )); then
    echo "  → Proceed with installation: ./install.sh"
else
    echo "  → Address compatibility issues above before installation"
    echo "  → Consider upgrading system components as needed"
fi

echo "  → Full installation guide: README.md"
echo "  → Support: https://github.com/project-trinitas/trinitas-agents/issues"
echo ""

# Exit with appropriate code
if (( compatibility_percentage >= 50 )); then
    exit 0
else
    exit 1
fi