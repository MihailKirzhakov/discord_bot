from datetime import datetime
import re

import discord
from discord.ui import Modal, InputText, View, button, select
from loguru import logger

from .embeds import (
    start_rcd_embed, rcd_list_embed, ask_veteran_embed,
    final_rcd_list_embed, publish_rcd_embed
)
from role_application.functions import has_required_role
from variables import VETERAN_ROLE, ANSWERS_IF_NO_ROLE


member_list: list = []
rcd_date_list: dict[str, str] = {}
embed: dict[str, discord.Embed] = {}
last_message_to_finish: dict[str, discord.Message] = {}
rcd_application_channel: dict[str, discord.TextChannel] = {}
publish_embed: dict[str, discord.Embed] = {}


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
            rcd_date_list['convert_rcd_date'] = convert_rcd_date
            embed['final_rcd_list_embed'] = final_rcd_list_embed(convert_rcd_date)
            embed['rcd_list_embed'] = rcd_list_embed(convert_rcd_date)
            await interaction.respond(embed=rcd_list_embed(convert_rcd_date), view=StartRCDButton())
            # await interaction.respond(
            #     '_РЧД заявки запущены!_',
            #     ephemeral=True,
            #     delete_after=1
            # )
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
    def __init__(self):
        super().__init__(title='Заявка на РЧД', timeout=None)

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
            if interaction.user.id in member_list:
                return await interaction.respond(
                    '_Ты уже подал заявку! ✅_',
                    ephemeral=True,
                    delete_after=1
                )
            honor: str = str(self.children[0].value)
            class_role: str = str(self.children[1].value)
            if not class_role:
                class_role = 'Любой класс'
            guild = interaction.user.mutual_guilds[0]
            member = guild.get_member(interaction.user.id)
            field_index = 0 if discord.utils.get(member.roles, name=VETERAN_ROLE) else 1
            embed.get('rcd_list_embed').fields[field_index].value += (
                f'{interaction.user.mention}: {class_role} ({honor})\n'
            )
            await last_message_to_finish.get('start_RCD_button_message').edit(embed=embed.get('rcd_list_embed'))
            member_list.append(interaction.user.id)
            if interaction.channel.type.value == 1:
                await interaction.message.delete()
            await interaction.respond(
                '_Заявка принята ✅_',
                ephemeral=True,
                delete_after=1
            )
            logger.info(
                f'Принята заявка на РЧД от {interaction.user.display_name}')
        except Exception as error:
            logger.error(
                f'При отправке заявки на РЧД пользователем '
                f'{interaction.user.display_name} произошла ошибка {error}'
            )


