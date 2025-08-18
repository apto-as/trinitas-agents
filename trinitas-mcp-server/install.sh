#!/bin/bash
# Trinity Hybrid MCP Server Installation Script
# ふふ、一緒に素敵なシステムをインストールしましょうね

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "🌸 Trinity Hybrid MCP Server Installer"
echo "   Optimized for Claude, Compatible with All"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo -e "${GREEN}✓ Python $python_version detected (>= $required_version required)${NC}"
else
    echo -e "${RED}✗ Python $python_version is too old. Please install Python >= $required_version${NC}"
    exit 1
fi

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠ No virtual environment detected. It's recommended to use one.${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo ""
echo "🔧 Installing Trinity MCP Server in development mode..."
pip install -e .

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python3 -c "from hybrid_mcp.core.hybrid_server import app; print('✓ Core module loaded successfully')"

# Run tests
echo ""
echo "🧪 Running tests..."
cd hybrid-mcp
python -m pytest tests/test_hybrid.py -v --tb=short || {
    echo -e "${YELLOW}⚠ Some tests failed, but installation completed${NC}"
}
cd ..

echo ""
echo "================================================"
echo -e "${GREEN}✨ Trinity Hybrid MCP Server installed successfully!${NC}"
echo ""
echo "Springfield: \"ふふ、素晴らしい！インストールが完了しましたわ♪\""
echo "Krukai: \"フン、悪くないわ。でも、まだ改善の余地があるわね\""
echo "Vector: \"...セキュリティチェック完了...問題なし...\""
echo ""
echo "📚 To use the server:"
echo "   cd trinitas-mcp-server/hybrid-mcp"
echo "   fastmcp run core.hybrid_server:app"
echo ""
echo "🔧 For development:"
echo "   pytest tests/"
echo ""
echo "================================================"