#!/usr/bin/env python3
"""
Research Cache Manager for DeepResearch Agent
Manages caching of research results to avoid redundant API calls
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class ResearchCache:
    def __init__(self, cache_dir: Path = None, ttl_hours: int = 24):
        """Initialize research cache with configurable TTL"""
        self.cache_dir = cache_dir or Path.home() / '.claude' / 'trinitas' / 'cache' / 'research'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.index_file = self.cache_dir / 'index.json'
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except:
                return {}
        return {}
    
    def _save_index(self):
        """Save cache index to disk"""
        self.index_file.write_text(json.dumps(self.index, indent=2))
    
    def _generate_key(self, query_type: str, query_params: Dict[str, Any]) -> str:
        """Generate cache key from query parameters"""
        # Create a stable string representation
        params_str = json.dumps(query_params, sort_keys=True)
        combined = f"{query_type}:{params_str}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get(self, query_type: str, query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if valid"""
        key = self._generate_key(query_type, query_params)
        
        if key not in self.index:
            return None
        
        entry = self.index[key]
        created_time = datetime.fromisoformat(entry['created'])
        
        # Check if cache entry is expired
        if datetime.now() - created_time > self.ttl:
            self._invalidate(key)
            return None
        
        # Load cached data
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                return data
            except:
                self._invalidate(key)
                return None
        
        return None
    
    def set(self, query_type: str, query_params: Dict[str, Any], result: Any):
        """Cache a research result"""
        key = self._generate_key(query_type, query_params)
        
        # Save to cache file
        cache_file = self.cache_dir / f"{key}.json"
        cache_data = {
            'query_type': query_type,
            'query_params': query_params,
            'result': result,
            'created': datetime.now().isoformat()
        }
        cache_file.write_text(json.dumps(cache_data, indent=2))
        
        # Update index
        self.index[key] = {
            'query_type': query_type,
            'query_summary': self._summarize_query(query_type, query_params),
            'created': datetime.now().isoformat(),
            'file': f"{key}.json"
        }
        self._save_index()
    
    def _summarize_query(self, query_type: str, query_params: Dict[str, Any]) -> str:
        """Create human-readable summary of query"""
        if query_type == 'context7':
            return f"Library: {query_params.get('library', 'unknown')}"
        elif query_type == 'arxiv':
            return f"Papers: {query_params.get('query', 'unknown')}"
        elif query_type == 'web':
            return f"Web: {query_params.get('query', 'unknown')[:50]}..."
        return f"{query_type}: {str(query_params)[:50]}..."
    
    def _invalidate(self, key: str):
        """Remove expired or invalid cache entry"""
        if key in self.index:
            del self.index[key]
            self._save_index()
        
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
    
    def clear_expired(self):
        """Remove all expired cache entries"""
        now = datetime.now()
        keys_to_remove = []
        
        for key, entry in self.index.items():
            created_time = datetime.fromisoformat(entry['created'])
            if now - created_time > self.ttl:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._invalidate(key)
        
        return len(keys_to_remove)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.index)
        expired_count = 0
        size_bytes = 0
        
        by_type = {}
        
        for key, entry in self.index.items():
            query_type = entry['query_type']
            by_type[query_type] = by_type.get(query_type, 0) + 1
            
            created_time = datetime.fromisoformat(entry['created'])
            if datetime.now() - created_time > self.ttl:
                expired_count += 1
            
            cache_file = self.cache_dir / entry['file']
            if cache_file.exists():
                size_bytes += cache_file.stat().st_size
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'active_entries': total_entries - expired_count,
            'total_size_mb': round(size_bytes / (1024 * 1024), 2),
            'by_type': by_type,
            'cache_dir': str(self.cache_dir)
        }


def main():
    """CLI interface for cache management"""
    import sys
    
    cache = ResearchCache()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'stats':
            stats = cache.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif command == 'clear-expired':
            removed = cache.clear_expired()
            print(f"Removed {removed} expired entries")
        
        elif command == 'test':
            # Test cache functionality
            test_params = {'library': 'react', 'version': '18.0.0'}
            
            # Test set
            cache.set('context7', test_params, {'docs': 'test data'})
            print("✓ Cache set successful")
            
            # Test get
            result = cache.get('context7', test_params)
            if result and result['result']['docs'] == 'test data':
                print("✓ Cache get successful")
            else:
                print("✗ Cache get failed")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: stats, clear-expired, test")
    else:
        print("Research Cache Manager")
        print("Usage: research_cache.py [stats|clear-expired|test]")


if __name__ == '__main__':
    main()