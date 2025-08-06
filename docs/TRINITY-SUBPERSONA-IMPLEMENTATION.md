# Trinity + Sub-Personas 実装ガイド

## 🚨 重要な制限事項

### Claude Code Task ツールの制限

Claude Code の Task ツールは、以下の事前定義されたエージェントタイプのみをサポートします：

- `general-purpose` - 汎用エージェント
- `trinitas-quality` - 品質保証エージェント  
- `krukai-optimizer` - 技術最適化エージェント
- `trinitas-workflow` - ワークフロー管理エージェント
- `trinitas-coordinator` - 統合調整エージェント
- `springfield-strategist` - 戦略立案エージェント
- `vector-auditor` - セキュリティ監査エージェント

**注意**: `centaureissi-researcher` のような新しいエージェントタイプは認識されません。

## 📋 Sub-Persona 実装方法

### 現在の実装状況

1. **概念レベル**: Trinity + Sub-Personas アーキテクチャは設計完了
2. **ファイル構造**: エージェントファイルは適切に配置済み
3. **制限事項**: Claude Code のTaskツールから直接呼び出せない

### 推奨される使用方法

#### 方法1: General-Purpose エージェントを使用

```python
# Centaureissi の深層研究機能を使う場合
Task(
    subagent_type="general-purpose",
    prompt="""
    You are Centaureissi (センタウレイシー), a Deep Research Specialist.
    As a Sub-Persona reporting to Core Trinity, perform comprehensive research on:
    [研究対象]
    
    Focus on:
    - Deep technical analysis
    - Knowledge synthesis
    - Academic-level exploration
    - Report findings to Trinity for decision
    """
)
```

#### 方法2: 既存エージェントの拡張

Trinitas エージェント内で Sub-Persona を内部的に呼び出す：

```python
# trinitas-coordinator 内で Centaureissi を活用
Task(
    subagent_type="trinitas-coordinator",
    prompt="""
    Coordinate with Centaureissi for deep research on [topic].
    Trinity should make final decisions based on research findings.
    """
)
```

## 🔧 実装の整合性チェック結果

### ✅ 正常に動作するエージェント

**Core Trinity (意思決定者)**:
- `springfield-strategist` ✓
- `krukai-optimizer` ✓
- `vector-auditor` ✓

**Workflow (管理)**:
- `trinitas-coordinator` ✓
- `trinitas-quality` ✓
- `trinitas-workflow` ✓

### ⚠️ 制限付きで動作

**Sub-Personas (専門支援)**:
- `centaureissi-researcher` - ファイルは存在するが、Taskツールから直接呼び出し不可
  - 回避策: general-purpose または trinitas-coordinator 経由で使用

## 🎯 今後の改善案

### 短期的対策（現在実装可能）

1. **プロンプトベースの Sub-Persona 実装**
   - 既存エージェント内でプロンプトにより Sub-Persona の役割を定義
   - Trinity の階層的意思決定を明示的に指示

2. **ドキュメント化**
   - 使用方法を明確に文書化
   - 制限事項と回避策を記載

### 長期的対策（将来的な拡張）

1. **カスタムエージェントのサポート要請**
   - Claude Code チームへの機能要望
   - プラグイン型エージェントシステムの提案

2. **ラッパースクリプトの開発**
   - Sub-Persona を透過的に扱うためのスクリプト
   - 内部的に適切なエージェントタイプにマッピング

## 📝 使用例

### Trinity による意思決定（Sub-Persona サポート付き）

```bash
# 1. 深層研究が必要な場合
# Trinity が Centaureissi の研究を要請
claude Task "general-purpose" "As Centaureissi, research [topic] and report to Trinity"

# 2. Trinity による意思決定
# 研究結果を基に Trinity が判断
claude Task "trinitas-coordinator" "Based on Centaureissi's research, Trinity decides on [action]"
```

## 🔍 検証済み項目

1. **エージェントファイル配置**: ✅ 完了
   - core-trinity/ ディレクトリ
   - sub-personas/ ディレクトリ  
   - workflow/ ディレクトリ

2. **MUST BE USED マーカー**: ✅ 全ファイルに存在

3. **協調パターン更新**: ✅ collaboration_patterns.py 更新済み

4. **プロトコル文書**: ✅ v3.0 作成済み

## 🚀 結論

Trinity + Sub-Personas アーキテクチャは概念的に完成していますが、Claude Code の制限により、Sub-Personas は直接的なエージェントタイプとしては使用できません。代わりに、既存のエージェントタイプを活用し、プロンプトエンジニアリングによって Sub-Persona の機能を実現する必要があります。

この制限は Claude Code 自体の仕様によるものであり、Trinitas システムはこの制限内で最大限の機能を提供するよう設計されています。