#!/usr/bin/env python3
"""
Trinitas Settings Merger - Safe Integration with Existing Hooks
Vector: "……既存の設定を破壊することなく、慎重に統合する……"
Springfield: "ユーザーの既存設定を尊重しながら、新機能を追加します"
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import copy
import argparse
from datetime import datetime

class SettingsMerger:
    """Safely merge Trinitas parallel agent settings with existing configurations"""
    
    def __init__(self, existing_settings_path: str):
        self.existing_path = Path(existing_settings_path)
        self.existing_settings = self._load_existing_settings()
        self.backup_created = False
        
    def _load_existing_settings(self) -> Dict[str, Any]:
        """Load existing settings.json"""
        if not self.existing_path.exists():
            print(f"[INFO] No existing settings found at {self.existing_path}")
            return {"hooks": {}}
        
        try:
            with open(self.existing_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in existing settings: {e}")
            sys.exit(1)
    
    def create_backup(self) -> Path:
        """Create backup of existing settings"""
        if not self.existing_path.exists():
            return None
            
        backup_path = self.existing_path.with_suffix(
            f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(self.existing_settings, f, indent=2)
        
        self.backup_created = True
        print(f"[SUCCESS] Backup created: {backup_path}")
        return backup_path
    
    def check_conflicts(self) -> List[str]:
        """Check for potential conflicts with existing hooks"""
        conflicts = []
        hooks = self.existing_settings.get('hooks', {})
        
        # Check for existing SubagentStop hooks
        if 'SubagentStop' in hooks:
            for entry in hooks['SubagentStop']:
                if entry.get('matcher') == 'Task':
                    conflicts.append(
                        "Existing SubagentStop hook for Task tool detected. "
                        "This may interfere with parallel agent result capture."
                    )
        
        # Check for conflicting PreToolUse hooks
        if 'PreToolUse' in hooks:
            for entry in hooks['PreToolUse']:
                if entry.get('matcher') == 'Task':
                    # Check if it's our prepare_parallel_tasks.py
                    commands = [h.get('command', '') for h in entry.get('hooks', [])]
                    if not any('prepare_parallel_tasks.py' in cmd for cmd in commands):
                        conflicts.append(
                            "Existing PreToolUse hook for Task tool detected. "
                            "This may prevent parallel task preparation."
                        )
        
        # Check for Python environment conflicts
        for hook_type, entries in hooks.items():
            for entry in entries:
                for hook in entry.get('hooks', []):
                    if hook.get('type') == 'command' and '.py' in hook.get('command', ''):
                        if 'environment' not in hook or 'PYTHONPATH' not in hook.get('environment', {}):
                            conflicts.append(
                                f"Python hook without PYTHONPATH in {hook_type}. "
                                "May cause import errors for Trinitas Python modules."
                            )
        
        return conflicts
    
    def merge_settings(self, parallel_enabled: bool = True) -> Dict[str, Any]:
        """Merge Trinitas parallel settings with existing configuration"""
        merged = copy.deepcopy(self.existing_settings)
        
        if 'hooks' not in merged:
            merged['hooks'] = {}
        
        hooks = merged['hooks']
        
        # Add SubagentStop hook (critical for parallel execution)
        if parallel_enabled:
            if 'SubagentStop' not in hooks:
                hooks['SubagentStop'] = []
            
            # Check if our capture hook already exists
            task_subagent_exists = False
            for entry in hooks['SubagentStop']:
                if entry.get('matcher') == 'Task':
                    commands = [h.get('command', '') for h in entry.get('hooks', [])]
                    if any('capture_subagent_result.sh' in cmd for cmd in commands):
                        task_subagent_exists = True
                        break
            
            if not task_subagent_exists:
                # Add our SubagentStop configuration
                hooks['SubagentStop'].append({
                    "matcher": "Task",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "~/.claude/trinitas/hooks/post-execution/capture_subagent_result.sh"
                        },
                        {
                            "type": "command",
                            "command": "~/.claude/trinitas/hooks/python/integrate_parallel_results.py",
                            "runCondition": "TRINITAS_INTEGRATION_SESSION"
                        }
                    ]
                })
                print("[INFO] Added SubagentStop hooks for parallel execution")
        
        # Add PreToolUse hook for task preparation
        if parallel_enabled:
            if 'PreToolUse' not in hooks:
                hooks['PreToolUse'] = []
            
            # Check if prepare_parallel_tasks already exists
            task_prepare_exists = False
            for entry in hooks['PreToolUse']:
                if entry.get('matcher') == 'Task':
                    commands = [h.get('command', '') for h in entry.get('hooks', [])]
                    if any('prepare_parallel_tasks.py' in cmd for cmd in commands):
                        task_prepare_exists = True
                        break
            
            if not task_prepare_exists:
                # Insert at beginning to run before other Task hooks
                hooks['PreToolUse'].insert(0, {
                    "matcher": "Task",
                    "hooks": [{
                        "type": "command",
                        "command": "~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py",
                        "environment": {
                            "TRINITAS_PARALLEL_ENABLED": "true" if parallel_enabled else "false"
                        }
                    }]
                })
                print("[INFO] Added PreToolUse hook for parallel task preparation")
        
        return merged
    
    def validate_merged_settings(self, merged: Dict[str, Any]) -> List[str]:
        """Validate the merged settings for potential issues"""
        issues = []
        
        # Check for duplicate commands
        seen_commands = set()
        hooks = merged.get('hooks', {})
        
        for hook_type, entries in hooks.items():
            for entry in entries:
                for hook in entry.get('hooks', []):
                    cmd = hook.get('command', '')
                    if cmd in seen_commands:
                        issues.append(f"Duplicate command found: {cmd}")
                    seen_commands.add(cmd)
        
        # Check hook order dependencies
        if 'PreToolUse' in hooks:
            task_hooks = [e for e in hooks['PreToolUse'] if e.get('matcher') == 'Task']
            if len(task_hooks) > 1:
                # Ensure prepare_parallel_tasks runs first
                first_hooks = task_hooks[0].get('hooks', [])
                if not any('prepare_parallel_tasks.py' in h.get('command', '') for h in first_hooks):
                    issues.append(
                        "prepare_parallel_tasks.py should run before other Task PreToolUse hooks"
                    )
        
        return issues
    
    def write_merged_settings(self, merged: Dict[str, Any], output_path: str = None) -> Path:
        """Write merged settings to file"""
        if output_path:
            output = Path(output_path)
        else:
            output = self.existing_path
        
        # Ensure directory exists
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Merged settings written to: {output}")
        return output

def main():
    """Main entry point for settings merger"""
    parser = argparse.ArgumentParser(
        description="Safely merge Trinitas parallel agent settings"
    )
    parser.add_argument(
        'settings_path',
        help='Path to existing settings.json'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path for merged settings (default: overwrite existing)'
    )
    parser.add_argument(
        '--disable-parallel',
        action='store_true',
        help='Disable parallel agent features'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force merge even with conflicts'
    )
    
    args = parser.parse_args()
    
    # Create merger
    merger = SettingsMerger(args.settings_path)
    
    # Check conflicts
    conflicts = merger.check_conflicts()
    if conflicts and not args.force:
        print("\n[WARNING] Potential conflicts detected:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        print("\nUse --force to proceed anyway, or resolve conflicts manually.")
        return 1
    
    # Create backup (unless dry run)
    if not args.dry_run:
        merger.create_backup()
    
    # Merge settings
    merged = merger.merge_settings(parallel_enabled=not args.disable_parallel)
    
    # Validate
    issues = merger.validate_merged_settings(merged)
    if issues:
        print("\n[WARNING] Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Write or display result
    if args.dry_run:
        print("\n[DRY RUN] Merged settings would be:")
        print(json.dumps(merged, indent=2))
    else:
        merger.write_merged_settings(merged, args.output)
    
    print("\n[SUCCESS] Settings merge completed!")
    return 0

if __name__ == '__main__':
    sys.exit(main())