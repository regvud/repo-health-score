from typing import Any

from django.core.cache import cache

TTL: int = 3600


def get_cache(key: str) -> Any | None:
    return cache.get(key)


def set_cache(key: str, data: Any) -> None:
    cache.set(key, data, TTL)
