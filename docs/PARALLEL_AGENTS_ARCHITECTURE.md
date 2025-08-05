# Trinitas-Core 並列サブエージェント アーキテクチャ設計

## 概要

Trinitas-Core並列サブエージェントシステムは、Springfield、Krukai、Vectorの3つの専門エージェントを並列実行し、その結果を統合することで、より高速で包括的な分析と実装を実現します。

## アーキテクチャ

### 1. コンポーネント構成

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code                          │
│                  (メインコーディネーター)                   │
└────────────────────┬───────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   Trinitas Protocol     │
        │   Injector (Hooks)      │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼──────┐  ┌─────▼─────┐  ┌──────▼────┐
│Springfield│  │  Krukai   │  │  Vector   │
│Strategist │  │ Optimizer │  │ Auditor   │
└───┬──────┘  └─────┬─────┘  └──────┬────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
            ┌────────▼────────┐
            │ Result Integrator│
            │    (Hooks)       │
            └─────────────────┘
```

### 2. 実行フロー

#### Phase 1: タスク分解
```javascript
// trinitas-coordinator がタスクを分析し、並列実行可能な部分を特定
const task = "新しいAPIエンドポイントの実装";
const parallelTasks = {
  strategic: "APIの全体設計とインターフェース定義",
  technical: "実装の最適化とパフォーマンス考慮",
  security: "認証・認可とセキュリティ脆弱性チェック"
};
```

#### Phase 2: 並列実行
```javascript
// 単一メッセージで複数エージェントを起動
<function_calls>
<invoke name="Task">
  <parameter name="description">API設計</parameter>
  <parameter name="subagent_type">springfield-strategist</parameter>
  <parameter name="prompt">RESTful API設計: ${parallelTasks.strategic}</parameter>
</invoke>
<invoke name="Task">
  <parameter name="description">実装最適化</parameter>
  <parameter name="subagent_type">krukai-optimizer</parameter>
  <parameter name="prompt">パフォーマンス分析: ${parallelTasks.technical}</parameter>
</invoke>
<invoke name="Task">
  <parameter name="description">セキュリティ監査</parameter>
  <parameter name="subagent_type">vector-auditor</parameter>
  <parameter name="prompt">セキュリティ評価: ${parallelTasks.security}</parameter>
</invoke>
</function_calls>
```

#### Phase 3: 結果統合
SubagentStopフックを使用して各エージェントの完了を検知し、結果を統合。

### 3. Hooksの活用

#### 3.1 SessionStart - プロトコル注入
```bash
# trinitas_protocol_injector.sh
# セッション開始時にTrinitas-Coreプロトコルを読み込み
# 全エージェントが一貫した行動原則に従うことを保証
```

#### 3.2 PreToolUse - 並列タスク準備
```python
# prepare_parallel_tasks.py
def prepare_parallel_execution(tool_input):
    if is_complex_task(tool_input):
        return {
            "parallel_mode": True,
            "task_distribution": distribute_to_agents(tool_input)
        }
```

#### 3.3 SubagentStop - 個別結果キャプチャ
```bash
# capture_subagent_result.sh
# 各サブエージェントの結果を一時ファイルに保存
echo "$CLAUDE_SUBAGENT_RESULT" > "/tmp/trinitas_${CLAUDE_SESSION_ID}_${SUBAGENT_TYPE}.json"
```

#### 3.4 PostToolUse - 結果統合
```python
# integrate_parallel_results.py
def integrate_results():
    results = load_all_subagent_results()
    conflicts = detect_conflicts(results)
    return merge_with_priority(results, conflicts)
```

#### 3.5 PreCompact - コンテキスト保存
```bash
# 並列実行の結果と決定理由を要約に含める
enhance_compact_summary() {
    echo "Preserve parallel analysis results:"
    echo "- Strategic decisions by Springfield"
    echo "- Technical optimizations by Krukai"
    echo "- Security assessments by Vector"
}
```

### 4. 実装詳細

#### 4.1 並列度の制御
```python
MAX_PARALLEL_AGENTS = 3
TIMEOUT_PER_AGENT = 30  # seconds

def get_optimal_parallelism(task_complexity, system_load):
    if task_complexity == "high" and system_load < 0.7:
        return MAX_PARALLEL_AGENTS
    elif task_complexity == "medium":
        return 2
    else:
        return 1  # Sequential execution for simple tasks
```

#### 4.2 結果の優先順位
```python
PRIORITY_MATRIX = {
    "security_critical": ["vector", "krukai", "springfield"],
    "performance_critical": ["krukai", "vector", "springfield"],
    "user_experience": ["springfield", "krukai", "vector"],
    "default": ["springfield", "krukai", "vector"]
}
```

#### 4.3 エラーハンドリング
```python
def handle_partial_failure(results):
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]
    
    if len(successful) >= 2:
        # 2つ以上成功していれば続行
        return integrate_partial_results(successful)
    else:
        # フォールバック: trinitas-coordinatorで統合分析
        return fallback_to_coordinator()
```

### 5. 設定例

#### settings.json
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/core/trinitas_protocol_injector.sh"
      }]
    }],
    "PreToolUse": [{
      "matcher": "Task",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/parallel/prepare_parallel_tasks.sh"
      }]
    }],
    "SubagentStop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/parallel/capture_subagent_result.sh"
      }]
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/trinitas/hooks/parallel/integrate_final_results.sh"
      }]
    }]
  }
}
```

### 6. 利点

1. **高速化**: 独立したタスクを並列実行
2. **包括性**: 3つの視点から同時に分析
3. **品質向上**: 専門性を活かした深い分析
4. **一貫性**: プロトコル注入による統一された行動

### 7. 制限事項と対策

1. **コンテキスト共有**: 各エージェントは独立したコンテキスト
   - 対策: 共通プロトコルと結果統合メカニズム

2. **API制限**: 同時実行数の上限
   - 対策: 動的な並列度調整

3. **複雑性**: 結果の統合ロジック
   - 対策: 明確な優先順位マトリックス

### 8. 今後の拡張

1. **動的エージェント選択**: タスクに応じて最適なエージェントを選択
2. **カスケード実行**: 前のエージェントの結果を次に渡す
3. **学習機能**: 過去の並列実行パターンから最適化