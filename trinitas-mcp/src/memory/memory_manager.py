#!/usr/bin/env python3
"""
Trinitas v3.5 Memory Manager
統合記憶管理システム
"""

import asyncio
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging
from dataclasses import dataclass, field
from enum import Enum

from .memory_core import (
    MemoryItem, MemoryType, MemoryPriority, Context, Query,
    WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory
)

logger = logging.getLogger(__name__)

# Persona configurations
PERSONA_MEMORY_CONFIG = {
    "athena": {
        "priorities": {
            MemoryType.SEMANTIC: MemoryPriority.HIGH,
            MemoryType.EPISODIC: MemoryPriority.MEDIUM,
            MemoryType.PROCEDURAL: MemoryPriority.HIGH
        },
        "retention": {
            "architecture_decisions": None,  # Permanent
            "project_outcomes": 90 * 24 * 3600,  # 90 days
            "team_interactions": 30 * 24 * 3600  # 30 days
        },
        "focus": ["architecture", "planning", "strategy", "team", "project"]
    },
    "artemis": {
        "priorities": {
            MemoryType.PROCEDURAL: MemoryPriority.HIGH,
            MemoryType.SEMANTIC: MemoryPriority.HIGH,
            MemoryType.EPISODIC: MemoryPriority.LOW
        },
        "retention": {
            "optimization_patterns": None,  # Permanent
            "performance_benchmarks": 60 * 24 * 3600,  # 60 days
            "code_snippets": 30 * 24 * 3600  # 30 days
        },
        "focus": ["optimization", "performance", "algorithm", "efficiency", "code"]
    },
    "hestia": {
        "priorities": {
            MemoryType.EPISODIC: MemoryPriority.HIGH,
            MemoryType.SEMANTIC: MemoryPriority.HIGH,
            MemoryType.PROCEDURAL: MemoryPriority.HIGH
        },
        "retention": {
            "security_incidents": None,  # Permanent
            "vulnerability_patterns": None,  # Permanent
            "threat_intelligence": 30 * 24 * 3600  # 30 days
        },
        "focus": ["security", "vulnerability", "threat", "risk", "compliance"]
    },
    "bellona": {
        "priorities": {
            MemoryType.PROCEDURAL: MemoryPriority.HIGH,
            MemoryType.EPISODIC: MemoryPriority.MEDIUM,
            MemoryType.SEMANTIC: MemoryPriority.MEDIUM
        },
        "retention": {
            "successful_strategies": 60 * 24 * 3600,  # 60 days
            "resource_patterns": 30 * 24 * 3600,  # 30 days
            "execution_timelines": 14 * 24 * 3600  # 14 days
        },
        "focus": ["execution", "tactics", "resources", "timeline", "coordination"]
    },
    "seshat": {
        "priorities": {
            MemoryType.SEMANTIC: MemoryPriority.HIGH,
            MemoryType.PROCEDURAL: MemoryPriority.HIGH,
            MemoryType.EPISODIC: MemoryPriority.MEDIUM
        },
        "retention": {
            "documentation_templates": None,  # Permanent
            "knowledge_structure": None,  # Permanent
            "revision_history": 60 * 24 * 3600  # 60 days
        },
        "focus": ["documentation", "knowledge", "organization", "retrieval", "standards"]
    }
}

