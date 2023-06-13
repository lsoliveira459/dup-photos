"""
Defining db connections, tables and helper functions.

Sources:
- [stackoverflow.com/../database-on-the-fly-with-scripting-languages](https://stackoverflow.com/a/2580543):
    On how to work with sqlalchemy.Table to dinamically create Columns.
"""
from typing import Any, Optional

from sqlalchemy import Column, ForeignKey, String, Table, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, Session

association_table = Table(
    "association_table",
    Base.metadata,
    Column("file_id", ForeignKey("files.id"), primary_key=True),
    Column("hash_id", ForeignKey("hashes.id"), primary_key=True),
)

class Files(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String)
    filetype: Mapped[Optional[str]]
    hashes: Mapped[list["Hashes"]] = relationship(secondary=association_table,
                                                 back_populates="files",)

    def __repr__(self) -> str:
        return f"Files(path={self.path!r}, filetype={self.filetype!r}, hashes={len(self.hashes)})"

    @classmethod
    async def get_one(cls, path):
        async with Session.begin() as session:
            query = select(Files).filter_by(path = path).scalar_one()
            item = await session.execute(query)
            return item

    @classmethod
    async def get_cached_items(cls):
        async with Session.begin() as session:
            query = select(cls.path, Hashes.hashtype)\
                .join_from(Files, association_table)\
                .join(Hashes)
            result = await session.stream(query)
            return {(row.path, row.hashtype) async for row in result}

    @classmethod
    async def is_it_cached(cls):
        raise NotImplementedError()

    @classmethod
    async def total_cached(cls) -> int:
        async with Session.begin() as session:
            count_query = select(func.count(Files.id))
            result = await session.execute(count_query)
            return result.scalar()
        # return sum(1 for f in cached_files.values() for _ in f.keys())

    @classmethod
    async def update_hashes(cls, file, hashes: list["Hashes"]) -> None:
        async with Session.begin() as session:
            query = select(cls).filter_by(path = file)
            item = (await session.execute(query)).scalar_one()
            item.hashes.update(hashes)

class Hashes(Base):
    __tablename__ = "hashes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hashtype: Mapped[str] = mapped_column(String)
    hashvalue: Mapped[str] = mapped_column(String)
    files: Mapped[list["Files"]] = relationship(secondary=association_table,
                                               back_populates="hashes",)

    def __repr__(self) -> str:
        return f"Hashes(id={self.id!r}, file={self.file.path!r}, )"

async def add_all(buffer: list[Any]):
    async with Session.begin() as session:
        if buffer:
            session.add_all(buffer)