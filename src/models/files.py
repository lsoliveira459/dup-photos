from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.orm import declarative_base, create_session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from hashlib import algorithms_available
import asyncio

engine = create_async_engine("sqlite+aiosqlite:///database.db")
metadata = MetaData()

Files = Table('files', metadata,
                Column('path', String, primary_key=True),
                Column('visual', String, index=True),
                *(Column(rowname, String) for rowname in algorithms_available))

Session = sessionmaker(engine,
                        autoflush=True,
                        class_=AsyncSession)

async def async_create_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def async_drop_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

def async2sync(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)