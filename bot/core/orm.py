from .db import async_engine, async_session_factory
from .models import Base, Auction, MessageData


class AsyncORM:

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            # await conn.run_sync(AuctionModel.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_bid_data():
        async with async_session_factory() as session:
            test_bid = Auction(user_id='12345678', user_bid=300000)
            session.add_all([test_bid])
            await session.flush()
            await session.commit()

    @staticmethod
    async def insert_message_data():
        async with async_session_factory() as session:
            test_message_data = MessageData(message_id='12345678', message_name='test_message')
            session.add_all([test_message_data])
            await session.flush()
            await session.commit()
