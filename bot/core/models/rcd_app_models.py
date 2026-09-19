from core import (
    Base,
    bool_empty,
    int_empty,
    int_uniq,
    intpk,
    str_empty,
    str_uniq,
    strpk,
)
from sqlalchemy.orm import Mapped


class MemberIdModel(Base):
    """Базовая модель с полем member_id"""
    __abstract__ = True

    member_id: Mapped[intpk]


class AppMemberList(MemberIdModel):
    """Модель ID пользователей, кто подал заявки на РЧД"""
    pass


class AskMemberList(MemberIdModel):
    """Модель рекрутёров на РЧД"""
    pass


class DateInfo(Base):
    """Модель информации о дате РЧД"""
    date_name: Mapped[strpk]
    date: Mapped[str_uniq]


class NoticeList(Base):
    """Модель списка пользователей для оповещения об РЧД"""
    members_id: Mapped[strpk]
    action: Mapped[str]
    role: Mapped[str]


class RcdApplication(Base):
    """Модель списка названия сообщений и их ID"""
    message_name: Mapped[strpk]
    message_id: Mapped[int_uniq]


class ButtonInfo(Base):
    """Модель для информации о кнопке"""
    custom_id: Mapped[strpk]
    label: Mapped[str_empty]
    style: Mapped[int_empty]
    disabled: Mapped[bool_empty]
