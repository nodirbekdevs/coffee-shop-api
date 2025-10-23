from __future__ import annotations

from uuid import uuid4

from asyncpg import Connection

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


class CConnection(Connection):  # type: ignore
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


async_engine = create_async_engine(
    url=settings.DB.DATABASE_URL,
    echo=False,
    pool_size=settings.DB.POOL_SIZE,
    max_overflow=settings.DB.MAX_OVERFLOW,
    pool_timeout=settings.DB.POOL_TIMEOUT,
    pool_recycle=settings.DB.POOL_RECYCLE,
    pool_pre_ping=True,
)
async_session_maker = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
