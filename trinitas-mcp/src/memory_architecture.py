"""
Memory Architecture for Trinitas v5.0
ペルソナ別メモリ管理システム

This module provides a tiered memory system (short/medium/long-term)
for each persona with efficient storage and recall mechanisms.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import hashlib
from abc import ABC, abstractmethod

class MemoryTier(Enum):
    """メモリ階層定義"""
    SHORT_TERM = "short"     # 1時間以内の作業記憶
    MEDIUM_TERM = "medium"   # 1日〜1週間のプロジェクト記憶
    LONG_TERM = "long"       # 永続的な知識・パターン

class MemoryImportance(Enum):
    """メモリ重要度レベル"""
    CRITICAL = 1.0   # 絶対に忘れてはいけない
    HIGH = 0.8       # 重要な決定・知識
    MEDIUM = 0.5     # 通常の作業記憶
    LOW = 0.3        # 参考情報
    TRIVIAL = 0.1    # 些細な情報

@dataclass
class MemoryItem:
    """メモリアイテム"""
    id: str
    persona: str
    tier: MemoryTier
    content: Any
    importance: float
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    def calculate_priority(self) -> float:
        """優先度計算（重要度 × アクセス頻度 × 時間減衰）"""
        time_decay = self._calculate_time_decay()
        access_boost = min(1.0, self.access_count / 10)
        return self.importance * (0.5 + 0.3 * access_boost + 0.2 * time_decay)
    
    def _calculate_time_decay(self) -> float:
        """時間減衰計算"""
        age = datetime.now() - self.created_at
        if self.tier == MemoryTier.SHORT_TERM:
            # 短期記憶は急速に減衰
            half_life = timedelta(hours=1)
        elif self.tier == MemoryTier.MEDIUM_TERM:
            # 中期記憶はゆっくり減衰
            half_life = timedelta(days=7)
        else:
            # 長期記憶はほぼ減衰しない
            half_life = timedelta(days=365)
        
        decay_factor = 0.5 ** (age / half_life)
        return max(0.1, decay_factor)

class MemoryBackend(ABC):
    """メモリバックエンド抽象基底クラス"""
    
    @abstractmethod
    async def store(self, item: MemoryItem) -> bool:
        """メモリアイテムを保存"""
        pass
    
    @abstractmethod
    async def retrieve(self, id: str) -> Optional[MemoryItem]:
        """IDでメモリアイテムを取得"""
        pass
    
    @abstractmethod
    async def search(self, 
                    persona: Optional[str] = None,
                    tier: Optional[MemoryTier] = None,
                    tags: Optional[List[str]] = None,
                    min_importance: float = 0.0,
                    limit: int = 10) -> List[MemoryItem]:
        """条件に基づいてメモリを検索"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """メモリアイテムを削除"""
        pass

class PersonaMemoryManager:
    """ペルソナ専用メモリマネージャー"""
    
    def __init__(self, persona: str, backend: MemoryBackend):
        self.persona = persona
        self.backend = backend
        self.cache = {}  # 高速アクセス用キャッシュ
        self.tier_limits = {
            MemoryTier.SHORT_TERM: 100,   # 最大100アイテム
            MemoryTier.MEDIUM_TERM: 500,  # 最大500アイテム
            MemoryTier.LONG_TERM: 2000,   # 最大2000アイテム
        }
    
    async def remember(self, 
                      content: Any,
                      tier: MemoryTier,
                      importance: float,
                      tags: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """新しい記憶を保存"""
        # IDを生成
        content_str = json.dumps(content, sort_keys=True, default=str)
        id = hashlib.sha256(f"{self.persona}:{content_str}".encode()).hexdigest()[:16]
        
        # 有効期限を設定
        if tier == MemoryTier.SHORT_TERM:
            expires_at = datetime.now() + timedelta(hours=1)
        elif tier == MemoryTier.MEDIUM_TERM:
            expires_at = datetime.now() + timedelta(days=7)
        else:
            expires_at = None  # 長期記憶は期限なし
        
        item = MemoryItem(
            id=id,
            persona=self.persona,
            tier=tier,
            content=content,
            importance=importance,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            tags=tags or [],
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        # 容量制限チェックと古いアイテムの削除
        await self._enforce_tier_limits(tier)
        
        # 保存
        success = await self.backend.store(item)
        if success:
            self.cache[id] = item
        
        return id if success else None
    
    async def recall(self,
                    query: Optional[str] = None,
                    tier: Optional[MemoryTier] = None,
                    tags: Optional[List[str]] = None,
                    min_importance: float = 0.0,
                    limit: int = 10,
                    semantic: bool = False) -> List[MemoryItem]:
        """記憶を想起"""
        # バックエンドから検索
        items = await self.backend.search(
            persona=self.persona,
            tier=tier,
            tags=tags,
            min_importance=min_importance,
            limit=limit * 2  # 後でフィルタリングするため多めに取得
        )
        
        # セマンティック検索が必要な場合
        if semantic and query:
            # TODO: ベクトル類似度検索の実装
            # 現在は簡易的なテキストマッチング
            filtered = []
            for item in items:
                content_str = str(item.content).lower()
                if query.lower() in content_str:
                    filtered.append(item)
            items = filtered
        
        # 優先度でソート
        items.sort(key=lambda x: x.calculate_priority(), reverse=True)
        
        # アクセスカウントを更新
        for item in items[:limit]:
            item.access_count += 1
            item.accessed_at = datetime.now()
            await self.backend.store(item)  # 更新を保存
        
        return items[:limit]
    
    async def forget(self, id: str) -> bool:
        """特定の記憶を削除"""
        success = await self.backend.delete(id)
        if success and id in self.cache:
            del self.cache[id]
        return success
    
    async def consolidate(self):
        """記憶の整理・統合（定期実行）"""
        # 期限切れアイテムの削除
        all_items = await self.backend.search(persona=self.persona, limit=10000)
        now = datetime.now()
        
        for item in all_items:
            if item.expires_at and item.expires_at < now:
                await self.forget(item.id)
        
        # 短期記憶から中期記憶への昇格
        short_term = await self.backend.search(
            persona=self.persona,
            tier=MemoryTier.SHORT_TERM,
            min_importance=0.7,
            limit=20
        )
        
        for item in short_term:
            if item.access_count >= 3:  # 3回以上アクセスされた
                # 中期記憶として再保存
                await self.remember(
                    content=item.content,
                    tier=MemoryTier.MEDIUM_TERM,
                    importance=min(1.0, item.importance * 1.2),
                    tags=item.tags,
                    metadata={**item.metadata, "promoted_from": "short_term"}
                )
                await self.forget(item.id)
        
        # 中期記憶から長期記憶への昇格
        medium_term = await self.backend.search(
            persona=self.persona,
            tier=MemoryTier.MEDIUM_TERM,
            min_importance=0.8,
            limit=10
        )
        
        for item in medium_term:
            age = datetime.now() - item.created_at
            if age > timedelta(days=3) and item.access_count >= 10:
                # 長期記憶として再保存
                await self.remember(
                    content=item.content,
                    tier=MemoryTier.LONG_TERM,
                    importance=min(1.0, item.importance * 1.5),
                    tags=item.tags + ["consolidated"],
                    metadata={**item.metadata, "promoted_from": "medium_term"}
                )
                await self.forget(item.id)
    
    async def _enforce_tier_limits(self, tier: MemoryTier):
        """階層別の容量制限を適用"""
        items = await self.backend.search(
            persona=self.persona,
            tier=tier,
            limit=self.tier_limits[tier] + 100
        )
        
        if len(items) >= self.tier_limits[tier]:
            # 優先度が低いアイテムを削除
            items.sort(key=lambda x: x.calculate_priority())
            to_delete = items[:len(items) - self.tier_limits[tier] + 1]
            
            for item in to_delete:
                await self.forget(item.id)

class TrinitasMemoryOrchestrator:
    """全ペルソナのメモリを統括"""
    
    def __init__(self, backend: MemoryBackend):
        self.backend = backend
        self.personas = {}
        self.global_patterns = {}  # ペルソナ間で共有されるパターン
    
    def get_persona_memory(self, persona: str) -> PersonaMemoryManager:
        """ペルソナ専用メモリマネージャーを取得"""
        if persona not in self.personas:
            self.personas[persona] = PersonaMemoryManager(persona, self.backend)
        return self.personas[persona]
    
    async def cross_persona_search(self,
                                  query: str,
                                  personas: Optional[List[str]] = None,
                                  limit: int = 10) -> Dict[str, List[MemoryItem]]:
        """複数ペルソナ横断検索"""
        results = {}
        target_personas = personas or list(self.personas.keys())
        
        for persona in target_personas:
            if persona in self.personas:
                items = await self.personas[persona].recall(
                    query=query,
                    semantic=True,
                    limit=limit
                )
                if items:
                    results[persona] = items
        
        return results
    
    async def share_memory(self,
                          from_persona: str,
                          to_persona: str,
                          memory_id: str,
                          transform: Optional[callable] = None):
        """ペルソナ間でメモリを共有"""
        from_memory = self.get_persona_memory(from_persona)
        to_memory = self.get_persona_memory(to_persona)
        
        # 元のメモリを取得
        item = await from_memory.backend.retrieve(memory_id)
        if not item:
            return False
        
        # 必要に応じて変換
        content = transform(item.content) if transform else item.content
        
        # 共有先に保存
        await to_memory.remember(
            content=content,
            tier=item.tier,
            importance=item.importance * 0.8,  # 共有時は重要度を少し下げる
            tags=item.tags + [f"shared_from_{from_persona}"],
            metadata={**item.metadata, "original_persona": from_persona}
        )
        
        return True
    
    async def extract_patterns(self):
        """全ペルソナから共通パターンを抽出"""
        all_long_term = {}
        
        # 各ペルソナの長期記憶を収集
        for persona_name, persona_memory in self.personas.items():
            items = await persona_memory.recall(
                tier=MemoryTier.LONG_TERM,
                min_importance=0.7,
                limit=100
            )
            all_long_term[persona_name] = items
        
        # パターン抽出ロジック（簡易版）
        # TODO: より高度なパターン認識アルゴリズムの実装
        patterns = {}
        for persona, items in all_long_term.items():
            for item in items:
                # タグベースでパターンを分類
                for tag in item.tags:
                    if tag not in patterns:
                        patterns[tag] = []
                    patterns[tag].append({
                        "persona": persona,
                        "content": item.content,
                        "importance": item.importance
                    })
        
        # 複数ペルソナで共通するパターンを抽出
        self.global_patterns = {
            tag: instances
            for tag, instances in patterns.items()
            if len(set(inst["persona"] for inst in instances)) >= 2
        }
        
        return self.global_patterns