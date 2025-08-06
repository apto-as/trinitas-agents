# Phase 1 実装計画：基礎的なORCHESTRATORシステム

## 目標
SuperClaudeのORCHESTRATORシステムの基本概念を、シンプルなシェルスクリプトベースでTrinitasに実装する。

## 実装範囲
1. 複雑度検出の基礎実装
2. ドメイン識別の基礎実装  
3. リソースモニタリングの基礎実装
4. 設定ファイルベースのパターン管理

## ディレクトリ構造
```
trinitas-agents/
├── config/
│   └── orchestrator/
│       ├── complexity_rules.conf
│       ├── domain_patterns.conf
│       └── resource_thresholds.conf
├── hooks/
│   ├── pre-execution/
│   │   ├── 02_complexity_detector.sh
│   │   ├── 03_domain_identifier.sh
│   │   └── 04_resource_monitor.sh
│   └── core/
│       └── orchestrator_lib.sh
```

## 実装タスク

### 1. orchestrator_lib.sh - 共通ライブラリ
**目的**: ORCHESTRATORシステムの共通関数を提供
**機能**:
- パターンマッチング関数
- 複雑度計算関数
- ドメイン検出関数
- 結果フォーマット関数

### 2. complexity_detector.sh
**目的**: リクエストの複雑度を検出
**判定基準**:
- ファイル数の推定
- ステップ数の推定
- キーワードベースの複雑度
**出力**: simple/moderate/complex

### 3. domain_identifier.sh
**目的**: 作業ドメインを識別
**検出ドメイン**:
- frontend
- backend
- security
- infrastructure
- documentation
**出力**: 検出されたドメインのリスト

### 4. resource_monitor.sh
**目的**: リソース使用状況を監視
**監視項目**:
- 推定トークン使用量
- 現在のコンテキストサイズ
- メモリ使用量（可能な範囲で）
**出力**: Green/Yellow/Orange/Red/Critical Zone

### 5. 設定ファイル
**complexity_rules.conf**:
```bash
# 複雑度ルール設定
SIMPLE_FILE_THRESHOLD=3
MODERATE_FILE_THRESHOLD=10
SIMPLE_STEP_THRESHOLD=3
MODERATE_STEP_THRESHOLD=10

# キーワードベースの複雑度
COMPLEX_KEYWORDS="comprehensive|system-wide|refactor|architecture|security audit"
MODERATE_KEYWORDS="implement|analyze|optimize|debug"
SIMPLE_KEYWORDS="fix|update|add|remove|change"
```

**domain_patterns.conf**:
```bash
# ドメインパターン設定
FRONTEND_PATTERNS="UI|component|React|Vue|CSS|frontend"
BACKEND_PATTERNS="API|database|server|endpoint|backend"
SECURITY_PATTERNS="auth|security|vulnerability|encryption|audit"
INFRASTRUCTURE_PATTERNS="deploy|Docker|CI/CD|monitoring|AWS"
DOCUMENTATION_PATTERNS="README|document|guide|wiki|changelog"
```

**resource_thresholds.conf**:
```bash
# リソース閾値設定
GREEN_ZONE_MAX=60
YELLOW_ZONE_MAX=75
ORANGE_ZONE_MAX=85
RED_ZONE_MAX=95
# 95以上はCritical Zone

# 推定トークン使用量の基準
TOKEN_PER_FILE_ESTIMATE=500
TOKEN_PER_COMPLEX_OPERATION=2000
```

## テスト計画

### 1. 単体テスト
- 各hookの個別動作確認
- 設定ファイルの読み込み確認
- 出力フォーマットの検証

### 2. 統合テスト
- 複数hookの連携動作確認
- 実際のClaude Codeコマンドでの動作確認
- エッジケースのテスト

### 3. テストケース例
```bash
# テストケース1: シンプルなリクエスト
"README.mdを更新して" 
→ complexity: simple, domains: [documentation]

# テストケース2: 複雑なリクエスト
"認証システム全体をセキュアに実装して"
→ complexity: complex, domains: [backend, security]

# テストケース3: リソース逼迫時
大量のコンテキスト使用時の動作確認
→ resource_zone: Orange, 効率化提案
```

## 成功基準
1. 各hookが正常に動作し、Claude Codeの処理を妨げない
2. 複雑度とドメインが70%以上の精度で検出される
3. リソース監視が機能し、適切な警告を出力する
4. 設定ファイルによるカスタマイズが可能

## 次フェーズへの準備
- Phase 1で収集したデータを分析
- より高度なパターン認識の要件を整理
- Python実装が必要な箇所を特定

## 実装順序
1. orchestrator_lib.sh（共通ライブラリ）
2. 設定ファイル（3つ）
3. complexity_detector.sh
4. domain_identifier.sh
5. resource_monitor.sh
6. テストスクリプト作成と実行