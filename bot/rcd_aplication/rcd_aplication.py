from datetime import datetime
import re

import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button, select
from loguru import logger

from core import async_session_factory
from .embeds import (
    start_rcd_embed, app_list_embed, ask_veteran_embed,
    rcd_list_embed, publish_rcd_embed, rcd_notification_embed,
    publish_rcd_second_embed, mailing_notification_embed
)
from core.orm import rcd_app_orm
from role_application.functions import has_required_role
from core import (
    VETERAN_ROLE, ANSWERS_IF_NO_ROLE, INDEX_CLASS_ROLE,
    SERGEANT_ROLE, LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE,
    RCD_APPLICATION_CHANNEL_ID, GUEST_ROLE
)


class StaticNames:
    """Костантные наименования для работы с РЧД списками"""
    ATACK: str = 'АТАКА'
    ATTENTION_MESSAGE: str = 'attention_message'
    DEFENCE: str = 'ЗАЩИТА'
    DATE: str = 'date'
    DATE_NAME: str = 'date_name'
    DATE_INFO: str = 'date_info'
    RCD_DATE: str = 'rcd_date'
    RCD_LIST_MESSAGE: str = 'rcd_list_message'
    RCD_APPCHANNEL_MESSAGE: str = 'rcd_appchannel_message'
    RCD_APPLICATION: str = 'rcd_application'
    MESSAGE_ID: str = 'message_id'
    MESSAGE_NAME: str = 'message_name'
    START_RCD_MESSAGE: str = 'start_rcd_message'
    RCD_LIST_CHANNEL: str = 'rcd_list_channel'


class RcdDate(Modal):
    """
    Модальное окно для ввода даты РЧД.
    """
    def __init__(self):
        super().__init__(title='Введи дату проведения РЧД', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи дату в формате ДД.ММ',
                placeholder='ДД.ММ',
                max_length=5
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=False, ephemeral=True)
        date_str: str = str(self.children[0].value)
        date_pattern = r'^([0-2][0-9]|3[0-1])[.,/](0[1-9]|1[0-2])$'
        date_match = re.match(date_pattern, date_str)
        rcd_app_channel: discord.TextChannel = interaction.guild.get_channel(RCD_APPLICATION_CHANNEL_ID)  # type: ignore

        if not date_match:
            return await interaction.respond(
                '_Неправильный формат даты. Пожалуйста, используйте формат ДД.ММ_',
                delete_after=5
            )

        try:
            async with async_session_factory() as session:
                day, month = map(int, date_match.groups())
                current_year = datetime.now().year
                rcd_date = datetime(
                    year=current_year,
                    month=month,
                    day=day)
                if rcd_date < datetime.now():
                    rcd_date = rcd_date.replace(year=current_year + 1)
                convert_rcd_date = discord.utils.format_dt(rcd_date, style="D")
                await rcd_app_orm.insert_date_info(
                    session, StaticNames.RCD_DATE, convert_rcd_date
                )
                await interaction.channel.send(embed=app_list_embed(convert_rcd_date), view=StartRCDButton())
                await rcd_app_channel.send(embed=start_rcd_embed(convert_rcd_date), view=RCDButton())
                await rcd_app_orm.insert_message_id(
                    session=session,
                    message_name=StaticNames.RCD_APPCHANNEL_MESSAGE,
                    message_id=rcd_app_channel.last_message_id
                )
                await rcd_app_orm.insert_message_id(
                    session=session,
                    message_name=StaticNames.START_RCD_MESSAGE,
                    message_id=interaction.guild.get_channel(interaction.channel_id).last_message_id
                )
                rcd_buttons_embed_list: list[discord.Embed] = [rcd_list_embed(convert_rcd_date, StaticNames.ATACK)]
                view: discord.ui.View = CreateRCDList()
                for index, role in INDEX_CLASS_ROLE.items():
                    view.add_item(AddMemberToListButton(
                        label=f'Редактировать "{role[:-2]}ов"',
                        custom_id=f'{index}КнопкаДобавления'
                    ))
                await interaction.channel.send(view=view, embeds=rcd_buttons_embed_list)
                await rcd_app_orm.insert_message_id(
                    session=session,
                    message_name=StaticNames.RCD_LIST_MESSAGE,
                    message_id=interaction.guild.get_channel(interaction.channel_id).last_message_id
                )
                await rcd_app_orm.insert_message_id(
                    session=session,
                    message_name=StaticNames.RCD_LIST_CHANNEL,
                    message_id=interaction.guild.get_channel(interaction.channel_id).id
                )
                await session.commit()
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При вводе даты РЧД возникла ошибка "{error}"')


