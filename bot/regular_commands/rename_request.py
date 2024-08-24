import discord
from discord.ui import Modal, InputText, View, button
from loguru import logger

from .embeds import (
    rename_embed, changed_rename_embed,
    denied_rename_embed, denied_send_embed
)


que_request: dict = {}


class AccessDeniedButton(View):
    """
    Кнопки для одобрения или отказа в ренейме.
    """
    def __init__(
            self,
            old_nickname: str,
            new_nickname: str,
            user: discord.Member,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.old_nickname = old_nickname
        self.new_nickname = new_nickname
        self.user = user

    @button(label='Сменить никнейм', style=discord.ButtonStyle.green)
    async def callback_accept(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            self.disable_all_items()
            self.clear_items()
            await self.user.edit(nick=self.new_nickname)
            await interaction.message.edit(
                embed=changed_rename_embed(
                    user=self.old_nickname, nickname=self.new_nickname
                ),
                view=self
            )
            que_request[self.user] = False
            await interaction.respond('✅', delete_after=1)
            logger.info(
                f'Никнейм пользователя {self.user} изменён '
                f'на {self.new_nickname}'
            )
        except Exception as error:
            logger.error(
                f'При попытке изменить никнейм возникла ошибка {error}'
            )

    @button(
        label='Отказать в ренейме, если не совпадает с игровым',
        style=discord.ButtonStyle.red
    )
    async def callback_denied(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            self.disable_all_items()
            self.clear_items()
            try:
                await self.user.send(
                    embed=denied_send_embed()
                )
            except discord.Forbidden:
                logger.warning(f'Пользователю "{self.user.display_name}" запрещено отправлять сообщения')
            await interaction.message.edit(
                embed=denied_rename_embed(user=self.user.display_name),
                view=self
            )
            que_request[self.user] = False
            await interaction.respond('✅', delete_after=1)
            logger.info(f'Никнейм пользователя {self.user.display_name} НЕ изменён')
        except Exception as error:
            logger.error(
                f'При попытке отказа в изменении никнейма возникла ошибка {error}'
            )


class RenameModal(Modal):
    """
    Модальное окно для ввода нового никнейма.
    """
    def __init__(
            self,
            channel: discord.TextChannel
    ):
        super().__init__(title='Ренеймер', timeout=None)
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Впиши новый игровой никнейм',
                placeholder='Длина никнейма как в игре 3-14 символов',
                min_length=3,
                max_length=14
            )
        )

    async def callback(self, interaction: discord.Interaction):
        new_nickname: str = self.children[0].value
        user: discord.Member = interaction.user
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if interaction.user.display_name == new_nickname:
                return await interaction.respond(
                    '_Зачем менять никнейм на свой текущий? 🤔_',
                    delete_after=3
                )
            if que_request.get(user):
                await interaction.respond(
                    '_Ты уже отправил запрос на смену ника, ожидай! 👌_',
                    delete_after=3
                )
            else:
                await self.channel.send(
                    embed=rename_embed(user=user.display_name, nickname=new_nickname),
                    view=AccessDeniedButton(old_nickname=user.display_name, user=user, new_nickname=new_nickname)
                    )
                await interaction.respond(
                    '_Запрос отправлен, погоди чутка! ✅_',
                    delete_after=3
                )
                que_request[user] = True
                logger.info(
                    f'Отправлен запрос на смену ника пользователем {user.display_name}'
                )
        except Exception as error:
            logger.error(
                f'При попытке отправить запрос на смену ника возникла ошибка {error}'
            )


class RenameButton(View):
    """
    Кнопка для запуска модального окна для ввода нового никнейма.
    """
    def __init__(
            self,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(
            label='Запрос на смену ника', style=discord.ButtonStyle.green,
            emoji='👋', custom_id='Ренеймер'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.send_modal(
                RenameModal(channel=self.channel)
            )
        except Exception as error:
            logger.error(f'При нажатии на кнопку RenameButton возникла ошибка {error}')
