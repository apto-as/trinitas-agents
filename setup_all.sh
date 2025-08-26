#!/bin/bash
# Trinitas v3.5 Complete Setup Script
# UV専用、dotenv環境変数、MCP統合対応版

set -e  # エラーで停止

# カラーコード
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Trinitas v3.5 - Complete Setup${NC}"
echo -e "${BLUE}================================================${NC}"

# プロジェクトルート取得
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ===========================
# Part 1: Claude Agents Setup
# ===========================
echo -e "\n${CYAN}[Part 1/3] Installing Claude Agents...${NC}"
./install_to_claude.sh

# ===========================
# Part 2: MCP Tools with UV
# ===========================
echo -e "\n${CYAN}[Part 2/3] Setting up MCP Tools with UV...${NC}"

cd "$PROJECT_ROOT/v35-mcp-tools"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo -e "${GREEN}✓${NC} UV is installed"

# UV sync dependencies (no venv needed)
echo -e "${BLUE}Installing dependencies with UV...${NC}"
uv sync

# Create .env file from template if not exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env configuration file...${NC}"
    cat > .env << 'EOF'
# Trinitas v3.5 Environment Configuration
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
# Part 3: MCP Registration
# ===========================
echo -e "\n${CYAN}[Part 3/3] Configuring MCP Server...${NC}"

CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"

# Create MCP configuration
cat > /tmp/trinitas_mcp_config.json << EOF
{
  "mcpServers": {
    "trinitas-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "$PROJECT_ROOT/v35-mcp-tools",
        "run",
        "trinitas-server"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT/v35-mcp-tools",
        "TRINITAS_ENV_FILE": "$PROJECT_ROOT/v35-mcp-tools/.env"
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

# Check UV tools
cd "$PROJECT_ROOT/v35-mcp-tools"
if uv run python -c "from src.core.trinitas_mcp_tools import TrinitasMCPTools; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✓${NC} MCP Tools ready"
else
    echo -e "${RED}✗${NC} MCP Tools import failed"
fi

# ===========================
# Completion
# ===========================
echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Next Steps:"
echo "1. Restart Claude Desktop to load new agents and MCP server"
echo "2. (Optional) Start Redis for hybrid memory: docker-compose up -d"
echo "3. Test with commands like:"
echo "   - 'Plan a system architecture' (Athena)"
echo "   - 'Optimize this code' (Artemis)"
echo "   - 'Check security vulnerabilities' (Hestia)"
echo ""
echo "Configuration:"
echo "  • Agents: ~/.claude/agents/"
echo "  • Settings: v35-mcp-tools/.env"
echo "  • MCP Config: ~/.claude/claude_desktop_config.json"
echo ""
echo -e "${GREEN}Athena${NC}: 'ふふ、完璧にセットアップできましたわ'"
echo -e "${BLUE}Artemis${NC}: 'フン、効率的な構成ね'"
echo -e "${RED}Hestia${NC}: '……システム準備完了……安全性確認済み……'"
echo -e "${YELLOW}Bellona${NC}: '戦術的に最適な配置です'"
echo -e "${CYAN}Seshat${NC}: 'すべての設定が記録されました'"