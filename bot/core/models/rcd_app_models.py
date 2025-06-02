from sqlalchemy.orm import Mapped

from core import Base, intpk, int_uniq, strpk, str_uniq


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
    """Модель списка поданных заявок"""
    message_name: Mapped[strpk]
    message_id: Mapped[int_uniq]
