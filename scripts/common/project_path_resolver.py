#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Unified Project Path Resolution System
Springfield式思いやり設計: プロジェクトパス問題の統一解決

Purpose:
- CI/CD scripts, hooks, and toolsで共通のパス解決方式を提供
- CLAUDE_PROJECT_DIR環境変数の正しい処理
- フォールバック機能による安全な動作
- 絶対パス/相対パスの自動判別

Created by: Springfield - The Strategic Architect
"""

import os
from pathlib import Path
from typing import Optional


class TrinitasProjectResolver:
    """
    Springfield式統合プロジェクトパス解決システム
    """

    def __init__(self):
        self._project_root: Optional[Path] = None
        self._resolution_method: str = ""

    @property
    def project_root(self) -> Path:
        """
        プロジェクトルートディレクトリを取得
        """
        if self._project_root is None:
            self._project_root = self._resolve_project_root()
        return self._project_root

    def _resolve_project_root(self) -> Path:
        """
        Springfield式多段階パス解決アルゴリズム
        """
        # Method 1: CLAUDE_PROJECT_DIR environment variable
        claude_project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        if claude_project_dir:
            path = Path(claude_project_dir).resolve()
            if path.exists() and path.is_dir():
                self._resolution_method = f"CLAUDE_PROJECT_DIR: {claude_project_dir}"
                return path
            else:
                print(
                    f"⚠️  CLAUDE_PROJECT_DIR points to non-existent path: {claude_project_dir}"
                )

        # Method 2: Current working directory with .claude directory
        cwd = Path.cwd().resolve()
        if (cwd / ".claude").exists():
            self._resolution_method = f"Current working directory with .claude: {cwd}"
            return cwd

        # Method 3: Look for trinitas-agents in parent directories (DISABLED during testing)
        # This prevents interference during testing
        if not os.environ.get("TRINITAS_TESTING_MODE"):
            current = Path.cwd().resolve()
            for parent in [current] + list(current.parents):
                if (
                    parent.name == "trinitas-agents"
                    or (parent / "trinitas-agents").exists()
                ):
                    target = (
                        parent / "trinitas-agents"
                        if (parent / "trinitas-agents").exists()
                        else parent
                    )
                    self._resolution_method = f"Trinitas project directory: {target}"
                    return target

        # Method 4: Fallback to current working directory
        self._resolution_method = f"Fallback to current working directory: {cwd}"
        print(
            "⚠️  Using current working directory as fallback - consider setting CLAUDE_PROJECT_DIR"
        )
        return cwd

    def get_hooks_directory(self) -> Path:
        """
        Claude Code hooks ディレクトリを取得
        """
        return self.project_root / ".claude" / "hooks"

    def get_settings_file(self, scope: str = "project") -> Path:
        """
        Claude Code settings.json ファイルを取得

        Args:
            scope: 'user' または 'project'
        """
        if scope == "user":
            return Path.home() / ".claude" / "settings.json"
        else:
            return self.project_root / ".claude" / "settings.json"

    def get_trinitas_scripts_directory(self) -> Path:
        """
        Trinitasスクリプトディレクトリを取得
        """
        # Try to find the trinitas-agents project root
        current = self.project_root

        # If we're inside trinitas-agents project
        if current.name == "trinitas-agents" or "trinitas-agents" in str(current):
            if (current / "scripts").exists():
                return current / "scripts"

        # Look for trinitas-agents in parent directories
        for parent in [current] + list(current.parents):
            trinitas_path = parent / "trinitas-agents"
            if trinitas_path.exists() and (trinitas_path / "scripts").exists():
                return trinitas_path / "scripts"

        # Fallback: assume current project has its own scripts
        return current / "scripts"

    def ensure_claude_directory(self) -> Path:
        """
        .claudeディレクトリを確保（存在しない場合は作成）
        """
        claude_dir = self.project_root / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        return claude_dir

    def ensure_hooks_directory(self) -> Path:
        """
        .claude/hooksディレクトリを確保
        """
        hooks_dir = self.get_hooks_directory()
        hooks_dir.mkdir(parents=True, exist_ok=True)
        return hooks_dir

    def get_resolution_info(self) -> dict:
        """
        現在のパス解決状況を取得（デバッグ用）
        """
        return {
            "project_root": str(self.project_root),
            "resolution_method": self._resolution_method,
            "claude_dir_exists": (self.project_root / ".claude").exists(),
            "hooks_dir_exists": self.get_hooks_directory().exists(),
            "settings_exists": self.get_settings_file().exists(),
            "current_working_directory": str(Path.cwd()),
            "claude_project_dir_env": os.environ.get("CLAUDE_PROJECT_DIR", "Not set"),
        }

    def validate_project_structure(self) -> tuple[bool, list[str]]:
        """
        プロジェクト構造の妥当性を検証
        """
        issues = []

        # Check if project root exists and is accessible
        if not self.project_root.exists():
            issues.append(f"Project root does not exist: {self.project_root}")
        elif not os.access(self.project_root, os.R_OK | os.W_OK):
            issues.append(f"Project root is not readable/writable: {self.project_root}")

        # Check Claude directory structure
        claude_dir = self.project_root / ".claude"
        if claude_dir.exists() and not os.access(claude_dir, os.R_OK | os.W_OK):
            issues.append(f".claude directory is not accessible: {claude_dir}")

        return len(issues) == 0, issues


# Global resolver instance for easy import
resolver = TrinitasProjectResolver()


def get_project_root() -> Path:
    """
    Convenience function to get project root
    """
    return resolver.project_root


def get_hooks_directory() -> Path:
    """
    Convenience function to get hooks directory
    """
    return resolver.get_hooks_directory()


def get_settings_file(scope: str = "project") -> Path:
    """
    Convenience function to get settings file
    """
    return resolver.get_settings_file(scope)


def print_resolution_info():
    """
    Print current path resolution information
    """
    info = resolver.get_resolution_info()
    print("🎯 Trinitas Project Path Resolution Status:")
    print(f"   Project Root: {info['project_root']}")
    print(f"   Resolution: {info['resolution_method']}")
    print(f"   .claude exists: {'✅' if info['claude_dir_exists'] else '❌'}")
    print(f"   hooks exists: {'✅' if info['hooks_dir_exists'] else '❌'}")
    print(f"   settings exists: {'✅' if info['settings_exists'] else '❌'}")
    print(f"   CWD: {info['current_working_directory']}")
    print(f"   CLAUDE_PROJECT_DIR: {info['claude_project_dir_env']}")


if __name__ == "__main__":
    print_resolution_info()

    # Validate structure
    valid, issues = resolver.validate_project_structure()
    if not valid:
        print("\n❌ Project structure issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Project structure validation passed")
