from sqlalchemy import delete, select, func

from .db import async_engine, async_session_factory
from .models import Base, UserBid, MessageData, RoleApplicationData


class AsyncORM:

    # --------------------------------------------------------------------------------
    # Создание БД
    @staticmethod
    async def create_tables():
        """Метод для инициализации БД и создания таблиц"""
        async with async_engine.begin() as conn:
            # await conn.run_sync(AuctionModel.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    # --------------------------------------------------------------------------------
    # Методы для добавления данных в БД
    @staticmethod
    async def add_flush_commit(session, data):
        session.add_all([data])
        await session.flush()
        await session.commit()

    @staticmethod
    async def insert_bid_data(user_id, user_bid, lot_id):
        """Метод для добавления ставки в БД"""
        async with async_session_factory() as session:
            data = UserBid(
                user_id=user_id,
                user_bid=user_bid,
                lot_id=lot_id
            )
            await AsyncORM.add_flush_commit(session, data)

    @staticmethod
    async def insert_message_data(message_id, message_name):
        """Метод для добавления данных в напоминалку"""
        async with async_session_factory() as session:
            data = MessageData(
                message_id=message_id,
                message_name=message_name
            )
            await AsyncORM.add_flush_commit(session, data)

    @staticmethod
    async def insert_role_application_data(
        nickname, user_id, acc_btn_cstm_id, den_btn_cstm_id
    ):
        """Метод для добавления данных в напоминалку"""
        async with async_session_factory() as session:
            data = RoleApplicationData(
                nickname=nickname,
                user_id=user_id,
                acc_btn_cstm_id=acc_btn_cstm_id,
                den_btn_cstm_id=den_btn_cstm_id
            )
            await AsyncORM.add_flush_commit(session, data)

    # --------------------------------------------------------------------------------
    # Методы для получения данных из БД
    @staticmethod
    async def get_obj_by_pk(model, pk):
        """Метод для получения данных из БД по первичному ключу"""
        async with async_session_factory() as session:
            result = await session.get(model, pk)
            return result

    @staticmethod
    async def get_filter_obj(model, field_name, value):
        """Метод для получения данных из БД по значению в поле модели"""
        async with async_session_factory() as session:
            # Получаем поле модели по имени
            result = await session.execute(
                select(model).where(getattr(model, field_name) == value)
            )
            return result.scalars().first()

    @staticmethod
    async def get_roleapp_obj(pk):
        """Метод для получения данных из БД по первичному ключу"""
        async with async_session_factory() as session:
            result = await session.get(RoleApplicationData, pk)
            return result

    @staticmethod
    async def get_roleapp_count():
        """Метод для получения количества строк в таблице"""
        async with async_session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(RoleApplicationData)
            )
            count = result.scalar()
            return count

    @staticmethod
    async def get_btn_cstm_ids():
        """Метод для получения всех значений столбцов acc_btn_cstm_id и den_btn_cstm_id из БД"""
        async with async_session_factory() as session:
            stmt = select(
                RoleApplicationData.acc_btn_cstm_id,
                RoleApplicationData.den_btn_cstm_id
            )
            result = await session.execute(stmt)
            return result.all()

    # --------------------------------------------------------------------------------
    # Методы для обновления данных в БД
    @staticmethod
    async def update_bid_data(user_id, new_value):
        """Метод для изменения ставки по названию поля"""
        async with async_session_factory() as session:
            # Получаем объект по полю user_id
            obj = await AsyncORM.get_filter_obj(UserBid, 'user_id', user_id)

            if obj:
                setattr(obj, 'user_bid', new_value)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
            else:
                raise ValueError("Объект не найден")

    # --------------------------------------------------------------------------------
    # Методы для удаления данных из БД
    @staticmethod
    async def delete_bid_data(user_id):
        """Метод для удаления ставки из БД"""
        async with async_session_factory() as session:
            obj = await AsyncORM.get_filter_obj(UserBid, 'user_id', user_id)
            await session.delete(obj)
            await session.commit()

    @staticmethod
    async def delete_roleapp_data(pk):
        """Метод для удаления заявки из бд"""
        async with async_session_factory() as session:
            obj = await AsyncORM.get_obj_by_pk(RoleApplicationData, pk)
            await session.delete(obj)
            await session.commit()

    @staticmethod
    async def clear_auction_table():
        """Метод для удаления очистки таблицы auction в БД"""
        async with async_session_factory() as session:
            await session.execute(delete(UserBid))
            await session.commit()

    @staticmethod
    async def clear_roleapp_table():
        """Метод для удаления очистки таблицы заявок в БД"""
        async with async_session_factory() as session:
            await session.execute(delete(RoleApplicationData))
            await session.commit()
