"""
Database connection and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from models.base import Base


# Get settings
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL in debug mode
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all tables - use with caution!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Get an async database session"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncSession:
    """Dependency for FastAPI - yields a database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
