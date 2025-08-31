# Trinitas v5.0 完全仕様書
## Unified Intelligence System Complete Specification

---

# 📋 開発ルールと規約

## 🚨 厳守事項（MUST FOLLOW）

### 1. ファイル配置規則
```bash
# 作業記録・計画書
./temp/docs/           # 一時的なドキュメント、作業記録、計画書

# テストコード
./tests/               # すべてのテストスクリプト

# 本番コード
./trinitas-mcp/src/    # MCPサーバー実装
./agents/              # ペルソナ定義
./hooks/               # セキュリティフック

# 設定
./config/              # 設定ファイル（.envなど）
```

### 2. 開発サイクル（TDD遵守）
```python
# 1. テスト作成（RED）
def test_new_feature():
    """テストを先に書く"""
    assert feature_function() == expected_result  # FAIL

# 2. 実装（GREEN）
def feature_function():
    """最小限の実装でテストを通す"""
    return expected_result  # PASS

# 3. リファクタリング（REFACTOR）
def feature_function():
    """コードを洗練させる"""
    # 最適化された実装
```

### 3. プロジェクトクリーンアップ規則
- **毎作業終了時**: 不要なファイルを削除
- **コミット前**: `git status`で確認、不要ファイルを除外
- **定期的**: `find . -name "*.pyc" -delete`などでクリーンアップ
- **一時ファイル**: 必ず`./temp/`以下に配置

### 4. セキュリティ規則
- **認証情報**: `.env`ファイルに記載、絶対にコミットしない
- **エラー情報**: `security_utils.py`でサニタイズ
- **入力検証**: すべての入力を検証してから処理
- **ログ**: センシティブ情報を含めない

### 5. コーディング標準
```python
# Pythonコーディング規約
- PEP 8準拠
- Type hints必須
- Docstring必須（Google Style）
- 非同期処理優先（async/await）
```

### 6. ドキュメント規則
```markdown
# ドキュメント作成規則
- README.md: プロジェクト概要
- API文書: OpenAPI 3.0形式
- 設計文書: Markdown形式
- 作業記録: ./temp/docs/配下
```

---

# 🏗️ システムアーキテクチャ

## 1. 概要

Trinitasは、5つの専門化されたAIペルソナが協調動作する統合知能システムです。

### システム構成図
```
┌─────────────────────────────────────────────────────┐
│                  Claude Desktop                       │
│                    (User Interface)                   │
└────────────────────┬───────────────────────────────┘
                      │ MCP Protocol
┌────────────────────┴───────────────────────────────┐
│              Trinitas MCP Server v5.0               │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │            Core Orchestrator (Hera)          │  │
│  └──────────────────┬───────────────────────────┘  │
│                      │                              │
│  ┌──────────────────┴───────────────────────────┐  │
│  │              Five Personas System             │  │
│  │                                                │  │
│  │  🏛️ Athena     - Strategic Architect          │  │
│  │  🏹 Artemis    - Technical Perfectionist      │  │
│  │  🔥 Hestia     - Security Guardian            │  │
│  │  ⚔️ Eris       - Distributed Processor        │  │
│  │  📚 Muses      - Memory Architects            │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │           Memory & Learning System            │  │
│  │                                                │  │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │  Redis  │ │ChromaDB  │ │ SQLite   │      │  │
│  │  │(短期)   │ │(ベクトル)│ │(長期)    │      │  │
│  │  └─────────┘ └──────────┘ └──────────┘      │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │            LLM Router & Distribution          │  │
│  │                                                │  │
│  │  Priority 1: Local LLM (when enabled)         │  │
│  │  Priority 2: Claude Code Headless             │  │
│  │  Priority 3: Qwen Code Headless               │  │
│  │  Priority 4: Main Claude (fallback)           │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## 2. コンポーネント詳細

### 2.1 Core Orchestrator (Hera)
**役割**: 全ペルソナの統括と調整
**実装状態**: ✅ 基本実装完了

### 2.2 Five Personas System

#### 🏛️ Athena - Strategic Architect
- **役割**: システム全体の戦略立案
- **実装**: `agents/athena-strategist.md`
- **トリガー**: strategy, planning, architecture, vision

#### 🏹 Artemis - Technical Perfectionist  
- **役割**: コード品質とパフォーマンス最適化
- **実装**: `agents/artemis-optimizer.md`
- **トリガー**: optimization, performance, quality, refactor

#### 🔥 Hestia - Security Guardian
- **役割**: セキュリティ監査とリスク評価
- **実装**: `agents/hestia-auditor.md`
- **トリガー**: security, audit, risk, vulnerability

#### ⚔️ Eris - Distributed Processor
- **役割**: タスク分散とLLMルーティング
- **実装**: `src/eris_distributor.py`
- **トリガー**: parallel, distribute, coordinate

#### 📚 Muses - Memory Architects
- **役割**: メモリ管理とナレッジ整理
- **実装**: `src/muses_monitor.py`
- **トリガー**: memory, knowledge, document, archive

### 2.3 Memory System

#### 階層型メモリアーキテクチャ
```python
class MemoryTier(Enum):
    SHORT_TERM = "short"     # 1時間以内（Redis）
    MEDIUM_TERM = "medium"   # 1週間以内（Redis + SQLite）
    LONG_TERM = "long"       # 永続（SQLite + ChromaDB）
