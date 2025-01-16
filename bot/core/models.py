from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


uniq_id = Annotated[str, mapped_column(unique=True)]


class Auction(Base):

    user_id: Mapped[uniq_id]
    user_bid: Mapped[int | None]


class MessageData(Base):

    message_id: Mapped[uniq_id]
    message_name: Mapped[str | None] = mapped_column(unique=True)
