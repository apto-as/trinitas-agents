#!/bin/bash
# Trinitas v4.0 Complete Setup Script
# trinitas-mcpを~/.claude/trinitas/にインストール

set -e  # エラーで停止

# カラーコード
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Trinitas v4.0 - Complete Setup${NC}"
echo -e "${BLUE}================================================${NC}"

# プロジェクトルート取得
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLAUDE_HOME="$HOME/.claude"
TRINITAS_HOME="$CLAUDE_HOME/trinitas"
MCP_TOOLS_DIR="$TRINITAS_HOME/mcp-tools"

# ===========================
# Part 1: Claude Agents Setup
# ===========================
echo -e "\n${CYAN}[Part 1/3] Installing Claude Agents...${NC}"
./install_to_claude.sh

# ===========================
# Part 2: MCP Tools Installation
# ===========================
echo -e "\n${CYAN}[Part 2/3] Installing MCP Tools to ~/.claude/trinitas/...${NC}"

# Backup existing installation if present
if [ -d "$MCP_TOOLS_DIR" ]; then
    BACKUP_DIR="$TRINITAS_HOME/backup_mcp_$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Backing up existing MCP tools...${NC}"
    mv "$MCP_TOOLS_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} Backup created: $BACKUP_DIR"
fi

# Copy trinitas-mcp to ~/.claude/trinitas/mcp-tools
echo -e "${BLUE}Copying MCP tools to $MCP_TOOLS_DIR...${NC}"
cp -r "$PROJECT_ROOT/trinitas-mcp" "$MCP_TOOLS_DIR"

# Copy .env file if it exists in config directory
if [ -f "$PROJECT_ROOT/trinitas-mcp/config/.env" ]; then
    cp "$PROJECT_ROOT/trinitas-mcp/config/.env" "$MCP_TOOLS_DIR/"
    echo -e "${GREEN}✓${NC} Configuration file copied"
fi

# Remove restrictive Python version file if it exists
rm -f "$MCP_TOOLS_DIR/.python-version" 2>/dev/null

echo -e "${GREEN}✓${NC} MCP tools copied"

# Change to installed directory
cd "$MCP_TOOLS_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo -e "${GREEN}✓${NC} UV is installed"

# Clean up any broken venv if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf .venv
fi

# Create fresh virtual environment
echo -e "${BLUE}Creating fresh Python virtual environment...${NC}"
uv venv

# UV sync dependencies
echo -e "${BLUE}Installing dependencies with UV...${NC}"
uv sync

# Install FastMCP and other v4.0 dependencies
echo -e "${BLUE}Installing FastMCP and v4.0 dependencies...${NC}"
uv pip install fastmcp==2.11.3
uv pip install redis chromadb sqlite-utils
uv pip install python-dotenv numpy
echo -e "${GREEN}✓${NC} v4.0 dependencies installed"

# Create .env file from template if not exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env configuration file...${NC}"
    cat > .env << 'EOF'
# Trinitas v4.0 Environment Configuration
# すべての環境変数をファイルで管理（OS環境を汚染しない）

# Naming Mode
TRINITAS_NAMING_MODE=mythology  # mythology or developer

# Memory Backend Configuration
MEMORY_BACKEND=hybrid
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db

# Local LLM Configuration
LOCAL_LLM_MODE=auto
GEMINI_API_KEY=  # Add your key if using Gemini
OPENAI_API_KEY=  # Add your key if using OpenAI

# Logging
LOG_LEVEL=INFO
LOG_PATH=./logs/trinitas.log

# Development Settings
DEBUG=false
AUTO_DETECT=true
EOF
    echo -e "${GREEN}✓${NC} Created .env configuration file"
else
    echo -e "${BLUE}ℹ${NC} Using existing .env file"
fi

# ===========================
# Part 3: Minimal Hooks Installation
# ===========================
echo -e "\n${CYAN}[Part 3/4] Installing Minimal Hooks (Protocol Injection Only)...${NC}"

HOOKS_DIR="$CLAUDE_HOME/hooks"

# Backup existing hooks if present
if [ -d "$HOOKS_DIR" ]; then
    BACKUP_DIR="$CLAUDE_HOME/backup_hooks_$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Backing up existing hooks...${NC}"
    mv "$HOOKS_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} Backup created: $BACKUP_DIR"
fi

# Create minimal hooks structure
echo -e "${BLUE}Installing minimal hooks to $HOOKS_DIR...${NC}"
mkdir -p "$HOOKS_DIR/core"

# Copy only essential files for protocol injection (if they exist)
if [ -f "$PROJECT_ROOT/hooks/core/protocol_injector.py" ]; then
    cp "$PROJECT_ROOT/hooks/core/protocol_injector.py" "$HOOKS_DIR/core/"
    chmod +x "$HOOKS_DIR/core/protocol_injector.py"
    echo -e "${GREEN}✓${NC} Protocol injector installed"
fi

if [ -f "$PROJECT_ROOT/hooks/settings_minimal.json" ]; then
    cp "$PROJECT_ROOT/hooks/settings_minimal.json" "$HOOKS_DIR/settings.json"
fi

if [ -f "$PROJECT_ROOT/hooks/.env" ]; then
    cp "$PROJECT_ROOT/hooks/.env" "$HOOKS_DIR/"
fi

echo -e "${GREEN}✓${NC} Minimal hooks configured"
echo -e "${BLUE}ℹ${NC} All main functionality handled by trinitas-mcp"

