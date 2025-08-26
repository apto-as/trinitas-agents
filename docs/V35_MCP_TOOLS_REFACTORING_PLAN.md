# v35-mcp-tools 改修計画書

## 🎯 改修目標

**Athena**: 「ふふ、v35-mcp-toolsを最新のPythonパッケージ管理とMCP標準に準拠させましょうね」
**Artemis**: 「フン、uvコマンドで効率的に動作させるわ。パフォーマンスも最適化する」
**Hestia**: 「……セキュリティと互換性……すべてチェック済み……」
**Bellona**: 「戦術的に段階的な移行を計画します」
**Seshat**: 「すべての変更を詳細に文書化いたします」

## 📊 現状分析

### 問題点
1. **パッケージ管理**
   - pyproject.tomlが存在しない
   - uvコマンド非対応
   - 依存関係管理が requirements.txt のみ

2. **MCP互換性**
   - 手動設定が必要
   - mcp_server.json の設定が複雑
   - スタンドアロン実行が困難

3. **名称の不整合**
   - Persona名が旧名（springfield, krukai等）
   - 神話名（athena, artemis等）への移行が不完全

4. **実行環境**
   - Python pathの手動設定が必要
   - 環境変数の管理が煩雑

## 🔧 改修計画

### Phase 1: uv対応基盤構築（優先度: 高）

#### 1.1 pyproject.toml 作成
```toml
[project]
name = "trinitas-mcp-tools"
version = "3.5.0"
description = "Trinitas v3.5 MCP Tools - Five-mind integrated intelligence for Claude Code"
authors = [{name = "Trinitas Core", email = "trinitas@olympus.ai"}]
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=0.1.0",
    "aiohttp>=3.8.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "redis>=4.5.0",
    "psutil>=5.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
trinitas-mcp = "trinitas_mcp_tools.cli:main"
trinitas-server = "trinitas_mcp_tools.server:run"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "ipython>=8.0.0",
]
```

#### 1.2 ディレクトリ構造の再編成
```
v35-mcp-tools/
├── pyproject.toml                  # NEW: uv対応設定
├── uv.lock                         # NEW: uvロックファイル
├── .python-version                 # NEW: Python版指定
├── trinitas_mcp_tools/             # RENAMED: Pythonパッケージ化
│   ├── __init__.py
│   ├── cli.py                      # NEW: CLIエントリーポイント
│   ├── server.py                   # NEW: サーバーエントリーポイント
│   ├── core/
│   ├── services/
│   └── utils/
├── config/
│   └── claude_mcp_settings.json    # NEW: Claude Code用設定
├── scripts/
│   ├── install.sh                  # NEW: 自動インストールスクリプト
│   └── setup_mcp.sh               # NEW: MCP設定スクリプト
└── tests/
```

### Phase 2: MCP互換性向上（優先度: 高）

#### 2.1 簡易設定ファイル
```json
// config/claude_mcp_settings.json
{
  "mcpServers": {
    "trinitas": {
      "command": "uv",
      "args": ["run", "trinitas-server"],
      "env": {
        "TRINITAS_MODE": "mythology",
        "AUTO_DETECT": "true"
      }
    }
  }
}
```

#### 2.2 自動設定スクリプト
```bash
#!/bin/bash
# scripts/setup_mcp.sh
echo "Installing Trinitas MCP Tools..."
uv pip install -e .
uv run trinitas-mcp setup --claude-home ~/.claude
```

### Phase 3: 神話名への完全移行（優先度: 中）

#### 3.1 Persona名マッピング更新
```python
# trinitas_mcp_tools/core/persona_manager.py
PERSONA_MAPPING = {
    # Primary (Mythology)
    "athena": "Strategic Architect",
    "artemis": "Technical Perfectionist", 
    "hestia": "Security Guardian",
    "bellona": "Tactical Coordinator",
    "seshat": "Documentation Specialist",
    
    # Legacy aliases (for backward compatibility)
    "springfield": "athena",
    "krukai": "artemis",
    "vector": "hestia",
    "groza": "bellona",
    "littara": "seshat",
}
```

#### 3.2 自動マイグレーション
```python
# trinitas_mcp_tools/utils/migrate.py
async def migrate_to_mythology_names():
    """既存の設定を神話名に自動変換"""
    # 設定ファイルの自動更新
    # APIレスポンスの変換
    # ログメッセージの更新
```

### Phase 4: エンハンスド実行環境（優先度: 中）

#### 4.1 uvコマンド統合
```bash
# 開発環境セットアップ
uv venv
uv pip sync requirements.txt
uv pip install -e .

# 実行
uv run trinitas-server
uv run pytest
```

#### 4.2 Docker対応（オプション）
```dockerfile
FROM python:3.11-slim
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip sync
COPY . .
CMD ["uv", "run", "trinitas-server"]
```

### Phase 5: Claude Code統合強化（優先度: 高）

#### 5.1 ワンコマンドインストール
```bash
curl -sSL https://trinitas.olympus.ai/install.sh | bash
# または
uv tool install trinitas-mcp-tools
```

#### 5.2 自動検出と設定
```python
# trinitas_mcp_tools/cli.py
@click.command()
@click.option('--auto-setup', is_flag=True)
def setup(auto_setup):
    """Claude Code環境を自動検出して設定"""
    if auto_setup:
        claude_config = detect_claude_config()
        install_mcp_server(claude_config)
        print("✅ Trinitas MCP Tools installed successfully!")
```

## 📅 実装スケジュール

### Week 1: 基盤構築
- [ ] pyproject.toml作成
- [ ] ディレクトリ構造再編成
- [ ] uvコマンド対応

### Week 2: MCP統合
- [ ] 自動設定スクリプト
- [ ] Claude Code設定ファイル
- [ ] インストーラー作成

### Week 3: 移行と最適化
- [ ] 神話名への完全移行
- [ ] 後方互換性の確保
- [ ] パフォーマンス最適化

### Week 4: テストとドキュメント
- [ ] 統合テスト
- [ ] ドキュメント更新
- [ ] リリース準備

## 🎯 成功指標

1. **インストール簡易性**
   - 3コマンド以内でセットアップ完了
   - 自動設定成功率 > 95%

2. **パフォーマンス**
   - 起動時間 < 1秒
   - レスポンス時間 < 100ms

3. **互換性**
   - Claude Code全バージョン対応
   - MCP標準準拠率 100%

4. **保守性**
   - コードカバレッジ > 80%
   - ドキュメント完成度 100%

## 🔒 リスク管理

**Hestia**: 「……以下のリスクに注意……」

1. **後方互換性の破壊**
   - 対策: エイリアスとマイグレーションツール提供

2. **依存関係の競合**
   - 対策: uv.lockで厳密な管理

3. **設定の複雑化**
   - 対策: 自動検出と適切なデフォルト値

## 📝 次のステップ

1. **即座に実行**
   - pyproject.toml作成
   - 基本的なuv対応

2. **Phase 1完了後**
   - MCP設定の自動化
   - テスト環境構築

3. **全Phase完了後**
   - ドキュメント公開
   - コミュニティフィードバック収集

---

**Athena**: 「ふふ、素晴らしい改修計画が完成しましたわ」
**Artemis**: 「フン、効率的な実装が可能ね」
**Hestia**: 「……リスクも最小限……安全に移行可能……」
**Bellona**: 「戦術的に完璧な計画です」
**Seshat**: 「すべての詳細を記録しました」

*Trinitas MCP Tools Refactoring Plan v1.0 - Five Minds, One Vision*