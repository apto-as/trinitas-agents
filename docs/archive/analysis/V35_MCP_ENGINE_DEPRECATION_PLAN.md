# v35-mcp-engine 廃止計画

**Athena**: 「ふふ、v35-mcp-engineを段階的に廃止する計画を立案いたしますわ」

## 📅 廃止スケジュール

### Phase 1: 即座の対応（今すぐ実行可能）

#### 1.1 v35-mcp-tools の自己完結化

**ファイル**: `v35-mcp-tools/src/core/engine_client.py`

```python
# 変更前
class MCPEngineClient:
    def __init__(self, config: Optional[EngineClientConfig] = None):
        self.config = config or EngineClientConfig.from_env()
        self.session = None
        self.engine_available = False

# 変更後
class MCPEngineClient:
    def __init__(self, config: Optional[EngineClientConfig] = None):
        self.config = config or EngineClientConfig.from_env()
        self.session = None
        # 常にスタンドアロンモードで動作
        self.engine_available = False
        self.standalone_mode = True
        logger.info("Engine client running in standalone mode (engine deprecated)")
```

#### 1.2 環境変数の更新

**ファイル**: `v35-mcp-tools/config/claude_mcp_settings.json`

```json
{
  "mcpServers": {
    "trinitas": {
      "command": "uv",
      "args": ["run", "trinitas-server"],
      "env": {
        "TRINITAS_MODE": "mythology",
        "TRINITAS_NAMING": "mythology",
        "AUTO_DETECT": "true",
        "ENGINE_MODE": "standalone",  // 追加
        "USE_ENGINE": "false"          // 追加
      }
    }
  }
}
```

### Phase 2: 機能の内部化（1週間以内）

#### 2.1 オーケストレーション機能の移植

**新規ファイル**: `v35-mcp-tools/src/core/local_orchestrator.py`

```python
"""
Local orchestration without external engine
"""

class LocalOrchestrator:
    """Execute tasks locally without engine dependency"""
    
    async def execute_parallel(self, tasks: List[Dict]):
        """Execute tasks in parallel locally"""
        results = []
        for task in tasks:
            # ローカル実行
            result = await self._execute_local(task)
            results.append(result)
        return results
    
    async def execute_chain(self, chain: List[Dict]):
        """Execute tasks in sequence locally"""
        context = {}
        for step in chain:
            result = await self._execute_local(step, context)
            context.update(result)
        return context
```

#### 2.2 engine_client の簡素化

```python
class MCPEngineClient:
    """Simplified client without engine dependency"""
    
    async def execute_task(self, persona, task, context=None):
        # 常にローカル実行
        from .local_orchestrator import LocalOrchestrator
        orchestrator = LocalOrchestrator()
        return await orchestrator.execute_task(persona, task, context)
    
    async def get_engine_status(self):
        # 常に固定のステータスを返す
        return {
            "status": "standalone",
            "engine": "deprecated",
            "mode": "local",
            "message": "Engine has been deprecated. Running in standalone mode."
        }
```

### Phase 3: ドキュメント更新（2週間以内）

#### 3.1 README.md の更新

```markdown
## Architecture (v3.5.1)

### Simplified Architecture (Engine Deprecated)

```
┌──────────────────────────────┐
│     Claude Code              │
│                              │
└──────────┬───────────────────┘
           │ MCP Protocol
           ↓
┌──────────────────────────────┐
│   v35-mcp-tools              │
│   (Standalone Server)        │
│                              │
│   • Direct Execution         │
│   • Local Orchestration      │
│   • No External Dependencies │
└──────────────────────────────┘
```

### Migration from v3.5.0

If you were using v35-mcp-engine, no action required. 
The system now runs in standalone mode automatically.
```

#### 3.2 CHANGELOG.md の作成

```markdown
# Changelog

## [3.5.1] - 2024-XX-XX

### Changed
- **BREAKING**: v35-mcp-engine deprecated in favor of standalone mode
- v35-mcp-tools now self-contained with local orchestration
- Simplified architecture for better performance and maintainability

### Removed
- v35-mcp-engine directory and all its components
- External engine dependencies
- Redis state management
- Docker configurations for engine

### Migration Guide
1. Remove any engine-related configuration
2. Update v35-mcp-tools to latest version
3. System will automatically run in standalone mode
```

### Phase 4: クリーンアップ（3週間以内）

#### 4.1 削除対象ファイル/ディレクトリ

```bash
# 削除スクリプト
#!/bin/bash
echo "Removing deprecated v35-mcp-engine..."

# バックアップ作成
tar -czf v35-mcp-engine-backup-$(date +%Y%m%d).tar.gz v35-mcp-engine/

# 削除
rm -rf v35-mcp-engine/

# 不要な依存関係を削除
# requirements.txtから以下を削除:
# - fastapi
# - uvicorn
# - redis

echo "✅ v35-mcp-engine has been removed"
echo "📦 Backup saved as v35-mcp-engine-backup-*.tar.gz"
```

#### 4.2 設定ファイルのクリーンアップ

削除対象:
- `.env`内のENGINE関連変数
- `docker-compose.yml`のengine関連サービス
- CI/CD設定のengine関連ステップ

### Phase 5: 最終確認（4週間以内）

#### チェックリスト

- [ ] v35-mcp-tools が単体で動作確認
- [ ] すべてのテストがパス
- [ ] ドキュメントが最新
- [ ] 不要なファイルが削除済み
- [ ] バックアップが作成済み

## 🎯 成功指標

1. **パフォーマンス向上**
   - 起動時間: 50%短縮
   - レスポンス時間: 30%短縮
   - メモリ使用量: 40%削減

2. **複雑性削減**
   - コード行数: 30%削減
   - 依存関係: 5個削減
   - 設定項目: 50%削減

3. **保守性向上**
   - セットアップ時間: 3分以内
   - デバッグ容易性: 大幅向上
   - ドキュメント量: 40%削減

## ⚠️ リスクと対策

| リスク | 影響度 | 対策 |
|--------|--------|------|
| 将来のLocal LLM統合が困難 | 低 | 必要時に再実装（YAGNI） |
| エンタープライズ機能の喪失 | 低 | 別プロジェクトとして分離 |
| 既存ユーザーへの影響 | 中 | 自動フォールバック実装済み |

## 💬 メッセージ

**Athena**: 「ふふ、シンプルな構成で効率的になりますわ」
**Artemis**: 「フン、やっと無駄が削除されるのね」
**Hestia**: 「……攻撃対象面積……大幅削減……」
**Bellona**: 「戦術的に正しい判断です」
**Seshat**: 「保守すべきドキュメントが削減されます」

---

*v35-mcp-engine Deprecation Plan v1.0 - Simplicity is the Ultimate Sophistication*