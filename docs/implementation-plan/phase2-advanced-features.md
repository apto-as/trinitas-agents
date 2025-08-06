# Phase 2 実装計画：高度なORCHESTRATOR機能

## 概要
Phase 1で構築した基礎の上に、より高度な協調機能とPython実装を追加します。

## 実装範囲
1. **Cross-Persona Collaboration** - ペルソナ間の協調メカニズム
2. **MCP Coordinator** - 複数MCPサーバーの統合管理
3. **Workflow Generator** - 基礎的なワークフロー生成
4. **Python Migration** - 高度な分析機能のPython実装

## アーキテクチャ

### 1. Cross-Persona Collaboration System

```
hooks/
├── python/
│   ├── persona_coordinator.py      # ペルソナ協調エンジン
│   ├── collaboration_patterns.py   # 協調パターン定義
│   └── conflict_resolver.py       # 対立解決メカニズム
└── post-execution/
    └── 05_persona_harmonizer.sh    # 協調結果の記録
```

#### 機能詳細
- **Primary-Consulting-Validation モデル**
  - Primary: 主導的な意思決定
  - Consulting: 専門的インプット
  - Validation: 品質・セキュリティ検証

- **協調パターン**
  - `springfield + krukai`: 設計と技術の融合
  - `krukai + vector`: セキュアな実装
  - `springfield + vector`: リスクを考慮した設計

- **対立解決**
  - 優先度マトリックス
  - コンテキストベースの判断
  - エスカレーションパス

### 2. MCP Coordinator

```
hooks/
├── python/
│   ├── mcp_coordinator.py         # MCPサーバー調整
│   ├── mcp_cache_manager.py       # キャッシュ管理
│   └── mcp_fallback_handler.py    # フォールバック処理
└── core/
    └── mcp_integration.sh          # シェルスクリプト統合
```

#### 機能詳細
- **マルチサーバー調整**
  - context7 + arxiv の統合検索
  - 結果の統合と重複排除
  - 優先度に基づくサーバー選択

- **キャッシュ戦略**
  - サーバー間共有キャッシュ
  - TTLベースの自動更新
  - パターンベースのプリフェッチ

- **エラーハンドリング**
  - 自動リトライ機構
  - フォールバックチェーン
  - 部分的結果の活用

### 3. Workflow Generator (基礎版)

```
hooks/
├── python/
│   ├── workflow_generator.py       # ワークフロー生成エンジン
│   └── task_dependency_mapper.py   # 依存関係マッピング
└── templates/
    ├── workflow_simple.yaml
    ├── workflow_moderate.yaml
    └── workflow_complex.yaml
```

#### 機能詳細
- **テンプレートベース生成**
  - 複雑度に応じたテンプレート選択
  - 動的なステップ追加
  - 依存関係の自動解決

- **統合ポイント**
  - Phase 1の複雑度検出を活用
  - ドメインに基づくステップ調整
  - TodoWriteとの連携

### 4. Python実装の段階的移行

#### 移行対象
1. **高優先度（即座に移行）**
   - persona_coordinator.py - 複雑な協調ロジック
   - mcp_coordinator.py - 非同期処理が必要

2. **中優先度（必要に応じて）**
   - pattern_analyzer.py - 機械学習の準備
   - resource_predictor.py - 予測的リソース管理

3. **低優先度（将来的に）**
   - learning_engine.py - 適応的学習
   - performance_optimizer.py - 高度な最適化

## 実装手順

### Step 1: Persona Coordinator (Week 1)
1. **collaboration_patterns.py**
   - 基本的な協調パターンの定義
   - Trinitasの3ペルソナ用に最適化

2. **conflict_resolver.py**
   - シンプルな優先度ベースの解決
   - コンテキスト判断の基礎実装

3. **persona_coordinator.py**
   - 協調フローの管理
   - 結果の統合

### Step 2: MCP Coordinator (Week 1-2)
1. **mcp_coordinator.py**
   - 基本的なサーバー選択ロジック
   - 同期的な実行（まずは単純に）

2. **mcp_cache_manager.py**
   - research_cache.pyを拡張
   - クロスサーバーキャッシュ

3. **統合テスト**
   - context7との連携確認
   - エラーハンドリングの検証

### Step 3: Workflow Generator (Week 2)
1. **基本テンプレート作成**
   - YAMLベースのワークフロー定義
   - 3つの複雑度レベル

2. **workflow_generator.py**
   - テンプレート選択ロジック
   - 動的なカスタマイズ

3. **TodoWrite統合**
   - ワークフローからタスクへの変換
   - 進捗追跡の実装

## 設定ファイル

### persona_collaboration.yaml
```yaml
collaboration_patterns:
  design_implementation:
    primary: springfield
    consultants: [krukai]
    validators: [vector]
    
  secure_development:
    primary: krukai
    consultants: [vector]
    validators: [springfield]
    
  system_review:
    primary: springfield
    consultants: [krukai, vector]
    validators: []

conflict_resolution:
  priority_matrix:
    security: 100
    reliability: 90
    performance: 80
    maintainability: 70
    features: 60
```

### mcp_servers.yaml
```yaml
servers:
  context7:
    priority: 1
    timeout: 30
    retry: 3
    cache_ttl: 3600
    
  arxiv:
    priority: 2
    timeout: 60
    retry: 2
    cache_ttl: 86400
    
fallback_chains:
  documentation:
    - context7
    - web_search
    - local_knowledge
```

## テスト計画

### 1. Persona Collaboration Tests
- 協調パターンの動作確認
- 対立解決のテスト
- 統合結果の検証

### 2. MCP Coordinator Tests
- マルチサーバー調整
- キャッシュ効果測定
- エラー時のフォールバック

### 3. Workflow Generator Tests
- テンプレート選択の精度
- 依存関係の正確性
- TodoWrite統合の動作

### 4. Performance Tests
- Python実装の速度比較
- メモリ使用量の監視
- 並行処理の効果測定

## 成功基準

### 機能面
- [ ] 3つのペルソナが協調して動作
- [ ] MCPサーバーの統合管理が機能
- [ ] 基本的なワークフロー生成が可能
- [ ] Python実装部分が正常動作

### 性能面
- [ ] 協調オーバーヘッド < 500ms
- [ ] キャッシュヒット率 > 60%
- [ ] ワークフロー生成 < 3秒
- [ ] メモリ使用量 < 100MB増加

### 品質面
- [ ] テストカバレッジ > 80%
- [ ] エラーハンドリング完備
- [ ] ドキュメント更新完了
- [ ] 後方互換性維持

## リスクと対策

### 技術的リスク
1. **Python/Shell統合の複雑性**
   - 対策: JSON経由のシンプルな通信
   - 段階的な移行

2. **パフォーマンス劣化**
   - 対策: プロファイリングの実施
   - 必要に応じてShell版を維持

### 運用リスク
1. **設定の複雑化**
   - 対策: デフォルト値の提供
   - 設定検証ツールの作成

2. **デバッグの困難さ**
   - 対策: 詳細なログ出力
   - トレーシング機能の追加

## Phase 3への橋渡し

Phase 2で構築した基盤により、Phase 3では以下が可能に：
- Centaureissiサブペルソナの追加
- 機械学習による適応的最適化
- 完全な非同期処理への移行
- エンタープライズ機能の実装