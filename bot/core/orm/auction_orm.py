from datetime import datetime
from typing import cast

from core.models import AuctionDataInfo, UserBid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_async_orm import AsyncORM


class AuctionORM(AsyncORM):

    def __init__(self):
        super().__init__()

    # --------------------------------------------------------------------------------
    # Вставка данных в БД
    async def insert_auc_info_data(
        self,
        session: AsyncSession,
        name_auc: str,
        data: str,
        start_auc_user_id: int,
        start_bid: int,
        lot_amount: int,
        stop_time: datetime,
        channel_id: int,
        message_id: int | None = None,
        status: str = 'active'
    ):
        """Метод для добавления информации об аукционе в БД"""
        await self.insert_data(
            session,
            AuctionDataInfo,
            name_auc=name_auc,
            data=data,
            start_auc_user_id=start_auc_user_id,
            start_bid=start_bid,
            lot_amount=lot_amount,
            stop_time=stop_time,
            channel_id=channel_id,
            message_id=message_id,
            status=status
        )

    async def insert_bid_data(
        self,
        session: AsyncSession,
        auction_id: int,
        lot_index: int,
        user_bid: int,
        user_id: int | None = None
    ):
        """Метод для добавления ставки по лоту в БД"""
        await self.insert_data(
            session,
            UserBid,
            auction_id=auction_id,
            lot_index=lot_index,
            user_id=user_id,
            user_bid=user_bid
        )

    # --------------------------------------------------------------------------------
    # Получение данных
    async def get_bid_obj(self, session: AsyncSession, pk: int):
        """Метод для получения ставки по первичному ключу"""
        return await self.get_obj_by_pk(session, UserBid, pk)

    async def get_auc_info_obj(self, session: AsyncSession, pk: int):
        """Метод для получения аукциона по первичному ключу"""
        return await self.get_obj_by_pk(session, AuctionDataInfo, pk)

    async def get_auc_info_by_name(self, session: AsyncSession, name_auc: str):
        """Метод для получения аукциона по имени"""
        return await self.get_filter_obj_first(
            session,
            AuctionDataInfo,
            name_auc=name_auc,
            status='active'
        )

    async def get_bids_by_auction(self, session: AsyncSession, auction_id: int):
        """Получение всех ставок конкретного аукциона"""
        return await self.get_filter_obj_all(
            session,
            UserBid,
            auction_id=auction_id
        )

    async def get_active_auctions(self, session: AsyncSession):
        """Получение всех активных аукционов"""
        return await self.get_filter_obj_all(
            session,
            AuctionDataInfo,
            status='active'
        )

    async def get_bids_by_auction_sorted(
        self, session: AsyncSession, auction_id: int
    ):
        """Получение всех ставок конкретного аукциона с сортировкой по индексу лота"""
        result = await session.execute(
            select(UserBid).where(UserBid.auction_id == auction_id).order_by(UserBid.lot_index)
        )
        return result.scalars().all()

    async def get_lot_bid(
        self,
        session: AsyncSession,
        auction_id: int,
        lot_index: int
    ):
        """Получение ставки конкретного лота"""
        return await self.get_filter_obj_first(
            session,
            UserBid,
            auction_id=auction_id,
            lot_index=lot_index
        )

    # --------------------------------------------------------------------------------
    # Обновление данных
    async def upsert_lot_bid(
        self,
        session: AsyncSession,
        auction_id: int,
        lot_index: int,
        user_id: int,
        user_bid: int
    ):
        """
        Обновляет ставку лота, если запись существует,
        иначе создаёт новую.
        """
        bid_obj = await self.get_lot_bid(session, auction_id, lot_index)
        if bid_obj:
            bid_obj.user_id = user_id
            bid_obj.user_bid = user_bid
            await session.flush()
            return bid_obj

        await self.insert_bid_data(
            session=session,
            auction_id=auction_id,
            lot_index=lot_index,
            user_bid=user_bid,
            user_id=user_id
        )
        return await self.get_lot_bid(session, auction_id, lot_index)

    async def set_auction_message_id(
        self, session: AsyncSession, auction_id: int, message_id: int
    ):
        """Обновляет message_id у аукциона"""
        auction_obj = await self.get_auc_info_obj(session, auction_id)
        self.obj_validation(auction_obj)
        auction_obj = cast(AuctionDataInfo, auction_obj)
        auction_obj.message_id = message_id
        await session.flush()

    async def set_auction_status(
        self, session: AsyncSession, auction_id: int, status: str
    ):
        """Изменяет статус аукциона"""
        auction_obj = await self.get_auc_info_obj(session, auction_id)
        self.obj_validation(auction_obj)
        auction_obj = cast(AuctionDataInfo, auction_obj)
        auction_obj.status = status
        await session.flush()

    # --------------------------------------------------------------------------------
    # Удаление данных
    async def delete_bid_data(self, session: AsyncSession, bid_obj: UserBid):
        """Удаление записи ставки из БД"""
        await self.delete_data(session, bid_obj)

    async def delete_bids_by_auction(self, session: AsyncSession, auction_id: int):
        """Удаление всех ставок конкретного аукциона"""
        bids = await self.get_bids_by_auction(session, auction_id)
        for bid in bids:
            await self.delete_data(session, bid)

    async def delete_auction_data(self, session: AsyncSession, auction_id: int):
        """Удаление информации о конкретном аукционе"""
        auction_obj = await self.get_auc_info_obj(session, auction_id)
        self.obj_validation(auction_obj)
        await self.delete_data(session, auction_obj)

    async def clear_userbid_table(self, session: AsyncSession):
        """Очистка таблицы ставок"""
        await self.clear_table(session, UserBid)


auc_orm = AuctionORM()
