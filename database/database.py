"""
database/database.py — Async PostgreSQL ulanish va session boshqaruvi
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine,
    create_async_engine, async_sessionmaker
)
from sqlalchemy.pool import NullPool
from loguru import logger

from config import config
from database.models import Base


# ─── Engine ───────────────────────────────────────────────────────────────────

engine: AsyncEngine = create_async_engine(
    config.db.url,
    echo=False,
    poolclass=NullPool,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def create_tables() -> None:
    """Barcha jadvallarni yaratish (agar mavjud bo'lmasa)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ Database jadvallari yaratildi / tekshirildi.")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection uchun session generator."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncSession:
    """Handler ichida ishlatish uchun session qaytaradi."""
    return AsyncSessionFactory()