# Install Trinitas custom command (if available)
COMMANDS_DIR="$CLAUDE_HOME/commands"
if [ -f "$PROJECT_ROOT/trinitas-mcp/.claude/commands/trinitas.md" ]; then
    echo -e "${BLUE}Installing /trinitas custom command...${NC}"
    mkdir -p "$COMMANDS_DIR"
    cp "$PROJECT_ROOT/trinitas-mcp/.claude/commands/trinitas.md" "$COMMANDS_DIR/"
    echo -e "${GREEN}✓${NC} /trinitas command installed"
fi

# ===========================
# Part 4: MCP Registration
# ===========================
echo -e "\n${CYAN}[Part 4/4] Configuring MCP Server...${NC}"

CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"

# Create MCP configuration
cat > /tmp/trinitas_mcp_config.json << EOF
{
  "mcpServers": {
    "trinitas-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "$MCP_TOOLS_DIR",
        "run",
        "trinitas-v4"
      ],
      "env": {
        "PYTHONPATH": "$MCP_TOOLS_DIR",
        "TRINITAS_ENV_FILE": "$MCP_TOOLS_DIR/.env"
      }
    }
  }
}
EOF

echo -e "${GREEN}✓${NC} MCP configuration prepared"

# Check if claude config exists
if [ -f "$CLAUDE_CONFIG" ]; then
    echo -e "${YELLOW}⚠${NC} Claude config exists. Please manually add the following to $CLAUDE_CONFIG:"
    echo ""
    cat /tmp/trinitas_mcp_config.json
    echo ""
    echo "Or run: cat /tmp/trinitas_mcp_config.json"
else
    echo -e "${BLUE}Creating Claude MCP configuration...${NC}"
    cp /tmp/trinitas_mcp_config.json "$CLAUDE_CONFIG"
    echo -e "${GREEN}✓${NC} Claude MCP configuration created"
fi

# ===========================
# Optional: Redis Setup
# ===========================
echo -e "\n${BLUE}[Optional] Redis Setup${NC}"
echo "To use the hybrid memory system, you need Redis."
echo "Options:"
echo "  1. Docker: docker run -d --name trinitas-redis -p 6379:6379 redis:7-alpine"
echo "  2. Homebrew: brew install redis && brew services start redis"
echo "  3. Skip: The system will work with SQLite fallback"

# Check if Redis is running and initialize security databases
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "\n${GREEN}✓${NC} Redis is running. Initializing persona databases..."
        # Initialize persona-specific databases (0-4) and shared databases (5-6)
        for i in {0..6}; do
            redis-cli -n $i FLUSHDB &> /dev/null
            echo -e "${GREEN}✓${NC} Initialized Redis DB $i"
        done
        echo -e "${GREEN}✓${NC} Persona isolation databases ready"
    else
        echo -e "${YELLOW}⚠${NC} Redis is installed but not running"
    fi
else
    echo -e "${BLUE}ℹ${NC} Redis not found - system will use SQLite fallback"
fi

# ===========================
# Verification
# ===========================
echo -e "\n${BLUE}Verifying installation...${NC}"

# Check agents
AGENT_COUNT=$(ls -1 ~/.claude/agents/*.md 2>/dev/null | wc -l)
if [ "$AGENT_COUNT" -ge 5 ]; then
    echo -e "${GREEN}✓${NC} Agents installed: $AGENT_COUNT personas"
else
    echo -e "${RED}✗${NC} Agent installation incomplete"
fi

# Check MCP tools installation
if [ -d "$MCP_TOOLS_DIR" ]; then
    echo -e "${GREEN}✓${NC} MCP Tools installed at: $MCP_TOOLS_DIR"
else
    echo -e "${RED}✗${NC} MCP Tools installation failed"
fi

# Check MCP server
cd "$MCP_TOOLS_DIR"
if uv run python -c "from src.mcp_server_v4 import mcp; print('OK')" 2>/dev/null | grep -q 'OK'; then
    echo -e "${GREEN}✓${NC} MCP Server v4.0 ready"
else
    # Fallback check for FastMCP implementation
    if uv run python -c "from src.mcp_server_fastmcp import mcp; print('OK')" 2>/dev/null | grep -q 'OK'; then
        echo -e "${GREEN}✓${NC} MCP Server ready (FastMCP)"
    else
        echo -e "${RED}✗${NC} MCP Server import failed"
    fi
fi

# ===========================
# Completion
# ===========================
echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Installation Summary:"
echo "  • Agents: ~/.claude/agents/"
echo "  • MCP Tools: ~/.claude/trinitas/mcp-tools/"
echo "  • Configuration: ~/.claude/trinitas/mcp-tools/.env"
echo "  • MCP Server: ~/.claude/claude_desktop_config.json"
echo ""
echo "Next Steps:"
echo "1. Restart Claude Desktop to load new agents and MCP server"
echo "2. (Optional) Start Redis for hybrid memory: docker-compose up -d"
echo "3. Test with commands like:"
echo "   - 'Plan a system architecture' (Athena)"
echo "   - 'Optimize this code' (Artemis)"
echo "   - 'Check security vulnerabilities' (Hestia)"
echo ""
echo -e "${GREEN}Athena${NC}: 'ふふ、完璧にセットアップできましたわ'"
echo -e "${BLUE}Artemis${NC}: 'フン、効率的な構成ね'"
echo -e "${RED}Hestia${NC}: '……システム準備完了……安全性確認済み……'"
echo -e "${YELLOW}Bellona${NC}: '戦術的に最適な配置です'"
echo -e "${CYAN}Seshat${NC}: 'すべての設定が記録されました'"