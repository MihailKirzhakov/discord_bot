from datetime import datetime
import re

import discord
from discord.ui import Modal, InputText, View, button, select
from loguru import logger

from .embeds import (
    start_rcd_embed, rcd_list_embed, ask_veteran_embed,
    final_rcd_list_embed
)
from variables import VETERAN_ROLE


member_list: list = []
channel_last_message: list[discord.Message] = []
rcd_channel: list[discord.TextChannel] = []
rcd_date_list: list[str] = []
embed: list[discord.Embed] = []
last_message_to_finish: dict[int: discord.Message] = {}


class RcdDate(Modal):
    """
    Модальное окно для ввода даты РЧД.

    Attributes:
    ----------
        date: str
            Дата проведения РЧД.
    """
    def __init__(self):
        super().__init__(title='Введи дату проведения РЧД', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи дату в формате ДД.ММ',
                placeholder='ДД.ММ',
                max_length=5
            )
        )

    async def callback(self, interaction: discord.Interaction):
        date_str: str = str(self.children[0].value)
        date_pattern = r'^([0-2][0-9]|3[0-1])[.,/](0[1-9]|1[0-2])$'
        date_match = re.match(date_pattern, date_str)

        if not date_match:
            return await interaction.respond(
                'Неправильный формат даты. Пожалуйста, используйте формат ДД.ММ',
                ephemeral=True,
                delete_after=5
            )

        try:
            day, month = map(int, date_match.groups())
            current_year = datetime.now().year
            rcd_date = datetime(
                year=current_year,
                month=month,
                day=day)
            if rcd_date < datetime.now():
                rcd_date = rcd_date.replace(year=current_year + 1)
            convert_rcd_date = discord.utils.format_dt(rcd_date, style="D")
            rcd_date_list.append(convert_rcd_date)
            embed.append(final_rcd_list_embed(convert_rcd_date))
            await interaction.respond(embed=rcd_list_embed())
            await interaction.respond(view=StartRCDButton())
            await interaction.respond(
                '_РЧД заявки запущены!_',
                ephemeral=True,
                delete_after=2
            )
        except Exception as error:
            logger.error(
                f'При вводе даты РЧД возникла ошибка {error}'
            )


class RaidChampionDominionApplication(Modal):
    """
    Модальное окно для ввода данных на заявку РЧД.

    Attributes:
    ----------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    def __init__(
            self,
            embed: discord.Embed
    ):
        super().__init__(title='Заявка на РЧД', timeout=None)
        self.embed = embed

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи количество чести',
                placeholder='0-500',
                max_length=3
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи классы, на которых хочешь идти на РЧД',
                placeholder='Если не заполнять, значит любой класс',
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.display_name in member_list:
                return await interaction.respond(
                    '_Ты уже подал заявку! ✅_',
                    ephemeral=True,
                    delete_after=5
                )
            honor: str = str(self.children[0].value)
            class_role: str = str(self.children[1].value)
            if not class_role:
                class_role = 'Любой класс'
            field_index = 0 if discord.utils.get(interaction.user.roles, name=VETERAN_ROLE) else 1
            self.embed.fields[field_index].value += (
                f'{interaction.user.mention}: {class_role} ({honor})\n'
            )
            await channel_last_message[0].edit(embed=self.embed)
            member_list.append(f'{interaction.user.display_name}')
            await interaction.respond(
                '_Заявка принята ✅_',
                ephemeral=True,
                delete_after=5
            )
            logger.info(
                f'Принята заявка на РЧД от {interaction.user.display_name}')
        except Exception as error:
            logger.error(
                f'При отправке заявки на РЧД пользователем '
                f'{interaction.user.display_name} произошла ошибка{error}'
            )


class RCDButton(View):
    """
    Кнопка для запуска модального окна для заявки РЧД.

    Attributes:
    ----------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    def __init__(
            self,
            embed: discord.Embed,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.embed = embed

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
            await interaction.response.send_modal(
                RaidChampionDominionApplication(
                    embed=self.embed
                ))
        except Exception as error:
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем {interaction.user.display_name} '
                f'возникла ошибка {error}'
            )


class SelectMemberToRCD(View):
    """
    Меню для выбора пользователей в РЧД список.

    Attributes:
    ----------
        index: int
            Индекс поля втстраимого сообщения Embed.

        embed: discord.Embed
            Встраиваемое сообщение.
    """
    def __init__(self, index: int) -> None:
        super().__init__(timeout=None)
        self.index = index

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=4,
        placeholder='Выбери игроков...'
    )
    async def select_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction
    ):
        await self.update_embed(
            interaction,', '.join(user.mention for user in select.values)
        )

    @button(label='Пусто', style=discord.ButtonStyle.gray, custom_id='Пусто')
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_embed(interaction, 'Пусто')

    async def update_embed(
        self,
        interaction: discord.Interaction,
        value: str
    ) -> None:
        embed[0].fields[self.index].value = value
        await last_message_to_finish.get(3).edit(embed=embed[0])
        await interaction.message.delete()
        await interaction.respond(
            f'Добавлено {"✅" if value else "⭕"}',
            ephemeral=True,
            delete_after=1
        )


