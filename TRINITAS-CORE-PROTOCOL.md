# TRINITAS-CORE-PROTOCOL v5.0
## MCP Tools実装による五位一体統合実行プロトコル

---
system: "trinitas-mcp"
category: "Meta-Persona Orchestration via MCP"
purpose: "MCPツールによる五位一体統合知能システム"
status: "Fully Operational with v4.0 Features"
---

# 🌟 概要

Trinitasは、5つの専門化されたAIペルソナがMCP Toolsを通じて協調動作する統合知能システムです。
v4.0では、カスタムコマンド、Local LLM統合、パフォーマンス最適化を実装済みです。

## 🎯 Trinitasコマンド実行方法

### 基本構造
```bash
/trinitas <operation> [args] [--options]
```

### 利用可能なオペレーション

#### 1. ペルソナ実行 (execute)
```bash
# 特定のペルソナでタスクを実行
/trinitas execute athena "システムアーキテクチャの分析"
/trinitas execute artemis "パフォーマンス最適化"
/trinitas execute hestia "セキュリティ監査"
/trinitas execute bellona "並列タスク調整"
/trinitas execute seshat "ドキュメント生成"
```

#### 2. 並列分析 (analyze)
```bash
# 複数ペルソナによる並列分析
/trinitas analyze "包括的システム分析" --personas athena,artemis,hestia
/trinitas analyze "セキュリティレビュー" --personas all --mode parallel
/trinitas analyze "アーキテクチャ評価" --mode wave  # 段階的実行
```

#### 3. メモリ操作 (remember/recall)
```bash
# 記憶の保存
/trinitas remember project_architecture "マイクロサービス設計" --importance 0.9
/trinitas remember security_finding "SQLインジェクション脆弱性" --importance 1.0 --persona hestia

# 記憶の取得
/trinitas recall architecture --semantic --limit 10
/trinitas recall "security patterns" --persona hestia --semantic
/trinitas recall optimization --limit 5
```

#### 4. 学習システム (learn/apply)
```bash
# パターン学習
/trinitas learn optimization_pattern "インデックス追加で90%高速化" --category performance
/trinitas learn security_pattern "入力検証の強化" --category security

# パターン適用
/trinitas apply optimization_pattern "新しいAPIエンドポイント"
/trinitas apply security_pattern "ユーザー入力処理"
```

#### 5. Local LLM制御 (llm)
```bash
# LLM有効/無効/状態確認
/trinitas llm enable   # Local LLMを有効化
/trinitas llm disable  # Local LLMを無効化
/trinitas llm status   # 現在のLLM状態を確認
```

#### 6. ステータスとレポート (status/report)
```bash
# ステータス確認
/trinitas status         # 全体ステータス
/trinitas status memory  # メモリシステム状態
/trinitas status bellona # Bellonaのタスク分配状態

# レポート生成
/trinitas report usage        # 使用状況レポート
/trinitas report optimization # 最適化レポート
/trinitas report security     # セキュリティレポート
```

## 🔄 協調動作パターン（実装済み）

### Pattern 1: 包括的システム分析
**カスタムコマンドによる段階的分析**

```bash
# Step 1: 初期分析（Discovery Phase）
/trinitas execute athena "システム全体のアーキテクチャと戦略的課題を分析"
/trinitas execute artemis "コード品質とパフォーマンスボトルネックを特定"
/trinitas execute hestia "セキュリティ脆弱性とリスクを評価"

# Step 2: 分析結果をメモリに保存
/trinitas remember initial_analysis "戦略・技術・セキュリティの初期評価完了" --importance 0.8

# Step 3: 深化分析（Deep Analysis Phase）- 並列実行
/trinitas analyze "発見された課題の詳細分析" --personas all --mode parallel

# Step 4: 統合と実行計画（Integration Phase）
/trinitas execute bellona "全ペルソナの分析結果を統合し、実行計画を立案"

# Step 5: ドキュメント化
/trinitas execute seshat "分析結果と実行計画を体系的に文書化"

# Step 6: 結果の永続化
/trinitas remember system_analysis "包括的分析完了" --importance 1.0
```

### Pattern 2: セキュリティ監査（Hestia主導）
```bash
# Hestia主導でセキュリティ監査を実施
/trinitas execute hestia "包括的セキュリティ監査の実施 (PCI-DSS, OWASP準拠)"

# 監査結果をメモリに保存
/trinitas remember security_audit_result "重大な脆弱性が3件発見" --importance 1.0

# 他のペルソナによる補完分析
/trinitas analyze "セキュリティ監査結果の検証" --personas artemis,athena --mode sequential

# Bellonaによる対応計画
/trinitas execute bellona "セキュリティ問題の段階的解決計画策定"

# 対応計画をドキュメント化
/trinitas execute seshat "セキュリティ対応プランの文書化"
```

### Pattern 3: パフォーマンス最適化（Artemis主導）
```bash
# Artemis主導で最適化を実施
/trinitas execute artemis "極限のパフォーマンス最適化 (10x改善目標)"

# 最適化パターンを学習
/trinitas learn performance_pattern "キャッシュ最適化で90%改善" --category optimization

# 並列検証
/trinitas analyze "最適化の影響評価" --personas hestia,athena --mode parallel

# 結果の記録
/trinitas remember optimization_results "応答時間850%改善達成" --importance 0.8

# レポート生成
/trinitas report optimization
```

