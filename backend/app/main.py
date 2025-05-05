"""Main application module for the news aggregator API."""

import uvicorn
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
    """Root endpoint that returns a welcome message and performs
    DB call for performance testing.

    Returns:
        dict[str, str]: A welcome message and database status.
    """
    from app.db.session import get_session
    from sqlalchemy import text
    from datetime import datetime

    # Perform a simple database query for performance testing
    session = None
    try:
        async for db_session in get_session():
            session = db_session
            result = await session.execute(text("SELECT 1"))
            db_status = "connected" if result.scalar() == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "message": "Welcome to the News Aggregator API",
        "database_status": db_status,
        "timestamp": str(datetime.now())
    }


if __name__ == "__main__":
    # Use 127.0.0.1 instead of 0.0.0.0 to avoid binding to all interfaces
    # This addresses security issue B104: hardcoded_bind_all_interfaces
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
