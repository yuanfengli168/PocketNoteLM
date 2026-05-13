"""
In-process TTL cache for repeated questions.

Uses a hash of (question, session_id) as key. If the exact same question
is asked in the same session within the TTL window, the cached answer is
returned without hitting the LLM or vector store.
"""

import hashlib

from cachetools import TTLCache

from config import get_settings

_cache: TTLCache | None = None


def _get_cache() -> TTLCache:
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = TTLCache(maxsize=256, ttl=settings.cache_ttl)
    return _cache


def _make_key(question: str, session_id: str) -> str:
    raw = f"{session_id}::{question.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_answer(question: str, session_id: str) -> str | None:
    return _get_cache().get(_make_key(question, session_id))


def set_cached_answer(question: str, session_id: str, answer: str) -> None:
    _get_cache()[_make_key(question, session_id)] = answer
