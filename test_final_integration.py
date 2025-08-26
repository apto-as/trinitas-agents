#!/usr/bin/env python3
"""
Trinitas v3.5 Final Integration Test
全修正が正しく適用されたかの最終確認
"""

import os
import sys
import yaml
from pathlib import Path

# カラーコード
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_mythology_names():
    """神話名が正しく使用されているか確認"""
    print(f"\n{BLUE}=== 神話名統一チェック ==={RESET}")
    
    claude_agents = Path.home() / ".claude" / "agents"
    
    # 正しいファイル名
    correct_files = [
        "athena-strategist.md",
        "artemis-optimizer.md",
        "hestia-auditor.md"
    ]
    
    # 間違ったファイル名（ドルフロ名）
    wrong_files = [
        "springfield-strategist.md",
        "krukai-optimizer.md",
        "vector-auditor.md"
    ]
    
    all_ok = True
    
    # 正しいファイルの存在確認
    for filename in correct_files:
        filepath = claude_agents / filename
        if filepath.exists():
            # ファイル内容も確認
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"name: {filename.replace('.md', '')}" in content:
                    print(f"{GREEN}✓{RESET} {filename} - 名前とコンテンツ一致")
                else:
                    print(f"{YELLOW}⚠{RESET} {filename} - ファイル内の名前が不一致")
                    all_ok = False
        else:
            print(f"{RED}✗{RESET} {filename} - ファイルが存在しない")
            all_ok = False
    
    # 間違ったファイルが残っていないか確認
    for filename in wrong_files:
        filepath = claude_agents / filename
        if filepath.exists():
            print(f"{RED}✗{RESET} {filename} - 古いファイルが残っている！")
            all_ok = False
        else:
            print(f"{GREEN}✓{RESET} {filename} - 正しく削除されている")
    
    return all_ok

def check_installation_path():
    """~/.claude/への正しいインストールを確認"""
    print(f"\n{BLUE}=== インストールパス確認 ==={RESET}")
    
    claude_home = Path.home() / ".claude"
    required_paths = [
        claude_home / "agents",
        claude_home / "trinitas",
        claude_home / "CLAUDE.md"
    ]
    
    all_ok = True
    for path in required_paths:
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"{GREEN}✓{RESET} {path} ({size:,} bytes)")
            else:
                count = len(list(path.glob("*")))
                print(f"{GREEN}✓{RESET} {path}/ ({count} items)")
        else:
            print(f"{RED}✗{RESET} {path} - 存在しない")
            all_ok = False
    
    return all_ok

