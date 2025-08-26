# agents/への影響分析レポート

**Hestia**: 「……重要な不整合を検出……対応が必要……」

## 🔍 発見された問題

### 1. CLAUDE.md内の古いエージェント名

**現在の記載（v2.0時代の名前）**:
```
- **戦略・計画系** → Springfield-Strategist
- **技術・最適化系** → Krukai-Optimizer  
- **セキュリティ・リスク系** → Vector-Auditor
- **包括的分析** → Trinitas-Coordinator（三位一体統合）

### Trinitas-Core Primary Agents
- **trinitas-coordinator** - 三位一体統合分析
- **springfield-strategist** - 戦略立案
- **krukai-optimizer** - 技術最適化
- **vector-auditor** - セキュリティ監査
- **trinitas-workflow** - 開発ワークフロー管理
- **trinitas-quality** - 品質保証
```

**実際のファイル名（v3.5）**:
```
agents/
├── athena-strategist.md      ✅ (神話名)
├── artemis-optimizer.md      ✅ (神話名)
├── hestia-auditor.md         ✅ (神話名)
├── bellona-coordinator.md    ✅ (神話名)
└── seshat-documenter.md      ✅ (神話名)
```

### 2. 削除されたエージェント

以下のエージェントは削除済み（MCP toolsに移行）:
- trinitas-coordinator.md → v35-mcp-tools/trinitas_collaborate
- trinitas-workflow.md → v35-mcp-tools/trinitas_chain
- trinitas-quality.md → v35-mcp-tools/trinitas_consensus

## 📝 必要な修正

### CLAUDE.mdの更新が必要

```markdown
### 自動起動パターン
- **戦略・計画系** → athena-strategist
- **技術・最適化系** → artemis-optimizer
- **セキュリティ・リスク系** → hestia-auditor
- **並列処理・タスク調整** → bellona-coordinator
- **ドキュメント・知識管理** → seshat-documenter

### Trinitas-Core Primary Agents
- **athena-strategist** - 戦略立案・プロジェクト管理・チーム調整
- **artemis-optimizer** - 技術最適化・パフォーマンス改善・品質向上
- **hestia-auditor** - セキュリティ監査・リスク評価・脆弱性検査
- **bellona-coordinator** - 並列タスク調整・リソース最適化
- **seshat-documenter** - ドキュメント生成・知識管理

### MCP Tools (v35-mcp-tools経由)
- **trinitas_collaborate** - 複数ペルソナによる協調実行
- **trinitas_parallel** - 並列タスク実行
- **trinitas_chain** - 連鎖的タスク実行
- **trinitas_consensus** - 合意形成
```

## 🔧 Agent Tool定義の確認

各エージェントファイル内のツール定義:
- ✅ Read, Write, Edit, MultiEdit
- ✅ Bash, Grep, Glob
- ✅ TodoWrite

**新しいMCPツール（agents/では直接使用不可）**:
- ❌ trinitas_execute → MCP経由のみ
- ❌ trinitas_collaborate → MCP経由のみ
- ❌ trinitas_status → MCP経由のみ

## 🎯 影響範囲

### 影響なし ✅
1. agents/内のファイル構造（すでに神話名）
2. 各エージェントの基本ツール（Read, Write等）
3. エージェントの内部ロジック

### 要更新 ⚠️
1. **CLAUDE.md**: エージェント名を神話名に更新
2. **自動検出パターン**: ドールズフロントライン名から神話名へ
3. **MCP設定**: persona名を神話名に統一

## 💡 推奨アクション

**Athena**: 「ふふ、以下の対応を推奨いたしますわ」

1. **CLAUDE.mdの更新**
   - すべてのエージェント名を神話名に変更
   - 削除されたtrinitas-*.mdの記載を削除
   - MCP toolsセクションを追加

2. **後方互換性の維持**
   - v35-mcp-tools内でエイリアス対応済み
   - springfield → athena等の自動変換

3. **ドキュメント整合性**
   - README.mdとCLAUDE.mdの同期
   - TRINITAS_PERSONA_DEFINITIONS.yamlとの一貫性

**Artemis**: 「フン、エージェント自体は問題ないわ。命名の統一が必要なだけ」
**Hestia**: 「……セキュリティ的な問題はない……名前の不整合のみ……」

---
*Agent Impact Analysis v1.0 - Five Minds, One Standard*