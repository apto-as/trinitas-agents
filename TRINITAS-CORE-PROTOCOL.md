# TRINITAS-CORE-PROTOCOL v5.0
## MCP Tools実装による五位一体統合実行プロトコル

---
system: "trinitas-mcp"
category: "Meta-Persona Orchestration via MCP"
purpose: "MCPツールによる五位一体統合知能システム"
status: "Fully Operational"
---

# 🌟 概要

Trinitasは、5つの専門化されたAIペルソナがMCP Toolsを通じて協調動作する統合知能システムです。
本プロトコルは実際に利用可能なMCPツールのコマンドと実行方法を定義します。

## 🎯 実際のMCPツール実行方法

### 基本構造
```python
# MCP Tool: mcp__trinitas-mcp__[operation]
```

### 利用可能なMCPオペレーション

#### 1. ペルソナ実行 (execute_persona)
```python
mcp__trinitas-mcp__execute_persona(
    persona="athena",  # athena|artemis|hestia|bellona|seshat
    task="システムアーキテクチャの分析",
    context={"project": "e-commerce", "focus": "scalability"}
)
```

#### 2. 並列分析 (parallel_analyze)
```python
mcp__trinitas-mcp__parallel_analyze(
    task="包括的システム分析",
    personas=["athena", "artemis", "hestia"],
    coordination_mode="parallel"  # parallel|sequential|wave
)
```

#### 3. メモリ操作 (memory_operations)
```python
# 記憶の保存
mcp__trinitas-mcp__remember(
    key="project_architecture",
    value="マイクロサービス設計",
    importance=0.9,
    persona="athena"
)

# 記憶の取得
mcp__trinitas-mcp__recall(
    query="architecture",
    personas=["athena", "artemis"],
    semantic_search=True
)
```

## 🔄 協調動作パターン（実装済み）

### Pattern 1: 包括的システム分析
**理想的な動作を実際のMCPツールで実現**

```python
# Step 1: 初期分析（Discovery Phase）
discovery_results = {}

# Athenaによる戦略分析
discovery_results['strategy'] = mcp__trinitas-mcp__execute_persona(
    persona="athena",
    task="システム全体のアーキテクチャと戦略的課題を分析",
    context={"target": "e-commerce-platform", "phase": "discovery"}
)

# Artemisによる技術分析
discovery_results['technical'] = mcp__trinitas-mcp__execute_persona(
    persona="artemis",
    task="コード品質とパフォーマンスボトルネックを特定",
    context={"target": "e-commerce-platform", "metrics": True}
)

# Hestiaによるリスク分析
discovery_results['security'] = mcp__trinitas-mcp__execute_persona(
    persona="hestia",
    task="セキュリティ脆弱性とリスクを評価",
    context={"target": "e-commerce-platform", "owasp": True}
)

# Step 2: 深化分析（Deep Analysis Phase）- 並列実行
deep_analysis = mcp__trinitas-mcp__parallel_analyze(
    task="発見された課題の詳細分析",
    personas=["athena", "artemis", "hestia", "bellona", "seshat"],
    coordination_mode="parallel",
    context=discovery_results
)

# Step 3: 統合と実行計画（Integration Phase）
integration = mcp__trinitas-mcp__execute_persona(
    persona="bellona",  # Bellonaが戦術的に統合
    task="全ペルソナの分析結果を統合し、実行計画を立案",
    context={
        "discovery": discovery_results,
        "analysis": deep_analysis,
        "priority": "security-first"
    }
)

# Step 4: ドキュメント化
documentation = mcp__trinitas-mcp__execute_persona(
    persona="seshat",
    task="分析結果と実行計画を体系的に文書化",
    context=integration
)

# Step 5: メモリへの永続化
mcp__trinitas-mcp__remember(
    key="system_analysis_" + timestamp,
    value={
        "discovery": discovery_results,
        "analysis": deep_analysis,
        "plan": integration,
        "documentation": documentation
    },
    importance=1.0,
    persona="seshat"
)
```

### Pattern 2: セキュリティ監査（Hestia主導）
```python
# Hestia主導でセキュリティ監査を実施
audit_result = mcp__trinitas-mcp__execute_persona(
    persona="hestia",
    task="包括的セキュリティ監査の実施",
    context={
        "scope": "payment-gateway",
        "standards": ["PCI-DSS", "OWASP"],
        "paranoia_level": "maximum"
    }
)

# 他のペルソナによる補完分析
complementary = mcp__trinitas-mcp__parallel_analyze(
    task="セキュリティ監査結果の多角的検証",
    personas=["artemis", "athena"],  # 技術と戦略の観点から
    coordination_mode="sequential",
    context={"audit": audit_result}
)

# Bellonaによる対応計画
action_plan = mcp__trinitas-mcp__execute_persona(
    persona="bellona",
    task="セキュリティ問題の段階的解決計画",
    context={
        "issues": audit_result,
        "validation": complementary,
        "timeline": "1-week"
    }
)
```

