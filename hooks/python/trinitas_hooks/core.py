"""
Core classes and utilities for Trinitas Python hooks.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class HookStatus(Enum):
    """Hook execution status."""

    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BLOCKED = "blocked"


@dataclass
class HookResult:
    """Result of a hook execution."""

    status: HookStatus
    message: str
    details: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_shell_format(self) -> str:
        """Format result for shell output."""
        # Color codes
        colors = {
            HookStatus.SUCCESS: "\033[0;32m",  # Green
            HookStatus.WARNING: "\033[1;33m",  # Yellow
            HookStatus.ERROR: "\033[0;31m",  # Red
            HookStatus.BLOCKED: "\033[0;31m",  # Red
        }
        reset = "\033[0m"

        # Status symbols
        symbols = {
            HookStatus.SUCCESS: "✓",
            HookStatus.WARNING: "⚠",
            HookStatus.ERROR: "✗",
            HookStatus.BLOCKED: "⛔",
        }

        # Format output
        color = colors[self.status]
        symbol = symbols[self.status]
        output = (
            f"{color}{symbol} Hook {self.status.value.title()}{reset}: {self.message}"
        )

        if self.details:
            output += f"\n{self.details}"

        return output


class TrinitasHook(ABC):
    """Base class for all Trinitas Python hooks."""

    def __init__(self) -> None:
        """Initialize hook with Claude environment."""
        self.project_dir: str = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        self.tool_name: str = os.environ.get("CLAUDE_TOOL_NAME", "")
        self.tool_args_raw: str = os.environ.get("CLAUDE_TOOL_ARGUMENTS", "{}")

        # Parse tool arguments
        self.tool_args: Dict[str, Any]
        try:
            self.tool_args = json.loads(self.tool_args_raw)
        except json.JSONDecodeError:
            self.tool_args = {}

    def validate_environment(self) -> bool:
        """Validate Claude Code environment."""
        if not self.tool_name:
            return False
        if not os.path.isdir(self.project_dir):
            return False
        return True

    @abstractmethod
    def run(self) -> HookResult:
        """Execute the hook logic."""
        pass

    def execute(self) -> int:
        """Execute hook and return shell exit code."""
        # Validate environment
        if not self.validate_environment():
            result = HookResult(
                status=HookStatus.ERROR,
                message="Invalid Claude Code environment",
                details="Required environment variables are missing or invalid",
            )
            print(result.to_shell_format(), file=sys.stderr)
            return 1

        # Run hook
        try:
            result = self.run()
        except Exception as e:
            result = HookResult(
                status=HookStatus.ERROR,
                message=f"Hook execution failed: {str(e)}",
                details=f"Exception type: {type(e).__name__}",
            )

        # Output result
        print(result.to_shell_format())

        # Return appropriate exit code
        if result.status in (HookStatus.ERROR, HookStatus.BLOCKED):
            return 1
        return 0


class CharacterLogger:
    """Logger with Trinitas character personalities."""

    @staticmethod
    def springfield(message: str) -> None:
        """Springfield's encouraging messages."""
        print(f"\033[0;35m[Springfield]\033[0m {message}", file=sys.stderr)

    @staticmethod
    def krukai(message: str) -> None:
        """Krukai's perfectionist messages."""
        print(f"\033[0;34m[Krukai]\033[0m {message}", file=sys.stderr)

    @staticmethod
    def vector(message: str) -> None:
        """Vector's security-focused messages."""
        print(f"\033[0;36m[Vector]\033[0m {message}", file=sys.stderr)