```

#### メモリ優先度システム
```python
class MemoryImportance(Enum):
    CRITICAL = 1.0   # 絶対に忘れてはいけない
    HIGH = 0.8       # 重要な決定・知識
    MEDIUM = 0.5     # 通常の作業記憶
    LOW = 0.3        # 参考情報
    TRIVIAL = 0.1    # 些細な情報
```

### 2.4 LLM Router

#### ルーティング優先順位
1. **重要タスク** → Main Claude
2. **軽量タスク + LocalLLM有効** → Local LLM
3. **軽量タスク + LocalLLM無効** → Claude Code Headless
4. **Claude Code無効** → Qwen Code Headless
5. **全て無効** → Main Claude (fallback)

---

# 📦 実装状態

## ✅ 実装済み機能（v4.0）

### 1. Core Features
- [x] MCP Server基本実装
- [x] 5ペルソナシステム（mock実装）
- [x] カスタムコマンド（/trinitas）
- [x] ハイブリッドメモリシステム
- [x] Local LLM統合
- [x] LRUキャッシュ最適化
- [x] 非同期処理アーキテクチャ

### 2. Memory & Learning
- [x] Redis統合（短期記憶）
- [x] SQLite統合（長期記憶）
- [x] ChromaDB統合（ベクトル検索）
- [x] 重要度スコアリング
- [x] パターン学習システム（基本）

### 3. Distribution & Routing
- [x] Eris分散処理システム
- [x] LLMルーター実装
- [x] ヘッドレスモード自動切替
- [x] ヘルスチェック機能

## 🚧 部分実装（要改善）

### 1. Security
- [ ] 認証・認可システム（0%）
- [ ] データ暗号化（0%）
- [ ] 入力検証（30%）
- [ ] セキュア通信（0%）

### 2. Performance
- [ ] Connection Pool（未実装）
- [ ] ベクトル類似度検索（部分）
- [ ] 高度なパターン認識（未実装）
- [ ] クエリ最適化（理論のみ）

### 3. Documentation
- [ ] API完全仕様書（60%）
- [ ] テスト戦略書（30%）
- [ ] 運用手順書（40%）
- [ ] トラブルシューティング（50%）

## 🔴 未実装機能

### 1. Advanced Features
- [ ] Web Dashboard
- [ ] ナレッジグラフ可視化
- [ ] 高度なオーケストレーション
- [ ] コンセンサス実行

### 2. Enterprise Features
- [ ] マルチテナント対応
- [ ] 監査ログ
- [ ] バックアップ・リストア
- [ ] 高可用性（HA）構成

---

# 🚀 実装計画

## Phase 1: セキュリティ強化（最優先）
**期間**: 1-2週間
**目標**: 本番環境での使用を可能にする

### Week 1: 基本セキュリティ
```python
# 1. 認証システム実装
class AuthenticationSystem:
    async def authenticate(self, token: str) -> bool:
        """JWT/APIキー認証"""
        pass

