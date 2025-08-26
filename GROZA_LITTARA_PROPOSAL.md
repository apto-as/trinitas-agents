# Groza(Bellona)・Littara(Seshat) 実装提案

## 🎯 目的
Local LLM並列処理の専門ペルソナとして機能しつつ、Local LLM不在時もフォールバック動作を保証

## 🏗️ 提案アーキテクチャ

### 1. 二重配置戦略

```
agents/
├── athena-strategist.md     # Claude Native
├── artemis-optimizer.md     # Claude Native  
├── hestia-auditor.md        # Claude Native
├── bellona-coordinator.md   # Hybrid (New)
└── seshat-documenter.md     # Hybrid (New)

local-llm/personas/
├── groza-strategist.md      # Local LLM optimized version
└── littara-technician.md    # Local LLM optimized version
```

### 2. 動作モード定義

```yaml
bellona:  # Groza
  primary_role: "Parallel Task Coordinator"
  modes:
    local_llm_available:
      - Local LLMに処理を委譲
      - 並列実行の調整
      - リソース管理
    
    local_llm_unavailable:
      - Claude APIで代替実行
      - タスク分解と順次処理
      - 進捗管理とレポート
    
    offline_mode:
      - 事前定義された応答パターン
      - タスク計画の生成のみ

seshat:  # Littara
  primary_role: "Documentation Specialist"
  modes:
    local_llm_available:
      - 高速ドキュメント生成
      - 詳細な技術文書作成
      
    local_llm_unavailable:
      - Claude APIで実行
      - 要約版ドキュメント生成
      
    offline_mode:
      - テンプレートベース生成
      - 構造化ドキュメントのみ
```

### 3. 実装方法

#### Option A: 条件付きエージェント（推奨）

```markdown
---
name: bellona-coordinator
description: Tactical coordination and parallel task management
tools: [Read, Write, Edit, Bash, TodoWrite]
execution_modes: [local_llm_preferred, claude_fallback, offline_capable]
---

# Bellona - The Tactical Coordinator

## Execution Logic
1. Check Local LLM availability
2. If available → Delegate to local-llm/groza-strategist.md
3. If unavailable → Execute with Claude API
4. If offline → Return structured task plan
```

#### Option B: v35-mcp-tools統合

```python
# v35-mcp-tools/src/hybrid_personas.py
class HybridPersona:
    def execute(self, task):
        if self.local_llm_available():
            return self.local_llm_execute(task)
        elif self.claude_available():
            return self.claude_execute(task)
        else:
            return self.offline_execute(task)
```

## 📊 メリット・デメリット

### メリット
1. **可用性向上**: Local LLM障害時も動作継続
2. **柔軟性**: 状況に応じた最適な実行方法
3. **統合性**: 5人体制として完全統合
4. **コスト最適化**: 可能な限りLocal LLMを使用

### デメリット
1. **複雑性増加**: 実装とメンテナンスが複雑
2. **一貫性リスク**: モードによって応答品質が変化
3. **テスト負荷**: 全モードのテストが必要

## 🎯 推奨実装

### Phase 1: エージェントファイル作成
1. `agents/bellona-coordinator.md` 作成
2. `agents/seshat-documenter.md` 作成
3. 両ファイルにフォールバックロジック記載

### Phase 2: PERSONA_DEFINITIONS更新
```yaml
bellona:
  display_name: Bellona
  developer_name: Groza
  role: Tactical Coordinator
  execution_priority:
    1: local_llm
    2: claude_api
    3: offline_template

seshat:
  display_name: Seshat
  developer_name: Littara
  role: Documentation Specialist
  execution_priority:
    1: local_llm
    2: claude_api
    3: offline_template
```

### Phase 3: 統合テスト
- Local LLM接続時の動作
- Local LLM切断時のフォールバック
- 完全オフライン時の動作

## 🔄 状態遷移図

```
[Task Request]
      ↓
[Check Local LLM]
    ↙    ↘
[Available] [Unavailable]
    ↓          ↓
[Local Execute] [Check Claude]
    ↓          ↙    ↘
    ↓    [Available] [Unavailable]
    ↓        ↓           ↓
    ↓    [Claude Exec] [Template]
    ↓        ↓           ↓
    └────────┴───────────┘
            ↓
        [Result]
```