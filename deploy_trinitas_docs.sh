#!/bin/bash

# TRINITAS Documentation Deploy Script
# Deploys built documentation to appropriate locations
# REQUIRES USER PERMISSION TO WRITE TO ~/.claude/

set -e

# Configuration
OUTPUT_DIR="output"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        print_error "Output directory not found. Run ./build_trinitas_docs.sh first"
        exit 1
    fi
    
    if [ ! -f "$OUTPUT_DIR/CLAUDE.md" ] || [ ! -f "$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md" ]; then
        print_error "Built files not found. Run ./build_trinitas_docs.sh first"
        exit 1
    fi
}

# Create backup
create_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_path="$BACKUP_DIR/trinitas_backup_$timestamp"
    
    mkdir -p "$backup_path"
    
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        cp "$CLAUDE_DIR/CLAUDE.md" "$backup_path/" 2>/dev/null || true
        print_status "Backed up existing CLAUDE.md"
    fi
    
    if [ -f "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md" ]; then
        cp "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md" "$backup_path/" 2>/dev/null || true
        print_status "Backed up existing TRINITAS-CORE-PROTOCOL.md"
    fi
}

# Deploy with confirmation
deploy_with_confirmation() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              TRINITAS Documentation Deployment              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    print_warning "This will deploy to $CLAUDE_DIR/"
    print_info "Files to deploy:"
    print_info "  - CLAUDE.md ($(wc -l < "$OUTPUT_DIR/CLAUDE.md") lines)"
    print_info "  - TRINITAS-CORE-PROTOCOL.md ($(wc -l < "$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md") lines)"
    echo ""
    
    read -p "Do you want to proceed? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Create backup
    create_backup
    
    # Deploy files
    print_status "Deploying CLAUDE.md..."
    cp "$OUTPUT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    
    print_status "Deploying TRINITAS-CORE-PROTOCOL.md..."
    cp "$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md" "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md"
    
    print_status "✅ Deployment successful"
}

# Dry run mode
dry_run() {
    echo ""
    print_info "DRY RUN MODE - No files will be modified"
    echo ""
    
    print_info "Would deploy:"
    print_info "  $OUTPUT_DIR/CLAUDE.md → $CLAUDE_DIR/CLAUDE.md"
    print_info "  $OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md → $CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md"
    echo ""
    
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        print_info "Would overwrite existing CLAUDE.md"
    fi
    
    if [ -f "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md" ]; then
        print_info "Would overwrite existing TRINITAS-CORE-PROTOCOL.md"
    fi
}

# Show diff
show_diff() {
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        print_status "Changes in CLAUDE.md:"
        diff -u "$CLAUDE_DIR/CLAUDE.md" "$OUTPUT_DIR/CLAUDE.md" 2>/dev/null | head -50 || print_info "No differences or new file"
    fi
    
    if [ -f "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md" ]; then
        print_status "Changes in TRINITAS-CORE-PROTOCOL.md:"
        diff -u "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md" "$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md" 2>/dev/null | head -50 || print_info "No differences or new file"
    fi
}

# Main
main() {
    check_prerequisites
    
    case "${1:-}" in
        --dry-run)
            dry_run
            ;;
        --diff)
            show_diff
            ;;
        --force)
            print_warning "Force deployment without confirmation"
            create_backup
            cp "$OUTPUT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
            cp "$OUTPUT_DIR/TRINITAS-CORE-PROTOCOL.md" "$CLAUDE_DIR/TRINITAS-CORE-PROTOCOL.md"
            print_status "✅ Force deployment complete"
            ;;
        --help|-h|help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run  - Show what would be deployed without making changes"
            echo "  --diff     - Show differences between current and new files"
            echo "  --force    - Deploy without confirmation prompt"
            echo "  --help     - Show this help message"
            echo ""
            echo "No options: Interactive deployment with confirmation"
            ;;
        *)
            deploy_with_confirmation
            ;;
    esac
}

# Ensure we have permission warning
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                         ⚠️  WARNING ⚠️                        ║"
echo "║                                                              ║"
echo "║  This script will modify files in ~/.claude/                ║"
echo "║  Make sure you have appropriate permissions!                ║"
echo "╚══════════════════════════════════════════════════════════════╝"

main "$@"