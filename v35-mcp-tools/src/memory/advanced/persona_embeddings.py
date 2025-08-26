#!/usr/bin/env python3
"""
Trinitas v3.5 Persona-Specific Embedding Models
ペルソナ特化型エンベディングモデル
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import pickle
from pathlib import Path

# Try importing sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("sentence-transformers not installed - using fallback embeddings")

logger = logging.getLogger(__name__)

@dataclass
class PersonaVocabulary:
    """ペルソナ固有の語彙と重み"""
    persona: str
    domain_terms: Dict[str, float]  # Term -> weight
    concept_clusters: Dict[str, List[str]]  # Concept -> related terms
    importance_patterns: List[str]  # Patterns that indicate importance

# Define persona-specific vocabularies
PERSONA_VOCABULARIES = {
    "athena": PersonaVocabulary(
        persona="athena",
        domain_terms={
            # Architecture terms
            "architecture": 1.5, "system": 1.3, "design": 1.4,
            "scalability": 1.2, "microservices": 1.5, "api": 1.3,
            "integration": 1.2, "framework": 1.3, "pattern": 1.4,
            "structure": 1.3, "component": 1.2, "module": 1.2,
            # Japanese terms
            "アーキテクチャ": 1.5, "設計": 1.4, "システム": 1.3,
            "統合": 1.2, "フレームワーク": 1.3, "パターン": 1.4
        },
        concept_clusters={
            "system_design": ["architecture", "design", "pattern", "structure"],
            "scalability": ["scaling", "load", "performance", "capacity"],
            "integration": ["api", "interface", "protocol", "communication"]
        },
        importance_patterns=[
            "critical decision", "architecture change", "major refactoring",
            "breaking change", "design pattern", "system overhaul"
        ]
    ),
    "artemis": PersonaVocabulary(
        persona="artemis",
        domain_terms={
            # Optimization terms
            "optimization": 1.5, "performance": 1.4, "algorithm": 1.3,
            "complexity": 1.2, "efficiency": 1.5, "benchmark": 1.3,
            "profiling": 1.2, "cache": 1.3, "latency": 1.4,
            "throughput": 1.3, "memory": 1.2, "cpu": 1.2,
            # Japanese terms
            "最適化": 1.5, "パフォーマンス": 1.4, "アルゴリズム": 1.3,
            "効率": 1.5, "ベンチマーク": 1.3, "プロファイリング": 1.2
        },
        concept_clusters={
            "performance": ["speed", "latency", "throughput", "response"],
            "optimization": ["improve", "enhance", "boost", "accelerate"],
            "resource": ["memory", "cpu", "disk", "network", "cache"]
        },
        importance_patterns=[
            "performance improvement", "optimization achieved", "bottleneck fixed",
            "10x faster", "memory leak fixed", "algorithm optimized"
        ]
    ),
    "hestia": PersonaVocabulary(
        persona="hestia",
        domain_terms={
            # Security terms
            "security": 1.5, "vulnerability": 1.4, "encryption": 1.3,
            "authentication": 1.3, "threat": 1.4, "compliance": 1.2,
            "audit": 1.3, "attack": 1.4, "defense": 1.3,
            "firewall": 1.2, "certificate": 1.2, "token": 1.3,
            # Japanese terms
            "セキュリティ": 1.5, "脆弱性": 1.4, "暗号化": 1.3,
            "認証": 1.3, "脅威": 1.4, "攻撃": 1.4
        },
        concept_clusters={
            "authentication": ["auth", "login", "identity", "credential"],
            "vulnerability": ["exploit", "weakness", "flaw", "risk"],
            "protection": ["defense", "guard", "shield", "prevent"]
        },
        importance_patterns=[
            "security breach", "vulnerability found", "zero-day",
            "critical patch", "authentication bypass", "data leak"
        ]
    ),
    "bellona": PersonaVocabulary(
        persona="bellona",
        domain_terms={
            # Tactical execution terms
            "deployment": 1.4, "execution": 1.3, "strategy": 1.3,
            "coordination": 1.2, "pipeline": 1.3, "rollout": 1.2,
            "migration": 1.3, "release": 1.3, "staging": 1.2,
            "production": 1.4, "rollback": 1.3, "canary": 1.2,
            # Japanese terms
            "デプロイ": 1.4, "実行": 1.3, "戦略": 1.3,
            "移行": 1.3, "リリース": 1.3, "本番": 1.4
        },
        concept_clusters={
            "deployment": ["deploy", "release", "rollout", "launch"],
            "coordination": ["sync", "align", "orchestrate", "manage"],
            "execution": ["run", "execute", "perform", "implement"]
        },
        importance_patterns=[
            "production deployment", "successful rollout", "zero downtime",
            "migration complete", "coordinated release", "deployment failed"
        ]
    ),
    "seshat": PersonaVocabulary(
        persona="seshat",
        domain_terms={
            # Documentation terms
            "documentation": 1.5, "knowledge": 1.3, "information": 1.2,
            "reference": 1.3, "guide": 1.3, "tutorial": 1.2,
            "specification": 1.4, "standard": 1.3, "template": 1.3,
            "glossary": 1.2, "diagram": 1.3, "annotation": 1.2,
            # Japanese terms
            "ドキュメント": 1.5, "知識": 1.3, "情報": 1.2,
            "仕様": 1.4, "標準": 1.3, "テンプレート": 1.3
        },
        concept_clusters={
            "documentation": ["docs", "document", "record", "write"],
            "knowledge": ["info", "data", "wisdom", "insight"],
            "organization": ["structure", "categorize", "classify", "arrange"]
        },
        importance_patterns=[
            "documentation updated", "knowledge captured", "standard defined",
            "specification finalized", "guide published", "reference created"
        ]
    )
}

class PersonaEmbeddingModel:
    """ペルソナ特化型エンベディングモデル"""
    
    def __init__(self, persona: str):
        self.persona = persona
        self.vocabulary = PERSONA_VOCABULARIES.get(persona)
        
        if not self.vocabulary:
            raise ValueError(f"Unknown persona: {persona}")
        
        # Load base model
        if HAS_TRANSFORMERS:
            self.base_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384
        else:
            self.base_model = None
            self.embedding_dim = 128  # Fallback dimension
        
        self.fine_tuned_weights = None
        self.training_history = []
        
        logger.info(f"Initialized embedding model for {persona}")
    
    def encode(self, text: str) -> np.ndarray:
        """テキストをペルソナ特化エンベディングに変換"""
        if not text:
            return np.zeros(self.embedding_dim)
        
        # Get base embedding
        if self.base_model:
            base_embedding = self.base_model.encode(text)
        else:
            # Simple fallback embedding
            base_embedding = self._fallback_encode(text)
        
        # Apply persona-specific adjustments
        adjusted_embedding = self._apply_persona_weights(base_embedding, text)
        
        # Apply fine-tuning if available
        if self.fine_tuned_weights is not None:
            adjusted_embedding = self._apply_fine_tuning(adjusted_embedding)
        
        # Normalize
        norm = np.linalg.norm(adjusted_embedding)
        if norm > 0:
            adjusted_embedding = adjusted_embedding / norm
        
        return adjusted_embedding
    
    def _fallback_encode(self, text: str) -> np.ndarray:
        """Fallback encoding when sentence-transformers not available"""
        # Simple hash-based embedding
        embedding = np.zeros(self.embedding_dim)
        
        words = text.lower().split()
        for i, word in enumerate(words):
            hash_val = hash(word)
            idx = abs(hash_val) % self.embedding_dim
            embedding[idx] += 1.0 / (i + 1)  # Position-weighted
        
        return embedding
    
    def _apply_persona_weights(self, embedding: np.ndarray, text: str) -> np.ndarray:
        """Apply persona-specific term weights"""
        text_lower = text.lower()
        weight_multiplier = 1.0
        
        # Check domain terms
        for term, weight in self.vocabulary.domain_terms.items():
            if term.lower() in text_lower:
                weight_multiplier *= weight
        
        # Check importance patterns
        for pattern in self.vocabulary.importance_patterns:
            if pattern.lower() in text_lower:
                weight_multiplier *= 1.2
        
        # Apply concept clustering bonus
        for concept, related_terms in self.vocabulary.concept_clusters.items():
            match_count = sum(1 for term in related_terms if term in text_lower)
            if match_count > 1:
                weight_multiplier *= (1 + 0.1 * match_count)
        
        return embedding * min(weight_multiplier, 2.0)  # Cap at 2x
    
    def _apply_fine_tuning(self, embedding: np.ndarray) -> np.ndarray:
        """Apply fine-tuned weights"""
        if self.fine_tuned_weights is not None:
            # Simple linear transformation
            return embedding @ self.fine_tuned_weights
        return embedding
    
    async def fine_tune(self, training_data: List[Tuple[str, str, float]]):
        """Fine-tune model on persona-specific data
        
        Args:
            training_data: List of (text1, text2, similarity_score) tuples
        """
        if not training_data:
            logger.warning(f"No training data provided for {self.persona}")
            return
        
        logger.info(f"Fine-tuning {self.persona} model with {len(training_data)} samples")
        
        # Extract patterns from training data
        patterns = self._extract_patterns(training_data)
        
        # Update vocabulary weights based on patterns
        self._update_vocabulary_weights(patterns)
        
        # Create fine-tuning matrix
        self.fine_tuned_weights = self._create_fine_tuning_matrix(patterns)
        
        # Record training
        self.training_history.append({
            "timestamp": datetime.now().isoformat(),
            "samples": len(training_data),
            "patterns": len(patterns)
        })
        
        logger.info(f"Fine-tuning complete for {self.persona}")
    
    def _extract_patterns(self, training_data: List[Tuple[str, str, float]]) -> Dict:
        """Extract patterns from training data"""
        patterns = {
            "high_similarity_terms": {},
            "low_similarity_terms": {},
            "co_occurrences": {}
        }
        
        for text1, text2, similarity in training_data:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if similarity > 0.8:
                # High similarity - these terms are related
                common = words1.intersection(words2)
                for word in common:
                    patterns["high_similarity_terms"][word] = patterns["high_similarity_terms"].get(word, 0) + 1
            elif similarity < 0.3:
                # Low similarity - these terms are unrelated
                diff = words1.symmetric_difference(words2)
                for word in diff:
                    patterns["low_similarity_terms"][word] = patterns["low_similarity_terms"].get(word, 0) + 1
        
        return patterns
    
    def _update_vocabulary_weights(self, patterns: Dict):
        """Update vocabulary weights based on patterns"""
        # Increase weights for frequently related terms
        for term, count in patterns["high_similarity_terms"].items():
            if term in self.vocabulary.domain_terms:
                self.vocabulary.domain_terms[term] *= (1 + 0.01 * count)
        
        # Add new important terms
        threshold = 5
        for term, count in patterns["high_similarity_terms"].items():
            if count > threshold and term not in self.vocabulary.domain_terms:
                self.vocabulary.domain_terms[term] = 1.1
    
    def _create_fine_tuning_matrix(self, patterns: Dict) -> np.ndarray:
        """Create fine-tuning transformation matrix"""
        # Simple diagonal matrix with learned weights
        matrix = np.eye(self.embedding_dim)
        
        # Adjust based on pattern frequency
        for i in range(self.embedding_dim):
            # Slightly randomize to break symmetry
            matrix[i, i] *= (0.9 + 0.2 * np.random.random())
        
        return matrix
    
    def save(self, path: str):
        """Save model to disk"""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "persona": self.persona,
            "vocabulary": self.vocabulary,
            "fine_tuned_weights": self.fine_tuned_weights,
            "training_history": self.training_history,
            "embedding_dim": self.embedding_dim
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Saved {self.persona} model to {save_path}")
    
    @classmethod
    def load(cls, path: str, persona: str) -> "PersonaEmbeddingModel":
        """Load model from disk"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        if model_data["persona"] != persona:
            raise ValueError(f"Model persona mismatch: expected {persona}, got {model_data['persona']}")
        
        model = cls(persona)
        model.vocabulary = model_data["vocabulary"]
        model.fine_tuned_weights = model_data["fine_tuned_weights"]
        model.training_history = model_data["training_history"]
        
        logger.info(f"Loaded {persona} model from {path}")
        return model

