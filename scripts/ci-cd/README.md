# Trinitas CI/CD Integration

Trinity品質ゲートシステムを GitHub Actions、GitLab CI、Jenkins等のCI/CDパイプラインに統合するためのスクリプト群です。

## 🎭 Overview

Trinitas CI/CD統合により、以下の三位一体品質チェックが自動化されます：

- **🌸 Springfield**: 戦略的分析 (プロジェクト構造、チーム協調、持続可能性)
- **⚡ Krukai**: 技術的品質 (コード品質、パフォーマンス、技術的卓越性)
- **🛡️ Vector**: セキュリティ分析 (脆弱性検査、リスク評価、コンプライアンス)

## 🚀 Quick Start

### GitHub Actions Integration

1. **Workflow配置**
```bash
# GitHub Actionsワークフローをコピー
cp scripts/ci-cd/github-actions-integration.yml .github/workflows/trinitas-quality.yml
```

2. **Secretsの設定**
```bash
# GitHub リポジトリのSecretsに以下を設定（必要に応じて）
# YAML設定ファイルを使用するため、個別の環境変数は最小限に
TRINITAS_CONFIG_PATH=~/.claude/agents/trinitas/config.yaml
TRINITAS_MODE=ci  # CI環境用のオーバーライド
```

3. **プッシュまたはPR作成**
```bash
git push origin main
# または Pull Request を作成
```

### Manual Execution

```bash
# 依存関係インストール
pip install -r scripts/ci-cd/requirements.txt

# 各エージェントを個別実行
python scripts/ci-cd/springfield_ci_analysis.py
python scripts/ci-cd/krukai_quality_gate.py  
python scripts/ci-cd/vector_security_scan.py

# Trinity統合評価
python scripts/ci-cd/trinity_gate_coordinator.py \
  --strategic=85.0 --technical=78.0 --security=92.0

# HTMLレポート生成
python scripts/ci-cd/generate_trinity_report.py
```

## 📁 File Structure

```
scripts/ci-cd/
├── github-actions-integration.yml  # GitHub Actions workflow
├── requirements.txt                # Python dependencies
├── springfield_ci_analysis.py      # Springfield strategic analysis
├── krukai_quality_gate.py         # Krukai quality gate  
├── vector_security_scan.py        # Vector security scanner
├── trinity_gate_coordinator.py    # Trinity coordination system
├── generate_trinity_report.py     # HTML report generator
└── README.md                      # This file
```

## 🌸 Springfield - Strategic Analysis

プロジェクトの戦略的健全性を評価：

### 評価項目
- **Project Structure** (30点): ディレクトリ構成、設定ファイル、文書化
- **Team Sustainability** (40点): Git活動、コラボレーション、継続性
- **Long-term Vision** (30点): バージョン管理、ロードマップ、CI/CD

### 出力
- `strategic_score.txt`: 数値スコア
- `springfield_analysis.json`: 詳細分析結果

### 使用例
```python
from springfield_ci_analysis import SpringfieldStrategicAnalyzer

analyzer = SpringfieldStrategicAnalyzer("/path/to/project")
result = analyzer.run_complete_analysis()
print(f"Strategic Score: {result['scores']['overall_strategic']}")
```

## ⚡ Krukai - Quality Gate

コード品質と技術的卓越性を厳格に評価：

### 評価項目
- **Code Quality** (35%): Pylint、型ヒント、ドキュメント
- **Performance Indicators** (25%): 非同期処理、最適化パターン
- **Security Quality** (25%): セキュアコーディング、暗号化使用
- **Technical Debt** (15%): TODO/FIXME、大きなファイル

### 品質基準
```yaml
krukai_standards:
  code_quality_minimum: 85
  performance_grade_minimum: 80  
  security_score_minimum: 95
  technical_debt_maximum: 25
```

### 出力
- `quality_score.txt`: 数値スコア
- `krukai_quality.json`: 詳細品質メトリクス

## 🛡️ Vector - Security Scanner

セキュリティ脆弱性を超悲観的に検査：

### 検査項目
- **Hardcoded Secrets**: パスワード、APIキー、トークン
- **Dependency Vulnerabilities**: Python/npm既知脆弱性
- **Insecure Patterns**: SQLインジェクション、XSS、弱い暗号化
- **File Permissions**: 機密ファイルの権限設定

### 脅威レベル
```yaml
threat_levels:
  CRITICAL: 50 points  # 即座に危険
  HIGH: 30 points      # 重大なリスク
  MEDIUM: 15 points    # 潜在的脆弱性
  LOW: 5 points        # 軽微な問題
  INFO: 1 point        # 改善余地
```

### 出力
- `security_score.txt`: セキュリティスコア
- `vector_security.json`: 詳細脆弱性レポート

## 🎭 Trinity Gate Coordinator

三位一体の評価を統合し、最終的なデプロイ判定を実行：

### 統合アルゴリズム
```python
# 基本スコア計算
base_score = strategic * 0.35 + technical * 0.35 + security * 0.30

# 相乗効果係数
synergy_factor = balance_factor * excellence_bonus * failure_penalty

# 最終スコア
final_score = base_score * synergy_factor
```

