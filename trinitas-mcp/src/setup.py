#!/usr/bin/env python3
"""
Trinitas MCP Tools Setup Helper
Automated setup for Claude Code integration
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

def find_claude_home() -> Optional[Path]:
    """Find Claude Code home directory"""
    possible_paths = [
        Path.home() / ".claude",
        Path.home() / "Library" / "Application Support" / "Claude",
        Path.home() / "AppData" / "Roaming" / "Claude",
        Path.home() / ".config" / "claude",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def create_mcp_config() -> Dict[str, Any]:
    """Create MCP configuration for Trinitas"""
    return {
        "mcpServers": {
            "trinitas": {
                "command": "uv",
                "args": ["run", "trinitas-server"],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent.parent),
                    "TRINITAS_MODE": "mythology",
                    "TRINITAS_NAMING": "mythology",
                    "AUTO_DETECT": "true"
                }
            }
        }
    }

def merge_configs(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Merge new configuration with existing"""
    if "mcpServers" not in existing:
        existing["mcpServers"] = {}
    
    existing["mcpServers"].update(new["mcpServers"])
    return existing

def setup_claude(auto: bool = False, claude_home: Optional[str] = None) -> bool:
    """
    Setup Trinitas MCP Tools for Claude Code
    
    Args:
        auto: Automatically configure without prompts
        claude_home: Path to Claude home directory
    
    Returns:
        True if setup successful, False otherwise
    """
    print("🚀 Trinitas MCP Tools Setup")
    print("-" * 40)
    
    # Find or validate Claude home
    if claude_home:
        claude_path = Path(claude_home)
        if not claude_path.exists():
            print(f"❌ Claude home not found at: {claude_home}")
            return False
    else:
        claude_path = find_claude_home()
        if not claude_path:
            print("❌ Could not find Claude Code installation")
            print("Please specify Claude home with --claude-home option")
            return False
    
    print(f"✓ Found Claude home: {claude_path}")
    
    # Create MCP configuration
    config_file = claude_path / "mcp_config.json"
    new_config = create_mcp_config()
    
    # Handle existing configuration
    if config_file.exists():
        print(f"Found existing configuration at: {config_file}")
        
        if not auto:
            response = input("Merge with existing configuration? [Y/n]: ")
            if response.lower() == 'n':
                print("Setup cancelled")
                return False
        
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
            
            # Backup existing config
            backup_file = config_file.with_suffix('.json.backup')
            shutil.copy2(config_file, backup_file)
            print(f"✓ Backed up existing config to: {backup_file}")
            
            # Merge configurations
            final_config = merge_configs(existing_config, new_config)
        except json.JSONDecodeError:
            print("⚠ Existing configuration is invalid")
            final_config = new_config
    else:
        final_config = new_config
    
    # Write configuration
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(final_config, f, indent=2)
    
    print(f"✓ Configuration written to: {config_file}")
    
    # Create agents directory if needed
    agents_dir = claude_path / "agents"
    if not agents_dir.exists():
        agents_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created agents directory: {agents_dir}")
    
    # Copy agent files if they exist
    source_agents = Path(__file__).parent.parent / "agents"
    if source_agents.exists():
        agent_files = [
            "athena-strategist.md",
            "artemis-optimizer.md",
            "hestia-auditor.md",
            "bellona-coordinator.md",
            "seshat-documenter.md"
        ]
        
        for agent_file in agent_files:
            source = source_agents / agent_file
            if source.exists():
                dest = agents_dir / agent_file
                if not dest.exists() or auto:
                    shutil.copy2(source, dest)
                    print(f"✓ Installed agent: {agent_file}")
    
    print()
    print("✨ Setup Complete!")
    print("-" * 40)
    print("Next steps:")
    print("1. Restart Claude Code")
    print("2. Trinitas tools will be available automatically")
    print("3. Try: 'Plan a system architecture' to activate Athena")
    print()
    print("**Athena**: 'ふふ、準備が整いましたわ'")
    print("**Artemis**: 'フン、効率的なセットアップね'")
    print("**Hestia**: '……セキュリティも……確認済み……'")
    
    return True

def main():
    """Main entry point for setup command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Trinitas MCP Tools")
    parser.add_argument('--auto', action='store_true', help='Automatic setup')
    parser.add_argument('--claude-home', help='Path to Claude home directory')
    
    args = parser.parse_args()
    
    success = setup_claude(auto=args.auto, claude_home=args.claude_home)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()