class RaidChampionDominionApplication(Modal):
    """
    Модальное окно для ввода данных на заявку РЧД.
    """
    def __init__(self):
        super().__init__(title='Заявка на РЧД', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи количество чести',
                placeholder='Если не указать, то 0 по дефолту',
                required=False,
                max_length=3
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи классы, на которых хочешь идти на РЧД',
                placeholder='Если не заполнять, значит любой класс',
                required=False,
                max_length=80
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                honor: str = str(self.children[0].value)
                if not honor:
                    honor = '0'
                if not honor.isdigit():
                    return await interaction.respond(
                        '_Строка для ввода чести принимает только целые числа, повтори снова ⚠️_',
                        delete_after=2
                    )
                class_role: str = str(self.children[1].value)
                if not class_role:
                    class_role = 'Любой класс'
                guild = interaction.user.mutual_guilds[0]
                member: discord.Member = guild.get_member(interaction.user.id)
                field_index = 0 if discord.utils.get(member.roles, name=VETERAN_ROLE) else 1
                start_rcd_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.START_RCD_MESSAGE
                )
                rcd_list_channel_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_LIST_CHANNEL
                )
                rcd_list_channel: discord.TextChannel = guild.get_channel(rcd_list_channel_obj.message_id)
                start_rcd_message: discord.Message = (
                    await rcd_list_channel.fetch_message(start_rcd_message_obj.message_id)
                )
                during_embed: discord.Embed = start_rcd_message.embeds[0]
                field_value = during_embed.fields[field_index].value
                pattern = re.compile(rf'{member.mention}: (🟡|🔴)')
                match = pattern.search(field_value)
                if match:
                    new_value = field_value.replace(
                        match.group(0), f'{member.mention}: {class_role} ({honor})'
                    )
                else:
                    new_value = field_value + f'\n{member.mention}: {class_role} ({honor})'
                during_embed.fields[field_index].value = new_value
                await start_rcd_message.edit(embed=during_embed)
                await rcd_app_orm.insert_appmember_id(session, interaction.user.id)
                await session.commit()
                if interaction.channel.type.value == 1:
                    await interaction.message.delete()
                await interaction.respond(
                    '_Заявка принята ✅_',
                    delete_after=1
                )
                logger.info(f'Принята заявка на РЧД от "{interaction.user.display_name}"')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При отправке заявки на РЧД пользователем '
                f'"{interaction.user.display_name}" произошла ошибка "{error}"'
            )


class PrivateMessageView(View):
    """
    Кнопка для отказа или соглашения идти на РЧД.
    """
    def __init__(self):
        super().__init__(timeout=None)

    @button(
        label='Отправить заявку на РЧД', style=discord.ButtonStyle.green,
        emoji='📋', custom_id='ЗаявкаРЧДприват'
    )
    async def acces_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            async with async_session_factory() as session:
                all_member_ids = await rcd_app_orm.get_all_appmember_ids(session)
                if interaction.user.id in all_member_ids:
                    return await interaction.respond('_Ты уже подал заявку! ✅_', delete_after=1)
                await interaction.response.send_modal(RaidChampionDominionApplication())
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )

    @button(
        label='Меня не будет ❌',
        style=discord.ButtonStyle.red,
        custom_id='МеняНеБудет'
    )
    async def denied_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                guild = interaction.user.mutual_guilds[0]
                member = guild.get_member(interaction.user.id)
                field_index = 0 if discord.utils.get(member.roles, name=VETERAN_ROLE) else 1
                start_rcd_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.START_RCD_MESSAGE
                )
                rcd_list_channel_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_LIST_CHANNEL
                )
                rcd_list_channel: discord.TextChannel = guild.get_channel(rcd_list_channel_obj.message_id)
                start_rcd_message: discord.Message = (
                    await rcd_list_channel.fetch_message(start_rcd_message_obj.message_id)
                )
                during_embed: discord.Embed = start_rcd_message.embeds[0]
                field_value = during_embed.fields[field_index].value
                if member.mention in field_value:
                    new_value = field_value.replace(f'{member.mention}: 🟡', f'{member.mention}: 🔴')
                    during_embed.fields[field_index].value = new_value
                    await start_rcd_message.edit(embed=during_embed)
                await interaction.message.delete()
                await interaction.respond('_Принято ✅_', delete_after=1)
                logger.info(f'"{interaction.user.display_name}" отказался быть на РЧД')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При отправке отказа пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )


