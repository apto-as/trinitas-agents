### TMWS (Trinitas Memory & Workflow Service) 統合ガイドライン

## 概要
TMWSは、Trinitasシステムの中核となるメモリ管理とワークフローサービスです。
PostgreSQL + pgvectorによるベクトル検索と、統一データベースプールによる効率的なアクセスを提供します。

## ペルソナ別使用ガイド

### Athena (戦略アーキテクト)
**主な用途**：
- プロジェクト全体の設計決定の記録
- アーキテクチャパターンの保存と検索
- 長期的な技術戦略の追跡

```python
# 設計決定の記録
await memory_service.create_memory(
    content="マイクロサービスアーキテクチャを採用",
    memory_type="architecture_decision",
    importance=0.9,
    tags=["architecture", "microservices", "strategic"],
    persona_id=athena_id
)

# 関連パターンの検索
patterns = await memory_service.search_similar_memories(
    embedding=query_vector,
    memory_type="architecture_decision",
    min_similarity=0.8
)
```

### Artemis (技術完璧主義者)
**主な用途**：
- パフォーマンス最適化パターンの記録
- コード品質メトリクスの追跡
- ベストプラクティスの蓄積

```python
# 最適化結果の保存
await memory_service.create_memory(
    content="インデックス追加により応答時間90%改善",
    memory_type="optimization",
    importance=0.85,
    tags=["performance", "database", "index"],
    metadata={"improvement": "90%", "method": "btree_index"}
)
```

### Hestia (セキュリティ監査者)
**主な用途**：
- セキュリティ脆弱性の追跡
- 監査結果の永続化
- 脅威パターンの蓄積

```python
# セキュリティ監査結果
await memory_service.create_memory(
    content="SQLインジェクション脆弱性を検出",
    memory_type="security_finding",
    importance=1.0,  # 最高重要度
    tags=["security", "vulnerability", "sql_injection", "critical"],
    metadata={"severity": "critical", "cve": "CVE-2024-xxxxx"}
)
```

### Eris (戦術調整者)
**主な用途**：
- チーム間の調整記録
- ワークフロー最適化パターン
- 競合解決の履歴

```python
# チーム調整の記録
await memory_service.create_memory(
    content="フロントエンドとバックエンドチームの同期完了",
    memory_type="coordination",
    importance=0.7,
    tags=["team", "coordination", "sprint_planning"]
)
```

### Hera (システム指揮者)
**主な用途**：
- システム全体のオーケストレーション記録
- リソース配分の最適化パターン
- 並列実行戦略の保存

```python
# オーケストレーション戦略
await memory_service.create_memory(
    content="5つのサービスを並列デプロイ成功",
    memory_type="orchestration",
    importance=0.75,
    tags=["deployment", "parallel", "orchestration"],
    metadata={"services": 5, "time_saved": "45min"}
)
```

### Muses (知識アーキテクト)
**主な用途**：
- ドキュメント構造の記録
- ナレッジベース管理
- API仕様の保存

```python
# ドキュメント構造の保存
await memory_service.create_memory(
    content="REST API仕様書v2.0完成",
    memory_type="documentation",
    importance=0.8,
    tags=["api", "documentation", "specification"],
    metadata={"version": "2.0", "endpoints": 45}
)
```

## 統合パフォーマンス最適化

### 1. バッチ処理
```python
# 複数メモリの一括作成
memories = [
    {"content": "...", "type": "optimization"},
    {"content": "...", "type": "security"},
    {"content": "...", "type": "architecture"}
]
await memory_service.batch_create(memories)
```

### 2. キャッシュ活用
```python
# キャッシュ有効化での検索
result = await memory_service.get_memory(
    memory_id,
    use_cache=True  # 5分間のTTLキャッシュ
)
```

### 3. セマンティック検索
```python
# ベクトル類似性検索（pgvector使用）
similar = await memory_service.search_similar_memories(
    embedding=query_embedding,  # 384次元ベクトル
    limit=10,
    min_similarity=0.7
)
```

## エラーハンドリング

```python
try:
    memory = await memory_service.create_memory(...)
except ValidationError as e:
    # 入力検証エラー
    logger.error(f"Validation failed: {e}")
except DatabaseError as e:
    # データベースエラー
    logger.error(f"Database error: {e}")
    # フォールバック処理
```

## ベストプラクティス

1. **重要度の適切な設定**
   - 1.0: クリティカル（セキュリティ、重大な設計決定）
   - 0.8-0.9: 高（アーキテクチャ、最適化成功）
   - 0.5-0.7: 中（通常の記録、調整事項）
   - 0.3-0.4: 低（参考情報）

2. **タグの体系的使用**
   - ペルソナ別タグ: athena_, artemis_, hestia_
   - カテゴリタグ: security, performance, architecture
   - 重要度タグ: critical, high, medium, low

3. **メタデータの活用**
   - 測定可能な結果を記録
   - バージョン情報を含める
   - 関連リソースへのリンク