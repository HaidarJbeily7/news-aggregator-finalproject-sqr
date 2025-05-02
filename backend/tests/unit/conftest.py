"""Test configuration and fixtures."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models import Base


async def create_test_engine():
    """Create a test database engine."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )


async def setup_test_database(engine):
    """Set up the test database schema."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_test_session(engine):
    """Create a test database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session()


@pytest.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    engine = await create_test_engine()
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine):
    """Create a test database session."""
    await setup_test_database(engine)
    session = await create_test_session(engine)
    yield session
    await session.rollback()
    await session.close()