class RCDButton(View):
    """
    Кнопка для запуска модального окна для заявки РЧД.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
            label='Отправить заявку на РЧД', style=discord.ButtonStyle.green,
            emoji='📋', custom_id='ЗаявкаРЧД'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            async with async_session_factory() as session:
                all_member_ids = await rcd_app_orm.get_all_appmember_ids(session)
                if interaction.user.id in all_member_ids:
                    return await interaction.respond(
                        '_Ты уже подал заявку! ✅_',
                        delete_after=1,
                        ephemeral=True
                    )
                await interaction.response.send_modal(RaidChampionDominionApplication())
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )


class SelectMemberToRCD(View):
    """
    Меню для выбора пользователей в РЧД список.
    """

    def __init__(
        self,
        index: int,
    ) -> None:
        super().__init__(timeout=None)
        self.index: int = index

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=3,
        placeholder='Выбери игроков...'
    )
    async def select_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                if not has_required_role(interaction.user):
                    return await interaction.respond(
                        ANSWERS_IF_NO_ROLE,
                        delete_after=2
                    )
                rcd_list_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_LIST_MESSAGE
                )
                rcd_list_message: discord.Message = (
                    await interaction.channel.fetch_message(
                        rcd_list_message_obj.message_id
                    )
                )
                rcd_list_message_embeds = rcd_list_message.embeds
                f_embed: discord.Embed = rcd_list_message_embeds[0]
                s_embed: discord.Embed = (rcd_list_message_embeds[1] if len(rcd_list_message_embeds) > 1 else None)
                during_embed_list: list[discord.Embed] = [f_embed]
                check_set: set[str] = set()

                if s_embed:
                    during_embed_list.append(s_embed)

                for each_embed in during_embed_list:
                    for field in each_embed.fields:
                        for value in field.value.split(','):
                            check_set.add(value.strip())

                for user in select.values:
                    if user.mention in check_set:
                        return await interaction.respond(
                            '_Повторно добавлять одного и того же нельзя, проверь списки! ❌_',
                            delete_after=3
                        )
                await self.update_embed(
                    interaction,
                    ', '.join(user.mention for user in select.values),
                    ','.join(str(user.id) for user in select.values)
                )
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При выборе игроков возникла ошибка "{error}"'
            )

    @button(label='Очистить', style=discord.ButtonStyle.gray, custom_id='Очистить')
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(invisible=False, ephemeral=True)
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                delete_after=2
            )
        await self.update_embed(interaction, '', None)

    async def update_embed(
        self,
        interaction: discord.Interaction,
        value: str,
        members_id: str | None
    ) -> None:
        try:
            async with async_session_factory() as session:
                rcd_list_message_obj = await rcd_app_orm.get_message_data_obj(
                        session=session,
                        pk=StaticNames.RCD_LIST_MESSAGE
                    )
                rcd_list_message: discord.Message = (
                    await interaction.channel.fetch_message(rcd_list_message_obj.message_id)
                )
                tumbler_button: discord.ui.Button = rcd_list_message.components[0].children[1]
                is_red = tumbler_button.style == discord.ButtonStyle.red

                during_embeds = rcd_list_message.embeds
                during_embed = during_embeds[1] if is_red else during_embeds[0]
                during_embed.fields[self.index].value = value
                role = INDEX_CLASS_ROLE.get(self.index)
                action = StaticNames.DEFENCE if is_red else StaticNames.ATACK

                if not members_id:
                    try:
                        await rcd_app_orm.delete_from_notice_list(session, action=action, role=role)
                    except Exception:
                        pass
                else:
                    await rcd_app_orm.insert_members_to_notice_list(
                        session, members_id=members_id, action=action, role=role
                    )

                await rcd_list_message.edit(embeds=during_embeds)
                await session.commit()
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При обработке игроков возникла ошибка "{error}"')


class AddMemberToListButton(discord.ui.Button):
    """Кнопка для добавления игроков к классам"""

    def __init__(
        self,
        custom_id: str,
        label: str,
        style=discord.ButtonStyle.green,
    ):
        super().__init__(
            label=label,
            style=style,
            custom_id=custom_id
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE, delete_after=2
                )
            check_label: str = self.label.split()[1]
            for index, role in INDEX_CLASS_ROLE.items():
                if role[:-2] in check_label:
                    await interaction.respond(view=SelectMemberToRCD(index=index))
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При нажатии на кнопку добавления игроков возникла ошибка "{error}"')


class CreateRCDList(View):
    """
    Кнопки для создания РЧД списка, и отправки готового списка.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
        label='Создать второй список', style=discord.ButtonStyle.green,
        custom_id='СоздатьСписок'
    )
    async def create_list_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                if not has_required_role(interaction.user):
                    return await interaction.respond(
                        ANSWERS_IF_NO_ROLE,
                        delete_after=2
                    )
                date_data_obj = await rcd_app_orm.get_rcd_date_obj(
                    session=session,
                    pk=StaticNames.RCD_DATE
                )
                button.label = '⬆️ Списки созданы выше ⬆️'
                button.style = discord.ButtonStyle.gray
                button.disabled = True
                tumbler_button: discord.ui.Button = self.children[1]
                tumbler_button.label = 'СЕЙЧАС работа с 1️⃣ списком'
                tumbler_button.style = discord.ButtonStyle.blurple
                tumbler_button.disabled = False
                during_embeds = interaction.message.embeds
                during_embeds.append(rcd_list_embed(date_data_obj.date, StaticNames.DEFENCE))
                await interaction.message.edit(embeds=during_embeds, view=self)
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При создании списка возникла ошибка "{error}"')

    @button(
        label='Переключение между списками',
        style=discord.ButtonStyle.gray,
        custom_id='ПереключениеСписков',
        disabled=True
    )
    async def tumbler_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    ephemeral=True,
                    delete_after=2
                )
            if button.style == discord.ButtonStyle.blurple:
                button.label = 'СЕЙЧАС работа с 2️⃣ списком'
                button.style = discord.ButtonStyle.red
            else:
                button.label = 'СЕЙЧАС работа с 1️⃣ списком'
                button.style = discord.ButtonStyle.blurple
            await interaction.response.edit_message(view=self)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При переключении списков возникла ошибка "{error}"')

    @button(
        label='Опубликовать 📨',
        style=discord.ButtonStyle.blurple,
        custom_id='Опубликовать',
    )
    async def publish_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                if not has_required_role(interaction.user):
                    return await interaction.respond(
                        ANSWERS_IF_NO_ROLE,
                        delete_after=2
                    )
                rcd_appchannel_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_APPCHANNEL_MESSAGE
                )
                rcd_app_channel: discord.TextChannel = (interaction.guild.get_channel(RCD_APPLICATION_CHANNEL_ID))
                rcd_app_message: discord.Message = await rcd_app_channel.fetch_message(
                    rcd_appchannel_message_obj.message_id
                )
                rcd_app_message_embeds: list[discord.Embed] = rcd_app_message.embeds
                during_embed_list: list[discord.Embed] = interaction.message.embeds
                f_embed: discord.Embed = during_embed_list[0]
                if len(during_embed_list) > 1:
                    s_embed: discord.Embed = during_embed_list[1]
                date_data_obj = await rcd_app_orm.get_rcd_date_obj(
                    session=session,
                    pk=StaticNames.RCD_DATE
                )
                atack_embed: discord.Embed = publish_rcd_embed(date=date_data_obj.date)
                defense_embed: discord.Embed = publish_rcd_second_embed(date=date_data_obj.date)
                if self.children[1].style == discord.ButtonStyle.red:
                    if 'Заявки на РЧД' in rcd_app_message_embeds[0].title:
                        return await interaction.respond('_Сначала нужно отправить список "АТАКА"! ❌_', delete_after=3)
                    for field in [field for field in s_embed.fields if field.value != '']:
                        name, value, inline = field.name, field.value, field.inline
                        defense_embed.add_field(name=name, value=value, inline=inline)

                    if len(rcd_app_message_embeds) > 1:
                        rcd_app_message_embeds[1] = defense_embed
                    else:
                        rcd_app_message_embeds.append(defense_embed)
                    await rcd_app_message.edit(embeds=rcd_app_message_embeds)
                    logger.info(
                        f'Список "ЗАЩИТА" изменён в {rcd_app_channel.name} '
                        f'пользователем {interaction.user.display_name}'
                    )
                else:
                    for field in [field for field in f_embed.fields if field.value != '']:
                        name, value, inline = field.name, field.value, field.inline
                        atack_embed.add_field(name=name, value=value, inline=inline)
                    rcd_app_message_embeds[0] = atack_embed
                    await rcd_app_message.edit(embeds=rcd_app_message_embeds, view=None)
                    logger.info(
                        f'Список "АТАКА" изменён в {rcd_app_channel.name} '
                        f'пользователем {interaction.user.display_name}'
                    )
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(f'При публикации списка возникла ошибка "{error}"')

    @button(
        label='Оповестить об РЧД из списка 📣', style=discord.ButtonStyle.blurple,
        custom_id='ОповеститьОСписке'
    )
    async def notification_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)

            async def send_notification(member: discord.Member, rcd_role: str, date):
                try:
                    await member.send(
                        embed=rcd_notification_embed(
                            interaction_user=interaction.user.display_name,
                            date=date,
                            jump_url=jump_url,
                            rcd_role=rcd_role
                        ),
                        delete_after=72000
                    )
                except discord.Forbidden:
                    logger.warning(f'Пользователю "{member.display_name}" запрещено отправлять сообщения')

            async def get_members_by_role(session, notice_data_list, action_name, date):

                if not notice_data_list:
                    return await interaction.channel.send(  # type: ignore
                        '_Дядь, в списке пусто 🤔\n'
                        f'Или всем людям из списка {action_name} уже были отправлены оповещения 👌_',
                        delete_after=3,
                        ephemeral=True
                    )

                for dict_item in notice_data_list:
                    action = dict_item.get('action')
                    role = dict_item.get('role')
                    members_id = dict_item.get('members_id')

                    await rcd_app_orm.delete_from_notice_list(session, action=action, role=role)

                    for member_id in members_id:
                        member = await interaction.guild.fetch_member(member_id)
                        await send_notification(member, role, date)
                        logger.info(f'"{member.display_name}" оповещён об РЧД')

            async with async_session_factory() as session:
                sergaunt_role: discord.Role = discord.utils.get(interaction.guild.roles, name=SERGEANT_ROLE)
                date_data_obj = await rcd_app_orm.get_rcd_date_obj(
                    session=session,
                    pk=StaticNames.RCD_DATE
                )
                rcd_appchannel_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_APPCHANNEL_MESSAGE
                )
                rcd_app_channel: discord.TextChannel = (interaction.guild.get_channel(RCD_APPLICATION_CHANNEL_ID))
                rcd_app_message: discord.Message = await rcd_app_channel.fetch_message(
                    rcd_appchannel_message_obj.message_id
                )
                attention_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.ATTENTION_MESSAGE
                )
                permissions_for_sergaunt: discord.permissions = (
                    rcd_app_channel.permissions_for(sergaunt_role).read_messages
                )
                jump_url = (
                    rcd_app_channel.jump_url if 'Список РЧД'
                    in rcd_app_message.embeds[0].title
                    and permissions_for_sergaunt == True else None
                )

                if self.children[1].style == discord.ButtonStyle.red:
                    if await rcd_app_orm.get_notice_list_data(session, StaticNames.ATACK):
                        return await interaction.respond(
                            '❌\n_Сперва отправь оповещения из списка АТАКИ_',
                            delete_after=3
                        )
                    await get_members_by_role(
                        session,
                        await rcd_app_orm.get_notice_list_data(session, StaticNames.DEFENCE),
                        StaticNames.DEFENCE, date_data_obj.date
                    )
                else:
                    await get_members_by_role(
                        session,
                        await rcd_app_orm.get_notice_list_data(session, StaticNames.ATACK),
                        StaticNames.ATACK, date_data_obj.date
                    )

                await session.flush()
                notice_list_atack = await rcd_app_orm.get_notice_list_data(session, StaticNames.ATACK)
                notice_list_defence = await rcd_app_orm.get_notice_list_data(session, StaticNames.DEFENCE)
                if not notice_list_atack and not notice_list_defence:
                    button.label = 'Все оповещения были отправлены ✅'
                    button.style = discord.ButtonStyle.gray
                    button.disabled = True
                    await interaction.message.edit(view=self)
                if not attention_message_obj:
                    await rcd_app_channel.send(
                        embed=mailing_notification_embed(date=date_data_obj.date)
                    )
                    await rcd_app_orm.insert_message_id(
                        session, StaticNames.ATTENTION_MESSAGE,
                        rcd_app_channel.last_message_id
                    )
                await session.commit()
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                'При отправке уведомлений пользователям из списка '
                f'РЧД возникла ошибка: "{error}"!'
            )

    @button(
        label='Завершить работу со списком РЧД', style=discord.ButtonStyle.red,
        custom_id='ЗавершитьРЧДСписок'
    )
    async def stop_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                if not has_required_role(interaction.user):
                    return await interaction.respond(
                        ANSWERS_IF_NO_ROLE,
                        delete_after=2
                    )
                await interaction.message.delete()
                rcd_appchannel_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.RCD_APPCHANNEL_MESSAGE
                )
                attention_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.ATTENTION_MESSAGE
                )
                rcd_app_channel: discord.TextChannel = interaction.guild.get_channel(RCD_APPLICATION_CHANNEL_ID)
                rcd_app_message: discord.Message = await rcd_app_channel.fetch_message(
                    rcd_appchannel_message_obj.message_id
                )
                if attention_message_obj:
                    attention_message: discord.Message = await rcd_app_channel.fetch_message(
                        attention_message_obj.message_id
                    )
                    await attention_message.delete()
                if 'Заявки на РЧД' in rcd_app_message.embeds[0].title:
                    await rcd_app_message.delete()
                start_rcd_message_obj = await rcd_app_orm.get_message_data_obj(
                    session=session,
                    pk=StaticNames.START_RCD_MESSAGE
                )
                start_rcd_message: discord.Message = await interaction.channel.fetch_message(
                    start_rcd_message_obj.message_id
                )
                await start_rcd_message.edit(view=None)
                await rcd_app_orm.clear_rcd_data(session)
                await session.commit()
                await interaction.respond('✅', delete_after=1)
                logger.info(f'Пользователь "{interaction.user.display_name}" завершил работу с РЧД списками')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При завершении работы с РЧД возникла ошибка "{error}"')