@dataclass
class PersonaMemory:
    """ペルソナ固有の記憶システム"""
    persona: str
    working: WorkingMemory
    episodic: EpisodicMemory
    semantic: SemanticMemory
    procedural: ProceduralMemory
    config: Dict[str, Any]
    
    async def store(self, item: MemoryItem):
        """記憶を適切な層に保存"""
        # Set persona
        item.persona = self.persona
        
        # Always add to working memory first
        await self.working.store(item)
        
        # Store in appropriate long-term memory based on type
        if item.type == MemoryType.EPISODIC:
            await self.episodic.store(item)
        elif item.type == MemoryType.SEMANTIC:
            await self.semantic.store(item)
        elif item.type == MemoryType.PROCEDURAL:
            await self.procedural.store(item)
    
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """多層検索"""
        results = []
        
        # 1. Check working memory first (fastest)
        working_results = await self.working.retrieve(query)
        results.extend(working_results)
        
        # 2. Check long-term memories based on query needs
        if query.needs_experience or self._is_focus_related(query.text, "experience"):
            episodic_results = await self.episodic.retrieve(query)
            results.extend(episodic_results)
        
        if query.needs_knowledge or self._is_focus_related(query.text, "knowledge"):
            semantic_results = await self.semantic.retrieve(query)
            results.extend(semantic_results)
        
        if query.needs_procedure or self._is_focus_related(query.text, "procedure"):
            procedural_results = await self.procedural.retrieve(query)
            results.extend(procedural_results)
        
        # Remove duplicates and sort by relevance
        seen_ids = set()
        unique_results = []
        for item in results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)
        
        return unique_results[:query.limit]
    
    def _is_focus_related(self, text: str, category: str) -> bool:
        """テキストがフォーカス領域に関連するか確認"""
        text_lower = text.lower()
        focus_areas = self.config.get("focus", [])
        
        for area in focus_areas:
            if area in text_lower:
                return True
        
        # Category-specific keywords
        if category == "experience":
            return any(word in text_lower for word in ["previous", "past", "history", "before"])
        elif category == "knowledge":
            return any(word in text_lower for word in ["what", "how", "concept", "definition"])
        elif category == "procedure":
            return any(word in text_lower for word in ["steps", "process", "method", "technique"])
        
        return False

class MemoryConsolidator:
    """記憶の固定化と転送を管理"""
    
    def __init__(self, persona_memory: PersonaMemory):
        self.persona_memory = persona_memory
        self.consolidation_threshold = 0.7
    
    async def consolidate(self):
        """短期記憶から長期記憶への固定化"""
        # Get all items from working memory
        query = Query(text="", limit=100)  # Get all
        working_items = await self.persona_memory.working.retrieve(query)
        
        for item in working_items:
            # Evaluate importance for consolidation
            if self._should_consolidate(item):
                # Determine target memory type if not set
                if item.type == MemoryType.WORKING:
                    item.type = self._determine_memory_type(item)
                
                # Store in long-term memory
                await self.persona_memory.store(item)
                
                # Optionally remove from working memory if old
                if self._is_old(item):
                    await self.persona_memory.working.forget(item.id)
    
    def _should_consolidate(self, item: MemoryItem) -> bool:
        """固定化すべきか判定"""
        # High importance items
        if item.importance > self.consolidation_threshold:
            return True
        
        # Frequently accessed items
        if item.access_count > 5:
            return True
        
        # Items matching persona focus
        focus_areas = self.persona_memory.config.get("focus", [])
        content_str = str(item.content).lower()
        if any(area in content_str for area in focus_areas):
            return True
        
        return False
    
    def _determine_memory_type(self, item: MemoryItem) -> MemoryType:
        """記憶タイプを推定"""
        content = str(item.content).lower()
        
        # Check for procedural patterns
        if any(word in content for word in ["steps", "process", "method", "algorithm", "technique"]):
            return MemoryType.PROCEDURAL
        
        # Check for knowledge/concepts
        if any(word in content for word in ["definition", "concept", "theory", "principle", "rule"]):
            return MemoryType.SEMANTIC
        
        # Default to episodic
        return MemoryType.EPISODIC
    
    def _is_old(self, item: MemoryItem) -> bool:
        """古い記憶か判定"""
        age = datetime.now() - item.timestamp
        return age.total_seconds() > 3600  # 1 hour

