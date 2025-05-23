from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


intpk = Annotated[int, mapped_column(primary_key=True, unique=True)]
strpk = Annotated[str, mapped_column(primary_key=True, unique=True)]
int_uniq = Annotated[int, mapped_column(unique=True)]
str_uniq = Annotated[str, mapped_column(unique=True)]


# --------------------------------------------------------------------------------
# Аукцион
class UserBid(Base):

    lot_id: Mapped[intpk] = mapped_column(ForeignKey('auctiondatainfo.name_auc'))
    user_id: Mapped[int_uniq | None]
    user_bid: Mapped[int]
    auction: Mapped["AuctionDataInfo"] = relationship('AuctionDataInfo', back_populates='bids')


class AuctionDataInfo(Base):

    name_auc: Mapped[strpk]
    data: Mapped[str]
    start_auc_user_id: Mapped[int_uniq]
    start_bid: Mapped[int]
    lot_amount: Mapped[int]
    bids: Mapped[list["UserBid"]] = relationship('UserBid', back_populates='auction')


# --------------------------------------------------------------------------------
# Заявки на доступ
class RoleApplicationData(Base):

    nickname: Mapped[strpk]
    user_id: Mapped[int_uniq]
    acc_btn_cstm_id: Mapped[str_uniq]
    den_btn_cstm_id: Mapped[str_uniq]


# --------------------------------------------------------------------------------
# Напоминалка
class MessageData(Base):

    message_id: Mapped[intpk]
    message_name: Mapped[str_uniq]