class AdaptiveEmbeddingSystem:
    """適応的エンベディング更新システム"""
    
    def __init__(self, storage_path: str = "/tmp/trinitas_embeddings"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, PersonaEmbeddingModel] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.update_threshold = 0.8
        
        # Initialize models for all personas
        for persona in PERSONA_VOCABULARIES.keys():
            self.models[persona] = PersonaEmbeddingModel(persona)
    
    def encode(self, text: str, persona: str) -> np.ndarray:
        """Encode text using persona-specific model"""
        if persona not in self.models:
            raise ValueError(f"No model for persona: {persona}")
        
        return self.models[persona].encode(text)
    
    async def evaluate_performance(self, persona: str, test_data: List[Tuple[str, str, float]]) -> float:
        """Evaluate model performance"""
        if not test_data:
            return 1.0
        
        model = self.models[persona]
        correct = 0
        
        for text1, text2, expected_similarity in test_data:
            # Encode both texts
            emb1 = model.encode(text1)
            emb2 = model.encode(text2)
            
            # Calculate cosine similarity
            similarity = np.dot(emb1, emb2)
            
            # Check if prediction matches expectation
            if abs(similarity - expected_similarity) < 0.2:
                correct += 1
        
        return correct / len(test_data)
    
    async def auto_retrain(self, training_data: Dict[str, List[Tuple[str, str, float]]]):
        """Automatically retrain underperforming models"""
        for persona, data in training_data.items():
            if persona not in self.models:
                continue
            
            # Evaluate current performance
            performance = await self.evaluate_performance(persona, data[:100])
            self.performance_metrics[persona] = performance
            
            # Retrain if below threshold
            if performance < self.update_threshold:
                logger.info(f"Retraining {persona} model (performance: {performance:.2%})")
                await self.models[persona].fine_tune(data)
                
                # Save updated model
                model_path = self.storage_path / f"{persona}_model.pkl"
                self.models[persona].save(str(model_path))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            "models": {},
            "overall_performance": np.mean(list(self.performance_metrics.values())) if self.performance_metrics else 0
        }
        
        for persona, model in self.models.items():
            stats["models"][persona] = {
                "vocabulary_size": len(model.vocabulary.domain_terms),
                "performance": self.performance_metrics.get(persona, 0),
                "training_history": len(model.training_history),
                "fine_tuned": model.fine_tuned_weights is not None
            }
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing Persona Embedding Models")
        print("="*60)
        
        # Test each persona
        for persona in ["athena", "artemis", "hestia"]:
            print(f"\nTesting {persona.upper()} model:")
            model = PersonaEmbeddingModel(persona)
            
            # Test encoding
            test_texts = [
                "microservices architecture design pattern",
                "database query optimization for performance",
                "security vulnerability in authentication system"
            ]
            
            for text in test_texts:
                embedding = model.encode(text)
                print(f"  '{text[:40]}...' -> shape: {embedding.shape}, norm: {np.linalg.norm(embedding):.3f}")
        
        # Test adaptive system
        print("\nTesting Adaptive Embedding System:")
        system = AdaptiveEmbeddingSystem()
        
        # Get statistics
        stats = system.get_statistics()
        print(f"  System stats: {json.dumps(stats, indent=2)}")
    
    asyncio.run(test())