#!/bin/bash
# Trinitas Python Enhancement Setup with uv
# Krukai: "uvで効率的なPython環境を構築するわ。妥協は許さない"

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common library
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# uv Installation Check
# =====================================================

check_uv_installed() {
    if command -v uv >/dev/null 2>&1; then
        local version=$(uv --version 2>/dev/null | cut -d' ' -f2)
        log_success "uv is installed (version: $version)"
        return 0
    else
        return 1
    fi
}

install_uv() {
    log_info "Installing uv package manager..."
    
    # Detect OS
    local os_type="$(uname -s)"
    
    case "$os_type" in
        Darwin)
            # macOS
            if command -v brew >/dev/null 2>&1; then
                log_info "Installing uv via Homebrew..."
                brew install uv
            else
                log_info "Installing uv via curl..."
                curl -LsSf https://astral.sh/uv/install.sh | sh
            fi
            ;;
        Linux)
            # Linux
            log_info "Installing uv via curl..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            ;;
        *)
            log_error "Unsupported OS: $os_type"
            return 1
            ;;
    esac
    
    # Add to PATH if needed
    if [[ -f "$HOME/.cargo/bin/uv" ]] && ! command -v uv >/dev/null 2>&1; then
        export PATH="$HOME/.cargo/bin:$PATH"
        log_info "Added uv to PATH. You may need to add this to your shell profile:"
        log_info "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
    fi
}

# =====================================================
# Python Environment Setup
# =====================================================

setup_python_environment() {
    local python_dir="$SCRIPT_DIR"
    
    krukai_says "Python環境を完璧に構築するわ"
    
    cd "$python_dir"
    
    # Create virtual environment with uv
    log_info "Creating virtual environment with uv..."
    uv venv .venv
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    log_info "Installing core dependencies..."
    uv pip install -e .
    
    # Install development dependencies if requested
    if [[ "${1:-}" == "--dev" ]]; then
        log_info "Installing development dependencies..."
        uv pip install -e ".[dev]"
    fi
    
    # Install enhanced features if requested
    if [[ "${1:-}" == "--enhanced" ]] || [[ "${2:-}" == "--enhanced" ]]; then
        log_info "Installing enhanced features..."
        uv pip install -e ".[enhanced]"
    fi
    
    # Install security tools if requested
    if [[ "${1:-}" == "--security" ]] || [[ "${2:-}" == "--security" ]] || [[ "${3:-}" == "--security" ]]; then
        log_info "Installing security tools..."
        uv pip install -e ".[security]"
    fi
    
    log_success "Python environment setup complete!"
}

# =====================================================
# Create Python Enhancement Wrapper
# =====================================================

create_wrapper_script() {
    local wrapper_path="$HOOKS_ROOT/python/run_python_hook.sh"
    
    cat > "$wrapper_path" << 'EOF'
#!/bin/bash
# Python hook wrapper for Trinitas
# Automatically activates uv environment and runs Python hooks

PYTHON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PYTHON_DIR/.venv"

# Check if virtual environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Error: Python environment not found. Run setup_uv.sh first." >&2
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the Python script with all arguments
exec python "$@"
EOF
    
    chmod +x "$wrapper_path"
    log_success "Created Python wrapper script: $wrapper_path"
}

# =====================================================
# Main Setup Function
# =====================================================

main() {
    springfield_says "Python強化層のセットアップを開始します"
    
    # Check if uv is installed
    if ! check_uv_installed; then
        install_uv
        
        # Verify installation
        if ! check_uv_installed; then
            log_error "Failed to install uv"
            exit 1
        fi
    fi
    
    # Setup Python environment
    setup_python_environment "$@"
    
    # Create wrapper script
    create_wrapper_script
    
    krukai_says "完璧！Python強化層の準備が整ったわ"
    
    # Show next steps
    echo
    log_info "Next steps:"
    log_info "1. Source the virtual environment: source $SCRIPT_DIR/.venv/bin/activate"
    log_info "2. Run Python hooks using: $HOOKS_ROOT/python/run_python_hook.sh <script.py>"
    log_info "3. Install additional features: $0 --enhanced --security"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi