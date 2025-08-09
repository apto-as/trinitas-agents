"""
Trinitas logging with character personalities and rich output.
"""

import sys
from datetime import datetime
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class TrinitasLogger:
    """Logger with Trinitas character personalities and rich output."""

    def __init__(self, use_rich: bool = True):
        """Initialize logger."""
        self.use_rich = use_rich and HAS_RICH
        if self.use_rich:
            self.console = Console(stderr=True)

    def springfield(self, message: str, title: Optional[str] = None):
        """Springfield's encouraging messages."""
        if self.use_rich:
            text = Text(message, style="magenta")
            if title:
                panel = Panel(
                    text,
                    title=f"[magenta]Springfield - {title}[/magenta]",
                    border_style="magenta",
                )
                self.console.print(panel)
            else:
                self.console.print("[magenta][Springfield][/magenta]", message)
        else:
            print(f"\033[0;35m[Springfield]\033[0m {message}", file=sys.stderr)

    def krukai(self, message: str, title: Optional[str] = None):
        """Krukai's perfectionist messages."""
        if self.use_rich:
            text = Text(message, style="blue")
            if title:
                panel = Panel(
                    text, title=f"[blue]Krukai - {title}[/blue]", border_style="blue"
                )
                self.console.print(panel)
            else:
                self.console.print("[blue][Krukai][/blue]", message)
        else:
            print(f"\033[0;34m[Krukai]\033[0m {message}", file=sys.stderr)

    def vector(self, message: str, title: Optional[str] = None):
        """Vector's security-focused messages."""
        if self.use_rich:
            text = Text(message, style="cyan")
            if title:
                panel = Panel(
                    text, title=f"[cyan]Vector - {title}[/cyan]", border_style="cyan"
                )
                self.console.print(panel)
            else:
                self.console.print("[cyan][Vector][/cyan]", message)
        else:
            print(f"\033[0;36m[Vector]\033[0m {message}", file=sys.stderr)

    def info(self, message: str):
        """General info message."""
        if self.use_rich:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"\033[0;34m[INFO]\033[0m {message}", file=sys.stderr)

    def success(self, message: str):
        """Success message."""
        if self.use_rich:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"\033[0;32m[SUCCESS]\033[0m {message}", file=sys.stderr)

    def warning(self, message: str):
        """Warning message."""
        if self.use_rich:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"\033[1;33m[WARNING]\033[0m {message}", file=sys.stderr)

    def error(self, message: str):
        """Error message."""
        if self.use_rich:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"\033[0;31m[ERROR]\033[0m {message}", file=sys.stderr)

    def code(self, code: str, language: str = "python", title: Optional[str] = None):
        """Display code with syntax highlighting."""
        if self.use_rich:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            if title:
                panel = Panel(syntax, title=title, border_style="green")
                self.console.print(panel)
            else:
                self.console.print(syntax)
        else:
            if title:
                print(f"\n--- {title} ---", file=sys.stderr)
            print(code, file=sys.stderr)

    def table(self, title: str, headers: list, rows: list):
        """Display data in a table."""
        if self.use_rich:
            table = Table(title=title)
            for header in headers:
                table.add_column(header, style="cyan")
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)
        else:
            # Simple text table
            print(f"\n{title}", file=sys.stderr)
            print("-" * 50, file=sys.stderr)
            print("\t".join(headers), file=sys.stderr)
            print("-" * 50, file=sys.stderr)
            for row in rows:
                print("\t".join(str(cell) for cell in row), file=sys.stderr)

    def progress_start(self, task: str):
        """Start a progress indicator."""
        if self.use_rich:
            self.console.print(f"[cyan]⏳[/cyan] {task}...", end="")
        else:
            print(f"⏳ {task}...", end="", file=sys.stderr)

    def progress_end(self, success: bool = True):
        """End a progress indicator."""
        if self.use_rich:
            if success:
                self.console.print(" [green]Done![/green]")
            else:
                self.console.print(" [red]Failed![/red]")
        else:
            if success:
                print(" Done!", file=sys.stderr)
            else:
                print(" Failed!", file=sys.stderr)

    def report(self, title: str, sections: dict):
        """Generate a formatted report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.use_rich:
            # Create main panel
            content = []

            for section_title, section_content in sections.items():
                content.append(f"\n[bold cyan]{section_title}[/bold cyan]")

                if isinstance(section_content, list):
                    for item in section_content:
                        content.append(f"  • {item}")
                elif isinstance(section_content, dict):
                    for key, value in section_content.items():
                        content.append(f"  {key}: {value}")
                else:
                    content.append(f"  {section_content}")

            panel = Panel(
                "\n".join(content),
                title=f"[bold magenta]{title}[/bold magenta]",
                subtitle=f"[dim]{timestamp}[/dim]",
                border_style="magenta",
            )
            self.console.print(panel)
        else:
            # Simple text report
            print(f"\n{'=' * 60}", file=sys.stderr)
            print(f"{title}", file=sys.stderr)
            print(f"Time: {timestamp}", file=sys.stderr)
            print(f"{'=' * 60}", file=sys.stderr)

            for section_title, section_content in sections.items():
                print(f"\n{section_title}:", file=sys.stderr)

                if isinstance(section_content, list):
                    for item in section_content:
                        print(f"  • {item}", file=sys.stderr)
                elif isinstance(section_content, dict):
                    for key, value in section_content.items():
                        print(f"  {key}: {value}", file=sys.stderr)
                else:
                    print(f"  {section_content}", file=sys.stderr)

            print(f"{'=' * 60}\n", file=sys.stderr)
