"""Redis client wrapper tests (PRD section 31, 46)."""
import redis as redis_lib

from app.core import redis_client


def test_is_available_false_when_redis_down(monkeypatch):
    def boom(*args, **kwargs):
        raise redis_lib.ConnectionError("no redis here")

    monkeypatch.setattr(redis_client.get_redis(), "ping", boom)
    assert redis_client.is_available() is False


def test_get_redis_is_cached():
    assert redis_client.get_redis() is redis_client.get_redis()