# 2. 入力検証強化  
class InputValidator:
    def validate(self, input: Any) -> Any:
        """全入力の検証"""
        pass

# 3. データ暗号化
class DataEncryption:
    def encrypt(self, data: str) -> str:
        """AES-256暗号化"""
        pass
```

### Week 2: 高度なセキュリティ
- アクセス制御実装
- 監査ログシステム
- セキュリティテスト

## Phase 2: パフォーマンス最適化
**期間**: 2-3週間
**目標**: 850%改善の実証と更なる最適化

### Week 3-4: Core最適化
```python
# 1. Connection Pool実装
class ConnectionPool:
    async def get_connection(self):
        """効率的な接続管理"""
        pass

# 2. ベクトル検索最適化
class VectorSearch:
    async def search(self, query: str):
        """ChromaDB完全活用"""
        pass
```

### Week 5: 高度な最適化
- クエリ最適化実装
- キャッシュ戦略改善
- 並列処理強化

## Phase 3: 機能完成
**期間**: 3-4週間
**目標**: v5.0としての完全な機能実装

### Week 6-7: ペルソナ実装
- ペルソナロジック実装
- 協調動作システム
- 高度なオーケストレーション

### Week 8-9: UI/UX
- Web Dashboard開発
- 可視化システム
- ユーザビリティ改善

## Phase 4: ドキュメント整備
**期間**: 1-2週間
**目標**: 完全なドキュメント体系

### Week 10: 技術文書
- API完全仕様書
- アーキテクチャ文書
- 開発者ガイド

### Week 11: 運用文書
- インストールガイド
- 運用手順書
- トラブルシューティング

---

# 🎯 成功指標（KPI）

## 技術指標
| 指標 | 現在値 | 目標値 | 期限 |
|-----|--------|--------|------|
| セキュリティスコア | 0.03/10 | 8.0/10 | 2週間 |
| コード品質 | 45/100 | 85/100 | 4週間 |
| テストカバレッジ | 60% | 95% | 3週間 |
| 応答時間 | 300ms | <100ms | 4週間 |
| メモリ使用量 | 124MB | <80MB | 5週間 |

## ビジネス指標
| 指標 | 現在値 | 目標値 | 期限 |
|-----|--------|--------|------|
| ドキュメント完成度 | 70% | 95% | 6週間 |
| API安定性 | 85% | 99.9% | 8週間 |
| ユーザー満足度 | - | 4.5/5.0 | 10週間 |

---

# 📝 設定仕様

## 環境変数（.env）
```bash
# Core Settings
TRINITAS_MODE=memory_focused
TRINITAS_VERSION=5.0

# Memory Backends
MEMORY_BACKEND=hybrid
REDIS_URL=redis://localhost:6379
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./sqlite_data.db

# LLM Settings
LOCAL_LLM_ENABLED=false
LOCAL_LLM_ENDPOINT=http://localhost:1234/v1
LOCAL_LLM_MODEL=auto

# Headless Mode (auto-enabled when LOCAL_LLM is off)
CLAUDE_CODE_HEADLESS_ENDPOINT=http://localhost:8080/v1/claude
QWEN_CODE_HEADLESS_ENDPOINT=http://localhost:8081/v1/qwen

# Performance
CACHE_MAX_SIZE=1000
CACHE_MAX_MEMORY_MB=100
DB_MAX_CONNECTIONS=10

