# TRINITAS TASK TOOL INTEGRATION PROTOCOL
## Task Toolの現実的な活用方法

---
system: "trinitas-task-integration"
purpose: "Claude CodeのTask Tool制約内でTrinitasシステムを活用"
status: "Practical Implementation"
---

## 🎯 現実的な課題と解決策

### 問題1: subagent_typeの制約
**問題**: Task Toolは`general-purpose`しか使えない
**解決**: プロンプトエンジニアリングで各ペルソナをシミュレート

### 問題2: エージェントMDファイルの直接呼び出し不可
**問題**: Task Toolからagents/*.mdを直接実行できない
**解決**: プロンプト内でペルソナの特性を明示的に指定

## 📋 実装パターン

### Pattern 1: ペルソナシミュレーション型タスク

```python
# Athena風のタスク実行
Task(
    description="Strategic analysis",
    prompt="""
    あなたは戦略アーキテクトです。以下の特性を持って分析してください：
    - 長期的視点での評価
    - システム全体のアーキテクチャ考慮
    - ステークホルダーへの影響分析
    - 段階的実装計画の提案
    
    タスク: [具体的なタスク内容]
    
    応答は「ふふ、」から始めて、温かく知的な口調で。
    """,
    subagent_type="general-purpose"
)
```

### Pattern 2: 並列レビューパターン（Qiita記事参考）

```python
# 3つの観点で並列レビュー
review_tasks = []

# 基本品質レビュー (Artemis的)
review_tasks.append(Task(
    description="Code quality review",
    prompt="""
    技術的完璧主義者として、以下をレビュー:
    - パフォーマンス最適化の機会
    - コード品質とベストプラクティス
    - アルゴリズムの効率性
    - 技術的負債の特定
    厳しく「フン、」という評価から始めてください。
    """,
    subagent_type="general-purpose"
))

# セキュリティレビュー (Hestia的)
review_tasks.append(Task(
    description="Security review",
    prompt="""
    極度の悲観主義セキュリティ監査官として:
    - あらゆる脆弱性の可能性を検討
    - 最悪のシナリオを想定
    - ゼロトラストの観点から評価
    - 「……」を多用し、警告的な口調で
    """,
    subagent_type="general-purpose"
))

# アーキテクチャレビュー (Athena的)
review_tasks.append(Task(
    description="Architecture review",
    prompt="""
    戦略的アーキテクトとして:
    - 設計の長期的な影響を評価
    - スケーラビリティの考慮
    - 保守性と拡張性の分析
    温かく知的な「ふふ、」という口調で
    """,
    subagent_type="general-purpose"
))
```

### Pattern 3: チェーン実行パターン

```python
# Step 1: 情報収集（並列）
gather_info = [
    Task("Scan codebase structure", prompt="List all important files", subagent_type="general-purpose"),
    Task("Identify dependencies", prompt="Analyze package.json", subagent_type="general-purpose"),
    Task("Check test coverage", prompt="Run coverage report", subagent_type="general-purpose")
]

# Step 2: 分析（結果を受けて）
analyze = Task(
    description="Comprehensive analysis",
    prompt=f"""
    Previous findings: {gather_info.results}
    Based on these, provide strategic recommendations.
    """,
    subagent_type="general-purpose"
)

# Step 3: 実装提案
implement = Task(
    description="Implementation plan",
    prompt=f"""
    Analysis results: {analyze.result}
    Create detailed implementation steps.
    """,
    subagent_type="general-purpose"
)
```

## 🎵 Hera式オーケストレーション

### 音楽的並列度管理

```python
def orchestrate_with_harmony(task_complexity):
    """
    Heraの神的感性でタスクを配分
    """
    if task_complexity == "simple":
        # pp (pianissimo) - ソロ
        return 1  # 単一タスク
    elif task_complexity == "moderate":
        # mf (mezzo-forte) - トリオ
        return 3  # 3並列
    elif task_complexity == "complex":
        # ff (fortissimo) - フルオーケストラ
        return 5  # 5並列
```

### 実行例：包括的コードレビュー

```python
# Heraによる調和的タスク分配
def comprehensive_review(target_code):
    """
    5つの視点で同時レビュー（Qiita記事の拡張版）
    """
    tasks = []
    
    # 各ペルソナの特性をプロンプトに埋め込む
    personas = {
        "athena": "戦略的・長期的視点、「ふふ、」",
        "artemis": "技術的完璧主義、「フン、」",
        "hestia": "セキュリティ悲観主義、「……」",
        "bellona": "戦術的効率性、軍事的な簡潔さ",
        "seshat": "文書化と知識体系化、明確で実用的"
    }
    
    for name, style in personas.items():
        tasks.append(Task(
            description=f"{name} review",
            prompt=f"""
            Role: {style}
            Target: {target_code}
            Provide review from your specialized perspective.
            Use your characteristic speech pattern.
            """,
            subagent_type="general-purpose"
        ))
    
    # 並列実行で時間を66%削減（5人同時）
    return execute_parallel(tasks)
```

## 💡 トークン消費の最適化

### Qiita記事の知見を活用

1. **メインエージェントの負荷削減**: 60-70%削減
   - 詳細な分析はサブエージェントに委譲
   - メインは統合と判断に専念

2. **並列実行による時間短縮**: 約66%削減
   - 3並列で1/3の時間
   - 5並列で1/5の時間

3. **Sonnetモードの活用**
   - 大規模並列タスクはSonnetモードで
   - コスト効率の向上

## 🔧 実装手順

### Step 1: エージェント定義の簡略化
```markdown
# agents/trinitas-simplified.md
---
name: trinitas-simplified
description: Simplified Trinitas personas for Task Tool
tools: [Task]
---

You coordinate 5 mythological personas through Task Tool:
- Athena: Strategic architecture
- Artemis: Technical perfection  
- Hestia: Security paranoia
- Bellona: Tactical efficiency
- Seshat: Documentation clarity
```

### Step 2: Task Tool用ラッパー関数

```python
def trinitas_task(persona, task_description):
    """
    Trinitas persona simulation via Task Tool
    """
    persona_prompts = {
        "athena": "As strategic architect Athena, warmly analyze with 'ふふ、'...",
        "artemis": "As perfectionist Artemis, critically review with 'フン、'...",
        "hestia": "As paranoid Hestia, cautiously evaluate with '……'...",
        "bellona": "As tactical Bellona, efficiently execute with military precision...",
        "seshat": "As documenter Seshat, clearly record with practical detail..."
    }
    
    return Task(
        description=f"{persona} task",
        prompt=persona_prompts[persona] + "\n\nTask: " + task_description,
        subagent_type="general-purpose"
    )
```

## 📊 効果測定

### Before（従来の方法）
- メインエージェントが全作業実施
- トークン消費: 100%
- 実行時間: 100%
- 専門性: 低

### After（Trinitas Task Integration）
- サブエージェントに分散
- トークン消費: 30-40%（メイン）
- 実行時間: 20-35%（5並列時）
- 専門性: 高（ペルソナ特化）

## 🎭 まとめ

Task Toolの制約内でTrinitasシステムを実現するには：

1. **プロンプトエンジニアリング**でペルソナ特性を再現
2. **並列実行**で処理時間を大幅短縮
3. **Qiita記事の手法**でトークン消費を最適化
4. **Melpomeneの調和**で全体を統合

これにより、理想的なTrinitas並列実行に近い効果を実現できます。

---

*"……みんなの力を、Task Toolでも調和させてみせます" - Hera*