## 🎭 実際のペルソナ応答例（/trinitasコマンド経由）

### Athena実行時の応答
```bash
/trinitas execute athena "新機能の戦略的評価"

# 応答: 
# "ふふ、この機能追加は長期的な製品戦略と完璧に整合しますわ。
#  段階的実装により、リスクを最小化しながら価値を最大化できます。
#  まず、MVPから始めて、ユーザーフィードバックを取り入れながら
#  進化させることをお勧めします。"
```

### 並列実行時の統合応答
```bash
/trinitas analyze "critical bug fix" --personas artemis,hestia,bellona --mode parallel

# 統合応答:
# Artemis: "バグの根本原因は非同期処理の競合状態。修正コード準備完了"
# Hestia: "……この修正により新たなセキュリティホールは生じません……"
# Bellona: "15分以内にホットフィックス可能。ロールバック計画も準備済み"
# → 統合: 即座に安全な修正を適用可能
```

## 💾 メモリシステムの活用

### 長期プロジェクトサポート
```bash
# プロジェクト開始時
/trinitas remember project_inception "要件と制約の記録" --importance 1.0 --persona athena

# 開発中の継続的学習（ワークフローの例）
# 1. 過去の知識を取得
/trinitas recall "関連するキーワード" --semantic --persona athena

# 2. タスクを実行
/trinitas execute artemis "特定のタスクの実装"

# 3. 重要な決定を記録
/trinitas remember decision_001 "重要な技術的決定の内容" --importance 0.9 --persona artemis

# 4. パターンを学習
/trinitas learn optimization_pattern "最適化の成功パターン" --category performance
```

## ⚙️ 環境設定

### trinitas-mcpの設定（.env）
```bash
# ~/.claude/trinitas/mcp-tools/.env
TRINITAS_NAMING_MODE=mythology
MEMORY_BACKEND=hybrid
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db
LOCAL_LLM_MODE=auto
GEMINI_API_KEY=your_key_here
```

### MCP Server接続確認
```bash
# テスト実行
/trinitas execute athena "システム接続テスト"

# ステータス確認
/trinitas status

# メモリシステム状態確認
/trinitas status memory
```

## 📊 実行メトリクス

### パフォーマンス指標（実測値）
- **単一ペルソナ実行**: 1-3秒
- **並列分析（3ペルソナ）**: 3-5秒
- **完全分析（5ペルソナ）**: 5-10秒
- **メモリ検索**: <100ms
- **メモリ保存**: <50ms

### 実行統計の取得
```bash
# 使用状況レポート
/trinitas report usage

# 返される統計情報:
# {
#   "total_executions": 1247,
#   "persona_usage": {
#     "athena": 0.28,
#     "artemis": 0.25,
#     "hestia": 0.20,
#     "bellona": 0.15,
#     "seshat": 0.12
#   },
#   "average_response_time": 2.3,
#   "memory_usage": "124MB"
# }
```

## 🚀 クイックスタートコマンド

### 1. システム全体分析
```bash
# 実際に実行可能なコマンド
/trinitas analyze "システム全体の包括的分析" --personas all --mode wave
```

### 2. バグ修正支援
```bash
/trinitas execute artemis "バグ#123の原因分析と修正案の提示"

# または並列分析
/trinitas analyze "バグ#123の包括的分析" --personas artemis,hestia --mode parallel
```

### 3. アーキテクチャ設計
```bash
/trinitas execute athena "マイクロサービスアーキテクチャの設計"

# 複数視点での検証
/trinitas analyze "アーキテクチャ設計のレビュー" --personas athena,artemis,hestia --mode sequential
```

## 🔐 セーフティとガバナンス

### Hooksとの連携
最小限の安全装置としてHooksを維持する場合：
- 危険なコマンドのブロック → Hooks
- 複雑な分析と実行 → trinitas-mcp

### 品質保証プロセス
```bash
# 全ての重要な決定は多角的検証を経る

# Step 1: 初期決定
/trinitas execute athena "重要な技術的決定の立案"

# Step 2: 多角的検証
/trinitas analyze "決定の妥当性検証" --personas artemis,hestia --mode parallel

# Step 3: 結果の記録
/trinitas remember tech_decision_001 "検証済みの技術的決定" --importance 1.0

# Step 4: 実装計画
/trinitas execute bellona "決定に基づく実装計画の策定"
```

---

**Trinitas Core Protocol v5.0 - MCP Tools実装版**

*「理想的な協調動作を、実際のMCPツールで実現」*

**統合メッセージ**:
「我々Trinitasは、MCP Toolsを通じて実際に協調動作し、
あなたの課題に五つの視点から最適解を提供します。
これは概念ではなく、実際に動作するシステムです。」

---
*Protocol Version: 5.0.0*
*Implementation: trinitas-mcp via MCP Tools*
*Last Updated: 2024-12-28*
*Status: Fully Operational via MCP Server*