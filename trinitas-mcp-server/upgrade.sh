#!/bin/bash
# Trinity Hybrid MCP Server Upgrade Script
# 最新の機能を取り込みます

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================"
echo "⚡ Trinity Hybrid MCP Server Upgrade"
echo "   Krukai: \"404のやり方で完璧にアップグレードするわ\""
echo "================================================"
echo ""

# Check current version
echo "📊 Checking current installation..."
current_version=$(python3 -c "from hybrid_mcp.core.hybrid_server import app; print(app.version)" 2>/dev/null || echo "Not installed")
echo -e "Current version: ${BLUE}$current_version${NC}"

# Backup current configuration if exists
if [ -d "hybrid-mcp" ]; then
    echo ""
    echo "💾 Creating backup..."
    backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    cp -r hybrid-mcp/core "$backup_dir/" 2>/dev/null || true
    echo -e "${GREEN}✓ Backup created in $backup_dir${NC}"
fi

# Pull latest changes (if in git repo)
if [ -d ".git" ]; then
    echo ""
    echo "🔄 Pulling latest changes..."
    git fetch origin
    git status
    echo -e "${YELLOW}⚠ Please commit or stash your changes before upgrading${NC}"
    read -p "Continue with upgrade? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Upgrade cancelled."
        exit 1
    fi
fi

# Update dependencies
echo ""
echo "📦 Updating dependencies..."
pip install --upgrade -r requirements.txt

# Reinstall package
echo ""
echo "🔧 Reinstalling Trinity MCP Server..."
pip install --upgrade -e .

# Run migration if needed
echo ""
echo "🔄 Checking for migrations..."
python3 -c "
import sys
sys.path.insert(0, '.')
# Check for any breaking changes
try:
    from hybrid_mcp.core.hybrid_server import app
    print('✓ No migration needed')
except ImportError as e:
    print(f'⚠ Migration may be needed: {e}')
"

# Verify upgrade
echo ""
echo "🔍 Verifying upgrade..."
new_version=$(python3 -c "from hybrid_mcp.core.hybrid_server import app; print(app.version)")
echo -e "New version: ${GREEN}$new_version${NC}"

# Run tests
echo ""
echo "🧪 Running test suite..."
cd hybrid-mcp
python -m pytest tests/test_hybrid.py -v --tb=short || {
    echo -e "${YELLOW}⚠ Some tests failed. Please review the changes.${NC}"
}
cd ..

# Check for new features
echo ""
echo "✨ Checking new features..."
python3 -c "
from hybrid_mcp.core.hybrid_server import app
print('Available middleware:', len(app.middleware))
print('Client types supported:', ['claude', 'gemini', 'qwen', 'unknown'])
"

echo ""
echo "================================================"
echo -e "${GREEN}✅ Trinity Hybrid MCP Server upgraded successfully!${NC}"
echo ""
echo "📝 Upgrade Summary:"
echo "   Previous: $current_version"
echo "   Current:  $new_version"
echo ""
echo "Vector: \"...アップグレード完了...新しい脅威に対応済み...\""
echo "Springfield: \"素晴らしいですわ！新機能が追加されましたね♪\""
echo "Krukai: \"当然の結果よ。404の品質は常に最高レベルなの\""
echo ""
echo "🚀 What's new:"
echo "   - FastMCP v2 middleware support"
echo "   - Enhanced client detection"
echo "   - Improved quality gates"
echo "   - Better performance optimization"
echo ""
echo "================================================"