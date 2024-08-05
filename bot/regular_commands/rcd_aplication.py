import discord
from discord.ui import Modal, InputText, Select, View, button
from loguru import logger

from .embeds import (
    start_rcd_embed, rcd_list_embed, ask_veteran_embed,
    final_rcd_list_embed
)
from variables import VETERAN_ROLE


member_list: list = []


class RaidChampionDominionApplication(Modal):
    """
    Модальное окно для ввода данных на заявку РЧД.
    """
    def __init__(
            self,
            embed: discord.Embed,
            message: discord.Message
    ):
        super().__init__(title='Заявка на РЧД', timeout=None)
        self.embed = embed
        self.message = message

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
                    delete_after=10
                )
            honor: str = str(self.children[0].value)
            class_role: str = str(self.children[1].value)
            if not class_role:
                class_role = 'Любой класс'
            field_index = 0 if discord.utils.get(interaction.user.roles, name=VETERAN_ROLE) else 1
            self.embed.fields[field_index].value += (
                f'{interaction.user.mention}: {class_role} ({honor})\n'
            )
            await self.message.edit(embed=self.embed)
            member_list.append(f'{interaction.user.display_name}')
            await interaction.respond(
                '_Заявка принята ✅_',
                ephemeral=True,
                delete_after=15
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

    Parametrs:
    ----------
        channel: discord.TextChannel
            Текстовый канал, в который отправляется запрос.

    Returns:
    --------
        None
    """
    def __init__(
            self,
            embed: discord.Embed,
            message: discord.Message,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.embed = embed
        self.message = message

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
                    embed=self.embed, message=self.message
                ))
        except Exception as error:
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем {interaction.user.display_name} '
                f'возникла ошибка {error}'
            )


class SelectMemberToRCD(Select):
    """
    Меню для выбора пользователей в РЧД список
    """
    def __init__(
            self,
            index: int,
            embed: discord.Embed,
            select_type: discord.ComponentType = discord.ComponentType.user_select
    ) -> None:
        super().__init__(select_type=select_type)
        self.index = index
        self.embed = embed

    def callback(self, interaction: discord.Interaction):
        if not self.values:
            self.embed.fields[self.index].value += 'Нет'
        else:
            selected_members = [user.mention for user in self.values]
            self.embed.fields[self.index].value += ', '.join(selected_members)


class CreateRCDList(View):
    """
    Кнопки для создания РЧД списка.

    Parametrs:
    ----------
        channel: discord.TextChannel
            Текстовый канал, в который отправляется запрос.

    Returns:
    --------
        None
    """
    embed = final_rcd_list_embed()

    def __init__(
        self,
        channel: discord.TextChannel,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(
        label='Создать список', style=discord.ButtonStyle.green,
        custom_id='СоздатьСписок'
    )
    async def create_list_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.respond(embed=self.embed)

    @button(
        label='Опубликовать список', style=discord.ButtonStyle.blurple,
        custom_id='ОпубликоватьСписок'
    )
    async def publish_list_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.channel.send(embed=self.embed)
        await interaction.respond(
            f'Список РЧД опубликован в канале {self.channel.mention}'
        )

    @button(
        label='Добавить "Воинов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьВоинов'
    )
    async def add_warior_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Воины:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=0, embed=self.embed)
        )

    @button(
        label='Добавить "Паладинов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьПаладинов'
    )
    async def add_paladin_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Паладин:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=1, embed=self.embed)
        )

    @button(
        label='Добавить "Инженеров"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьИнженеров'
    )
    async def add_ingeneer_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Инженеры:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=2, embed=self.embed)
        )

    @button(
        label='Добавить "Жрецов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьЖрецов'
    )
    async def add_priest_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Жрецы:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=3, embed=self.embed)
        )

    @button(
        label='Добавить "Друидов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьДруидов'
    )
    async def add_druid_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Шаман:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=4, embed=self.embed)
        )

    @button(
        label='Добавить "Мистиков"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьМистиков'
    )
    async def add_mistic_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Мистики:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=5, embed=self.embed)
        )

    @button(
        label='Добавить "Лучников"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьЛучников'
    )
    async def add_stalker_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Лучники:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=6, embed=self.embed)
        )

    @button(
        label='Добавить "Магов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьМагов'
    )
    async def add_mage_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Маги:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=7, embed=self.embed)
        )

    @button(
        label='Добавить "Некромантов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьНекромантов'
    )
    async def add_necromant_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Некроманты:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=8, embed=self.embed)
        )

    @button(
        label='Добавить "Бардов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьБардов'
    )
    async def add_bard_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Барды:',
            value='',
            inline=False
        )
        await interaction.respond(
            view=SelectMemberToRCD(index=9, embed=self.embed)
        )

    @button(
        label='Добавить "Демонологов"', style=discord.ButtonStyle.green,
        custom_id='ДобавитьДемонологов'
    )
    async def add_deamon_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        self.embed.add_field(
            name='Демоны:',
            value='',
            inline=False
        )
        view = discord.ui.View()
        view.add_item(SelectMemberToRCD(index=0, embed=self.embed))
        await interaction.respond(
            view=view
        )


class StartRCDButton(View):
    """
    Кнопка для запуска РЧД заявок.

    Parametrs:
    ----------
        channel: discord.TextChannel
            Текстовый канал, в который отправляется запрос.

    Returns:
    --------
        None
    """
    def __init__(
        self,
        channel: discord.TextChannel,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(
        label='Запустить заявки на РЧД', style=discord.ButtonStyle.green,
        custom_id='СтартЗаявокРЧД'
    )
    async def start_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.respond(embed=rcd_list_embed())
            message = interaction.channel.last_message
            await self.channel.send(
                embed=start_rcd_embed(),
                view=RCDButton(embed=rcd_list_embed(), message=message)
            )
            await interaction.respond(view=CreateRCDList(channel=self.channel))
            await interaction.respond(
                f'_Заявки запущены в канале {self.channel.mention} 👌_',
                ephemeral=True,
                delete_after=10
            )
            logger.info(
                f'Пользователь {interaction.user.display_name} запустил '
                f'заявки на РЧД'
            )
        except Exception as error:
            logger.error(f'При нажатии на кнопку StartRCDButton возникла ошибка {error}')

    @button(
        label='Спросить всех "Ветеранов"', style=discord.ButtonStyle.blurple,
        emoji='❓', custom_id='СпроситьВетеранов'
    )
    async def ask_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        url = self.channel.jump_url
        role = discord.utils.get(interaction.guild.roles, name=VETERAN_ROLE)
        veteran_members = [member for member in interaction.guild.members if role in member.roles]
        for veteran_member in veteran_members:
            await veteran_member.send(
                embed=ask_veteran_embed(
                    member=interaction.user, url=url
                ),
                delete_after=10800
            )
        await interaction.respond(
            'Сообщения были отправлены всем ветеранам',
            ephemeral=True,
            delete_after=10
        )
