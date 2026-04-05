import json
import os
import hashlib
from typing import Any, Optional

CACHE_DIR = "data"
CACHE_FILE = os.path.join(CACHE_DIR, "tavily_cache.json")

class DiskCache:
    def __init__(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=4)

    def _generate_key(self, query: str, start_date: str, end_date: str) -> str:
        """Creates a unique hash for the search parameters."""
        key_str = f"{query}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, start_date: str, end_date: str) -> Optional[Any]:
        key = self._generate_key(query, start_date, end_date)
        return self.cache.get(key)

    def set(self, query: str, start_date: str, end_date: str, data: Any):
        key = self._generate_key(query, start_date, end_date)
        self.cache[key] = data
        self._save_cache()