class PrivateMessageView(View):
    """
    Кнопка для отказа идти на РЧД.
    """
    def __init__(self):
        super().__init__(timeout=None)

    @button(
            label='Отправить заявку на РЧД', style=discord.ButtonStyle.green,
            emoji='📋', custom_id='ЗаявкаРЧД'
    )
    async def acces_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.send_modal(RaidChampionDominionApplication())
        except Exception as error:
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем {interaction.user.display_name} '
                f'возникла ошибка {error}'
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
            await interaction.message.delete()
            await interaction.respond(
                '_Принято ✅_',
                ephemeral=True,
                delete_after=1
            )
        except Exception as error:
            logger.error(
                f'При отправке отказа пользователем {interaction.user.display_name} '
                f'возникла ошибка {error}'
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
            await interaction.response.send_modal(
                RaidChampionDominionApplication())
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
        max_values=3,
        placeholder='Выбери игроков...'
    )
    async def select_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction
    ):
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        await self.update_embed(
            interaction,', '.join(user.mention for user in select.values)
        )

    @button(label='Очистить', style=discord.ButtonStyle.gray, custom_id='Очистить')
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        await self.update_embed(interaction, '')

    async def update_embed(
        self,
        interaction: discord.Interaction,
        value: str
    ) -> None:
        embed.get('final_rcd_list_embed').fields[self.index].value = value
        await last_message_to_finish.get('final_rcd_list_message').edit(embed=embed.get('final_rcd_list_embed'))
        await interaction.message.delete()


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
        9: 'Барды:',
        10: 'Демоны:'
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
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        last_message_to_finish['create_RCD_list_buttons'] = interaction.message
        obj_1: discord.ui.Button = self.children[0]
        obj_13: discord.ui.Button = self.children[12]

        obj_1.label = '⬇️ Список создан ниже ⬇️'
        obj_1.style = discord.ButtonStyle.gray
        obj_1.disabled = True

        for button in self.children[1:12]:
            button.style = discord.ButtonStyle.green
            button.disabled = False

        obj_13.style = discord.ButtonStyle.blurple
        obj_13.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(embed=embed.get('final_rcd_list_embed'))

    @button(
        label='Редактировать "Воинов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьВоинов', disabled=True
    )
    async def add_warior_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 0)

    @button(
        label='Редактировать "Паладинов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьПаладинов', disabled=True
    )
    async def add_paladin_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 1)

    @button(
        label='Редактировать "Инженеров"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьИнженеров', disabled=True
    )
    async def add_ingeneer_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 2)

    @button(
        label='Редактировать "Жрецов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьЖрецов', disabled=True
    )
    async def add_priest_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 3)

    @button(
        label='Редактировать "Друидов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьДруидов', disabled=True
    )
    async def add_druid_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 4)

    @button(
        label='Редактировать "Мистиков"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьМистиков', disabled=True
    )
    async def add_mistic_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 5)

    @button(
        label='Редактировать "Лучников"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьЛучников', disabled=True
    )
    async def add_stalker_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 6)

    @button(
        label='Редактировать "Магов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьМагов', disabled=True
    )
    async def add_mage_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 7)

    @button(
        label='Редактировать "Некромантов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьНекромантов', disabled=True
    )
    async def add_necromant_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 8)

    @button(
        label='Редактировать "Бардов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьБардов', disabled=True
    )
    async def add_bard_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 9)

    @button(
        label='Редактировать "Демонологов"', style=discord.ButtonStyle.gray,
        custom_id='РедактироватьДемонологов', disabled=True
    )
    async def add_deamon_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.check_interaction_permission(interaction, 10)

    @button(
        label='Опубликовать список 📨',
        style=discord.ButtonStyle.gray,
        custom_id='ОпубликоватьСписок',
        disabled=True
    )
    async def select_callback(
        self, button: discord.ui.Select, interaction: discord.Interaction
    ):
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        channel: discord.TextChannel = rcd_application_channel.get('rcd_aplication_channel')
        f_embed: discord.Embed = embed.get('final_rcd_list_embed')
        publish_embed: discord.Embed = publish_rcd_embed(date=rcd_date_list.get('convert_rcd_date'))
        for field in [field for field in f_embed.fields if field.value != '']:
            name, value, inline = field.name, field.value, field.inline
            publish_embed.add_field(name=name, value=value, inline=inline)
        if 'Список РЧД' in channel.last_message.embeds[0].title:
            await channel.last_message.edit(embed=publish_embed)
        else:
            await channel.last_message.delete()
            await channel.send(embed=publish_embed)
        button: discord.ui.Button = self.children[13]
        button.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(
            f'_Список РЧД опубликован в канале {channel.mention}_',
            ephemeral=True,
            delete_after=1
        )

    @button(
        label='Завершить работу со списком РЧД', style=discord.ButtonStyle.red,
        custom_id='ЗавершитьРЧДСписок', disabled=True
    )
    async def stop_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        await interaction.channel.delete_messages(
            [message for key, message in last_message_to_finish.items() if key != 'start_RCD_button_message']
        )
        await last_message_to_finish.get('start_RCD_button_message').edit(view=None)
        member_list.clear()
        rcd_date_list.clear()
        embed.clear()
        last_message_to_finish.clear()
        await interaction.respond(
            '_Работа со списком РЧД завершена! ✅_',
            ephemeral=True,
            delete_after=2

        )

    async def check_interaction_permission(
            self,
            interaction: discord.Interaction,
            index: int,
    ):
        if not last_message_to_finish.get('final_rcd_list_message'):
            last_message_to_finish['final_rcd_list_message'] = interaction.channel.last_message
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
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
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        last_message_to_finish['start_RCD_button_message'] = interaction.message
        channel: discord.TextChannel = select.values[0]
        rcd_application_channel['rcd_aplication_channel'] = channel
        try:
            await channel.send(
                embed=start_rcd_embed(rcd_date_list.get('convert_rcd_date')),
                view=RCDButton()
            )
            await interaction.respond(view=CreateRCDList())
            self.children[0].disabled = True
            self.children[1].disabled = False
            self.remove_item(self.children[0])
            await interaction.response.edit_message(view=self)
            logger.info(
                f'Пользователь {interaction.user.display_name} запустил '
                f'заявки на РЧД'
            )
        except Exception as error:
            logger.error(f'При нажатии на кнопку StartRCDButton возникла ошибка {error}')

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=24,
        placeholder='Выбери игроков, которых спросить об РЧД',
        disabled=True
    )
    async def ask_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction
    ):
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        await interaction.response.defer()
        ask_users: list[discord.Member] = [user for user in select.values]
        for user in ask_users:
            await user.send(
                embed=ask_veteran_embed(
                    member=interaction.user, date=rcd_date_list.get('convert_rcd_date')
                ),
                view=PrivateMessageView(),
                delete_after=10800
            )
        self.disable_all_items()
        self.clear_items()
        await interaction.message.edit(view=self)
        await interaction.respond('_Сообщения были отправлены, выбранным пользователям!_ ✅')
