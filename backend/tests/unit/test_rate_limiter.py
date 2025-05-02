"""Tests for the rate limiter."""
import pytest

from app.core.rate_limiter import RateLimiter


@pytest.fixture
def rate_limiter():
    """Create a rate limiter fixture."""
    return RateLimiter(max_requests=2, time_window=1)


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests(rate_limiter):
    """Test that the rate limiter allows requests within the limit."""
    client_id = "test_client"

    # First request should be allowed
    assert await rate_limiter.check_rate_limit(client_id) is True

    # Second request should be allowed
    assert await rate_limiter.check_rate_limit(client_id) is True


@pytest.mark.asyncio
async def test_rate_limiter_blocks_excess_requests(rate_limiter):
    """Test that the rate limiter blocks requests exceeding the limit."""
    client_id = "test_client"

    # Make two requests (within limit)
    await rate_limiter.check_rate_limit(client_id)
    await rate_limiter.check_rate_limit(client_id)

    # Third request should be blocked
    assert await rate_limiter.check_rate_limit(client_id) is False


@pytest.mark.asyncio
async def test_rate_limiter_resets_after_time_window(rate_limiter):
    """Test that the rate limiter resets after the time window."""
    client_id = "test_client"

    # Make two requests (within limit)
    await rate_limiter.check_rate_limit(client_id)
    await rate_limiter.check_rate_limit(client_id)

    # Third request should be blocked
    assert await rate_limiter.check_rate_limit(client_id) is False

    # Wait for time window to expire
    import time
    time.sleep(1)

    # Request should be allowed again
    assert await rate_limiter.check_rate_limit(client_id) is True
