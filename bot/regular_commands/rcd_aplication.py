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
embed: discord.Embed = final_rcd_list_embed()
last_message_rcd_list: list[discord.Message] = []


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
        embed.fields[self.index].value = value
        await last_message_rcd_list[0].edit(embed=embed)
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
        obj_1: discord.ui.Button = self.children[0]
        obj_2: discord.ui.Button = self.children[1]
        obj_13: discord.ui.Select = self.children[12]

        obj_1.label = '⬇️ Список создан ниже ⬇️'
        obj_1.style = discord.ButtonStyle.gray
        obj_1.disabled = True

        obj_2.style = discord.ButtonStyle.green
        obj_2.disabled = False

        obj_13.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(embed=embed)

    @button(
        label='Добавить "Воинов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьВоинов', disabled=True
    )
    async def add_warior_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        last_message_rcd_list.append(interaction.channel.last_message)
        await self.update_view_rcd_list(interaction, 'Воины:', 0)

    @button(
        label='Добавить "Паладинов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьПаладинов', disabled=True
    )
    async def add_paladin_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 2:
            embed.add_field(
                name='Паладин:',
                value='',
                inline=False
            )
        obj_4: discord.ui.Button = self.children[3]
        obj_4.style = discord.ButtonStyle.green
        obj_4.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=1))

    @button(
        label='Добавить "Инженеров"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьИнженеров', disabled=True
    )
    async def add_ingeneer_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 3:
            embed.add_field(
                name='Инженеры:',
                value='',
                inline=False
            )
        obj_5: discord.ui.Button = self.children[4]
        obj_5.style = discord.ButtonStyle.green
        obj_5.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=2))

    @button(
        label='Добавить "Жрецов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьЖрецов', disabled=True
    )
    async def add_priest_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 4:
            embed.add_field(
                name='Жрецы:',
                value='',
                inline=False
            )
        obj_6: discord.ui.Button = self.children[5]
        obj_6.style = discord.ButtonStyle.green
        obj_6.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=3))

    @button(
        label='Добавить "Друидов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьДруидов', disabled=True
    )
    async def add_druid_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 5:
            embed.add_field(
                name='Шаман:',
                value='',
                inline=False
            )
        obj_7: discord.ui.Button = self.children[6]
        obj_7.style = discord.ButtonStyle.green
        obj_7.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=4))

    @button(
        label='Добавить "Мистиков"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьМистиков', disabled=True
    )
    async def add_mistic_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 6:
            embed.add_field(
                name='Мистики:',
                value='',
                inline=False
            )
        obj_8: discord.ui.Button = self.children[7]
        obj_8.style = discord.ButtonStyle.green
        obj_8.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=5))

    @button(
        label='Добавить "Лучников"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьЛучников', disabled=True
    )
    async def add_stalker_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 7:
            embed.add_field(
                name='Лучники:',
                value='',
                inline=False
            )
        obj_9: discord.ui.Button = self.children[8]
        obj_9.style = discord.ButtonStyle.green
        obj_9.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=6))

    @button(
        label='Добавить "Магов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьМагов', disabled=True
    )
    async def add_mage_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 8:
            embed.add_field(
                name='Маги:',
                value='',
                inline=False
            )
        obj_10: discord.ui.Button = self.children[9]
        obj_10.style = discord.ButtonStyle.green
        obj_10.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=7))

    @button(
        label='Добавить "Некромантов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьНекромантов', disabled=True
    )
    async def add_necromant_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 9:
            embed.add_field(
                name='Некроманты:',
                value='',
                inline=False
            )
        obj_11: discord.ui.Button = self.children[10]
        obj_11.style = discord.ButtonStyle.green
        obj_11.disabled = False
        await interaction.message.edit(view=self)
        await interaction.respond(view=SelectMemberToRCD(index=8))

    @button(
        label='Добавить "Бардов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьБардов', disabled=True
    )
    async def add_bard_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.update_view_rcd_list(interaction, 'Барды:', 9)

    @button(
        label='Добавить "Демонологов"', style=discord.ButtonStyle.gray,
        custom_id='ДобавитьДемонологов', disabled=True
    )
    async def add_deamon_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        if len(embed.fields) < 11:
            embed.add_field(
                name='Демоны:',
                value='',
                inline=False
            )
        await interaction.respond(view=SelectMemberToRCD(index=10))

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
        await channel.last_message.delete()
        await channel.send(embed=embed)
        await interaction.respond(
            f'_Список РЧД опубликован в канале {channel.mention}_',
            ephemeral=True,
            delete_after=5
        )

    async def update_view_rcd_list(
            self,
            interaction: discord.Interaction,
            index: int,
    ) -> None:
        if len(embed.fields) < index + 1:
            embed.add_field(
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
        channel: discord.TextChannel = select.values[0]
        try:
            await channel.send(
                embed=start_rcd_embed(),
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
