#!/usr/bin/env python3
"""
Trinitas v3.5 Memory System Core Implementation
エージェント記憶システムの中核実装
"""

import asyncio
import json
import math
import sqlite3
import hashlib
from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

# Memory Types
class MemoryType(Enum):
    """記憶の種類"""
    WORKING = "working"          # 作業記憶
    EPISODIC = "episodic"        # エピソード記憶
    SEMANTIC = "semantic"        # 意味記憶
    PROCEDURAL = "procedural"    # 手続き記憶

class MemoryPriority(Enum):
    """記憶の優先度"""
    CRITICAL = 5    # 最重要
    HIGH = 4        # 高
    MEDIUM = 3      # 中
    LOW = 2         # 低
    MINIMAL = 1     # 最小

@dataclass
class MemoryItem:
    """記憶アイテム"""
    id: str
    content: Any
    type: MemoryType
    persona: str
    timestamp: datetime = field(default_factory=datetime.now)
    last_access: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 0.5
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            # Generate unique ID
            content_str = json.dumps(self.content, sort_keys=True)
            self.id = hashlib.sha256(
                f"{self.persona}_{content_str}_{self.timestamp.isoformat()}".encode()
            ).hexdigest()[:16]

@dataclass
class Context:
    """記憶検索用のコンテキスト"""
    current_task: str
    constraints: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)

@dataclass
class Query:
    """記憶検索クエリ"""
    text: str
    context: Optional[Context] = None
    needs_experience: bool = False
    needs_knowledge: bool = False
    needs_procedure: bool = False
    limit: int = 5
    threshold: float = 0.7

# Base Memory Class
class BaseMemory(ABC):
    """記憶ベースクラス"""
    
    @abstractmethod
    async def store(self, item: MemoryItem):
        """記憶を保存"""
        pass
    
    @abstractmethod
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """記憶を取得"""
        pass
    
    @abstractmethod
    async def forget(self, item_id: str):
        """記憶を忘却"""
        pass

# Working Memory Implementation
class WorkingMemory(BaseMemory):
    """作業記憶 - 短期記憶の実装"""
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.buffer: deque[MemoryItem] = deque(maxlen=capacity)
        self.attention_weights: Dict[str, float] = {}
        
    async def store(self, item: MemoryItem):
        """作業記憶に保存"""
        self.buffer.append(item)
        self.attention_weights[item.id] = item.importance
        
        # Capacity exceeded - oldest item is automatically removed by deque
        if item.id in self.attention_weights and len(self.attention_weights) > self.capacity:
            # Remove attention weight for oldest item
            oldest_id = next(iter(self.attention_weights))
            if oldest_id != item.id:
                del self.attention_weights[oldest_id]
    
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """関連性に基づいて取得"""
        if not self.buffer:
            return []
        
        # Simple text matching for working memory
        results = []
        query_text = query.text.lower()
        
        for item in self.buffer:
            relevance = self._calculate_relevance(item, query_text)
            if relevance > query.threshold:
                item.access_count += 1
                item.last_access = datetime.now()
                results.append((relevance, item))
        
        # Sort by relevance and return
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:query.limit]]
    
    async def forget(self, item_id: str):
        """作業記憶から削除"""
        self.buffer = deque(
            [item for item in self.buffer if item.id != item_id],
            maxlen=self.capacity
        )
        if item_id in self.attention_weights:
            del self.attention_weights[item_id]
    
    def _calculate_relevance(self, item: MemoryItem, query: str) -> float:
        """関連性を計算"""
        content_str = str(item.content).lower()
        
        # Simple keyword matching
        words = query.split()
        matches = sum(1 for word in words if word in content_str)
        
        # Factor in attention weight
        attention = self.attention_weights.get(item.id, 0.5)
        
        # Recency bonus
        time_diff = (datetime.now() - item.last_access).total_seconds()
        recency = math.exp(-time_diff / 3600)  # Decay over hours
        
        relevance = (matches / max(len(words), 1)) * 0.5 + attention * 0.3 + recency * 0.2
        return min(relevance, 1.0)

# Episodic Memory Implementation
class EpisodicMemory(BaseMemory):
    """エピソード記憶 - 経験の記録"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    persona TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    last_access TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    importance REAL DEFAULT 0.5,
                    metadata TEXT,
                    tags TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_persona ON episodes(persona)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON episodes(importance)")
    
    async def store(self, item: MemoryItem):
        """エピソードを保存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO episodes 
                (id, persona, content, timestamp, last_access, access_count, importance, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.persona,
                json.dumps(item.content),
                item.timestamp.isoformat(),
                item.last_access.isoformat(),
                item.access_count,
                item.importance,
                json.dumps(item.metadata),
                json.dumps(item.tags)
            ))
    
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """エピソードを検索"""
        with sqlite3.connect(self.db_path) as conn:
            # Simple text search in content
            cursor = conn.execute("""
                SELECT id, persona, content, timestamp, last_access, 
                       access_count, importance, metadata, tags
                FROM episodes
                WHERE content LIKE ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query.text}%", query.limit))
            
            results = []
            for row in cursor:
                item = MemoryItem(
                    id=row[0],
                    persona=row[1],
                    content=json.loads(row[2]),
                    type=MemoryType.EPISODIC,
                    timestamp=datetime.fromisoformat(row[3]),
                    last_access=datetime.fromisoformat(row[4]),
                    access_count=row[5],
                    importance=row[6],
                    metadata=json.loads(row[7]) if row[7] else {},
                    tags=json.loads(row[8]) if row[8] else []
                )
                
                # Update access info
                item.access_count += 1
                item.last_access = datetime.now()
                await self._update_access(item.id, item.access_count, item.last_access)
                
                results.append(item)
            
            return results
    
    async def forget(self, item_id: str):
        """エピソードを削除"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM episodes WHERE id = ?", (item_id,))
    
    async def _update_access(self, item_id: str, access_count: int, last_access: datetime):
        """アクセス情報を更新"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE episodes 
                SET access_count = ?, last_access = ?
                WHERE id = ?
            """, (access_count, last_access.isoformat(), item_id))