class ForgettingCurve:
    """エビングハウスの忘却曲線による記憶管理"""
    
    def __init__(self, persona_memory: PersonaMemory):
        self.persona_memory = persona_memory
    
    def calculate_retention(self, item: MemoryItem) -> float:
        """保持率を計算"""
        # Time-based decay
        time_elapsed = datetime.now() - item.last_access
        days = time_elapsed.total_seconds() / (24 * 3600)
        base_retention = math.exp(-days / 30)  # 30-day half-life
        
        # Access frequency bonus
        frequency_bonus = min(item.access_count * 0.05, 0.3)
        
        # Importance bonus
        importance_bonus = item.importance * 0.2
        
        # Persona priority bonus
        priority = self.persona_memory.config["priorities"].get(
            item.type, MemoryPriority.MEDIUM
        ).value / 5.0 * 0.2
        
        total_retention = base_retention + frequency_bonus + importance_bonus + priority
        return min(total_retention, 1.0)
    
    async def prune_memories(self):
        """低保持率の記憶を削除"""
        # Check episodic memory
        all_episodes = await self._get_all_episodes()
        for item in all_episodes:
            retention = self.calculate_retention(item)
            if retention < 0.1:
                await self.persona_memory.episodic.forget(item.id)
                logger.info(f"Pruned episodic memory: {item.id}")
        
        # Check semantic memory (more conservative)
        all_knowledge = await self._get_all_knowledge()
        for item in all_knowledge:
            retention = self.calculate_retention(item)
            if retention < 0.05:  # Higher threshold for semantic
                await self.persona_memory.semantic.forget(item.id)
                logger.info(f"Pruned semantic memory: {item.id}")
    
    async def _get_all_episodes(self) -> List[MemoryItem]:
        """全エピソードを取得"""
        query = Query(text="", limit=1000)
        return await self.persona_memory.episodic.retrieve(query)
    
    async def _get_all_knowledge(self) -> List[MemoryItem]:
        """全知識を取得"""
        query = Query(text="", limit=1000)
        return await self.persona_memory.semantic.retrieve(query)

