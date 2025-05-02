"""Middleware for rate limiting and caching."""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

from app.core.rate_limiter import RateLimiter
from app.core.cache import Cache


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(self, app: ASGIApp, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        """Dispatch the request with rate limiting."""
        client_ip = request.client.host
        if not await self.rate_limiter.check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )
        return await call_next(request)


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching responses."""

    def __init__(self, app: ASGIApp, cache: Cache):
        super().__init__(app)
        self.cache = cache

    async def dispatch(self, request: Request, call_next):
        """Dispatch the request with caching."""
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Generate cache key
        cache_key = f"{request.url.path}?{request.url.query}"
        # Try to get from cache
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            return JSONResponse(
                status_code=200,
                content=json.loads(cached_response),
            )

        # Process request
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            # Handle streaming responses which don't have a body attribute
            if hasattr(response, 'body'):
                await self.cache.set(cache_key, response.body.decode())

        return response
