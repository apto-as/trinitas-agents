#!/usr/bin/env python3
"""
Trinitas MCP Tools CLI
Command-line interface for managing and running Trinitas MCP Tools
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("Error: Required dependencies not installed.")
    print("Please run: uv pip install trinitas-mcp-tools")
    sys.exit(1)

console = Console()

@click.group()
@click.version_option(version="3.5.0", prog_name="Trinitas MCP Tools")
def cli():
    """
    Trinitas MCP Tools - Five-mind integrated intelligence for Claude Code
    
    \b
    Available personas:
      • Athena  - Strategic Architect
      • Artemis - Technical Perfectionist
      • Hestia  - Security Guardian
      • Bellona - Tactical Coordinator
      • Seshat  - Documentation Specialist
    """
    pass

@cli.command()
@click.option('--claude-home', default=None, help='Path to Claude home directory')
@click.option('--auto', is_flag=True, help='Automatically detect and configure')
def setup(claude_home: Optional[str], auto: bool):
    """Setup Trinitas MCP Tools for Claude Code"""
    
    console.print("[bold blue]🚀 Trinitas MCP Tools Setup[/bold blue]")
    
    # Auto-detect Claude home if not specified
    if not claude_home:
        default_paths = [
            Path.home() / ".claude",
            Path.home() / "Library" / "Application Support" / "Claude",
            Path.home() / "AppData" / "Roaming" / "Claude",
        ]
        
        for path in default_paths:
            if path.exists():
                claude_home = str(path)
                console.print(f"✓ Found Claude home: {claude_home}")
                break
    
    if not claude_home:
        console.print("[red]✗ Could not find Claude home directory[/red]")
        console.print("Please specify with --claude-home option")
        return
    
    claude_path = Path(claude_home)
    
    # Create MCP configuration
    mcp_config = {
        "mcpServers": {
            "trinitas": {
                "command": "uv",
                "args": ["run", "trinitas-server"],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent.parent),
                    "TRINITAS_MODE": "mythology",
                    "AUTO_DETECT": "true"
                }
            }
        }
    }
    
    # Write configuration
    config_file = claude_path / "mcp_config.json"
    
    if config_file.exists() and not auto:
        if not click.confirm(f"Configuration exists at {config_file}. Overwrite?"):
            console.print("[yellow]Setup cancelled[/yellow]")
            return
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Merge with existing config if present
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing = json.load(f)
                existing.get("mcpServers", {}).update(mcp_config["mcpServers"])
                mcp_config = existing
        except json.JSONDecodeError:
            console.print("[yellow]⚠ Existing config is invalid, creating new one[/yellow]")
    
    with open(config_file, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    console.print(f"[green]✓ Configuration written to {config_file}[/green]")
    
    # Show success message
    panel = Panel.fit(
        "[green]✨ Trinitas MCP Tools successfully configured![/green]\n\n"
        "Next steps:\n"
        "1. Restart Claude Code\n"
        "2. The Trinitas tools will be available automatically\n"
        "3. Try: 'Plan a system architecture' to activate Athena",
        title="Setup Complete",
        border_style="green"
    )
    console.print(panel)

@cli.command()
def status():
    """Check Trinitas MCP Tools status"""
    
    console.print("[bold blue]📊 Trinitas MCP Tools Status[/bold blue]\n")
    
    # Create status table
    table = Table(title="System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python", "✓", py_version)
    
    # Check dependencies
    try:
        import fastmcp
        table.add_row("FastMCP", "✓", fastmcp.__version__)
    except ImportError:
        table.add_row("FastMCP", "✗", "Not installed")
    
    # Check personas
    personas = ["Athena", "Artemis", "Hestia", "Bellona", "Seshat"]
    for persona in personas:
        table.add_row(f"Persona: {persona}", "✓", "Available")
    
    # Check configuration
    claude_homes = [
        Path.home() / ".claude" / "mcp_config.json",
        Path.home() / "Library" / "Application Support" / "Claude" / "mcp_config.json",
    ]
    
    config_found = False
    for config_path in claude_homes:
        if config_path.exists():
            table.add_row("Configuration", "✓", str(config_path))
            config_found = True
            break
    
    if not config_found:
        table.add_row("Configuration", "⚠", "Not configured (run: trinitas-mcp setup)")
    
    console.print(table)

@cli.command()
@click.argument('persona', type=click.Choice(['athena', 'artemis', 'hestia', 'bellona', 'seshat']))
@click.argument('task')
def execute(persona: str, task: str):
    """Execute a task with a specific persona"""
    
    console.print(f"[bold blue]🎭 Executing with {persona.title()}[/bold blue]")
    console.print(f"Task: {task}\n")
    
    # Import here to avoid circular dependencies
    from src.core.trinitas_mcp_tools import TrinitasMCPTools
    
    async def run_task():
        tools = TrinitasMCPTools()
        result = await tools.execute_task(persona, task)
        return result
    
    try:
        result = asyncio.run(run_task())
        console.print("[green]✓ Task completed successfully[/green]")
        console.print(Panel(str(result), title="Result", border_style="green"))
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def server():
    """Start the MCP server (for internal use)"""
    from src.mcp_server import run_server
    run_server()

def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()