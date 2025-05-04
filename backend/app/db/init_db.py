"""Database initialization script."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.models import Base


async def init_db() -> None:
    """Initialize the database."""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Close the engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
