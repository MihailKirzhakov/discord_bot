from typing import Annotated, TypeVar

from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declared_attr, DeclarativeBase,  mapped_column

from .config import settings


intpk = Annotated[int, mapped_column(primary_key=True, unique=True)]
strpk = Annotated[str, mapped_column(primary_key=True, unique=True)]
int_uniq = Annotated[int, mapped_column(unique=True)]
str_uniq = Annotated[str, mapped_column(unique=True)]
int_empty = Annotated[int, mapped_column(nullable=True)]
str_empty = Annotated[str, mapped_column(nullable=True)]
bool_empty = Annotated[bool, mapped_column(nullable=True)]


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__


ModelType = TypeVar('ModelType', bound=Base)
_is_sqlite = settings.database_url.startswith('sqlite')

async_engine = create_async_engine(
    settings.database_url,
    # Сессии держат write-lock, пока идут вызовы Discord API (fetch/edit),
    # и по умолчанию через 5 с конкурент получает "database is locked"
    connect_args={'timeout': 30} if _is_sqlite else {},
)

if _is_sqlite:
    @event.listens_for(async_engine.sync_engine, 'connect')
    def _sqlite_pragmas(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        # WAL: чтения не блокируют запись и наоборот
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.close()

async_session_factory = async_sessionmaker(async_engine)
