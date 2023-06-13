from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///database.db")

class Base(DeclarativeBase):
    pass

Session = sessionmaker(engine, autoflush=True, class_=AsyncSession)

async def async_create_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_drop_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

from .files import Files, Hashes, association_table