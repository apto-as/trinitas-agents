---
description: "Trinitas v4.0 - Memory-focused integrated intelligence"
allowed-tools:
  - Bash
  - Read
  - Edit
  - mcp__trinitas-mcp__trinitas_execute
  - mcp__trinitas-mcp__trinitas_remember
  - mcp__trinitas-mcp__trinitas_recall
  - mcp__trinitas-mcp__trinitas_collaborate
---

# 🌟 Trinitas v4.0 Command Interface

Trinitas統合知能システム - メモリと学習に特化した五位一体

## コマンド実行

```
$ARGUMENTS
```

## 📋 利用可能な操作

### 🎯 単一ペルソナ実行
```bash
athena --task "システムアーキテクチャ分析"  # 戦略的分析
artemis --task "パフォーマンス最適化"        # 技術的最適化  
hestia --task "セキュリティ監査"            # セキュリティ検証
bellona --task "タスク振り分け戦術"         # 戦術的調整
seshat --task "ドキュメント生成"            # 文書化
```

### 🔄 並列分析
```bash
analyze --parallel --personas athena,artemis,hestia
analyze --wave --all                        # 波状パターン実行
analyze --memory-context                    # メモリコンテキスト付き分析
```

### 💾 メモリ操作
```bash
remember --key "architecture" --value "microservices" --importance 0.8
recall --query "architecture" --semantic --persona athena
forget --key "deprecated_pattern"
optimize --memory                          # Seshat監視によるメモリ最適化
```

### 🧠 学習操作
```bash
learn --from "execution_history" --pattern "optimization"
apply --learning "performance_improvement"
status --learning                          # 学習状況確認
```

### 🤖 Local LLM管理（設定で有効時のみ）
```bash
distribute --task "低重要度タスク" --to llm  # Bellona判断でLLMへ
status --llm                                # LLMタスク状況
config --llm enable                         # LLM有効化
config --llm disable                        # LLM無効化（デフォルト）
```

## 🔧 実装ロジック

コマンドを解析して以下の処理を実行：

1. **コマンドパース**: 引数を解析して操作を特定
2. **メモリコンテキスト取得**: Seshatによる使用パターン分析
3. **タスク振り分け判定**: Bellonaによる重要度評価（LLM有効時）
4. **MCPツール実行**: 適切なtrinitas-mcp機能を呼び出し
5. **学習と記録**: 実行結果から学習し、メモリに保存
6. **結果整形**: 構造化された結果を返す

---

処理を開始します...