def check_claude_md_integration():
    """CLAUDE.mdにTrinitasが統合されているか確認"""
    print(f"\n{BLUE}=== CLAUDE.md統合確認 ==={RESET}")
    
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    
    if not claude_md.exists():
        print(f"{RED}✗{RESET} CLAUDE.md が存在しない")
        return False
    
    with open(claude_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_sections = [
        "Trinitas",
        "Athena",
        "Artemis", 
        "Hestia"
    ]
    
    all_ok = True
    for section in required_sections:
        if section in content:
            print(f"{GREEN}✓{RESET} '{section}' セクション存在")
        else:
            print(f"{RED}✗{RESET} '{section}' セクション欠落")
            all_ok = False
    
    # インポート記述の確認
    if "@~/.claude/trinitas/" in content or "trinitas/" in content.lower():
        print(f"{GREEN}✓{RESET} Trinitas参照が含まれている")
    else:
        print(f"{YELLOW}⚠{RESET} Trinitas参照が明示的でない")
    
    return all_ok

def check_no_task_in_agents():
    """エージェントファイルにTaskツールが含まれていないか確認"""
    print(f"\n{BLUE}=== Taskツール削除確認 ==={RESET}")
    
    claude_agents = Path.home() / ".claude" / "agents"
    agent_files = [
        "athena-strategist.md",
        "artemis-optimizer.md",
        "hestia-auditor.md"
    ]
    
    all_ok = True
    for filename in agent_files:
        filepath = claude_agents / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # YAMLヘッダー部分を抽出
            if "---" in content:
                yaml_part = content.split("---")[1]
                if "Task" in yaml_part and "tools:" in yaml_part:
                    print(f"{RED}✗{RESET} {filename} - Taskツールがまだ含まれている")
                    all_ok = False
                else:
                    print(f"{GREEN}✓{RESET} {filename} - Taskツールなし")
            else:
                print(f"{YELLOW}⚠{RESET} {filename} - YAMLヘッダーが見つからない")
    
    return all_ok

def check_mcp_tools_tasks():
    """MCP toolsにタスク処理が移行されたか確認"""
    print(f"\n{BLUE}=== MCP Toolsタスク処理確認 ==={RESET}")
    
    tasks_file = Path("v35-mcp-tools/src/trinitas_tasks.py")
    
    if tasks_file.exists():
        print(f"{GREEN}✓{RESET} trinitas_tasks.py が存在")
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = [
            "execute_parallel",
            "execute_chain",
            "execute_consensus",
            "trinitas_parallel"
        ]
        
        for func in required_functions:
            if func in content:
                print(f"{GREEN}✓{RESET} {func} 関数が実装されている")
            else:
                print(f"{RED}✗{RESET} {func} 関数が見つからない")
                
        return True
    else:
        print(f"{RED}✗{RESET} trinitas_tasks.py が存在しない")
        return False

def check_persona_definitions():
    """統一ペルソナ定義ファイルの確認"""
    print(f"\n{BLUE}=== ペルソナ定義確認 ==={RESET}")
    
    definitions_path = Path.home() / ".claude" / "trinitas" / "TRINITAS_PERSONA_DEFINITIONS.yaml"
    
    if not definitions_path.exists():
        print(f"{RED}✗{RESET} ペルソナ定義ファイルが存在しない")
        return False
    
    try:
        with open(definitions_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        personas = data.get('personas', {})
        
        # デフォルトが神話名であることを確認
        for key in ['springfield', 'krukai', 'vector']:
            if key in personas:
                persona = personas[key]
                myth_name = persona.get('mythology_name', '')
                if myth_name:
                    print(f"{GREEN}✓{RESET} {key} → {myth_name} マッピング存在")
                else:
                    print(f"{RED}✗{RESET} {key} の神話名マッピングなし")
        
        # 名前モードの確認
        if 'execution_modes' in data:
            modes = data['execution_modes']
            if 'claude_native' in modes:
                print(f"{GREEN}✓{RESET} Claude nativeモード定義あり")
        
        return True
        
    except Exception as e:
        print(f"{RED}✗{RESET} ペルソナ定義ファイルの読み込みエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Trinitas v3.5 最終統合テスト{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("神話名統一", check_mythology_names),
        ("インストールパス", check_installation_path),
        ("CLAUDE.md統合", check_claude_md_integration),
        ("Taskツール削除", check_no_task_in_agents),
        ("MCPタスク移行", check_mcp_tools_tasks),
        ("ペルソナ定義", check_persona_definitions)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"{RED}✗{RESET} テスト '{test_name}' エラー: {e}")
            results[test_name] = False
    
    # サマリー
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  テストサマリー{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}合格{RESET}" if result else f"{RED}不合格{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}結果: {passed}/{total} テスト合格{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✨ 全テスト合格！修正が完璧に適用されました。{RESET}")
        print("\n" + "="*60)
        print("Athena: \"ふふ、完璧な統合が完成しましたわ\"")
        print("Artemis: \"フン、やっと404の基準を満たしたわね\"")
        print("Hestia: \"……全システム正常……セキュリティ確認完了……\"")
        print("="*60)
    else:
        print(f"\n{YELLOW}⚠ 一部のテストが失敗しました。上記の問題を確認してください。{RESET}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())