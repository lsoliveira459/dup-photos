"""
Defining db connections, tables and helper functions.
TODO: Breakdown files.py into multiple files, modules and functions for readability and maintainability.

Sources:
- [stackoverflow.com/../database-on-the-fly-with-scripting-languages](https://stackoverflow.com/a/2580543):
    On how to work with sqlalchemy.Table to dinamically create Columns.
"""
from sqlalchemy import MetaData, Table, Column, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from hashlib import algorithms_available
import asyncio

engine = create_async_engine("sqlite+aiosqlite:///database.db")
metadata = MetaData()

Files = Table(
    "files",
    metadata,
    Column("path", String, primary_key=True),
    Column("filetype", JSON, index=True),
    Column("visual", String),
    *(Column(rowname, String) for rowname in algorithms_available)
)

Session = sessionmaker(engine, autoflush=True, class_=AsyncSession)


async def async_create_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def async_drop_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
