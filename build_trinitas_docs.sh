#!/bin/bash

# TRINITAS Documentation Build Script
# Builds CLAUDE.md and TRINITAS-CORE-PROTOCOL.md from source components

set -e

# Configuration
BUILD_DIR="trinitas_sources"
OUTPUT_DIR="output"  # Local output directory (not ~/.claude)
CLAUDE_FILE="$OUTPUT_DIR/CLAUDE.md"
PROTOCOL_FILE="$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if source directory exists
if [ ! -d "$BUILD_DIR" ]; then
    print_error "Directory $BUILD_DIR not found!"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build CLAUDE.md (user-facing, minimal)
build_claude() {
    print_status "Building CLAUDE.md..."
    
    {
        # Common components only
        for file in "$BUILD_DIR"/common/*.md; do
            if [ -f "$file" ]; then
                cat "$file"
                echo ""  # Add spacing between sections
            fi
        done
    } > "$CLAUDE_FILE"
    
    if [ -f "$CLAUDE_FILE" ]; then
        print_status "✅ Built CLAUDE.md ($(wc -l < "$CLAUDE_FILE") lines)"
    else
        print_error "Failed to create CLAUDE.md"
        return 1
    fi
}

# Build TRINITAS-CORE-PROTOCOL.md (complete agent protocol)
build_protocol() {
    print_status "Building TRINITAS-CORE-PROTOCOL.md..."
    
    {
        # Common components
        print_status "  Adding common components..."
        for file in "$BUILD_DIR"/common/*.md; do
            if [ -f "$file" ]; then
                cat "$file"
                echo ""
            fi
        done
        
        # Agent-specific components
        print_status "  Adding agent execution patterns..."
        for file in "$BUILD_DIR"/agent/*.md; do
            if [ -f "$file" ]; then
                echo ""
                echo "---"
                echo ""
                cat "$file"
                echo ""
            fi
        done
        
        # Tool guidelines
        print_status "  Adding tool guidelines..."
        if [ -d "$BUILD_DIR/agent/01_tool_guidelines" ]; then
            echo ""
            echo "## Tool Usage Guidelines"
            echo ""
            for file in "$BUILD_DIR"/agent/01_tool_guidelines/*.md; do
                if [ -f "$file" ]; then
                    cat "$file"
                    echo ""
                fi
            done
        fi
    } > "$PROTOCOL_FILE"
    
    if [ -f "$PROTOCOL_FILE" ]; then
        print_status "✅ Built TRINITAS-CORE-PROTOCOL.md ($(wc -l < "$PROTOCOL_FILE") lines)"
    else
        print_error "Failed to create TRINITAS-CORE-PROTOCOL.md"
        return 1
    fi
}

# Validate output
validate_output() {
    print_status "Validating output files..."
    
    local errors=0
    
    # Check file sizes
    if [ ! -s "$CLAUDE_FILE" ]; then
        print_error "CLAUDE.md is empty"
        errors=$((errors + 1))
    fi
    
    if [ ! -s "$PROTOCOL_FILE" ]; then
        print_error "TRINITAS-CORE-PROTOCOL.md is empty"
        errors=$((errors + 1))
    fi
    
    # Check for required sections in CLAUDE.md
    if ! grep -q "Available AI Personas" "$CLAUDE_FILE" 2>/dev/null; then
        print_warning "CLAUDE.md missing personas section"
    fi
    
    if ! grep -q "Trinitasコマンド実行方法" "$CLAUDE_FILE" 2>/dev/null; then
        print_warning "CLAUDE.md missing commands section"
    fi
    
    # Check for required sections in PROTOCOL
    if ! grep -q "協調動作パターン" "$PROTOCOL_FILE" 2>/dev/null; then
        print_warning "PROTOCOL missing execution patterns"
    fi
    
    if ! grep -q "Tool Usage Guidelines" "$PROTOCOL_FILE" 2>/dev/null; then
        print_warning "PROTOCOL missing tool guidelines"
    fi
    
    if [ $errors -eq 0 ]; then
        print_status "✅ Validation passed"
        return 0
    else
        print_error "Validation failed with $errors errors"
        return 1
    fi
}

# Show diff if files exist
show_diff() {
    if [ -f "$1" ] && [ -f "$2" ]; then
        print_status "Showing changes for $(basename "$1")..."
        diff -u "$1" "$2" 2>/dev/null | head -20 || true
    fi
}

# Main execution
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         TRINITAS Documentation Build System v1.0            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Build documentation
    build_claude
    build_protocol
    
    # Validate
    if validate_output; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║                    BUILD SUCCESSFUL                         ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
        print_status "Output files created in $OUTPUT_DIR/"
        print_status "  - CLAUDE.md ($(wc -l < "$CLAUDE_FILE") lines)"
        print_status "  - TRINITAS-CORE-PROTOCOL.md ($(wc -l < "$PROTOCOL_FILE") lines)"
        echo ""
        print_warning "Files are in $OUTPUT_DIR/ directory"
        print_warning "To deploy to ~/.claude/, use: ./deploy_trinitas_docs.sh"
        echo ""
    else
        echo ""
        print_error "Build completed with warnings/errors"
        exit 1
    fi
}

# Parse arguments
case "${1:-}" in
    claude)
        build_claude
        ;;
    protocol)
        build_protocol
        ;;
    validate)
        validate_output
        ;;
    help|--help|-h)
        echo "Usage: $0 [claude|protocol|validate|help]"
        echo ""
        echo "Commands:"
        echo "  claude    - Build only CLAUDE.md"
        echo "  protocol  - Build only TRINITAS-CORE-PROTOCOL.md"
        echo "  validate  - Validate existing output files"
        echo "  help      - Show this help message"
        echo ""
        echo "No arguments builds both files"
        ;;
    *)
        main
        ;;
esac