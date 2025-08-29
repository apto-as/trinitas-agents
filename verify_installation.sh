#!/bin/bash

# Trinitas v4.0 Installation Verification Script
# インストールの状態を確認

# カラーコード
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Trinitas v4.0 - Installation Verification${NC}"
echo -e "${BLUE}================================================${NC}"

# Variables
CLAUDE_HOME="$HOME/.claude"
AGENTS_DIR="$CLAUDE_HOME/agents"
TRINITAS_DIR="$CLAUDE_HOME/trinitas"
MCP_TOOLS_DIR="$TRINITAS_DIR/mcp-tools"
ERRORS=0
WARNINGS=0

echo ""
echo -e "${CYAN}[Checking Directory Structure]${NC}"
echo "----------------------------------------"

# Check Claude home
if [ -d "$CLAUDE_HOME" ]; then
    echo -e "${GREEN}✓${NC} Claude home exists: $CLAUDE_HOME"
else
    echo -e "${RED}✗${NC} Claude home missing: $CLAUDE_HOME"
    ERRORS=$((ERRORS + 1))
fi

# Check agents directory
if [ -d "$AGENTS_DIR" ]; then
    AGENT_COUNT=$(ls -1 $AGENTS_DIR/*.md 2>/dev/null | wc -l)
    if [ "$AGENT_COUNT" -eq 5 ]; then
        echo -e "${GREEN}✓${NC} All 5 agent personas installed"
        # List agents
        for agent in athena-strategist artemis-optimizer hestia-auditor bellona-coordinator seshat-documenter; do
            if [ -f "$AGENTS_DIR/$agent.md" ]; then
                echo -e "  ${GREEN}✓${NC} $agent.md"
            else
                echo -e "  ${RED}✗${NC} $agent.md missing"
                ERRORS=$((ERRORS + 1))
            fi
        done
    else
        echo -e "${YELLOW}⚠${NC} Found $AGENT_COUNT agents (expected 5)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗${NC} Agents directory missing: $AGENTS_DIR"
    ERRORS=$((ERRORS + 1))
fi

# Check Trinitas directory
if [ -d "$TRINITAS_DIR" ]; then
    echo -e "${GREEN}✓${NC} Trinitas directory exists: $TRINITAS_DIR"
else
    echo -e "${RED}✗${NC} Trinitas directory missing: $TRINITAS_DIR"
    ERRORS=$((ERRORS + 1))
fi

# Check MCP tools
if [ -d "$MCP_TOOLS_DIR" ]; then
    echo -e "${GREEN}✓${NC} MCP tools directory exists: $MCP_TOOLS_DIR"
    
    # Check for v4.0 server
    if [ -f "$MCP_TOOLS_DIR/src/mcp_server_v4.py" ]; then
        echo -e "  ${GREEN}✓${NC} v4.0 MCP server found"
    elif [ -f "$MCP_TOOLS_DIR/src/mcp_server_fastmcp.py" ]; then
        echo -e "  ${YELLOW}⚠${NC} FastMCP server found (fallback)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${RED}✗${NC} No MCP server found"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check .env file
    if [ -f "$MCP_TOOLS_DIR/.env" ]; then
        echo -e "  ${GREEN}✓${NC} .env configuration exists"
    else
        echo -e "  ${YELLOW}⚠${NC} .env configuration missing"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check virtual environment
    if [ -d "$MCP_TOOLS_DIR/.venv" ]; then
        echo -e "  ${GREEN}✓${NC} Python virtual environment exists"
    else
        echo -e "  ${YELLOW}⚠${NC} Python virtual environment missing"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} MCP tools not installed yet"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo -e "${CYAN}[Checking Protocol Files]${NC}"
echo "----------------------------------------"

# Check TRINITAS-BASE.md
if [ -f "$CLAUDE_HOME/TRINITAS-BASE.md" ]; then
    echo -e "${GREEN}✓${NC} TRINITAS-BASE.md installed"
else
    echo -e "${YELLOW}⚠${NC} TRINITAS-BASE.md not found"
    WARNINGS=$((WARNINGS + 1))
fi

# Check TRINITAS-CORE-PROTOCOL.md
if [ -f "$CLAUDE_HOME/TRINITAS-CORE-PROTOCOL.md" ]; then
    echo -e "${GREEN}✓${NC} TRINITAS-CORE-PROTOCOL.md installed"
else
    echo -e "${YELLOW}⚠${NC} TRINITAS-CORE-PROTOCOL.md not found"
    WARNINGS=$((WARNINGS + 1))
fi

# Check CLAUDE.md
if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
    if grep -q "Trinitas" "$CLAUDE_HOME/CLAUDE.md"; then
        echo -e "${GREEN}✓${NC} CLAUDE.md contains Trinitas integration"
    else
        echo -e "${YELLOW}⚠${NC} CLAUDE.md exists but lacks Trinitas section"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} CLAUDE.md not found"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo -e "${CYAN}[Checking Optional Components]${NC}"
echo "----------------------------------------"

# Check Redis
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓${NC} Redis is running (hybrid memory available)"
    else
        echo -e "${YELLOW}⚠${NC} Redis installed but not running"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${BLUE}ℹ${NC} Redis not installed (SQLite fallback will be used)"
fi

# Check MCP configuration
CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    if grep -q "trinitas-mcp" "$CLAUDE_CONFIG"; then
        echo -e "${GREEN}✓${NC} MCP server registered in Claude config"
    else
        echo -e "${YELLOW}⚠${NC} MCP server not registered in Claude config"
        echo -e "  Run: cat /tmp/trinitas_mcp_config.json"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} Claude Desktop config not found"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}================================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✨ Perfect! Everything is properly installed.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Desktop to load agents and MCP"
    echo "2. Test with: 'Plan a system architecture'"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Installation complete with $WARNINGS warnings.${NC}"
    echo ""
    echo "Recommendations:"
    if [ $WARNINGS -gt 0 ]; then
        echo "• Run ./setup_all.sh to install missing components"
        echo "• Check warnings above for specific actions"
    fi
    echo ""
else
    echo -e "${RED}✗ Installation has $ERRORS errors and $WARNINGS warnings.${NC}"
    echo ""
    echo "Required actions:"
    echo "1. Run ./install_to_claude.sh to install agents"
    echo "2. Run ./setup_all.sh for complete installation"
    echo ""
fi

# Display personas status
echo -e "${CYAN}Persona Status:${NC}"
echo -e "${GREEN}Athena${NC}: \"ふふ、システムの状態を確認しましたわ\""
echo -e "${BLUE}Artemis${NC}: \"フン、インストール状況をチェック完了\""
echo -e "${RED}Hestia${NC}: \"……セキュリティ確認……完了……\""
echo -e "${YELLOW}Bellona${NC}: \"戦術的検証を実施しました\""
echo -e "${CYAN}Seshat${NC}: \"インストール状態を記録しました\""