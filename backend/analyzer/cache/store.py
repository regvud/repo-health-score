import time
from typing import Any

_store: dict[str, tuple[Any, float]] = {}
TTL: int = 3600


def get_cache(key: str) -> Any | None:
    entry = _store.get(key)
    if entry and time.monotonic() - entry[1] < TTL:
        return entry[0]
    _store.pop(key, None)
    return None


def set_cache(key: str, data: Any) -> None:
    _store[key] = (data, time.monotonic())
