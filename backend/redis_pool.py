from __future__ import annotations

"""Redis connection pooling utility.

Provides a single shared :pyclass:`redis.Redis` connection using a global
:pyclass:`redis.ConnectionPool` with an upper bound on open TCP
connections (``max_connections=10``).
"""

import os
from typing import Final

try:
    import redis  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "The 'redis' package is required for Redis integration. Install with 'pip install redis'."
    ) from exc

REDIS_URL: Final[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_pool: redis.ConnectionPool = redis.ConnectionPool.from_url(REDIS_URL, max_connections=10)


def get_redis() -> "redis.Redis":
    """Return a Redis client using the shared connection *pool*."""
    return redis.Redis(connection_pool=_pool)