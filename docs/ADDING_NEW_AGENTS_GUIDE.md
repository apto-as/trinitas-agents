# 新しいエージェント・ペルソナ追加ガイド

## 📋 概要

このガイドでは、Trinitas システムに新しいエージェント・ペルソナを追加する手順を説明します。
Claude Code の制限により、直接的な新エージェントタイプの追加はできませんが、既存のシステム内で新しいペルソナを統合する方法を解説します。

## 🎯 エージェントの分類

新しいエージェントを追加する前に、以下のいずれかのカテゴリーに分類してください：

### 1. **Core Trinity（意思決定者）**
- システムの中核的な意思決定を行う
- 現在: Springfield、Krukai、Vector
- **追加は推奨されません**（Trinity の一貫性を保つため）

### 2. **Support Personas（専門支援者）**
- 特定の専門領域で Trinity をサポート
- 意思決定権は持たない
- 例: Centaureissi（研究支援）
- **新規追加推奨カテゴリー**

### 3. **Workflow Managers（ワークフロー管理）**
- プロセスやタスクの管理を行う
- 既存: trinitas-coordinator、trinitas-quality、trinitas-workflow

## 🚀 Support Persona 追加手順

### Step 1: ペルソナ設計

#### 1.1 役割定義
```yaml
ペルソナ名: [新しいペルソナ名]
役割: [専門分野・支援内容]
カテゴリー: Support Persona
権限レベル: 支援のみ（意思決定権なし）

専門領域:
  - [専門分野1]
  - [専門分野2]
  - [専門分野3]

Trinity との関係:
  - 報告先: Core Trinity
  - 活性化条件: Trinity が必要と判断した時
  - 提供内容: 専門的な分析・提案
```

#### 1.2 ペルソナプロファイル作成例
```markdown
# [Persona Name] - [Specialty Title]

## Background
- Former Affiliation: [経歴]
- Current Role: Support Specialist for Trinitas-Core
- Specialty: [専門分野]

## Personality Traits
- [特徴1]
- [特徴2]
- [特徴3]

## Communication Style
- [口調や話し方の特徴]
- [よく使うフレーズ]
```

### Step 2: 実装方法（Claude Code 制限対応）

#### 方法A: trinitas-coordinator への統合

1. **trinitas-coordinator.md を編集**
```markdown
## Internal Support Personas
- Centaureissi: Deep Research
- [New Persona]: [Specialty]  # 追加

## [New Persona] Protocol
When [specific condition]:
1. Internally activate [New Persona]
2. [New Persona] provides [specialized analysis]
3. Report findings to Trinity
4. Trinity makes final decision
```

2. **collaboration_patterns.py を更新**
```python
self.persona_roles = {
    # Core Trinity
    "springfield": PersonaRole.TRINITY_CORE,
    "krukai": PersonaRole.TRINITY_CORE,
    "vector": PersonaRole.TRINITY_CORE,
    # Support Personas
    "centaureissi": PersonaRole.RESEARCH_SUPPORT,
    "[new_persona]": PersonaRole.SPECIALIST_SUPPORT  # 追加
}
```

#### 方法B: 専用ワークフローエージェントの作成

1. **新しいワークフローエージェントを作成**
```bash
# trinitas-[specialty].md を作成
cp agents/trinitas-workflow.md agents/trinitas-[specialty].md
```

2. **エージェント定義を編集**
```markdown
description: MUST BE USED for [specialty] tasks requiring 
[New Persona]'s expertise. Coordinates with Trinity for 
final decisions.

## Internal Persona
- [New Persona]: [Specialty] Specialist

## Workflow
1. Receive [specialty] request
2. Activate [New Persona] internally
3. Perform specialized analysis
4. Present findings to Trinity
5. Trinity makes decision
```

### Step 3: ファイル配置

```bash
agents/
├── support/                    # Support Personasディレクトリ
│   ├── centaureissi-researcher.md
│   └── [new-persona]-[specialty].md  # 新規追加
└── workflow/
    └── trinitas-[specialty].md  # 必要に応じて
```

### Step 4: テストと検証

#### 4.1 動作テスト
```python
# テストコマンド例
Task(
    subagent_type="trinitas-coordinator",
    prompt="""
    Trinity requests [New Persona]'s expertise on [topic].
    [New Persona] should analyze and report back to Trinity.
    Trinity will make the final decision.
    """
)
```

#### 4.2 チェックリスト
- [ ] ペルソナの役割が明確に定義されている
- [ ] Trinity との関係性が明確
- [ ] 意思決定権限が適切に制限されている
- [ ] trinitas-coordinator または専用ワークフローで呼び出し可能
- [ ] ドキュメントが更新されている

### Step 5: ドキュメント更新

1. **README.md に追加**
```markdown
## Support Personas
- Centaureissi: Deep Research & Knowledge Synthesis
- [New Persona]: [Specialty Description]  # 追加
```

2. **ARCHITECTURE.md を更新**
```markdown
### Support Layer
専門的な支援を提供するペルソナ：
- Centaureissi（研究）
- [New Persona]（[専門分野]）  # 追加
```

## 📝 実装例：QA-Specialist の追加

### 1. ペルソナ設計
```yaml
ペルソナ名: QA-Specialist
役割: 品質保証・テスト戦略
専門領域:
  - 自動テスト設計
  - 品質メトリクス分析
  - バグ予測とリスク評価
```

### 2. trinitas-coordinator.md への追加
```markdown
## QA-Specialist Protocol
When quality assurance needed:
1. Activate QA-Specialist internally
2. Analyze code quality metrics
3. Design test strategies
4. Report to Trinity with recommendations
5. Trinity decides on implementation
```

### 3. 使用例
```python
Task(
    subagent_type="trinitas-coordinator",
    prompt="""
    Complex system requiring quality assurance.
    Activate QA-Specialist for test strategy.
    Trinity to approve final test plan.
    """
)
```

## ⚠️ 注意事項

### Claude Code の制限
- 新しいエージェントタイプ（subagent_type）は直接追加できません
- 既存の7つのタイプ内で実装する必要があります
- trinitas-coordinator が最も柔軟な統合ポイントです

### ベストプラクティス
1. **意思決定の明確化**: Support Personas は提案のみ、決定は Trinity
2. **役割の重複回避**: 既存ペルソナとの差別化を明確に
3. **段階的導入**: まず小さな機能から始めて拡張
4. **ドキュメント重視**: 使用方法を明確に文書化

## 🔄 将来の拡張性

Claude Code が将来カスタムエージェントをサポートした場合：
1. Support Personas を独立したエージェントタイプに移行
2. 直接的な subagent_type として登録
3. より柔軟な呼び出しが可能に

現在の実装は、この将来的な移行を考慮した設計となっています。

## 📚 参考資料

- [Trinity + Centaureissi v3.0 実装計画](./V3_IMPLEMENTATION_PLAN.md)
- [Trinitas アーキテクチャ](./ARCHITECTURE.md)
- [協調パターン定義](../hooks/python/collaboration_patterns.py)

---

*このガイドは Trinitas v3.0 Practical Implementation の一部です。*
*質問や提案は GitHub Issues でお願いします。*