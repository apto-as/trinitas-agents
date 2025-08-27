#!/usr/bin/env python3
"""
Trinitas Project - Persona Renaming Script
Safely renames all persona references across the codebase
"""

import os
import re
import yaml
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import json

class PersonaRenamer:
    """Handles safe renaming of personas across all files"""
    
    def __init__(self, config_file: str = "personas.yaml", backup: bool = True):
        """Initialize with configuration"""
        self.config_file = config_file
        self.backup = backup
        self.load_config()
        self.build_replacement_map()
        
    def load_config(self):
        """Load persona configuration"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.personas = self.config['personas']
        self.system = self.config['system']
        
    def build_replacement_map(self) -> Dict[str, str]:
        """Build comprehensive replacement mappings"""
        self.replacements = {}
        
        # Persona names (case variations)
        for key, persona in self.personas.items():
            original = persona['original_name']
            new = persona['name']
            
            # Add various case combinations
            self.replacements[original] = new
            self.replacements[original.lower()] = new.lower()
            self.replacements[original.upper()] = new.upper()
            
            # Handle title references
            if original == "Springfield":
                self.replacements["Mother Brain"] = "Strategic Mind"
            elif original == "Krukai":
                self.replacements["404"] = "Perfectionist"
                self.replacements["404 Standard"] = "Elite Standard"
                self.replacements["404の誇り"] = "Elite pride"
            elif original == "Vector":
                self.replacements["Oracle"] = "Guardian"
        
        # Location names
        self.replacements.update({
            "カフェ・ズッケロ": self.system['locations']['primary_base'],
            "Café Zuccaro": self.system['locations']['primary_base'],
            "Cafe Zuccaro": self.system['locations']['primary_base'],
            "Café Zuccaro": self.system['locations']['primary_base'],
            "エルモ号": self.system['locations']['mobile_base'],
            "Elmo-go": self.system['locations']['mobile_base'],
            "Elmo": self.system['locations']['mobile_base'],
            "Node-Prime": "Cafe Olympus",
            "Base-Mobile-01": "Argonauts",
            "Olympus Hub": "Cafe Olympus",
            "Argo Command": "Argonauts",
        })
        
        # Organization names
        self.replacements.update({
            "Griffin Systems": self.system['organizations']['corporation'],
            "H.I.D.E. 404": self.system['organizations']['elite_unit'],
            "Phoenix Protocol": self.system['organizations']['incident'],
        })
        
        # Japanese terms (keep Commander as is per user preference)
        self.replacements.update({
            "ふふ": "Hmm",
            "フン": "Hmph",
        })
        
        return self.replacements
    
    def get_files_to_process(self, extensions: List[str] = None) -> List[Path]:
        """Get all files to process"""
        if extensions is None:
            extensions = ['.py', '.md', '.yaml', '.yml', '.json', '.txt']
        
        files = []
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.env', 'venv'}
        exclude_files = {'personas.yaml', 'rename_personas.py'}
        
        for ext in extensions:
            for file_path in Path('.').rglob(f'*{ext}'):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                # Skip excluded files
                if file_path.name in exclude_files:
                    continue
                # Skip backup files
                if file_path.suffix == '.bak' or file_path.suffix == '.original':
                    continue
                    
                files.append(file_path)
        
        return files
    
    def create_backup(self, file_path: Path):
        """Create backup of file"""
        if self.backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.original')
            if not backup_path.exists():
                shutil.copy2(file_path, backup_path)
                print(f"  Backup created: {backup_path}")
    
    def replace_in_file(self, file_path: Path) -> int:
        """Replace all occurrences in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacement_count = 0
            
            # Apply replacements
            for old, new in self.replacements.items():
                # Use word boundaries for more accurate replacement
                pattern = r'\b' + re.escape(old) + r'\b'
                new_content = re.sub(pattern, new, content)
                
                if new_content != content:
                    replacement_count += len(re.findall(pattern, content))
                    content = new_content
            
            # Write back if changes were made
            if content != original_content:
                self.create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Updated: {file_path} ({replacement_count} replacements)")
                return replacement_count
            
            return 0
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            return 0
    
    def run(self, dry_run: bool = False):
        """Execute the renaming process"""
        print("=" * 60)
        print("Trinitas Project - Persona Renaming Tool")
        print("=" * 60)
        
        if dry_run:
            print("DRY RUN MODE - No changes will be made")
            print()
        
        # Get files to process
        files = self.get_files_to_process()
        print(f"Found {len(files)} files to process")
        print()
        
        # Show replacement mappings
        print("Replacement mappings:")
        for old, new in sorted(self.replacements.items()):
            if old != old.lower() and old != old.upper():  # Skip case variants
                print(f"  {old} → {new}")
        print()
        
        if dry_run:
            print("Files that would be modified:")
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                for old in self.replacements:
                    if old in content:
                        print(f"  - {file_path}")
                        break
        else:
            # Process files
            print("Processing files...")
            total_replacements = 0
            modified_files = 0
            
            for file_path in files:
                count = self.replace_in_file(file_path)
                if count > 0:
                    total_replacements += count
                    modified_files += 1
            
            print()
            print("=" * 60)
            print(f"Summary:")
            print(f"  Files modified: {modified_files}")
            print(f"  Total replacements: {total_replacements}")
            if self.backup:
                print(f"  Backups created with .original extension")
            print("=" * 60)
    
    def restore_from_backup(self):
        """Restore all files from backup"""
        print("Restoring from backups...")
        restored = 0
        
        for backup_file in Path('.').rglob('*.original'):
            original_file = backup_file.with_suffix('')
            shutil.copy2(backup_file, original_file)
            print(f"  Restored: {original_file}")
            restored += 1
        
        print(f"Restored {restored} files")
    
    def clean_backups(self):
        """Remove all backup files"""
        print("Cleaning backup files...")
        removed = 0
        
        for backup_file in Path('.').rglob('*.original'):
            backup_file.unlink()
            print(f"  Removed: {backup_file}")
            removed += 1
        
        print(f"Removed {removed} backup files")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Rename personas across Trinitas Project codebase"
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--no-backup', '-n',
        action='store_true',
        help='Skip creating backup files'
    )
    parser.add_argument(
        '--restore', '-r',
        action='store_true',
        help='Restore files from backup'
    )
    parser.add_argument(
        '--clean', '-c',
        action='store_true',
        help='Remove backup files'
    )
    parser.add_argument(
        '--config', '-f',
        default='personas.yaml',
        help='Path to configuration file (default: personas.yaml)'
    )
    
    args = parser.parse_args()
    
    # Initialize renamer
    renamer = PersonaRenamer(
        config_file=args.config,
        backup=not args.no_backup
    )
    
    # Execute requested action
    if args.restore:
        renamer.restore_from_backup()
    elif args.clean:
        renamer.clean_backups()
    else:
        renamer.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()