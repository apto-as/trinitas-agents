#!/usr/bin/env python3
"""
Trinitas v3.5 AI-Driven Memory Management
AI駆動の記憶管理システム
"""

import numpy as np
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import statistics

logger = logging.getLogger(__name__)

@dataclass
class MemoryContext:
    """記憶のコンテキスト情報"""
    total_memories: int
    recent_accesses: List[str]
    similar_memories: List[str]
    persona_distribution: Dict[str, int]
    time_range: Tuple[datetime, datetime]

@dataclass
class AnomalyReport:
    """異常検知レポート"""
    memory_id: str
    anomaly_type: str
    score: float
    reason: str
    timestamp: datetime
    recommended_action: str

@dataclass
class PredictionResult:
    """予測結果"""
    predicted_ids: List[str]
    confidence: float
    based_on_patterns: List[str]

class ImportanceScorer:
    """AI駆動の重要度スコアリング"""
    
    def __init__(self):
        self.feature_weights = {
            "uniqueness": 0.25,
            "recency": 0.15,
            "frequency": 0.20,
            "semantic_richness": 0.20,
            "connectivity": 0.20
        }
        self.scoring_history = []
        self.feedback_data = []
        
    async def score(self, 
                   content: Any,
                   persona: str,
                   context: MemoryContext) -> float:
        """記憶の重要度を自動スコアリング"""
        features = {}
        
        # Extract features
        features["uniqueness"] = await self._extract_uniqueness(content, context)
        features["recency"] = self._extract_recency(context)
        features["frequency"] = self._extract_frequency(context)
        features["semantic_richness"] = self._extract_semantic_richness(content)
        features["connectivity"] = self._extract_connectivity(context)
        
        # Calculate weighted score
        score = 0.0
        for feature, value in features.items():
            score += self.feature_weights[feature] * value
        
        # Apply persona-specific adjustments
        score = self._adjust_for_persona(score, persona, content)
        
        # Record scoring
        self.scoring_history.append({
            "timestamp": datetime.now().isoformat(),
            "persona": persona,
            "features": features,
            "final_score": score
        })
        
        return min(max(score, 0.0), 1.0)
    
    async def _extract_uniqueness(self, content: Any, context: MemoryContext) -> float:
        """ユニークさを評価 (0-1)"""
        if context.total_memories == 0:
            return 1.0
        
        # Check similarity with existing memories
        similar_count = len(context.similar_memories)
        uniqueness = 1.0 - (similar_count / min(context.total_memories, 100))
        
        return max(uniqueness, 0.0)
    
    def _extract_recency(self, context: MemoryContext) -> float:
        """最新性を評価 (0-1)"""
        if not context.time_range:
            return 0.5
        
        # Calculate time since last similar memory
        time_diff = datetime.now() - context.time_range[1]
        days_passed = time_diff.total_seconds() / 86400
        
        # Decay function: more recent = higher score
        recency = np.exp(-days_passed / 30)  # 30-day half-life
        
        return recency
    
    def _extract_frequency(self, context: MemoryContext) -> float:
        """アクセス頻度を評価 (0-1)"""
        if not context.recent_accesses:
            return 0.1
        
        # Normalize access count
        access_count = len(context.recent_accesses)
        frequency = min(access_count / 10, 1.0)  # Cap at 10 accesses
        
        return frequency
    
    def _extract_semantic_richness(self, content: Any) -> float:
        """意味的豊富さを評価 (0-1)"""
        content_str = str(content)
        
        # Simple heuristics for richness
        factors = {
            "length": min(len(content_str) / 500, 1.0),  # Longer = richer
            "complexity": self._calculate_complexity(content_str),
            "structure": 0.5 if isinstance(content, dict) else 0.3
        }
        
        richness = statistics.mean(factors.values())
        return richness
    
    def _calculate_complexity(self, text: str) -> float:
        """テキストの複雑さを計算"""
        words = text.split()
        if not words:
            return 0.0
        
        # Unique words ratio
        unique_ratio = len(set(words)) / len(words)
        
        # Average word length
        avg_length = sum(len(w) for w in words) / len(words)
        normalized_length = min(avg_length / 10, 1.0)
        
        return (unique_ratio + normalized_length) / 2
    
    def _extract_connectivity(self, context: MemoryContext) -> float:
        """他の記憶との関連性 (0-1)"""
        # More connections = higher importance
        connections = len(context.similar_memories)
        connectivity = min(connections / 5, 1.0)  # Cap at 5 connections
        
        return connectivity
    
    def _adjust_for_persona(self, score: float, persona: str, content: Any) -> float:
        """ペルソナ固有の調整"""
        adjustments = {
            "athena": self._adjust_for_athena,
            "artemis": self._adjust_for_artemis,
            "hestia": self._adjust_for_hestia,
            "bellona": self._adjust_for_bellona,
            "seshat": self._adjust_for_seshat
        }
        
        adjuster = adjustments.get(persona)
        if adjuster:
            return adjuster(score, content)
        
        return score
    
    def _adjust_for_athena(self, score: float, content: Any) -> float:
        """Athena: Architecture and planning focus"""
        content_str = str(content).lower()
        
        if any(term in content_str for term in ["architecture", "design", "strategy", "planning"]):
            score *= 1.2
        
        return min(score, 1.0)
    
    def _adjust_for_artemis(self, score: float, content: Any) -> float:
        """Artemis: Performance and optimization focus"""
        content_str = str(content).lower()
        
        if any(term in content_str for term in ["optimization", "performance", "speed", "efficiency"]):
            score *= 1.2
        
        # Boost for quantitative improvements
        if any(char in content_str for char in ["%", "x faster", "ms", "ops/sec"]):
            score *= 1.1
        
        return min(score, 1.0)
    
    def _adjust_for_hestia(self, score: float, content: Any) -> float:
        """Hestia: Security focus"""
        content_str = str(content).lower()
        
        if any(term in content_str for term in ["security", "vulnerability", "threat", "attack"]):
            score *= 1.3  # Security is critical
        
        return min(score, 1.0)
    
    def _adjust_for_bellona(self, score: float, content: Any) -> float:
        """Bellona: Execution and deployment focus"""
        content_str = str(content).lower()
        
        if any(term in content_str for term in ["deployment", "production", "release", "rollout"]):
            score *= 1.15
        
        return min(score, 1.0)
    
    def _adjust_for_seshat(self, score: float, content: Any) -> float:
        """Seshat: Documentation and knowledge focus"""
        content_str = str(content).lower()
        
        if any(term in content_str for term in ["documentation", "guide", "reference", "knowledge"]):
            score *= 1.15
        
        return min(score, 1.0)
    
    def update_weights(self, feedback: List[Tuple[str, float]]):
        """フィードバックに基づいて重みを更新"""
        self.feedback_data.extend(feedback)
        
        # Simple gradient update (would use ML in production)
        for feature, actual_importance in feedback:
            if feature in self.feature_weights:
                error = actual_importance - self.feature_weights[feature]
                # Learning rate = 0.1
                self.feature_weights[feature] += 0.1 * error
        
        # Normalize weights
        total = sum(self.feature_weights.values())
        for feature in self.feature_weights:
            self.feature_weights[feature] /= total

