#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Path Resolution Testing Suite
Springfield式品質保証: パス解決システムの包括テスト

Purpose:
- 統一パス解決システムの動作検証
- CI/CD環境での動作確認
- エッジケース検証（存在しないパス、権限エラーなど）

Created by: Springfield - The Strategic Architect (with Krukai optimization and Vector paranoia)
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.project_path_resolver import TrinitasProjectResolver


class PathResolutionTester:
    """
    Springfield式包括的パス解決テスト
    """

    def __init__(self):
        self.test_results: List[Tuple[str, bool, str]] = []
        self.temp_dirs: List[Path] = []

    def setup_test_environment(self):
        """
        テスト環境の準備
        """
        print("🧪 Setting up test environment...")

        # Create temporary directories for testing
        base_temp = Path(tempfile.mkdtemp(prefix="trinitas_path_test_"))
        self.temp_dirs.append(base_temp)

        # Create various test scenarios
        scenarios = {
            "trinitas_project": base_temp / "trinitas-agents",
            "claude_project": base_temp / "with_claude",
            "empty_project": base_temp / "empty",
            "nested_project": base_temp / "deep" / "nested" / "project",
        }

        for name, path in scenarios.items():
            path.mkdir(parents=True, exist_ok=True)
            if name != "empty_project":
                (path / ".claude").mkdir(exist_ok=True)
                (path / ".claude" / "settings.json").write_text('{"test": true}')

            if name == "trinitas_project":
                (path / "scripts").mkdir(exist_ok=True)
                (path / "hooks").mkdir(exist_ok=True)

        return scenarios

    def test_basic_resolution(self, scenarios: dict):
        """
        基本的なパス解決テスト
        """
        print("🔍 Testing basic path resolution...")

        # Test 1: CLAUDE_PROJECT_DIR environment variable
        test_path = str(scenarios["claude_project"])
        with patch.dict(
            os.environ, {"CLAUDE_PROJECT_DIR": test_path, "TRINITAS_TESTING_MODE": "1"}
        ):
            resolver = TrinitasProjectResolver()
            result = resolver.project_root.resolve() == Path(test_path).resolve()
            self.test_results.append(
                (
                    "CLAUDE_PROJECT_DIR resolution",
                    result,
                    f"Expected {Path(test_path).resolve()}, got {resolver.project_root}",
                )
            )

        # Test 2: Current working directory with .claude
        os.chdir(scenarios["claude_project"])
        with patch.dict(os.environ, {"TRINITAS_TESTING_MODE": "1"}):
            resolver = TrinitasProjectResolver()
            result = (
                resolver.project_root.resolve() == scenarios["claude_project"].resolve()
            )
            self.test_results.append(
                (
                    "CWD with .claude resolution",
                    result,
                    f"Expected {scenarios['claude_project'].resolve()}, got {resolver.project_root}",
                )
            )

        # Test 3: Fallback to CWD
        os.chdir(scenarios["empty_project"])
        with patch.dict(os.environ, {"TRINITAS_TESTING_MODE": "1"}):
            resolver = TrinitasProjectResolver()
            result = (
                resolver.project_root.resolve() == scenarios["empty_project"].resolve()
            )
            self.test_results.append(
                (
                    "Fallback to CWD",
                    result,
                    f"Expected {scenarios['empty_project'].resolve()}, got {resolver.project_root}",
                )
            )

    def test_edge_cases(self, scenarios: dict):
        """
        エッジケース・エラー処理テスト
        """
        print("🚨 Testing edge cases...")

        # Test 1: Non-existent CLAUDE_PROJECT_DIR
        os.chdir(scenarios["claude_project"])  # Ensure valid fallback location
        with patch.dict(
            os.environ,
            {"CLAUDE_PROJECT_DIR": "/nonexistent/path", "TRINITAS_TESTING_MODE": "1"},
        ):
            resolver = TrinitasProjectResolver()
            # Should fallback gracefully
            result = resolver.project_root.exists()
            self.test_results.append(
                (
                    "Non-existent CLAUDE_PROJECT_DIR fallback",
                    result,
                    f"Should exist after fallback: {resolver.project_root}",
                )
            )

        # Test 2: File instead of directory
        test_file = scenarios["claude_project"] / "test_file.txt"
        test_file.write_text("test")
        with patch.dict(
            os.environ,
            {"CLAUDE_PROJECT_DIR": str(test_file), "TRINITAS_TESTING_MODE": "1"},
        ):
            resolver = TrinitasProjectResolver()
            result = resolver.project_root != test_file
            self.test_results.append(
                (
                    "File instead of directory",
                    result,
                    f"Should not use file as project root: {resolver.project_root}",
                )
            )

    def test_directory_creation(self, scenarios: dict):
        """
        ディレクトリ作成機能テスト
        """
        print("📁 Testing directory creation...")

        os.chdir(scenarios["empty_project"])
        with patch.dict(os.environ, {"TRINITAS_TESTING_MODE": "1"}):
            resolver = TrinitasProjectResolver()

            # Test claude directory creation
            claude_dir = resolver.ensure_claude_directory()
            result = claude_dir.exists() and claude_dir.is_dir()
            self.test_results.append(
                (
                    "Claude directory creation",
                    result,
                    f"Directory should exist: {claude_dir}",
                )
            )

            # Test hooks directory creation
            hooks_dir = resolver.ensure_hooks_directory()
            result = hooks_dir.exists() and hooks_dir.is_dir()
            self.test_results.append(
                (
                    "Hooks directory creation",
                    result,
                    f"Directory should exist: {hooks_dir}",
                )
            )

    def test_validation(self, scenarios: dict):
        """
        バリデーション機能テスト
        """
        print("✅ Testing validation functions...")

        os.chdir(scenarios["claude_project"])
        with patch.dict(os.environ, {"TRINITAS_TESTING_MODE": "1"}):
            resolver = TrinitasProjectResolver()
            valid, issues = resolver.validate_project_structure()

            result = valid and len(issues) == 0
            self.test_results.append(
                (
                    "Project structure validation (valid)",
                    result,
                    f"Should be valid with no issues, got: {issues}",
                )
            )

    def test_convenience_functions(self, scenarios: dict):
        """
        便利関数テスト
        """
        print("🛠️  Testing convenience functions...")

        from common.project_path_resolver import (
            get_project_root,
            get_hooks_directory,
            get_settings_file,
        )

        os.chdir(scenarios["claude_project"])
        with patch.dict(os.environ, {"TRINITAS_TESTING_MODE": "1"}):
            # Test convenience functions
            project_root = get_project_root()
            hooks_dir = get_hooks_directory()
            settings_file = get_settings_file()

            result = (
                project_root.exists()
                and hooks_dir.parent.exists()
                and settings_file.name == "settings.json"
            )

            self.test_results.append(
                (
                    "Convenience functions",
                    result,
                    f"Project root: {project_root}, Hooks: {hooks_dir}, Settings: {settings_file}",
                )
            )

    def run_all_tests(self):
        """
        全テストの実行
        """
        print("🌸 Springfield式パス解決システム包括テスト開始")
        print("=" * 60)

        try:
            scenarios = self.setup_test_environment()

            # Store original CWD to restore later
            original_cwd = Path.cwd()

            # Run test suites
            self.test_basic_resolution(scenarios)
            self.test_edge_cases(scenarios)
            self.test_directory_creation(scenarios)
            self.test_validation(scenarios)
            self.test_convenience_functions(scenarios)

            # Restore original working directory
            os.chdir(original_cwd)

        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False
        finally:
            self.cleanup_test_environment()

        # Report results
        return self.report_results()

    def report_results(self) -> bool:
        """
        テスト結果の報告
        """
        print("\n" + "=" * 60)
        print("📊 テスト結果レポート")
        print("=" * 60)

        passed = 0
        failed = 0

        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if not success:
                print(f"      Details: {details}")

            if success:
                passed += 1
            else:
                failed += 1

        print(f"\n📈 総計: {passed} PASS, {failed} FAIL")

        if failed == 0:
            print("🎉 全テストが成功しました！")
            return True
        else:
            print("⚠️  一部テストが失敗しました。詳細を確認してください。")
            return False

    def cleanup_test_environment(self):
        """
        テスト環境のクリーンアップ
        """
        print("🧹 Cleaning up test environment...")
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Failed to cleanup {temp_dir}: {e}")


def main():
    """
    メイン実行関数
    """
    tester = PathResolutionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
