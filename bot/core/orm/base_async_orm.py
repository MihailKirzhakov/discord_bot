from typing import Type

from sqlalchemy import delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from core import Base, async_engine, ModelType


class AsyncORM():

    def __init__(self):
        super().__init__()

    # --------------------------------------------------------------------------------
    # Создание БД
    async def create_tables(self):
        """Метод для инициализации БД и создания таблиц"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # --------------------------------------------------------------------------------
    # Базовые методы
    async def add_flush(self, session: AsyncSession, data):
        """Метод для выполнения добавления данных в БД и обновления БД"""
        session.add_all([data])
        await session.flush()

    async def get_obj_by_pk(
        self, session: AsyncSession, model: Type[ModelType], pk
    ):
        """Метод для получения данных из БД по первичному ключу"""
        result = await session.get(model, pk)
        # self.obj_validation(result)
        return result

    async def get_filter_obj(
        self, session: AsyncSession, model: Type[ModelType], **filters
    ) -> Result:
        """Метод для получения данных из БД по значениям в полях модели"""
        query = select(model)
        conditions = []
        for field_name, value in filters.items():
            conditions.append(getattr(model, field_name) == value)
        if conditions:
            query = query.where(and_(*conditions))
        result = await session.execute(query)
        self.obj_validation(result)
        return result

    async def get_filter_obj_first(
        self, session: AsyncSession, model: Type[ModelType], **filters
    ):
        """Метод для получения первого найденного значения из БД по значениям в полях модели"""
        result = await self.get_filter_obj(session, model, **filters)
        return result.scalars().first()

    async def get_filter_obj_all(
        self, session: AsyncSession, model: Type[ModelType], **filters
    ):
        """Метод для получения всех данных из БД по значениям в полях модели"""
        result = await self.get_filter_obj(session, model, **filters)
        return result.scalars().all()

    async def delete_data(self, session: AsyncSession, obj):
        """Метод для удаления данных из БД"""
        self.obj_validation(obj)
        await session.delete(obj)
        await session.flush()

    async def clear_table(self, session: AsyncSession, model: Type[ModelType]):
        """Метод для очистки таблицы в БД"""
        await session.execute(delete(model))
        await session.flush()

    def obj_validation(self, obj):
        """
        Метод проверяет наличие получаемого объекта из БД и выбрасывает
        исключение, если объект не получен
        """
        if not obj:
            raise ValueError('Искомый объект не найден')


async_orm = AsyncORM()
