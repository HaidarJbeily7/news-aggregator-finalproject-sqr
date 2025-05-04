"""Main application module for the news aggregator API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.middleware import RateLimitMiddleware, CacheMiddleware
from app.core.rate_limiter import RateLimiter
from app.core.cache import Cache


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up rate limiting
    rate_limiter = RateLimiter(
        max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
        time_window=settings.RATE_LIMIT_TIME_WINDOW,
    )
    app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

    # Set up caching
    cache = Cache(
        max_size=settings.CACHE_MAX_SIZE,
        ttl=settings.CACHE_TTL,
    )
    app.add_middleware(CacheMiddleware, cache=cache)

    # Include API router
    app.include_router(api_router, prefix="")

    return app


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that returns a welcome message.

    Returns:
        dict[str, str]: A welcome message.
    """
    return {"message": "Welcome to the News Aggregator API"}
