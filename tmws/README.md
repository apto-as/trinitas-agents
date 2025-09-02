# TMWS - Trinitas Memory & Workflow Service

## 概要

TMWS (Trinitas Memory & Workflow Service)は、Trinitas AIエージェントシステムのバックエンドサービスです。
PostgreSQL + pgvectorを基盤とし、メモリ管理とワークフロー管理機能を提供します。

## アーキテクチャ

```
Claude Code Platform (Agents)
         ↓ API
    TMWS Service
         ↓
PostgreSQL + pgvector
```

## 主要機能

- **Memory Management**: ベクトル検索対応のメモリ保存・検索
- **Workflow Management**: エージェント間のタスク連携管理
- **Learning System**: パターン学習と適用
- **API Audit**: 全API呼び出しの監査ログ

## 環境構築

詳細は[TMWS_SETUP_INSTRUCTIONS.md](../TMWS_SETUP_INSTRUCTIONS.md)を参照してください。

### クイックスタート

```bash
# 依存関係のインストール
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# データベースマイグレーション
alembic upgrade head

# 開発サーバー起動
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## プロジェクト構造

```
tmws/
├── src/
│   ├── core/           # 共通機能
│   ├── database/       # DB接続・モデル
│   ├── memory/         # Memory API
│   ├── workflow/       # Workflow API
│   └── main.py         # FastAPIアプリ
├── tests/              # テスト
├── migrations/         # DBマイグレーション
└── .env               # 環境設定
```

## API仕様

### Memory API
- `POST /api/memory/store` - メモリ保存
- `POST /api/memory/recall` - メモリ検索

### Workflow API
- `POST /api/workflow/create` - ワークフロー作成
- `GET /api/workflow/{id}/status` - ステータス取得
- `POST /api/workflow/{id}/task/{task_id}/update` - タスク更新

## セキュリティ

- すべてのエラーメッセージはサニタイズ済み
- SQLインジェクション対策実装
- 入力検証にPydantic使用
- 監査ログ記録

## 開発

```bash
# テスト実行
pytest

# コードフォーマット
black src tests
isort src tests

# 型チェック
mypy src

# リント
ruff src
```

## ライセンス

MIT License