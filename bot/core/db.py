from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    declared_attr, DeclarativeBase, mapped_column, Mapped
)

from .config import settings


intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[intpk]


# Base: DeclarativeBase = declarative_base(cls=PreBase)
async_engine = create_async_engine(settings.database_url)
async_session_factory = async_sessionmaker(async_engine)


# async def get_async_session():
#     async with AsyncSessionLocal() as async_session:
#         yield async_session
