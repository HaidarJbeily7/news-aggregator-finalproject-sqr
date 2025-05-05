"""Cache implementation."""
from typing import Optional

from cachetools import TTLCache


class Cache:
    """Cache for API responses."""

    def __init__(
        self,
        max_size: int = 1000,
        ttl: int = 300,
    ) -> None:
        """Initialize the cache.

        Args:
            max_size: Maximum number of items in the cache.
            ttl: Time to live in seconds.
        """
        self.cache_storage = TTLCache(
            maxsize=max_size,
            ttl=ttl,
        )

    async def get(self, key: str) -> Optional[bytes]:
        """Get a value from the cache.

        Args:
            key: Cache key.

        Returns:
            Optional[bytes]: Cached value if found, None otherwise.
        """
        return self.cache_storage.get(key)

    async def set(self, key: str, value: bytes) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        self.cache_storage[key] = value