# Security (to be implemented)
JWT_SECRET_KEY=<generate-secure-key>
API_KEY=<generate-api-key>
ENCRYPTION_KEY=<generate-encryption-key>

# Monitoring
LOG_LEVEL=INFO
LOG_FILE=./logs/trinitas.log
METRICS_ENABLED=true
```

## MCP Server設定
```json
{
  "mcpServers": {
    "trinitas": {
      "command": "uv",
      "args": ["run", "trinitas"],
      "cwd": "/Users/apto-as/.claude/trinitas/mcp-tools/"
    }
  }
}
```

---

# 🔧 API仕様

## カスタムコマンド

### 基本実行
```bash
/trinitas execute <persona> "<task>"
```

### 並列分析
```bash
/trinitas analyze "<task>" --personas all --mode parallel
```

### メモリ操作
```bash
/trinitas remember <key> <value> --importance 0.9
/trinitas recall <query> --semantic --limit 10
```

### 学習システム
```bash
/trinitas learn <pattern> "<description>"
/trinitas apply <pattern> "<task>"
```

### ステータス確認
```bash
/trinitas status [memory|eris|muses|all]
/trinitas report [usage|optimization|security]
```

## MCP Tools API

### memory_store
```python
async def memory_store(
    key: str,
    value: Any,
    persona: str = "general",
    importance: float = 0.5,
    metadata: Optional[Dict] = None
) -> str:
    """メモリに情報を保存"""
```

### memory_recall
```python
async def memory_recall(
    query: str,
    semantic: bool = False,
    persona: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """メモリから情報を取得"""
```

### execute_with_memory
```python
async def execute_with_memory(
    persona: str,
    task: str,
    use_llm: Optional[bool] = None,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """メモリ強化実行"""
```

---

# 🐛 既知の問題と対策

## Critical Issues

### 1. セキュリティ脆弱性
**問題**: 認証・認可システムが未実装
**影響**: 誰でもシステムにアクセス可能
**対策**: Phase 1で最優先実装

### 2. Connection Pool未実装
**問題**: `_create_connection`が`return None`
**影響**: データベース接続が機能しない
**対策**: 即座に実装（15分で修正可能）

### 3. ベクトル検索未実装
**問題**: ChromaDBの機能が未活用
**影響**: セマンティック検索が機能しない
**対策**: Phase 2で実装

## Non-Critical Issues

### 1. ドキュメント不整合
**問題**: バージョン表記の不一致
**影響**: 混乱を招く可能性
**対策**: 統一作業実施

### 2. テストカバレッジ不足
**問題**: 60%のカバレッジ
**影響**: バグ検出率低下
**対策**: TDDの徹底

---

# 📚 参照資料

## 内部ドキュメント
- [README.md](./README.md)
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- [TRINITAS_PERSONA_DEFINITIONS.yaml](./TRINITAS_PERSONA_DEFINITIONS.yaml)

## 外部リソース
- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Redis Documentation](https://redis.io/docs)
- [ChromaDB Documentation](https://www.trychroma.com/docs)

---

# 🎯 次のアクション

1. **即座に実行（今日中）**
   - [ ] Connection Pool実装
   - [ ] 基本的な認証システム実装
   - [ ] セキュリティテスト作成

2. **今週中に実行**
   - [ ] 入力検証強化
   - [ ] データ暗号化実装
   - [ ] ドキュメント統一

3. **来週までに実行**
   - [ ] ベクトル検索実装
   - [ ] パフォーマンステスト
   - [ ] API仕様書完成

---

**Document Version**: 1.0.0
**Last Updated**: 2025-08-31
**Status**: DRAFT - Under Review
**Author**: Trinitas Core Team (Athena, Artemis, Hestia, Eris, Muses)

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|----------|--------|
| 1.0.0 | 2025-08-31 | 初版作成 | Trinitas Team |

---

**END OF SPECIFICATION**