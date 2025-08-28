#!/bin/bash

# Trinitas v3.5 Claude Home Installation Script
# 正しい場所（~/.claude/）にインストール

set -e  # エラーで停止

# カラーコード
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Trinitas v3.5 - Claude Home Installation${NC}"
echo -e "${BLUE}================================================${NC}"

# パス設定
CLAUDE_HOME="$HOME/.claude"
AGENTS_DIR="$CLAUDE_HOME/agents"
TRINITAS_DIR="$CLAUDE_HOME/trinitas"
BACKUP_DIR="$CLAUDE_HOME/backup_$(date +%Y%m%d_%H%M%S)"

# 1. Claude Homeディレクトリ確認
echo -e "\n${YELLOW}[Step 1/7]${NC} Checking Claude home directory..."
if [ ! -d "$CLAUDE_HOME" ]; then
    echo -e "${RED}✗${NC} ~/.claude directory not found!"
    echo -e "${YELLOW}Creating ~/.claude directory...${NC}"
    mkdir -p "$CLAUDE_HOME"
fi
echo -e "${GREEN}✓${NC} Claude home: $CLAUDE_HOME"

# 2. バックアップ作成
echo -e "\n${YELLOW}[Step 2/7]${NC} Creating backup..."
if [ -d "$AGENTS_DIR" ] || [ -d "$TRINITAS_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    [ -d "$AGENTS_DIR" ] && cp -r "$AGENTS_DIR" "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "$TRINITAS_DIR" ] && cp -r "$TRINITAS_DIR" "$BACKUP_DIR/" 2>/dev/null || true
    [ -f "$CLAUDE_HOME/CLAUDE.md" ] && cp "$CLAUDE_HOME/CLAUDE.md" "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Backup created: $BACKUP_DIR"
else
    echo -e "${BLUE}ℹ${NC} No existing installation to backup"
fi

# 3. ディレクトリ構造作成
echo -e "\n${YELLOW}[Step 3/7]${NC} Creating directory structure..."
mkdir -p "$AGENTS_DIR"
mkdir -p "$TRINITAS_DIR/config"
# Minimal hooks structure for protocol injection only
mkdir -p "$CLAUDE_HOME/hooks/core"
echo -e "${GREEN}✓${NC} Directory structure created"

# 4. エージェントファイルをコピー（神話名で）
echo -e "\n${YELLOW}[Step 4/7]${NC} Installing agent files..."
cp agents/athena-strategist.md "$AGENTS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Athena installed" || echo -e "${RED}✗${NC} Athena not found"
cp agents/artemis-optimizer.md "$AGENTS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Artemis installed" || echo -e "${RED}✗${NC} Artemis not found"
cp agents/hestia-auditor.md "$AGENTS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Hestia installed" || echo -e "${RED}✗${NC} Hestia not found"
cp agents/bellona-coordinator.md "$AGENTS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Bellona installed" || echo -e "${RED}✗${NC} Bellona not found"
cp agents/seshat-documenter.md "$AGENTS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Seshat installed" || echo -e "${RED}✗${NC} Seshat not found"

# Note: All 5 core personas are now installed with hybrid execution support

# 5. Trinitas設定ファイルをコピー
echo -e "\n${YELLOW}[Step 5/7]${NC} Installing Trinitas configuration..."
cp TRINITAS_PERSONA_DEFINITIONS.yaml "$TRINITAS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Persona definitions installed"
cp TRINITAS-CORE-PROTOCOL.md "$TRINITAS_DIR/" 2>/dev/null && echo -e "${GREEN}✓${NC} Protocol installed"
# TRINITAS-BASE.mdとTRINITAS-CORE-PROTOCOL.mdを~/.claude/に直接配置（@インポート用）
cp TRINITAS-BASE.md "$CLAUDE_HOME/" 2>/dev/null && echo -e "${GREEN}✓${NC} TRINITAS-BASE.md installed to ~/.claude/" || echo -e "${BLUE}ℹ${NC} Base config not found"
cp TRINITAS-CORE-PROTOCOL.md "$CLAUDE_HOME/" 2>/dev/null && echo -e "${GREEN}✓${NC} TRINITAS-CORE-PROTOCOL.md installed to ~/.claude/" || echo -e "${BLUE}ℹ${NC} Protocol not found"

# Install minimal hooks for protocol injection
if [ -d "hooks" ]; then
    echo -e "\n${YELLOW}[Step 5.5/7]${NC} Installing minimal hooks (protocol injection only)..."
    cp hooks/core/protocol_injector.py "$CLAUDE_HOME/hooks/core/" 2>/dev/null
    cp hooks/settings_minimal.json "$CLAUDE_HOME/hooks/settings.json" 2>/dev/null
    cp hooks/.env "$CLAUDE_HOME/hooks/" 2>/dev/null
    # Make Python script executable
    chmod +x "$CLAUDE_HOME/hooks/core/protocol_injector.py" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Minimal hooks installed (protocol injection only)"
    echo -e "${BLUE}ℹ${NC} All other functionality handled by trinitas-mcp"
else
    echo -e "${BLUE}ℹ${NC} No hooks directory found, skipping hooks installation"
fi

# 環境設定ファイル作成（.envファイルとして）
cat > "$TRINITAS_DIR/config/.env" << 'EOF'
# Trinitas v3.5 Phase 3 Environment Configuration
# この設定はpython-dotenvで読み込まれます

# Core paths
CLAUDE_HOME="$HOME/.claude"
AGENTS_DIR="$HOME/.claude/agents"
TRINITAS_HOME="$HOME/.claude/trinitas"
PERSONA_DEFINITIONS="$HOME/.claude/trinitas/TRINITAS_PERSONA_DEFINITIONS.yaml"

