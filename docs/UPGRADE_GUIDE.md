# Trinitas v2.0 アップグレードガイド

## 概要

Trinitas v2.0は、以下の大きな変更を含みます：
- Shell Script ベースのHooksシステム
- Python依存の最小化（オプション化）
- SessionStartとPreCompactフックによるプロトコル注入
- 改善されたディレクトリ構造

## アップグレード前の確認

### 現在のインストール状況を確認

```bash
./install.sh list
```

### バックアップの推奨

重要な設定がある場合は、手動でバックアップすることを推奨します：

```bash
cp -r ~/.claude ~/.claude.manual_backup
```

## アップグレード方法

### 方法1: 自動アップグレード（推奨）

```bash
./upgrade.sh
```

このスクリプトは以下を実行します：
1. 既存インストールの自動バックアップ
2. 古いPythonベースのフックの削除
3. 新しいShell Scriptベースのフックのインストール
4. settings.jsonの自動マージ（既存設定を保持）
5. プロトコル注入フックの追加

### 方法2: クリーンインストール

完全に新しい状態から始めたい場合：

```bash
# 1. 既存インストールをアンインストール
./install.sh uninstall

# 2. 新規インストール
./install.sh
```

### 方法3: 強制インストール

既存インストールを上書きする場合：

```bash
./install.sh --force
```

## アップグレード後の確認

### インストール状況の確認

```bash
./install.sh list
```

### 新機能の確認

1. **プロトコル注入の確認**
   - 新しいClaude Codeセッションを開始
   - セッション開始時にTrinitas-Coreプロトコルが読み込まれることを確認

2. **Hooksの動作確認**
   ```bash
   # テストコマンドを実行
   claude bash "echo 'Trinitas v2.0 is working!'"
   ```

3. **settings.jsonの確認**
   ```bash
   cat ~/.claude/settings.json | grep -A5 "SessionStart"
   ```

## トラブルシューティング

### 問題が発生した場合のロールバック

```bash
# ユーザーインストールのロールバック
./upgrade.sh --rollback user

# プロジェクトインストールのロールバック
./upgrade.sh --rollback project
```

### よくある問題

1. **settings.jsonのマージエラー**
   - `jq`がインストールされていない場合は、手動でマージが必要
   - `hooks/examples/trinitas_protocol_settings.json`を参考に手動で追加

2. **古いフックが残っている**
   ```bash
   # 手動で削除
   rm -rf ~/.claude/hooks/*.py
   rm -rf ~/.claude/scripts/hooks
   ```

3. **プロトコルが読み込まれない**
   - `~/.claude/TRINITAS-CORE-PROTOCOL.md`が存在することを確認
   - settings.jsonにSessionStartフックが設定されていることを確認

### 設定の自動更新

アップグレードスクリプトは以下の設定を自動的に追加します：

- **SessionStart**: Trinitas-Coreプロトコルの注入
- **PreCompact**: コンパクトサマリー時のプロトコル注入
- **PreToolUse**: 
  - Bashコマンドの安全性チェック
  - ファイル操作の安全性チェック
- **PostToolUse**:
  - コード品質チェック
  - テスト自動実行

## 主な変更点

### ディレクトリ構造の変更

```
旧構造:
~/.claude/
├── hooks/
│   ├── *.py (Pythonスクリプト)
│   └── utils/
├── scripts/
│   └── hooks/
│       └── setup_trinitas_hooks.py
└── settings.json

新構造:
~/.claude/
├── trinitas/
│   └── hooks/
│       ├── core/         (共通ライブラリ)
│       ├── pre-execution/
│       ├── post-execution/
│       └── python/       (オプション)
├── agents/
├── CLAUDE.md
├── TRINITAS-CORE-PROTOCOL.md
└── settings.json
```

### 新しいフック

1. **SessionStart**: セッション開始時のプロトコル注入
2. **PreCompact**: Compact Summary作成時の誘導
3. **既存フックの改善**: Shell Scriptベースで高速化

### Python機能（オプション）

Python機能が必要な場合：

```bash
cd hooks/python
./setup_uv.sh --enhanced --security
```

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください：
https://github.com/apto-as/trinitas-agents/issues