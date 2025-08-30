# 一般的な問題と解決策

## 🔧 トラブルシューティングガイド

### 問題1: MCPサーバーが起動しない

**症状**
```
Error: Failed to start MCP server
ModuleNotFoundError: No module named 'fastmcp'
```

**原因**
- Pythonバージョンが古い
- 依存関係がインストールされていない

**解決策**
```bash
# Python 3.10+を確認
python --version

# 依存関係をインストール
cd trinitas-mcp
uv sync

# 再起動
python src/mcp_server_v4.py
```

### 問題2: メモリエラー（str(e)問題）

**症状**
```
Error: password='secret123' is invalid
```

**原因**
- エラーメッセージに機密情報が含まれている
- str(e)を直接使用している

**解決策**
```python
# 修正前
except Exception as e:
    return {"error": str(e)}

# 修正後
from security_utils import sanitize_error

except Exception as e:
    return {"error": sanitize_error(e)}
```

### 問題3: dequeインデックスエラー

**症状**
```
TypeError: 'deque' object does not support indexing
```

**原因**
- dequeに対して直接インデックスアクセスしている

**解決策**
```python
# 修正前
first = self.access_history[0]
last = self.access_history[-1]

# 修正後
access_list = list(self.access_history)
first = access_list[0]
last = access_list[-1]
```

### 問題4: 無限ループ

**症状**
- プロセスがハングする
- CPU使用率が100%

**原因**
- _process_queueにタイムアウトがない

**解決策**
```python
# 修正後
async def _process_queue(self):
    while True:
        try:
            # タイムアウトを追加
            task_data = await asyncio.wait_for(
                self.task_queue.get(),
                timeout=60.0
            )
            # 処理
        except asyncio.TimeoutError:
            await asyncio.sleep(1)
```

### 問題5: ペルソナが応答しない

**症状**
```
Error: Persona executor not implemented
```

**原因**
- ペルソナ実行ロジックが未実装
- モックだけが存在

**解決策**
Phase 2でペルソナExecutorを実装する必要があります：
```python
class AthenaExecutor:
    async def execute(self, task: str, context: Dict) -> str:
        # 実装が必要
        pass
```

## 🚨 緊急時の対応

### システム完全停止時

1. **ログ確認**
```bash
tail -f logs/trinitas.log
```

2. **プロセス確認**
```bash
ps aux | grep mcp_server
```

3. **強制終了と再起動**
```bash
kill -9 [PID]
cd trinitas-mcp
python src/mcp_server_v4.py
```

### データ破損時

1. **バックアップから復旧**
```bash
cp sqlite_data.db.backup sqlite_data.db
```

2. **キャッシュクリア**
```bash
redis-cli FLUSHALL
```

3. **再初期化**
```python
from memory_manager_v4 import EnhancedMemoryManager
manager = EnhancedMemoryManager()
await manager.initialize()
```

## 📊 パフォーマンス問題

### 遅い応答時間

**診断コマンド**
```python
# パフォーマンスプロファイリング
import cProfile
cProfile.run('memory_recall(query)')
```

**最適化ポイント**
- インデックス追加
- キャッシュ有効化
- クエリ最適化
- 並列処理

### メモリリーク

**監視**
```python
import tracemalloc
tracemalloc.start()
# ... 処理 ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```

**対策**
- 明示的なリソース解放
- コネクションプール使用
- 弱参照の活用

## 🔍 デバッグのコツ

### ログレベル調整
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### ブレークポイント設定
```python
import pdb; pdb.set_trace()
```

### 非同期デバッグ
```python
import asyncio
asyncio.get_event_loop().set_debug(True)
```

## 📞 エスカレーション

### レベル1: 自己解決（このドキュメント）
- 一般的な問題の70%はここで解決

### レベル2: チーム内エスカレーション
- Slack: #trinitas-support
- 応答時間: 4時間以内

### レベル3: 緊急エスカレーション
- 緊急連絡先: emergency@trinitas.ai
- 電話: xxx-xxxx-xxxx（24/7）

---
作成者: Hestia (セキュリティガーディアン)
最終更新: 2025-08-30
バージョン: v1.0.0