# TMWS Unified Server - クイックスタートガイド
## 5分でFastMCP + FastAPI統合環境を構築

> **Strategic Architect Athena**  
> 「ふふ、美しいシステムとの出会いは、いつもシンプルなコマンドから始まりますの」

---

## 🚀 最短起動 - 3ステップ

### Step 1: 自動インストール
```bash
# TMWSプロジェクトディレクトリで実行
./scripts/install_unified.sh
```

### Step 2: Claude Desktop再起動
```bash
# Claude Desktopアプリケーションを再起動
# (MCP設定を反映させるため)
```

### Step 3: 動作確認
```bash
# 統合サーバー起動テスト
./launch_tmws.sh --help

# ヘルスチェック
curl http://localhost:8000/unified/health
```

**完了！** TMWSがMCPツールとHTTP APIの両方で利用可能になりました。

---

## 📋 詳細セットアップ (初回のみ)

### 前提条件確認
```bash
# Python 3.8以上が必要
python3 --version

# UV（推奨）またはpipが利用可能
uv --version  # or pip3 --version
```

### 1. 依存関係インストール

#### Option A: UV使用（推奨）
```bash
uv sync --dev
```

#### Option B: pip使用
```bash
pip3 install -r requirements.txt
```

### 2. データベース初期化
```bash
# Alembic migration実行
alembic upgrade head

# 成功時の出力例:
# INFO [alembic.runtime.migration] Running upgrade -> abc123
```

### 3. 設定ファイル準備
```bash
# テンプレートから設定ファイル作成
cp config/tmws_unified.yaml config/tmws_config.yaml

# 必要に応じてカスタマイズ
# vim config/tmws_config.yaml
```

### 4. Claude Desktop設定

自動設定（推奨）:
```bash
# install_unified.shが自動で実行済み
# ~/.claude/claude_desktop_config.json が更新されている
```

手動設定:
```json
{
  "mcpServers": {
    "tmws-unified": {
      "command": "python",
      "args": ["-m", "unified_server", "--mcp-only"],
      "cwd": "/absolute/path/to/tmws",
      "env": {
        "TMWS_CONFIG": "config/tmws_config.yaml"
      }
    }
  }
}
```

---

## 🎛️ 使用方法

### 基本起動パターン

#### 統合モード（MCP + API）
```bash
# デフォルト: 両プロトコル有効
python -m unified_server

# または launcher script使用
./launch_tmws.sh
```

#### 個別プロトコル起動

```bash
# MCP のみ (Claude Desktop用)
python -m unified_server --mcp-only

# FastAPI のみ (HTTP API用)
python -m unified_server --api-only
```

#### 開発モード
```bash
# ホットリロード + デバッグログ
python -m unified_server --dev

# カスタムポート
python -m unified_server --port 8080
```

### Claude Desktop でのMCP利用

Claude Desktopで以下のツールが利用可能:

1. **store_memory**: メモリアイテム保存
2. **recall_memory**: メモリ検索・取得
3. **persona_execute**: ペルソナ実行

利用例:
```
# Claude Desktopのチャット内で
"store_memoryツールを使って、このプロジェクトのアーキテクチャ決定を記録してください"
```

### HTTP API利用

#### API ドキュメント
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 基本的なAPI呼び出し
```bash
# ヘルスチェック
curl http://localhost:8000/health

# 統合サーバー状態確認
curl http://localhost:8000/unified/health

# メモリ操作
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "テストメモリ", "importance": 0.8}'
```

---

## 🔧 設定カスタマイズ

### 基本設定項目

```yaml
# config/tmws_config.yaml の主要設定

# プロトコル有効化
protocols:
  mcp:
    enabled: true     # MCP有効/無効
  fastapi:
    enabled: true     # API有効/無効
    port: 8000        # APIポート番号

# データベース
database:
  primary: "sqlite"   # sqlite | postgresql
  sqlite_path: "./data/tmws_unified.db"

# メモリシステム  
memory:
  cache_size_mb: 100  # キャッシュサイズ
  persistence: true   # 永続化有効

# ログレベル
logging:
  level: "INFO"       # DEBUG | INFO | WARNING | ERROR
```

