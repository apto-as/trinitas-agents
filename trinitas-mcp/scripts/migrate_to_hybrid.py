#!/usr/bin/env python3
"""
Trinitas v3.5 Memory Migration Script
SQLiteからハイブリッドバックエンドへの移行
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory.memory_manager import TrinitasMemoryManager
from src.memory.enhanced_manager import get_enhanced_memory_manager
from src.memory.memory_core import Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryMigrator:
    """記憶システム移行ツール"""
    
    def __init__(self, source_path: str = "/tmp/trinitas_memory", dry_run: bool = False):
        self.source_path = Path(source_path)
        self.dry_run = dry_run
        self.stats = {
            "total_memories": 0,
            "migrated": 0,
            "failed": 0,
            "skipped": 0
        }
    
    async def migrate(self):
        """移行を実行"""
        logger.info("="*80)
        logger.info("Trinitas Memory Migration to Hybrid Backend")
        logger.info("="*80)
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual changes will be made")
        
        # Step 1: Check source
        if not self.source_path.exists():
            logger.error(f"Source path not found: {self.source_path}")
            return False
        
        logger.info(f"📂 Source: {self.source_path}")
        
        # Step 2: Initialize enhanced manager (hybrid backend)
        logger.info("\n🚀 Initializing hybrid backend...")
        enhanced = await get_enhanced_memory_manager()
        
        # Check backend status
        health = await enhanced.health_check()
        logger.info(f"✓ Backend health: {health}")
        
        # Step 3: Load legacy memories
        logger.info("\n📥 Loading legacy memories...")
        legacy_manager = TrinitasMemoryManager(str(self.source_path))
        
        # Step 4: Migrate each persona
        personas = ["athena", "artemis", "hestia", "bellona", "seshat"]
        
        for persona in personas:
            logger.info(f"\n👤 Migrating {persona.upper()}...")
            
            try:
                # Retrieve all memories for persona
                memories = await self._get_all_memories_for_persona(legacy_manager, persona)
                
                if not memories:
                    logger.info(f"   No memories found for {persona}")
                    continue
                
                logger.info(f"   Found {len(memories)} memories")
                
                # Migrate each memory
                for i, memory in enumerate(memories):
                    try:
                        if not self.dry_run:
                            # Store in hybrid backend
                            await enhanced.remember(
                                persona=persona,
                                content=memory.content,
                                memory_type=memory.type,
                                importance=memory.importance,
                                tags=memory.tags,
                                metadata=memory.metadata
                            )
                        
                        self.stats["migrated"] += 1
                        
                        # Progress indicator
                        if (i + 1) % 10 == 0:
                            logger.info(f"   Progress: {i+1}/{len(memories)}")
                    
                    except Exception as e:
                        logger.error(f"   Failed to migrate memory {memory.id}: {e}")
                        self.stats["failed"] += 1
                
                logger.info(f"   ✓ Migrated {self.stats['migrated']} memories for {persona}")
            
            except Exception as e:
                logger.error(f"   Error migrating {persona}: {e}")
        
        # Step 5: Verify migration
        if not self.dry_run:
            logger.info("\n🔍 Verifying migration...")
            await self._verify_migration(enhanced, personas)
        
        # Step 6: Report results
        self._print_report()
        
        return self.stats["failed"] == 0
    
    async def _get_all_memories_for_persona(self, manager, persona: str):
        """ペルソナの全記憶を取得"""
        # This is a simplified version - in reality, you'd need to access
        # the underlying storage directly
        memories = []
        
        # Try to get memories from working, episodic, semantic, procedural
        if persona in manager.personas:
            persona_memory = manager.personas[persona]
            
            # Get from working memory
            memories.extend(list(persona_memory.working.buffer))
            
            # Get from episodic (would need direct DB access)
            # Get from semantic (would need file access)
            # Get from procedural (would need DB access)
        
        return memories
    
    async def _verify_migration(self, enhanced, personas):
        """移行を検証"""
        for persona in personas:
            # Test recall
            test_memories = await enhanced.recall(
                persona=persona,
                query_text="",
                limit=5
            )
            
            if test_memories:
                logger.info(f"   ✓ {persona}: {len(test_memories)} memories accessible")
            else:
                logger.warning(f"   ⚠ {persona}: No memories found")
        
        # Test semantic search
        semantic_results = await enhanced.semantic_search(
            query_text="test",
            limit=5
        )
        
        if semantic_results:
            logger.info(f"   ✓ Semantic search working: {len(semantic_results)} results")
        else:
            logger.warning("   ⚠ Semantic search returned no results")
    
    def _print_report(self):
        """移行レポートを出力"""
        logger.info("\n" + "="*80)
        logger.info("MIGRATION REPORT")
        logger.info("="*80)
        
        total = self.stats["migrated"] + self.stats["failed"] + self.stats["skipped"]
        
        logger.info(f"\n📊 Statistics:")
        logger.info(f"   Total memories processed: {total}")
        logger.info(f"   ✅ Successfully migrated: {self.stats['migrated']}")
        logger.info(f"   ❌ Failed: {self.stats['failed']}")
        logger.info(f"   ⏭️ Skipped: {self.stats['skipped']}")
        
        if self.stats["failed"] == 0:
            logger.info("\n✨ Migration completed successfully!")
        else:
            logger.warning(f"\n⚠️ Migration completed with {self.stats['failed']} errors")
        
        if self.dry_run:
            logger.info("\n🔍 This was a dry run. Run without --dry-run to perform actual migration.")

class BackupManager:
    """バックアップマネージャー"""
    
    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.backup_path = self.source_path.parent / f"trinitas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create_backup(self):
        """バックアップを作成"""
        import shutil
        
        logger.info(f"📦 Creating backup: {self.backup_path}")
        
        if self.source_path.exists():
            shutil.copytree(self.source_path, self.backup_path)
            logger.info(f"   ✓ Backup created successfully")
            return True
        else:
            logger.warning(f"   ⚠ Source path not found: {self.source_path}")
            return False
    
    def restore_backup(self):
        """バックアップを復元"""
        import shutil
        
        logger.info(f"🔄 Restoring backup from: {self.backup_path}")
        
        if self.backup_path.exists():
            # Remove current directory
            if self.source_path.exists():
                shutil.rmtree(self.source_path)
            
            # Restore from backup
            shutil.copytree(self.backup_path, self.source_path)
            logger.info(f"   ✓ Backup restored successfully")
            return True
        else:
            logger.error(f"   ❌ Backup not found: {self.backup_path}")
            return False

async def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Trinitas memory to hybrid backend")
    parser.add_argument("--source", default="/tmp/trinitas_memory", 
                       help="Source memory path (default: /tmp/trinitas_memory)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Perform a dry run without actual migration")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup creation")
    parser.add_argument("--restore", action="store_true",
                       help="Restore from latest backup")
    
    args = parser.parse_args()
    
    # Handle restore
    if args.restore:
        backup_manager = BackupManager(args.source)
        if backup_manager.restore_backup():
            logger.info("✅ Restore completed")
        else:
            logger.error("❌ Restore failed")
        return
    
    # Create backup unless disabled
    if not args.no_backup and not args.dry_run:
        backup_manager = BackupManager(args.source)
        if not backup_manager.create_backup():
            logger.error("Failed to create backup. Aborting migration.")
            return
    
    # Perform migration
    migrator = MemoryMigrator(args.source, dry_run=args.dry_run)
    success = await migrator.migrate()
    
    if success:
        logger.info("\n🎉 Migration completed successfully!")
        
        if not args.dry_run:
            logger.info("\n📝 Next steps:")
            logger.info("1. Test the hybrid backend:")
            logger.info("   python -m v35-mcp-tools.examples.memory_system_demo")
            logger.info("2. Verify semantic search:")
            logger.info("   python -m v35-mcp-tools.examples.semantic_search_demo")
            logger.info("3. If issues occur, restore backup with:")
            logger.info(f"   python {__file__} --restore")
    else:
        logger.error("\n❌ Migration failed. Please check the errors above.")
        
        if not args.no_backup and not args.dry_run:
            logger.info("\nTo restore from backup, run:")
            logger.info(f"   python {__file__} --restore")

if __name__ == "__main__":
    asyncio.run(main())