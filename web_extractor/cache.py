"""Caching module for pipeline results."""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Any, Optional
from config import CACHE_DIR, CACHE_ENABLED, CACHE_TTL


class Cache:
    """Simple file-based cache for pipeline results."""
    
    def __init__(self, cache_dir: str = CACHE_DIR, enabled: bool = CACHE_ENABLED):
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_path(self, key: str) -> Path:
        """Get full path for cache file."""
        return self.cache_dir / f"{key}.json"
    
    def get(self, query: str) -> Optional[dict]:
        """Retrieve cached result."""
        if not self.enabled:
            return None
        
        key = self._get_key(query)
        path = self._get_path(key)
        
        if not path.exists():
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check TTL
            if time.time() - data["timestamp"] > CACHE_TTL:
                path.unlink()  # Delete expired cache
                return None
            
            return data["result"]
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def set(self, query: str, result: dict) -> None:
        """Store result in cache."""
        if not self.enabled:
            return
        
        key = self._get_key(query)
        path = self._get_path(key)
        
        try:
            data = {
                "query": query,
                "timestamp": time.time(),
                "result": result
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear(self) -> None:
        """Clear all cache."""
        try:
            for file in self.cache_dir.glob("*.json"):
                file.unlink()
        except Exception as e:
            print(f"Cache clear error: {e}")


cache = Cache()
