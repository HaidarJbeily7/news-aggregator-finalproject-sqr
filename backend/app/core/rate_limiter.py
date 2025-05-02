"""Rate limiter implementation."""
from cachetools import TTLCache


class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed.
            time_window: Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.cache = TTLCache(
            maxsize=10000,
            ttl=time_window,
        )

    def is_allowed(self, client_id: str) -> bool:
        """Check if a client has exceeded the rate limit.

        Args:
            client_id: Client identifier (e.g., IP address).

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        # Get client's request count
        request_count = self.cache.get(client_id, 0)

        # Check if limit is exceeded
        if request_count >= self.max_requests:
            return False

        # Increment request count
        self.cache[client_id] = request_count + 1
        return True

    async def check_rate_limit(self, client_id: str) -> None:
        """Check if a client has exceeded the rate limit.

        Args:
            client_id: Client identifier (e.g., IP address).

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        return self.is_allowed(client_id)
