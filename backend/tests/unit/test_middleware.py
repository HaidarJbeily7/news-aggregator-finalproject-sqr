"""Tests for middleware functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.middleware import RateLimitMiddleware, CacheMiddleware
from app.core.rate_limiter import RateLimiter
from app.core.cache import Cache


@pytest.fixture
def mock_rate_limiter():
    """Fixture for mock rate limiter."""
    limiter = MagicMock(spec=RateLimiter)
    limiter.check_rate_limit = AsyncMock(return_value=True)
    return limiter


@pytest.fixture
def mock_cache():
    """Fixture for mock cache."""
    cache = MagicMock(spec=Cache)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    return cache


@pytest.fixture
def mock_app():
    """Fixture for mock FastAPI app."""
    app = FastAPI()
    return app


@pytest.mark.asyncio
async def test_rate_limit_middleware_allowed(mock_rate_limiter, mock_app):
    """Test rate limit middleware when request is allowed."""
    middleware = RateLimitMiddleware(mock_app, mock_rate_limiter)
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"message": "success"})

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 200
    assert response.body == b'{"message":"success"}'
    assert mock_rate_limiter.check_rate_limit.call_count == 1
    assert mock_rate_limiter.check_rate_limit.call_args[0][0] == "127.0.0.1"


@pytest.mark.asyncio
async def test_rate_limit_middleware_exceeded(mock_rate_limiter, mock_app):
    """Test rate limit middleware when request is not allowed."""
    mock_rate_limiter.check_rate_limit = AsyncMock(return_value=False)
    middleware = RateLimitMiddleware(mock_app, mock_rate_limiter)
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"message": "success"})

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.body.decode()
    assert mock_rate_limiter.check_rate_limit.call_count == 1
    assert mock_rate_limiter.check_rate_limit.call_args[0][0] == "127.0.0.1"


@pytest.mark.asyncio
async def test_cache_middleware_miss(mock_cache, mock_app):
    """Test cache middleware when cache miss occurs."""
    middleware = CacheMiddleware(mock_app, mock_cache)
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"message": "success"})

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 200
    assert response.body == b'{"message":"success"}'
    assert mock_cache.get.call_count == 1
    assert mock_cache.set.call_count == 1


@pytest.mark.asyncio
async def test_cache_middleware_hit(mock_cache, mock_app):
    """Test cache middleware when cache hit occurs."""
    # Create a proper JSONResponse for the cached value
    cached_response = JSONResponse({"message": "cached"})
    mock_cache.get = AsyncMock(return_value=cached_response.body.decode())

    middleware = CacheMiddleware(mock_app, mock_cache)
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"message": "success"})

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 200
    assert response.body == b'{"message":"cached"}'
    assert mock_cache.get.call_count == 1
    assert mock_cache.set.call_count == 0


@pytest.mark.asyncio
async def test_cache_middleware_non_get(mock_cache, mock_app):
    """Test cache middleware with non-GET requests."""
    middleware = CacheMiddleware(mock_app, mock_cache)
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "POST"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"message": "success"})

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 200
    assert response.body == b'{"message":"success"}'
    assert mock_cache.get.call_count == 0
    assert mock_cache.set.call_count == 0


@pytest.mark.asyncio
async def test_cache_middleware_error_response(mock_cache, mock_app):
    """Test cache middleware with error response."""
    middleware = CacheMiddleware(mock_app, mock_cache)
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    # Mock the call_next function
    async def mock_call_next(request):
        return JSONResponse({"error": "not found"}, status_code=404)

    response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 404
    assert response.body == b'{"error":"not found"}'
    assert mock_cache.get.call_count == 1
    assert mock_cache.set.call_count == 0
