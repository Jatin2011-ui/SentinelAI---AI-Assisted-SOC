"""Redis client wrapper (PRD section 31).

Provides a lazily-created, cached client for caching, temporary agent
state, rate limiting, and (in later phases) WebSocket fan-out.

The backend must never crash just because Redis is unavailable:
``is_available()`` returns False instead of raising, and callers are
expected to degrade gracefully (PRD section 52).
"""
from functools import lru_cache

import redis

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger("redis")


@lru_cache
def get_redis() -> redis.Redis:
    """Return a cached Redis client.

    The client object is cheap to construct and does not connect until
    first use, so this is safe to call even when Redis is down.
    """
    settings = get_settings()
    return redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=1.0,
        socket_timeout=1.0,
    )


def is_available() -> bool:
    """Ping Redis and report availability without raising."""
    try:
        return bool(get_redis().ping())
    except redis.RedisError as exc:
        log.warning("redis_unavailable", error=str(exc))
        return False
