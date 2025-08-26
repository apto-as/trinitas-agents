# Trinitas v3.5 Phase 3 - 手動環境構築手順

## 修正版手順（UV専用、dotenv対応）

### 前提条件
- Python 3.11以上
- Git
- Docker（オプション：Redis使用時）

---

## 🚀 自動セットアップ（推奨）

```bash
# リポジトリクローン
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents
git checkout feature/trinitas-v35-true

# 統合セットアップスクリプト実行
chmod +x setup_all.sh
./setup_all.sh
```

これですべてが自動設定されます。以下は手動で実行する場合の手順です。

---

## 📝 手動セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents
git checkout feature/trinitas-v35-true
```

### 2. Claude エージェントのインストール

```bash
# install_to_claude.sh を使用（推奨）
./install_to_claude.sh

# または手動でコピー
mkdir -p ~/.claude/agents/
cp agents/*.md ~/.claude/agents/
cp TRINITAS-CORE-PROTOCOL.md ~/.claude/
cp TRINITAS_PERSONA_DEFINITIONS.yaml ~/.claude/trinitas/
```

### 3. UV パッケージマネージャのインストール

```bash
# UVのインストール（venv不要）
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### 4. MCP Tools のインストール

MCP Toolsは`~/.claude/trinitas/mcp-tools/`にインストールされます：

```bash
# 方法1: 自動インストール（推奨）
./setup_all.sh  # これが全てを自動設定

# 方法2: 手動インストール
cp -r v35-mcp-tools ~/.claude/trinitas/mcp-tools
cd ~/.claude/trinitas/mcp-tools
uv sync
```

### 5. 環境変数設定（.envファイル）

```bash
cd ~/.claude/trinitas/mcp-tools

# .env ファイルの作成
cat > .env << 'EOF'
# Trinitas v3.5 環境設定
# OS環境変数を汚染せず、ファイルベースで管理

# ペルソナ名前モード
TRINITAS_NAMING_MODE=mythology  # mythology（デフォルト）or developer

# メモリバックエンド
MEMORY_BACKEND=hybrid
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db

# ローカルLLM設定
LOCAL_LLM_MODE=auto
GEMINI_API_KEY=  # Gemini使用時に設定
OPENAI_API_KEY=  # OpenAI使用時に設定

# ログ設定
LOG_LEVEL=INFO
LOG_PATH=./logs/trinitas.log
EOF
```

### 6. Claude Desktop MCP 設定

`~/.claude/claude_desktop_config.json` を編集:

```json
{
  "mcpServers": {
    "trinitas-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/YOUR_USERNAME/.claude/trinitas/mcp-tools",
        "run",
        "trinitas-server"
      ],
      "env": {
        "PYTHONPATH": "/Users/YOUR_USERNAME/.claude/trinitas/mcp-tools",
        "TRINITAS_ENV_FILE": "/Users/YOUR_USERNAME/.claude/trinitas/mcp-tools/.env"
      }
    }
  }
}
```

**重要**: `YOUR_USERNAME` を実際のユーザー名に置き換えてください。

### 7. Redis のセットアップ（オプション）

#### Docker を使用する場合:
```bash
cd v35-mcp-tools
docker-compose up -d redis
```

#### 手動インストール（macOS）:
```bash
brew install redis
brew services start redis
```

#### 手動インストール（Ubuntu/Debian）:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**注意**: Redisなしでも動作します（SQLiteフォールバック）

### 8. 動作確認

```bash
cd ~/.claude/trinitas/mcp-tools

# インポート確認
uv run python -c "from src.core.trinitas_mcp_tools import TrinitasMCPTools; print('✓ Import OK')"

# メモリシステムテスト
uv run python examples/memory_system_demo.py

# MCP サーバー起動テスト
uv run trinitas-server
# Ctrl+C で停止
```

### 9. 可視化ダッシュボード

```bash
# ブラウザで開く
open ~/.claude/trinitas/mcp-tools/visualization/memory_visualizer.html  # macOS
xdg-open ~/.claude/trinitas/mcp-tools/visualization/memory_visualizer.html  # Linux
# または手動でブラウザでファイルを開く
```

---

## 🔍 トラブルシューティング

### UV関連のエラー
```bash
# UV再インストール
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 依存関係の再同期
cd ~/.claude/trinitas/mcp-tools
uv sync --refresh
```

### インポートエラー
```bash
# PYTHONPATHの確認
cd ~/.claude/trinitas/mcp-tools
uv run python -c "import sys; print(sys.path)"

# 再インストール
uv pip install -e . --force-reinstall
```

### Redis接続エラー
```bash
# Redis動作確認
redis-cli ping
# PONGが返れば正常

# .envファイルのREDIS_URL確認
grep REDIS_URL .env
```

### Claude Desktopが認識しない
1. Claude Desktop を完全に終了
2. MCP設定ファイルのパスを絶対パスで記載
3. Claude Desktop を再起動

---

## 📋 チェックリスト

- [ ] Python 3.11以上がインストールされている
- [ ] UVパッケージマネージャがインストールされている
- [ ] ~/.claude/agents/ に5つのペルソナファイルがある
- [ ] ~/.claude/trinitas/mcp-tools/ にMCP Toolsがインストールされている
- [ ] ~/.claude/trinitas/mcp-tools/.env ファイルが設定されている
- [ ] uv run trinitas-server が正常に起動する
- [ ] Claude Desktop の MCP 設定が完了している
- [ ] （オプション）Redis が起動している

---

## 🎯 動作テスト

Claude Desktop で以下のコマンドを試してください：

1. **Athena（戦略）**: "Plan a microservices architecture"
2. **Artemis（技術）**: "Optimize this Python function for performance"
3. **Hestia（セキュリティ）**: "Audit this code for security vulnerabilities"
4. **Bellona（戦術）**: "Coordinate parallel deployment tasks"
5. **Seshat（文書）**: "Generate API documentation"

---

## 📚 参考情報

- **設定ファイル**: `~/.claude/trinitas/mcp-tools/.env`
- **ログファイル**: `~/.claude/trinitas/mcp-tools/logs/trinitas.log`
- **エージェント**: `~/.claude/agents/*.md`
- **MCP設定**: `~/.claude/claude_desktop_config.json`
- **MCP Tools**: `~/.claude/trinitas/mcp-tools/`

## 🔄 アンインストール

```bash
# エージェントの削除
rm -rf ~/.claude/agents/athena-*.md
rm -rf ~/.claude/agents/artemis-*.md
rm -rf ~/.claude/agents/hestia-*.md
rm -rf ~/.claude/agents/bellona-*.md
rm -rf ~/.claude/agents/seshat-*.md
rm -rf ~/.claude/trinitas/

# MCP設定の削除
# ~/.claude/claude_desktop_config.json から trinitas-mcp セクションを削除
```