# Semantic Memory Implementation
class SemanticMemory(BaseMemory):
    """意味記憶 - 知識と概念"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_base: Dict[str, MemoryItem] = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        """既存の知識を読み込み"""
        knowledge_file = self.storage_path / "knowledge.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.knowledge_base[key] = MemoryItem(
                            id=value['id'],
                            persona=value['persona'],
                            content=value['content'],
                            type=MemoryType.SEMANTIC,
                            timestamp=datetime.fromisoformat(value['timestamp']),
                            importance=value.get('importance', 0.5),
                            metadata=value.get('metadata', {}),
                            tags=value.get('tags', [])
                        )
            except Exception as e:
                logger.error(f"Failed to load knowledge: {e}")
    
    async def store(self, item: MemoryItem):
        """知識を保存"""
        self.knowledge_base[item.id] = item
        await self._persist_knowledge()
    
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """知識を検索"""
        if not self.knowledge_base:
            return []
        
        results = []
        query_text = query.text.lower()
        
        for item in self.knowledge_base.values():
            # Check content and tags
            content_str = str(item.content).lower()
            tags_str = " ".join(item.tags).lower()
            
            if query_text in content_str or query_text in tags_str:
                item.access_count += 1
                item.last_access = datetime.now()
                results.append((item.importance, item))
        
        # Sort by importance and return
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:query.limit]]
    
    async def forget(self, item_id: str):
        """知識を削除"""
        if item_id in self.knowledge_base:
            del self.knowledge_base[item_id]
            await self._persist_knowledge()
    
    async def _persist_knowledge(self):
        """知識を永続化"""
        knowledge_file = self.storage_path / "knowledge.json"
        data = {}
        for key, item in self.knowledge_base.items():
            data[key] = {
                'id': item.id,
                'persona': item.persona,
                'content': item.content,
                'timestamp': item.timestamp.isoformat(),
                'importance': item.importance,
                'metadata': item.metadata,
                'tags': item.tags
            }
        
        with open(knowledge_file, 'w') as f:
            json.dump(data, f, indent=2)

# Procedural Memory Implementation
class ProceduralMemory(BaseMemory):
    """手続き記憶 - 手法とパターン"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procedures (
                    id TEXT PRIMARY KEY,
                    persona TEXT NOT NULL,
                    pattern_name TEXT,
                    pattern_type TEXT,
                    steps TEXT NOT NULL,
                    conditions TEXT,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    timestamp TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON procedures(pattern_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success_rate ON procedures(success_rate)")
    
    async def store(self, item: MemoryItem):
        """手続きを保存"""
        with sqlite3.connect(self.db_path) as conn:
            # Extract pattern info from content
            content = item.content if isinstance(item.content, dict) else {'steps': str(item.content)}
            
            conn.execute("""
                INSERT OR REPLACE INTO procedures
                (id, persona, pattern_name, pattern_type, steps, conditions, 
                 success_rate, usage_count, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.persona,
                content.get('name', ''),
                content.get('type', ''),
                json.dumps(content.get('steps', [])),
                json.dumps(content.get('conditions', [])),
                content.get('success_rate', 0.0),
                content.get('usage_count', 0),
                item.timestamp.isoformat(),
                json.dumps(item.metadata)
            ))
    
    async def retrieve(self, query: Query) -> List[MemoryItem]:
        """手続きを検索"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, persona, pattern_name, steps, conditions,
                       success_rate, usage_count, timestamp, metadata
                FROM procedures
                WHERE steps LIKE ? OR pattern_name LIKE ?
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT ?
            """, (f"%{query.text}%", f"%{query.text}%", query.limit))
            
            results = []
            for row in cursor:
                content = {
                    'name': row[2],
                    'steps': json.loads(row[3]),
                    'conditions': json.loads(row[4]),
                    'success_rate': row[5],
                    'usage_count': row[6]
                }
                
                item = MemoryItem(
                    id=row[0],
                    persona=row[1],
                    content=content,
                    type=MemoryType.PROCEDURAL,
                    timestamp=datetime.fromisoformat(row[7]),
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                results.append(item)
            
            return results
    
    async def forget(self, item_id: str):
        """手続きを削除"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM procedures WHERE id = ?", (item_id,))