### ゲート判定
- **APPROVE_EXCELLENT** (90+): 🟢 即座にデプロイ可能
- **APPROVE_GOOD** (80+): 🟢 デプロイ承認
- **APPROVE_WITH_CONDITIONS** (70+): 🟡 条件付き承認
- **NEEDS_IMPROVEMENT** (60+): 🟠 改善後再評価
- **REJECT** (<60): 🔴 大幅な改善が必要

### 出力
- `trinity_gate_result.json`: 統合評価結果
- `trinity-summary.md`: PR用サマリー

## 📊 HTML Report Generator

美しいHTMLレポートを生成：

### 特徴
- 📱 レスポンシブデザイン
- 🎨 Trinity テーマカラー
- 📈 視覚的なメトリクス表示
- 💡 実用的な推奨事項

### カスタマイズ
```python
# CSSスタイルのカスタマイズ
generator = TrinityReportGenerator()
generator.template = custom_template  # カスタムHTMLテンプレート
report_path = generator.save_report()
```

## 🔧 Configuration

### 環境変数
```bash
# プロジェクトルート指定
export CLAUDE_PROJECT_DIR="/path/to/project"

# CI/CDモード指定（config.yamlの値をオーバーライド）
export TRINITAS_CONFIG_PATH="~/.claude/agents/trinitas/config.yaml"
export TRINITAS_MODE="ci"

# GitHub情報（Actions環境で自動設定）
export GITHUB_REPOSITORY="owner/repo"
```

### カスタム設定
各スクリプトは独立して動作し、必要に応じて閾値や評価基準をカスタマイズ可能です。

## 🚀 Integration Examples

### GitLab CI Integration
```yaml
stages:
  - trinitas-analysis

trinitas-quality:
  stage: trinitas-analysis
  image: python:3.11
  script:
    - pip install -r scripts/ci-cd/requirements.txt
    - python scripts/ci-cd/springfield_ci_analysis.py
    - python scripts/ci-cd/krukai_quality_gate.py
    - python scripts/ci-cd/vector_security_scan.py
    - python scripts/ci-cd/trinity_gate_coordinator.py --strategic=$(cat strategic_score.txt) --technical=$(cat quality_score.txt) --security=$(cat security_score.txt)
  artifacts:
    reports:
      junit: trinity-report.html
    expire_in: 1 week
```

### Jenkins Integration
```groovy
pipeline {
    agent any
    stages {
        stage('Trinity Analysis') {
            steps {
                sh 'pip install -r scripts/ci-cd/requirements.txt'
                sh 'python scripts/ci-cd/springfield_ci_analysis.py'
                sh 'python scripts/ci-cd/krukai_quality_gate.py'
                sh 'python scripts/ci-cd/vector_security_scan.py'
                
                script {
                    def strategic = readFile('strategic_score.txt').trim()
                    def technical = readFile('quality_score.txt').trim()
                    def security = readFile('security_score.txt').trim()
                    
                    sh "python scripts/ci-cd/trinity_gate_coordinator.py --strategic=${strategic} --technical=${technical} --security=${security}"
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'trinity-report.html',
                        reportName: 'Trinity Quality Report'
                    ])
                }
            }
        }
    }
}
```

## 🎯 Quality Standards

### Trinity Excellence Standards
```yaml
excellence_criteria:
  strategic_minimum: 70    # Springfield minimum
  technical_minimum: 70    # Krukai minimum  
  security_minimum: 70     # Vector minimum
  trinity_minimum: 70      # Overall minimum
  
balance_requirements:
  max_imbalance: 30        # Maximum score difference
  synergy_bonus_threshold: 90  # All agents excellent
  critical_failure_threshold: 50  # Any agent critical fail
```

## 📈 Metrics & KPIs

### Success Metrics
- **Quality Gate Pass Rate**: 目標 >85%
- **Security Issues Detected**: 継続的減少傾向
- **Technical Debt Ratio**: <15%維持
- **Team Satisfaction**: 品質プロセスへの満足度

### Performance Metrics
- **Analysis Time**: <5分（中規模プロジェクト）
- **False Positive Rate**: <10%
- **Coverage**: 全コードファイルの>90%

## 🤝 Contributing

### 新しいCI/CDプラットフォーム対応
1. `scripts/ci-cd/` に新しい設定ファイルを追加
2. 必要に応じてPythonスクリプトを調整
3. READMEにintegration exampleを追加

### 評価基準のカスタマイズ
1. 各エージェントスクリプトの閾値を調整
2. `trinity_gate_coordinator.py` の統合ロジックを修正
3. テストケースを追加

## 📞 Support

- 🐛 **Issues**: GitHub Issues でバグ報告
- 💬 **Discussions**: 使用方法や改善提案
- 📖 **Documentation**: 詳細なガイドは `docs/` ディレクトリ

---

**🎭 Trinity CI/CD Integration** - Automated Quality Excellence

*Springfield の戦略 • Krukai の技術 • Vector の安全性*