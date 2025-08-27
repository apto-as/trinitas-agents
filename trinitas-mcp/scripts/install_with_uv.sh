#!/bin/bash
# Trinitas MCP Tools - UV Installation Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Trinitas MCP Tools - UV Installation${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv is not installed. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo -e "${GREEN}✓${NC} uv is installed"

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${BLUE}Installing Trinitas MCP Tools...${NC}"

# Create virtual environment with uv
echo "Creating virtual environment..."
uv venv

# Install dependencies
echo "Installing dependencies..."
uv pip sync requirements.txt

# Install package in editable mode
echo "Installing Trinitas MCP Tools..."
uv pip install -e .

# Setup Claude Code integration
echo -e "\n${BLUE}Setting up Claude Code integration...${NC}"
uv run trinitas-setup --auto

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✨ Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "You can now use Trinitas MCP Tools with:"
echo "  • uv run trinitas-mcp --help"
echo "  • uv run trinitas-server"
echo ""
echo "Claude Code integration has been configured."
echo "Please restart Claude Code to load the new tools."
echo ""
echo -e "${GREEN}Athena${NC}: 'ふふ、インストールが完了しましたわ'"
echo -e "${BLUE}Artemis${NC}: 'フン、効率的なセットアップね'"
echo -e "${RED}Hestia${NC}: '……システム準備完了……'"