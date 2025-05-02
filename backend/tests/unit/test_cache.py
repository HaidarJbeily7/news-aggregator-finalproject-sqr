"""Tests for the cache."""
import pytest

from app.core.cache import Cache


@pytest.fixture
def cache():
    """Create a cache fixture."""
    return Cache(max_size=2, ttl=1)


@pytest.mark.asyncio
async def test_cache_set_and_get(cache):
    """Test setting and getting values from the cache."""
    key = "test_key"
    value = b"test_value"

    # Set value in cache
    await cache.set(key, value)

    # Get value from cache
    cached_value = await cache.get(key)
    assert cached_value == value


@pytest.mark.asyncio
async def test_cache_miss(cache):
    """Test getting a non-existent value from the cache."""
    key = "non_existent_key"

    # Get value from cache
    cached_value = await cache.get(key)
    assert cached_value is None


@pytest.mark.asyncio
async def test_cache_eviction(cache):
    """Test cache eviction when max size is reached."""
    # Set first value
    await cache.set("key1", b"value1")

    # Set second value
    await cache.set("key2", b"value2")

    # Set third value (should evict first value)
    await cache.set("key3", b"value3")

    # First value should be evicted
    assert await cache.get("key1") is None

    # Second and third values should still be in cache
    assert await cache.get("key2") == b"value2"
    assert await cache.get("key3") == b"value3"


@pytest.mark.asyncio
async def test_cache_expiration(cache):
    """Test cache expiration after TTL."""
    key = "test_key"
    value = b"test_value"

    # Set value in cache
    await cache.set(key, value)

    # Value should be in cache
    assert await cache.get(key) == value

    # Wait for TTL to expire
    import time
    time.sleep(1)

    # Value should be expired
    assert await cache.get(key) is None