class StartRCDButton(View):
    """
    Кнопка для запуска РЧД заявок.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=24,
        placeholder='Выбери игроков, которых спросить об РЧД',
        disabled=False,
        custom_id='ВыберитеИгроков'
    )
    async def ask_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            async with async_session_factory() as session:
                if not has_required_role(interaction.user):
                    return await interaction.respond(ANSWERS_IF_NO_ROLE, delete_after=2)
                guest_role = discord.utils.get(
                    interaction.guild.roles, name=GUEST_ROLE
                )
                during_embed: discord.Embed = interaction.message.embeds[0]
                ask_users: list[discord.Member] = [user for user in select.values]
                all_askmember_ids: list = await rcd_app_orm.get_all_askmember_ids(session)
                all_appmember_ids: list = await rcd_app_orm.get_all_appmember_ids(session)
                all_members = all_askmember_ids + all_appmember_ids
                date_obj = await rcd_app_orm.get_rcd_date_obj(session=session, pk=StaticNames.RCD_DATE)
                for user in ask_users:
                    if user.id in all_members or guest_role in user.roles:
                        continue
                    field_index = 0 if discord.utils.get(user.roles, name=VETERAN_ROLE) else 1
                    during_embed.fields[field_index].value += (f'\n{user.mention}: 🟡')
                    try:
                        await user.send(
                            embed=ask_veteran_embed(
                                member=interaction.user,
                                date=date_obj.date
                            ),
                            view=PrivateMessageView(),
                            delete_after=86400
                        )
                        await rcd_app_orm.insert_askmember_id(session, user.id)
                        logger.info(f'Пользователю "{user.display_name}" был отправлен вопрос об РЧД')
                    except discord.Forbidden:
                        logger.warning(f'Пользователю "{user.display_name}" запрещено отправлять сообщения')
                await session.commit()
                await interaction.message.edit(embed=during_embed)
                await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При опросе игроков возникла ошибка "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rcd_application(ctx: discord.ApplicationContext) -> None:
    """
    Команда для запуска кнопки старта РЧД заявок.
    """
    try:
        await ctx.response.send_modal(RcdDate())
        logger.info(
            f'Команда "/rcd_application" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/rcd_application"! '
            f'"{error}"'
        )


@rcd_application.error
async def rcd_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обрабатывать ошибки, возникающие
    при выполнении команды заявок на РЧД.
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер, Казначей или Офицер"!',
            ephemeral=True,
            delete_after=10
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=10
        )
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(rcd_application)