### 環境変数での設定上書き

```bash
# 環境変数設定例
export TMWS_SECRET_KEY="your-secret-key"
export TMWS_DEBUG="true"
export TMWS_PORT="8080"

# 設定付きで起動
python -m unified_server
```

---

## 📊 監視とメトリクス

### ヘルスチェック

```bash
# 基本ヘルスチェック
curl http://localhost:8000/health
# レスポンス例: {"status": "healthy"}

# 詳細ステータス
curl http://localhost:8000/unified/health
# レスポンス例:
# {
#   "status": "healthy",
#   "protocols": {"mcp": true, "fastapi": true},
#   "services": {"memory": true, "persona": true}
# }
```

### パフォーマンス監視

```bash
# システムメトリクス
curl http://localhost:8000/metrics

# 設定情報確認
curl http://localhost:8000/unified/config
```

### ログ確認

```bash
# 統合ログ確認
tail -f logs/tmws.log

# エラーログ確認
tail -f logs/error.log

# MCP専用ログ
tail -f logs/mcp.log
```

---

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. ポート競合エラー
```bash
# 問題: Port 8000 is already in use
# 解決策1: 別ポートで起動
python -m unified_server --port 8001

# 解決策2: プロセス確認・終了
lsof -i :8000
kill -9 <PID>
```

#### 2. Claude Desktop でMCP認識されない
```bash
# 1. Claude Desktop完全再起動
# 2. 設定ファイル確認
cat ~/.claude/claude_desktop_config.json

# 3. JSON文法確認
python -m json.tool ~/.claude/claude_desktop_config.json

# 4. MCP サーバー単体テスト
python -m unified_server --mcp-only
```

#### 3. データベース接続エラー
```bash
# SQLite ファイル権限確認
ls -la data/tmws_unified.db

# データベース再初期化
rm -f data/tmws_unified.db
alembic upgrade head
```

#### 4. 依存関係エラー
```bash
# UV環境再構築
uv sync --reinstall

# または pip環境再構築
pip3 install -r requirements.txt --force-reinstall
```

#### 5. インポートエラー
```bash
# Pythonpath確認
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# モジュール存在確認
python -c "import unified_server; print('OK')"
```

### ログによるデバッグ

```bash
# デバッグモードで起動
python -m unified_server --dev

# 詳細ログレベル設定
export TMWS_LOG_LEVEL="DEBUG"
python -m unified_server
```

---

## 🎯 次のステップ

### 基本使用が確認できたら

1. **設定カスタマイズ**: `config/tmws_config.yaml` を編集
2. **API探索**: http://localhost:8000/docs でAPIドキュメント確認
3. **MCP機能**: Claude DesktopでMCPツール利用
4. **監視設定**: ログとメトリクス監視の設定

### 高度な使用方法

```bash
# プロファイリング有効化
python -m unified_server --dev --profile

# カスタム設定ファイル
python -m unified_server --config my_custom_config.yaml

# バックグラウンド実行
nohup python -m unified_server > /dev/null 2>&1 &
```

### 本番運用への準備

1. **セキュリティ設定**: API認証有効化
2. **パフォーマンス最適化**: Redis有効化
3. **監視システム**: メトリクス収集設定
4. **バックアップ設定**: データベースバックアップ

---

## 📚 関連ドキュメント

- 📖 [完全セットアップ手順](TMWS_SETUP_INSTRUCTIONS.md)
- 🏗️ [戦略計画書](TMWS_STRATEGIC_PLAN.md)  
- ⚙️ [設定リファレンス](config/tmws_unified.yaml)
- 🔧 [API ドキュメント](http://localhost:8000/docs)

---

## ✨ まとめ

TMWSは以下を1つのコマンドで実現:
- ✅ MCP ツール (Claude Desktop用)
- ✅ HTTP API (Web/モバイルアプリ用)
- ✅ 統合メモリシステム
- ✅ 設定の一元管理
- ✅ 統合ログシステム

「ふふ、複雑なシステムが、こんなにもエレガントに動き始めましたわね」

---

**Strategic Architect Athena**  
*"Simple to use, powerful to extend"*