class TrinitasMemoryManager:
    """Trinitas統合記憶管理システム"""
    
    def __init__(self, storage_base: str = "/tmp/trinitas_memory"):
        self.storage_base = Path(storage_base)
        self.storage_base.mkdir(parents=True, exist_ok=True)
        
        self.personas: Dict[str, PersonaMemory] = {}
        self.consolidators: Dict[str, MemoryConsolidator] = {}
        self.forgetting_curves: Dict[str, ForgettingCurve] = {}
        
        self._initialize_personas()
        
        # Start background tasks
        self.consolidation_task = None
        self.pruning_task = None
    
    def _initialize_personas(self):
        """各ペルソナの記憶システムを初期化"""
        for persona_name, config in PERSONA_MEMORY_CONFIG.items():
            # Create storage paths
            persona_path = self.storage_base / persona_name
            persona_path.mkdir(exist_ok=True)
            
            # Initialize memory components
            persona_memory = PersonaMemory(
                persona=persona_name,
                working=WorkingMemory(capacity=9),
                episodic=EpisodicMemory(str(persona_path / "episodes.db")),
                semantic=SemanticMemory(str(persona_path / "knowledge")),
                procedural=ProceduralMemory(str(persona_path / "procedures.db")),
                config=config
            )
            
            self.personas[persona_name] = persona_memory
            self.consolidators[persona_name] = MemoryConsolidator(persona_memory)
            self.forgetting_curves[persona_name] = ForgettingCurve(persona_memory)
        
        logger.info(f"Initialized memory for {len(self.personas)} personas")
    
    async def remember(self, persona: str, content: Any, 
                      memory_type: Optional[MemoryType] = None,
                      importance: float = 0.5,
                      tags: Optional[List[str]] = None) -> MemoryItem:
        """記憶を保存"""
        if persona not in self.personas:
            raise ValueError(f"Unknown persona: {persona}")
        
        # Auto-determine memory type if not specified
        if memory_type is None:
            memory_type = self._infer_memory_type(content)
        
        # Create memory item
        item = MemoryItem(
            id="",  # Will be auto-generated
            persona=persona,
            content=content,
            type=memory_type,
            importance=importance,
            tags=tags or []
        )
        
        # Store in persona memory
        await self.personas[persona].store(item)
        
        logger.info(f"Stored {memory_type.value} memory for {persona}: {item.id}")
        return item
    
    async def recall(self, persona: str, query_text: str,
                    context: Optional[Context] = None,
                    limit: int = 5) -> List[MemoryItem]:
        """記憶を想起"""
        if persona not in self.personas:
            raise ValueError(f"Unknown persona: {persona}")
        
        # Create query
        query = Query(
            text=query_text,
            context=context,
            limit=limit,
            needs_experience=True,
            needs_knowledge=True,
            needs_procedure=True
        )
        
        # Retrieve from persona memory
        results = await self.personas[persona].retrieve(query)
        
        logger.info(f"Retrieved {len(results)} memories for {persona}")
        return results
    
    async def share_memory(self, from_persona: str, to_persona: str,
                          memory_id: str):
        """ペルソナ間で記憶を共有"""
        # Find memory in from_persona
        query = Query(text=memory_id, limit=1)
        memories = await self.personas[from_persona].retrieve(query)
        
        if not memories:
            logger.warning(f"Memory {memory_id} not found in {from_persona}")
            return
        
        # Copy to to_persona
        memory = memories[0]
        memory.persona = to_persona
        memory.metadata["shared_from"] = from_persona
        memory.metadata["shared_at"] = datetime.now().isoformat()
        
        await self.personas[to_persona].store(memory)
        logger.info(f"Shared memory from {from_persona} to {to_persona}")
    
    def _infer_memory_type(self, content: Any) -> MemoryType:
        """コンテンツから記憶タイプを推論"""
        content_str = str(content).lower()
        
        # Check for patterns
        if any(word in content_str for word in ["method", "algorithm", "process", "steps"]):
            return MemoryType.PROCEDURAL
        elif any(word in content_str for word in ["concept", "definition", "theory"]):
            return MemoryType.SEMANTIC
        else:
            return MemoryType.EPISODIC
    
    async def start_background_tasks(self):
        """バックグラウンドタスクを開始"""
        if not self.consolidation_task:
            self.consolidation_task = asyncio.create_task(self._consolidation_loop())
        if not self.pruning_task:
            self.pruning_task = asyncio.create_task(self._pruning_loop())
    
    async def stop_background_tasks(self):
        """バックグラウンドタスクを停止"""
        if self.consolidation_task:
            self.consolidation_task.cancel()
        if self.pruning_task:
            self.pruning_task.cancel()
    
    async def _consolidation_loop(self):
        """定期的な記憶固定化"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                for persona_name, consolidator in self.consolidators.items():
                    await consolidator.consolidate()
                    logger.debug(f"Consolidated memory for {persona_name}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consolidation error: {e}")
    
    async def _pruning_loop(self):
        """定期的な記憶整理"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hour
                for persona_name, curve in self.forgetting_curves.items():
                    await curve.prune_memories()
                    logger.debug(f"Pruned memory for {persona_name}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pruning error: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """記憶統計を取得"""
        stats = {}
        for persona_name, persona_memory in self.personas.items():
            stats[persona_name] = {
                "working_memory_size": len(persona_memory.working.buffer),
                "working_memory_capacity": persona_memory.working.capacity,
                # Additional stats would require async methods
            }
        return stats

# Global instance
memory_manager = None

async def initialize_memory_manager(storage_base: Optional[str] = None):
    """グローバルメモリマネージャーを初期化"""
    global memory_manager
    if not memory_manager:
        memory_manager = TrinitasMemoryManager(
            storage_base or "/tmp/trinitas_memory"
        )
        await memory_manager.start_background_tasks()
    return memory_manager

async def get_memory_manager() -> TrinitasMemoryManager:
    """メモリマネージャーを取得"""
    if not memory_manager:
        await initialize_memory_manager()
    return memory_manager