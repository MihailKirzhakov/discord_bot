from sqlalchemy import delete, update

from .db import async_engine, async_session_factory
from .models import Base, UserBid, MessageData


class AsyncORM:

    # --------------------------------------------------------------------------------
    # Создаybt БД
    @staticmethod
    async def create_tables():
        """Метод для инициализации БД и создания таблиц"""
        async with async_engine.begin() as conn:
            # await conn.run_sync(AuctionModel.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    # --------------------------------------------------------------------------------
    # Методы для добавления данных в БД
    @staticmethod
    async def insert_bid_data(user_id, user_bid, lot_id):
        """Метод для внесения данных в БД"""
        async with async_session_factory() as session:
            bid_data = UserBid(discord_id=user_id, user_bid=user_bid, lot_id=lot_id)
            session.add_all([bid_data])
            await session.flush()
            await session.commit()

    @staticmethod
    async def insert_message_data(message_id, message_name):
        async with async_session_factory() as session:
            message_data = MessageData(discord_id=message_id, message_name=message_name)
            session.add_all([message_data])
            await session.flush()
            await session.commit()

    # --------------------------------------------------------------------------------
    # Методы для обновления данных в БД
    @staticmethod
    async def update_bid_data(discord_id, user_bid):
        """Метод для обновления данных в БД"""
        async with async_session_factory() as session:
            bid_data = await session.get(UserBid, discord_id)
            bid_data.user_bid = user_bid
            session.add(bid_data)
            await session.commit()
            await session.refresh(bid_data)

    # --------------------------------------------------------------------------------
    # Методы для получения данных из БД
    @staticmethod
    async def get_id_data(discord_id):
        """Метод для получения данных из БД"""
        async with async_session_factory() as session:
            bid_data = await session.get(Auction, discord_id)
            return bid_data

    # --------------------------------------------------------------------------------
    # Методы для удаления данных из БД
    @staticmethod
    async def delete_bid_data(discord_id):
        """Метод для удаления ставки из БД"""
        async with async_session_factory() as session:
            bid_data = await session.get(Auction, discord_id)
            session.delete(bid_data)
            await session.commit()

    @staticmethod
    async def clear_tables():
        """Метод для удаления очистки таблицы auction в БД"""
        async with async_session_factory() as session:
            await session.execute(delete(Auction))
            await session.commit()
