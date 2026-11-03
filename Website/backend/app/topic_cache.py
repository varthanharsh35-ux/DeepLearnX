"""
DeepLearnX Topic Research and Concept Extraction Cache.

Caches:
1. Multi-source encyclopedic research and extracted facts per topic.
2. Topic interpretation (objectives, scope, discipline classification).
3. Synthesized/extracted concepts and prerequisite structures.

Reduces redundant external network requests and LLM generation calls.
"""

import os
import re
import json
import time
import hashlib
import threading
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("deeplearnx.topic_cache")


def _normalize_key(topic: str, context: str = "") -> str:
    clean_t = re.sub(r'[^a-z0-9]', '', (topic or "").lower().strip())
    clean_c = re.sub(r'[^a-z0-9]', '', (context or "").lower().strip()[:200])
    return f"{clean_t}::{clean_c}"


class TopicResearchCache:
    """Thread-safe cache for academic research, interpretations, and concept models."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, ttl_seconds: float = 86400.0):  # 24 hours
        if getattr(self, "_initialized", False):
            return
        self.ttl = ttl_seconds
        self._research_cache: Dict[str, Dict[str, Any]] = {}
        self._interpretation_cache: Dict[str, Dict[str, Any]] = {}
        self._concept_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._initialized = True

    def get_research(self, topic: str) -> Optional[Dict[str, Any]]:
        k = _normalize_key(topic)
        with self._cache_lock:
            entry = self._research_cache.get(k)
            if entry and (time.time() - entry["timestamp"]) < self.ttl:
                self._hits += 1
                logger.info(f"[TopicCache] Cache HIT for research on '{topic}'.")
                return entry["data"]
            self._misses += 1
            return None

    def set_research(self, topic: str, data: Dict[str, Any]) -> None:
        if not topic or not data:
            return
        k = _normalize_key(topic)
        with self._cache_lock:
            self._research_cache[k] = {
                "data": data,
                "timestamp": time.time()
            }
            logger.info(f"[TopicCache] Cached research for '{topic}' ({len(data.get('articles', []))} articles, {len(data.get('extracted_facts', []))} facts).")

    def get_interpretation(self, topic: str, syllabus: str = "") -> Optional[Dict[str, Any]]:
        k = _normalize_key(topic, syllabus)
        with self._cache_lock:
            entry = self._interpretation_cache.get(k)
            if entry and (time.time() - entry["timestamp"]) < self.ttl:
                self._hits += 1
                logger.info(f"[TopicCache] Cache HIT for interpretation of '{topic}'.")
                return entry["data"]
            self._misses += 1
            return None

    def set_interpretation(self, topic: str, syllabus: str, data: Dict[str, Any]) -> None:
        if not topic or not data:
            return
        k = _normalize_key(topic, syllabus)
        with self._cache_lock:
            self._interpretation_cache[k] = {
                "data": data,
                "timestamp": time.time()
            }
            logger.info(f"[TopicCache] Cached interpretation for '{topic}'.")

    def get_concepts(self, topic: str) -> Optional[Any]:
        k = _normalize_key(topic)
        with self._cache_lock:
            entry = self._concept_cache.get(k)
            if entry and (time.time() - entry["timestamp"]) < self.ttl:
                self._hits += 1
                return entry["data"]
            self._misses += 1
            return None

    def set_concepts(self, topic: str, data: Any) -> None:
        if not topic or not data:
            return
        k = _normalize_key(topic)
        with self._cache_lock:
            self._concept_cache[k] = {
                "data": data,
                "timestamp": time.time()
            }

    def clear(self) -> None:
        with self._cache_lock:
            self._research_cache.clear()
            self._interpretation_cache.clear()
            self._concept_cache.clear()
            self._hits = 0
            self._misses = 0


# Global instance
_global_topic_cache: Optional[TopicResearchCache] = None

def get_topic_cache() -> TopicResearchCache:
    global _global_topic_cache
    if _global_topic_cache is None:
        _global_topic_cache = TopicResearchCache()
    return _global_topic_cache