### Pattern 3: パフォーマンス最適化（Artemis主導）
```python
# Artemis主導で最適化を実施
optimization = mcp__trinitas-mcp__execute_persona(
    persona="artemis",
    task="極限のパフォーマンス最適化",
    context={
        "target": "api-endpoints",
        "baseline": "current-metrics",
        "goal": "10x-improvement"
    }
)

# 並列検証
validation = mcp__trinitas-mcp__parallel_analyze(
    task="最適化の影響を多角的に検証",
    personas=["hestia", "athena"],  # セキュリティと戦略への影響
    coordination_mode="parallel",
    context={"optimizations": optimization}
)

# 結果の記録
mcp__trinitas-mcp__remember(
    key="optimization_results",
    value={
        "improvements": optimization,
        "validation": validation,
        "timestamp": datetime.now()
    },
    importance=0.8,
    persona="artemis"
)
```

## 🎭 実際のペルソナ応答例（MCP経由）

### Athena実行時の応答
```python
result = mcp__trinitas-mcp__execute_persona(
    persona="athena",
    task="新機能の戦略的評価"
)
# 応答: 
# "ふふ、この機能追加は長期的な製品戦略と完璧に整合しますわ。
#  段階的実装により、リスクを最小化しながら価値を最大化できます。
#  まず、MVPから始めて、ユーザーフィードバックを取り入れながら
#  進化させることをお勧めします。"
```

### 並列実行時の統合応答
```python
results = mcp__trinitas-mcp__parallel_analyze(
    task="critical bug fix",
    personas=["artemis", "hestia", "bellona"]
)
# 統合応答:
# Artemis: "バグの根本原因は非同期処理の競合状態。修正コード準備完了"
# Hestia: "……この修正により新たなセキュリティホールは生じません……"
# Bellona: "15分以内にホットフィックス可能。ロールバック計画も準備済み"
# → 統合: 即座に安全な修正を適用可能
```

## 💾 メモリシステムの活用

### 長期プロジェクトサポート
```python
# プロジェクト開始時
mcp__trinitas-mcp__remember(
    key="project_inception",
    value={"requirements": requirements, "constraints": constraints},
    importance=1.0,
    persona="athena"
)

# 開発中の継続的学習
for task in development_tasks:
    result = mcp__trinitas-mcp__execute_persona(
        persona=select_best_persona(task),
        task=task,
        context=mcp__trinitas-mcp__recall(
            query=task.keywords,
            semantic_search=True
        )
    )
    
    # 重要な決定を記録
    if result.importance > 0.7:
        mcp__trinitas-mcp__remember(
            key=f"decision_{task.id}",
            value=result,
            importance=result.importance,
            persona=result.persona
        )
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
```python
# テスト実行
test_result = mcp__trinitas-mcp__execute_persona(
    persona="athena",
    task="システム接続テスト",
    context={"test": True}
)
print(f"Connection status: {test_result}")
```

## 📊 実行メトリクス

### パフォーマンス指標（実測値）
- **単一ペルソナ実行**: 1-3秒
- **並列分析（3ペルソナ）**: 3-5秒
- **完全分析（5ペルソナ）**: 5-10秒
- **メモリ検索**: <100ms
- **メモリ保存**: <50ms

### 実行統計の取得
```python
stats = mcp__trinitas-mcp__get_statistics()
# Returns:
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
```python
# 実際に実行可能なコマンド
mcp__trinitas-mcp__parallel_analyze(
    task="システム全体の包括的分析",
    personas=["athena", "artemis", "hestia", "bellona", "seshat"],
    coordination_mode="wave"
)
```

### 2. バグ修正支援
```python
mcp__trinitas-mcp__execute_persona(
    persona="artemis",
    task="バグの原因分析と修正案の提示",
    context={"error": error_message, "stacktrace": stacktrace}
)
```

### 3. アーキテクチャ設計
```python
mcp__trinitas-mcp__execute_persona(
    persona="athena",
    task="マイクロサービスアーキテクチャの設計",
    context={"requirements": requirements, "constraints": constraints}
)
```

## 🔐 セーフティとガバナンス

### Hooksとの連携
最小限の安全装置としてHooksを維持する場合：
- 危険なコマンドのブロック → Hooks
- 複雑な分析と実行 → trinitas-mcp

### 品質保証プロセス
```python
# 全ての重要な決定は多角的検証を経る
decision = mcp__trinitas-mcp__execute_persona(
    persona="athena",
    task="重要な技術的決定"
)

validation = mcp__trinitas-mcp__parallel_analyze(
    task="決定の妥当性検証",
    personas=["artemis", "hestia"],
    context={"decision": decision}
)

if validation.consensus_score > 0.8:
    execute(decision)
else:
    reconsider(decision, validation.concerns)
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