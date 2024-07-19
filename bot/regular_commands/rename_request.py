import discord
from discord.ui import Modal, InputText, View, button
from loguru import logger

from .embeds import (
    rename_embed, changed_rename_embed,
    denied_rename_embed, denied_send_embed
)


que_request: dict = {}


class AccessDeniedButton(View):
    def __init__(
            self,
            new_nickname: str,
            user: discord.abc.User,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.new_nickname = new_nickname
        self.user = user

    @button(label='Сменить никнейм', style=discord.ButtonStyle.green)
    async def callback_accept(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            self.disable_all_items()
            self.clear_items()
            await self.user.edit(nick=self.new_nickname)
            await interaction.message.edit(
                embed=changed_rename_embed(
                    user=self.user.display_name, nickname=self.new_nickname
                ),
                view=self
            )
            logger.info(
                f'Никнейм пользователя {self.user.display_name} изменён '
                f'на {self.new_nickname}'
            )
            que_request[self.user] = False
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
            self.disable_all_items()
            self.clear_items()
            await self.user.send(
                embed=denied_send_embed()
            )
            await interaction.message.edit(
                embed=denied_rename_embed(user=self.user.display_name),
                view=self
            )
            que_request[self.user] = False
            logger.info(f'Никнейм пользователя {self.user.display_name} НЕ изменён')
        except Exception as error:
            logger.error(
                f'При попытке отказа в изменении никнейма возникла ошибка {error}'
            )


class RenameModal(Modal):

    def __init__(
            self,
            channel: discord.TextChannel
    ):
        super().__init__(title='Ренеймер')
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Впиши новый игровой никнейм',
                min_length=3,
                max_length=14
            )
        )

    async def callback(self, interaction: discord.Interaction):
        new_nickname: str = self.children[0].value
        user: discord.abc.User = interaction.user
        try:
            if que_request.get(user):
                await interaction.respond(
                    '_Ты уже отправил запрос на смену ника, ожидай! 👌_',
                    ephemeral=True,
                    delete_after=10
                )
            else:
                await self.channel.send(
                    embed=rename_embed(user=user.display_name, nickname=new_nickname),
                    view=AccessDeniedButton(user=user, new_nickname=new_nickname)
                    )
                await interaction.response.send_message(
                    '_Запрос отправлен, погоди чутка! ✅_',
                    ephemeral=True,
                    delete_after=10
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

    def __init__(
            self,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(label='Запрос на смену ника', style=discord.ButtonStyle.green, emoji='👋')
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.send_modal(RenameModal(channel=self.channel))
        except Exception as error:
            logger.error(f'При нажатии на кнопку возникла ошибка {error}')
