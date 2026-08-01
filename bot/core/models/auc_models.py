from datetime import datetime

from core import Base, intpk
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AuctionDataInfo(Base):
    """Модель информации об аукционе"""
    id: Mapped[intpk]
    name_auc: Mapped[str]
    data: Mapped[str]
    start_auc_user_id: Mapped[int]
    start_bid: Mapped[int]
    lot_amount: Mapped[int]
    stop_time: Mapped[datetime] = mapped_column(DateTime)
    channel_id: Mapped[int]
    message_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active')
    bids: Mapped[list["UserBid"]] = relationship(
        'UserBid', back_populates='auction', cascade='all, delete-orphan'
    )


class UserBid(Base):
    """Модель текущих ставок по лотам аукциона"""
    id: Mapped[intpk]
    auction_id: Mapped[int] = mapped_column(ForeignKey('AuctionDataInfo.id'))
    lot_index: Mapped[int]
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    user_bid: Mapped[int]
    auction: Mapped["AuctionDataInfo"] = relationship(
        'AuctionDataInfo', back_populates='bids'
    )