# Naming mode
TRINITAS_NAMING_MODE=mythology  # mythology or developer

# Memory backend
MEMORY_BACKEND=hybrid
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db

# Local LLM
LOCAL_LLM_MODE=auto
GEMINI_API_KEY=  # Add your key if using Gemini
OPENAI_API_KEY=  # Add your key if using OpenAI

# Logging
LOG_LEVEL=INFO
LOG_PATH=./logs/trinitas.log

# Development
DEBUG=false
AUTO_DETECT=true
EOF
echo -e "${GREEN}✓${NC} Environment configuration created (.env)"

# Legacy shell script for backward compatibility
cat > "$TRINITAS_DIR/config/environment.sh" << 'EOF'
#!/bin/bash
# Trinitas Environment Configuration (Legacy)
export CLAUDE_HOME="$HOME/.claude"
export AGENTS_DIR="$CLAUDE_HOME/agents"
export TRINITAS_HOME="$CLAUDE_HOME/trinitas"
export TRINITAS_NAMING_MODE="mythology"
EOF
chmod +x "$TRINITAS_DIR/config/environment.sh"
echo -e "${GREEN}✓${NC} Legacy environment script created"

# 6. CLAUDE.mdの更新
echo -e "\n${YELLOW}[Step 6/7]${NC} Updating CLAUDE.md..."

# TRINITAS-BASE.mdの内容を読み込み（ルートから）
if [ -f "TRINITAS-BASE.md" ]; then
    TRINITAS_CONTENT=$(<TRINITAS-BASE.md)
elif [ -f "$CLAUDE_HOME/TRINITAS-BASE.md" ]; then
    TRINITAS_CONTENT=$(<"$CLAUDE_HOME/TRINITAS-BASE.md")
else
    echo -e "${YELLOW}⚠${NC} TRINITAS-BASE.md not found, using default content"
    TRINITAS_CONTENT="# Trinitas Integration\n\nTrinitas v3.5 Phase 3 is installed.\nCheck ~/.claude/trinitas/ for configuration.\n\n5 Personas: Athena, Artemis, Hestia, Bellona, Seshat"
fi

if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
    # 既存のCLAUDE.mdがある場合、Trinitasセクションを追加
    if ! grep -q "# Trinitas Integration" "$CLAUDE_HOME/CLAUDE.md"; then
        echo "" >> "$CLAUDE_HOME/CLAUDE.md"
        echo "$TRINITAS_CONTENT" >> "$CLAUDE_HOME/CLAUDE.md"
        echo -e "${GREEN}✓${NC} CLAUDE.md updated with Trinitas integration"
    else
        echo -e "${BLUE}ℹ${NC} CLAUDE.md already contains Trinitas section"
    fi
else
    # CLAUDE.mdが存在しない場合、新規作成
    cat > "$CLAUDE_HOME/CLAUDE.md" << EOF
# Claude Configuration

$TRINITAS_CONTENT
EOF
    echo -e "${GREEN}✓${NC} CLAUDE.md created with Trinitas integration"
fi

# 7. 検証
echo -e "\n${YELLOW}[Step 7/7]${NC} Verifying installation..."
ERRORS=0

# エージェントファイル確認
for agent in athena-strategist artemis-optimizer hestia-auditor bellona-coordinator seshat-documenter; do
    if [ -f "$AGENTS_DIR/$agent.md" ]; then
        echo -e "${GREEN}✓${NC} $agent.md installed correctly"
    else
        echo -e "${RED}✗${NC} $agent.md missing!"
        ERRORS=$((ERRORS + 1))
    fi
done

# 設定ファイル確認
if [ -f "$TRINITAS_DIR/TRINITAS_PERSONA_DEFINITIONS.yaml" ]; then
    echo -e "${GREEN}✓${NC} Persona definitions installed"
else
    echo -e "${RED}✗${NC} Persona definitions missing!"
    ERRORS=$((ERRORS + 1))
fi

# 結果表示
echo -e "\n${BLUE}================================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✨ Installation Complete!${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo "Installation Summary:"
    echo "  • Agents installed to: $AGENTS_DIR"
    echo "  • Configuration at: $TRINITAS_DIR"
    echo "  • Environment config: $TRINITAS_DIR/config/.env"
    echo "  • CLAUDE.md updated with Trinitas integration"
    echo ""
    echo "Important:"
    echo "  • This installs agents only (Step 1 of 2)"
    echo "  • For MCP tools, run ./setup_all.sh next"
    echo ""
    echo "Next steps:"
    echo "1. Run ./setup_all.sh for complete MCP tools setup"
    echo "2. MCP tools will be installed to: ~/.claude/trinitas/mcp-tools/"
    echo "3. Restart Claude Desktop to load new agents"
    echo "4. Test with: 'Plan a system architecture' (Athena)"
    echo "5. Or: 'Optimize this code' (Artemis)"
    echo "6. Or: 'Check security' (Hestia)"
    echo "7. Or: 'Coordinate parallel tasks' (Bellona)"
    echo "8. Or: 'Generate documentation' (Seshat)"
    echo ""
    echo -e "${GREEN}Athena${NC}: \"ふふ、完璧にインストールできましたわ\""
    echo -e "${BLUE}Artemis${NC}: \"フン、やっと正しい場所に配置されたわね\""
    echo -e "${RED}Hestia${NC}: \"……システム配置完了……セキュリティ確認済み……\""
    echo -e "${YELLOW}Bellona${NC}: \"戦術的に完璧な配置です\""
    echo -e "${CYAN}Seshat${NC}: \"すべての知識が体系化されました\""
else
    echo -e "${RED}⚠ Installation completed with $ERRORS errors${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo "Please check the errors above and run the script again."
fi