class CreateRCDList(View):
    """
    Кнопки для создания РЧД списка, и отправки готового списка.

    Attributes:
    ----------
        channel: discord.TextChannel
            Канал в котором будет создан список РЧД.
    """

    index_class_role = {
        0: 'Воины:',
        1: 'Паладины:',
        2: 'Инженеры:',
        3: 'Жрецы:',
        4: 'Шаманы:',
        5: 'Мистики:',
        6: 'Лучники:',
        7: 'Маги:',
        8: 'Некроманты:',
        9: 'Барды',
        10: 'Демоны'
    }

    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
        label='Создать список', style=discord.ButtonStyle.blurple,
        custom_id='СоздатьСписок'
    )
    async def create_list_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        last_message_to_finish[2] = interaction.message
        obj_1: discord.ui.Button = self.children[0]
        obj_2: discord.ui.Button = self.children[1]
        obj_14: discord.ui.Select = self.children[13]

        obj_1.label = '⬇️ Список создан ниже ⬇️'
        obj_1.style = discord.ButtonStyle.gray
        obj_1.disabled = True

        obj_2.style = discord.ButtonStyle.green
        obj_2.disabled = False

        obj_14.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(embed=embed[0])

    @button(
        label='Добавить "Воинов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьВоинов', disabled=True
    )
    async def add_warior_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        last_message_to_finish[3] = interaction.channel.last_message
        await self.update_view_rcd_list(interaction, 0)

    @button(
        label='Добавить "Паладинов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьПаладинов', disabled=True
    )
    async def add_paladin_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 1)

    @button(
        label='Добавить "Инженеров"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьИнженеров', disabled=True
    )
    async def add_ingeneer_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 2)

    @button(
        label='Добавить "Жрецов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьЖрецов', disabled=True
    )
    async def add_priest_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 3)

    @button(
        label='Добавить "Друидов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьДруидов', disabled=True
    )
    async def add_druid_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 4)

    @button(
        label='Добавить "Мистиков"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьМистиков', disabled=True
    )
    async def add_mistic_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 5)

    @button(
        label='Добавить "Лучников"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьЛучников', disabled=True
    )
    async def add_stalker_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 6)

    @button(
        label='Добавить "Магов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьМагов', disabled=True
    )
    async def add_mage_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 7)

    @button(
        label='Добавить "Некромантов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьНекромантов', disabled=True
    )
    async def add_necromant_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 8)

    @button(
        label='Добавить "Бардов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьБардов', disabled=True
    )
    async def add_bard_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 9)

    @button(
        label='Добавить "Демонологов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьДемонологов', disabled=True
    )
    async def add_deamon_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed[0].fields) < 11:
            embed[0].add_field(
                name='Демоны:',
                value='',
                inline=False
            )
        await interaction.respond(view=SelectMemberToRCD(index=10))

    @button(
        label='Завершить работу со списком РЧД', style=discord.ButtonStyle.red,
        custom_id='ЗавершитьРЧДСписок', disabled=True
    )
    async def stop_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.channel.delete_messages([message for message in last_message_to_finish.values()])
        await interaction.respond(
            '_Работа со списком РЧД завершена!_',
            ephemeral=True,
            delete_after=2

        )

    @select(
        select_type=discord.ComponentType.channel_select,
        min_values=1,
        max_values=1,
        placeholder='Выбери канал, куда отправить список РЧД',
        channel_types=[discord.ChannelType.text], disabled=True
    )
    async def select_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        channel: discord.TextChannel = select.values[0]
        if 'Список РЧД' in channel.last_message.embeds[0].title:
            await channel.last_message.edit(embed=embed[0])
        else:
            await channel.last_message.delete()
            await channel.send(embed=embed[0])
        button: discord.ui.Button = self.children[12]
        button.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(
            f'_Список РЧД опубликован в канале {channel.mention}_',
            ephemeral=True,
            delete_after=2
        )

    async def update_view_rcd_list(
            self,
            interaction: discord.Interaction,
            index: int,
    ) -> None:
        if len(embed[0].fields) < index + 1:
            embed[0].add_field(
                name=self.index_class_role.get(index),
                value='',
                inline=False
            )
        button: discord.ui.Button = self.children[index + 2]
        button.style = discord.ButtonStyle.green
        button.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=index))


class StartRCDButton(View):
    """
    Кнопка для запуска РЧД заявок.

    Attributes:
    ----------
        channel: discord.TextChannel
            Канал в котором будет создан список РЧД.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @select(
        select_type=discord.ComponentType.channel_select,
        min_values=1,
        max_values=1,
        placeholder='Выбери канал, в котором будет кнопка для заявок РЧД',
        channel_types=[discord.ChannelType.text]
    )
    async def select_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        last_message_to_finish[1] = interaction.message
        channel: discord.TextChannel = select.values[0]
        try:
            await channel.send(
                embed=start_rcd_embed(rcd_date_list[0]),
                view=RCDButton(
                    embed=rcd_list_embed()
                )
            )
            channel_last_message.append(interaction.channel.last_message)
            await interaction.respond(view=CreateRCDList())
            rcd_channel.append(channel)
            self.children[0].disabled = True
            self.children[1].disabled = False
            self.remove_item(self.children[0])
            await interaction.message.edit(view=self)
            await interaction.respond(
                f'_Заявки запущены в канале {channel.mention} 👌_',
                ephemeral=True,
                delete_after=3
            )
            logger.info(
                f'Пользователь {interaction.user.display_name} запустил '
                f'заявки на РЧД'
            )
        except Exception as error:
            logger.error(f'При нажатии на кнопку StartRCDButton возникла ошибка {error}')

    @button(
        label='Спросить всех "Ветеранов"', style=discord.ButtonStyle.blurple,
        emoji='❓', custom_id='СпроситьВетеранов', disabled=True
    )
    async def ask_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        url = rcd_channel[0].jump_url
        role = discord.utils.get(interaction.guild.roles, name=VETERAN_ROLE)
        veteran_members = [member for member in interaction.guild.members if role in member.roles]
        for veteran_member in veteran_members:
            await veteran_member.send(
                embed=ask_veteran_embed(
                    member=interaction.user, url=url
                ),
                delete_after=10800
            )
        await interaction.message.delete()
        await interaction.respond(
            'Сообщения были отправлены всем ветеранам',
            ephemeral=True,
            delete_after=3
        )
