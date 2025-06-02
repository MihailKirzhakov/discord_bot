from sqlalchemy.ext.asyncio import AsyncSession

from .base_async_orm import AsyncORM
from core.models import (
    AppMemberList, AskMemberList, DateInfo,
    NoticeList, RcdApplication
)


class RcdApplicationORM(AsyncORM):

    def __init__(self):
        super().__init__()

    # --------------------------------------------------------------------------------
    # Вставка данных в БД
    async def insert_date_info(self, session: AsyncSession, date_name, date):
        """
        Метод для добавления или обновления данных
        о внесении информации о дате РЧД
        """
        # Проверяем, есть ли уже данные с таким date_name
        obj = await self.get_rcd_date_obj(session, date_name)
        if obj:
            # Если запись существует, обновляем её
            obj.date = date
        else:
            # Если записи нет, создаем новую
            new_data = DateInfo(date_name=date_name, date=date)
            session.add(new_data)
        await session.flush()

    async def insert_message_id(self, session: AsyncSession, message_name, message_id):
        """
        Метод для добавления или обновления данных
        об ID и названии сообщения
        """
        obj = await self.get_message_data_obj(session, message_name)
        if obj:
            # Если запись существует, обновляем её
            obj.message_id = message_id
        else:
            # Если записи нет, создаем новую
            new_data = RcdApplication(message_name=message_name, message_id=message_id)
            session.add(new_data)
        await session.flush()

    async def insert_members_to_notice_list(
        self, session: AsyncSession, members_id, action, role
    ):
        """Добавляет информацию о пользователях, для отправки уведомления"""
        obj = await self.get_filter_obj_first(
            session, NoticeList, action=action, role=role
        )
        if obj:
            # Если запись существует, обновляем members_id
            obj.members_id = members_id
        else:
            # Если записи нет, создаем новую
            new_notice = NoticeList(
                members_id=members_id, action=action, role=role
            )
            session.add(new_notice)
        await session.flush()

    async def insert_appmember_id(self, session: AsyncSession, member_id):
        data = AppMemberList(member_id=member_id)
        session.add(data)
        await session.flush()

    async def insert_askmember_id(self, session: AsyncSession, member_id):
        data = AskMemberList(member_id=member_id)
        session.add(data)
        await session.flush()

    # --------------------------------------------------------------------------------
    # Получение данных
    async def get_rcd_date_obj(self, session: AsyncSession, pk):
        """"""
        result = await self.get_obj_by_pk(session, DateInfo, pk)
        return result

    async def get_message_data_obj(self, session: AsyncSession, pk):
        """"""
        result = await self.get_obj_by_pk(session, RcdApplication, pk)
        return result

    async def get_appmember_obj(self, session: AsyncSession, pk):
        """"""
        result = await self.get_obj_by_pk(session, AppMemberList, pk)
        return result

    async def get_askmember_obj(self, session: AsyncSession, pk):
        """"""
        result = await self.get_obj_by_pk(session, AskMemberList, pk)
        return result

    async def get_all_appmember_ids(self, session: AsyncSession):
        """Возвращает список всех ID пользователей, подавших заявку"""
        result = await self.get_filter_obj_all(session, AppMemberList)
        return result

    async def get_all_askmember_ids(self, session: AsyncSession):
        """Возвращает список всех ID пользователей, кого спрашивали про РЧД"""
        result = await self.get_filter_obj_all(session, AskMemberList)
        return result

    async def get_notice_list_data(self, session, action: str):
        """Получает информацию о списках уведомлений"""
        obj_list = await self.get_filter_obj_all(session, NoticeList, action=action)
        notice_list_data = []
        for obj in obj_list:
            members_id_list = [
                int(member_id) for member_id in obj.members_id.split(',')
            ]
            notice_dict_data = {
                'role': obj.role,
                'action': obj.action,
                'members_id': members_id_list
            }
            notice_list_data.append(notice_dict_data)
        return notice_list_data

    # --------------------------------------------------------------------------------
    # Удаление данных
    async def delete_from_notice_list(
        self, session: AsyncSession, action, role
    ):
        """Метод для удаления данных из списка оповещения"""
        obj = await self.get_filter_obj_first(
            session, NoticeList, action=action, role=role
        )
        await self.delete_data(session, obj)

    async def clear_rcd_data(self, session: AsyncSession):
        for model in [
            AppMemberList, AskMemberList, DateInfo,
            NoticeList, RcdApplication
        ]:
            await self.clear_table(session, model)


rcd_app_orm = RcdApplicationORM()