class PredictiveCache:
    """予測的キャッシング"""
    
    def __init__(self, cache_size: int = 1000):
        self.cache_size = cache_size
        self.access_patterns = defaultdict(list)
        self.sequence_length = 10
        self.min_pattern_count = 3
        
        # Simple cache implementation
        self.cache = {}
        self.cache_order = deque(maxlen=cache_size)
        
    async def record_access(self, current_id: str, next_id: str):
        """アクセスパターンを記録"""
        self.access_patterns[current_id].append(next_id)
        
        # Limit pattern history
        if len(self.access_patterns[current_id]) > 100:
            self.access_patterns[current_id] = self.access_patterns[current_id][-100:]
    
    async def predict_next_access(self, current_id: str) -> PredictionResult:
        """次にアクセスされる記憶を予測"""
        if current_id not in self.access_patterns:
            return PredictionResult([], 0.0, [])
        
        history = self.access_patterns[current_id]
        
        if len(history) < self.min_pattern_count:
            return PredictionResult([], 0.0, ["insufficient_data"])
        
        # Count frequency of next accesses
        next_counts = defaultdict(int)
        for next_id in history:
            next_counts[next_id] += 1
        
        # Sort by frequency
        predictions = sorted(next_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate confidence based on pattern consistency
        total_accesses = len(history)
        top_count = predictions[0][1] if predictions else 0
        confidence = top_count / total_accesses if total_accesses > 0 else 0.0
        
        # Get top predictions
        predicted_ids = [pid for pid, _ in predictions[:5]]
        
        return PredictionResult(
            predicted_ids=predicted_ids,
            confidence=confidence,
            based_on_patterns=[f"frequency_{top_count}"]
        )
    
    async def preload_cache(self, current_id: str, retriever):
        """予測に基づいてキャッシュをプリロード"""
        prediction = await self.predict_next_access(current_id)
        
        if prediction.confidence < 0.3:
            return  # Too uncertain
        
        preloaded = 0
        for memory_id in prediction.predicted_ids:
            if memory_id not in self.cache:
                # Fetch and cache
                memory = await retriever(memory_id)
                if memory:
                    self.cache[memory_id] = memory
                    self.cache_order.append(memory_id)
                    preloaded += 1
        
        if preloaded > 0:
            logger.debug(f"Preloaded {preloaded} predicted memories (confidence: {prediction.confidence:.2%})")
    
    def get(self, memory_id: str) -> Optional[Any]:
        """キャッシュから取得"""
        return self.cache.get(memory_id)
    
    def put(self, memory_id: str, memory: Any):
        """キャッシュに保存"""
        if len(self.cache) >= self.cache_size:
            # Evict oldest
            oldest = self.cache_order.popleft()
            del self.cache[oldest]
        
        self.cache[memory_id] = memory
        self.cache_order.append(memory_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        return {
            "cache_size": len(self.cache),
            "max_size": self.cache_size,
            "patterns_tracked": len(self.access_patterns),
            "total_pattern_entries": sum(len(p) for p in self.access_patterns.values())
        }

class MemoryAnomalyDetector:
    """記憶の異常検知"""
    
    def __init__(self):
        self.thresholds = {
            "size": {"min": 10, "max": 10000},  # bytes
            "importance": {"min": 0.0, "max": 1.0},
            "access_frequency": {"max": 100},  # per hour
            "similarity": {"min": 0.1}  # minimum uniqueness
        }
        self.anomaly_history = []
        self.detection_rules = [
            self._check_size_anomaly,
            self._check_importance_anomaly,
            self._check_access_anomaly,
            self._check_pattern_anomaly
        ]
    
    async def detect_anomalies(self, 
                              memories: List[Dict[str, Any]],
                              context: MemoryContext) -> List[AnomalyReport]:
        """異常な記憶パターンを検出"""
        anomalies = []
        
        for memory in memories:
            for rule in self.detection_rules:
                anomaly = await rule(memory, context)
                if anomaly:
                    anomalies.append(anomaly)
        
        # Record detection
        if anomalies:
            self.anomaly_history.append({
                "timestamp": datetime.now().isoformat(),
                "count": len(anomalies),
                "types": [a.anomaly_type for a in anomalies]
            })
        
        return anomalies
    
    async def _check_size_anomaly(self, memory: Dict, context: MemoryContext) -> Optional[AnomalyReport]:
        """サイズ異常をチェック"""
        size = len(json.dumps(memory.get("content", "")))
        
        if size < self.thresholds["size"]["min"]:
            return AnomalyReport(
                memory_id=memory.get("id", ""),
                anomaly_type="size_too_small",
                score=0.7,
                reason=f"Memory size {size} bytes is unusually small",
                timestamp=datetime.now(),
                recommended_action="Review memory content for completeness"
            )
        
        if size > self.thresholds["size"]["max"]:
            return AnomalyReport(
                memory_id=memory.get("id", ""),
                anomaly_type="size_too_large",
                score=0.8,
                reason=f"Memory size {size} bytes exceeds threshold",
                timestamp=datetime.now(),
                recommended_action="Consider compressing or splitting memory"
            )
        
        return None
    
    async def _check_importance_anomaly(self, memory: Dict, context: MemoryContext) -> Optional[AnomalyReport]:
        """重要度異常をチェック"""
        importance = memory.get("importance", 0.5)
        
        # Check if importance is out of bounds
        if importance < self.thresholds["importance"]["min"] or importance > self.thresholds["importance"]["max"]:
            return AnomalyReport(
                memory_id=memory.get("id", ""),
                anomaly_type="importance_invalid",
                score=0.9,
                reason=f"Importance {importance} is out of valid range",
                timestamp=datetime.now(),
                recommended_action="Recalculate importance score"
            )
        
        # Check if all memories have same importance (lack of differentiation)
        if context.total_memories > 10:
            # This would need actual importance distribution analysis
            pass
        
        return None
    
    async def _check_access_anomaly(self, memory: Dict, context: MemoryContext) -> Optional[AnomalyReport]:
        """アクセスパターン異常をチェック"""
        access_count = memory.get("access_count", 0)
        last_access = memory.get("last_access")
        
        if not last_access:
            return None
        
        # Calculate access frequency
        time_since_creation = datetime.now() - datetime.fromisoformat(memory.get("timestamp", datetime.now().isoformat()))
        hours_passed = time_since_creation.total_seconds() / 3600
        
        if hours_passed > 0:
            access_rate = access_count / hours_passed
            
            if access_rate > self.thresholds["access_frequency"]["max"]:
                return AnomalyReport(
                    memory_id=memory.get("id", ""),
                    anomaly_type="excessive_access",
                    score=0.6,
                    reason=f"Access rate {access_rate:.1f}/hour is unusually high",
                    timestamp=datetime.now(),
                    recommended_action="Check for access loops or cache this memory"
                )
        
        return None
    
    async def _check_pattern_anomaly(self, memory: Dict, context: MemoryContext) -> Optional[AnomalyReport]:
        """パターン異常をチェック"""
        # Check for duplicate or near-duplicate memories
        if len(context.similar_memories) > 5:
            return AnomalyReport(
                memory_id=memory.get("id", ""),
                anomaly_type="duplicate_pattern",
                score=0.5,
                reason=f"Found {len(context.similar_memories)} very similar memories",
                timestamp=datetime.now(),
                recommended_action="Consider deduplication or consolidation"
            )
        
        return None
    
    def update_thresholds(self, new_thresholds: Dict[str, Dict[str, float]]):
        """異常検知の閾値を更新"""
        for key, values in new_thresholds.items():
            if key in self.thresholds:
                self.thresholds[key].update(values)
    
    def get_statistics(self) -> Dict[str, Any]:
        """異常検知統計を取得"""
        if not self.anomaly_history:
            return {"total_anomalies": 0, "recent_anomalies": []}
        
        recent = self.anomaly_history[-10:]
        type_counts = defaultdict(int)
        
        for record in recent:
            for atype in record["types"]:
                type_counts[atype] += 1
        
        return {
            "total_anomalies": sum(r["count"] for r in self.anomaly_history),
            "recent_anomalies": recent,
            "anomaly_types": dict(type_counts),
            "detection_rules": len(self.detection_rules)
        }

# Example usage
if __name__ == "__main__":
    async def test():
        print("Testing AI-Driven Memory Management")
        print("="*60)
        
        # Test ImportanceScorer
        print("\n1. Testing ImportanceScorer:")
        scorer = ImportanceScorer()
        
        context = MemoryContext(
            total_memories=100,
            recent_accesses=["mem1", "mem2", "mem3"],
            similar_memories=["mem4", "mem5"],
            persona_distribution={"athena": 40, "artemis": 30, "hestia": 30},
            time_range=(datetime.now() - timedelta(days=7), datetime.now())
        )
        
        test_content = {
            "text": "Critical security vulnerability found in authentication system",
            "severity": "high",
            "tags": ["security", "urgent"]
        }
        
        score = await scorer.score(test_content, "hestia", context)
        print(f"  Importance score for security issue: {score:.3f}")
        
        # Test PredictiveCache
        print("\n2. Testing PredictiveCache:")
        cache = PredictiveCache(cache_size=10)
        
        # Simulate access pattern
        await cache.record_access("mem1", "mem2")
        await cache.record_access("mem1", "mem2")
        await cache.record_access("mem1", "mem3")
        await cache.record_access("mem1", "mem2")
        
        prediction = await cache.predict_next_access("mem1")
        print(f"  Predicted next access: {prediction.predicted_ids}")
        print(f"  Confidence: {prediction.confidence:.2%}")
        
        # Test MemoryAnomalyDetector
        print("\n3. Testing MemoryAnomalyDetector:")
        detector = MemoryAnomalyDetector()
        
        test_memories = [
            {"id": "mem1", "content": "x", "importance": 0.5, "access_count": 1000, "timestamp": datetime.now().isoformat()},
            {"id": "mem2", "content": "normal content", "importance": 1.5, "access_count": 5},
            {"id": "mem3", "content": "a" * 20000, "importance": 0.7, "access_count": 10}
        ]
        
        anomalies = await detector.detect_anomalies(test_memories, context)
        for anomaly in anomalies:
            print(f"  Anomaly detected: {anomaly.anomaly_type} - {anomaly.reason}")
        
        print("\nAll tests completed!")
    
    asyncio.run(test())