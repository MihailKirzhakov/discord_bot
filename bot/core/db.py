from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    declared_attr, DeclarativeBase, mapped_column, Mapped
)

from .config import settings


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


async_engine = create_async_engine(settings.database_url)
async_session_factory = async_sessionmaker(async_engine)
