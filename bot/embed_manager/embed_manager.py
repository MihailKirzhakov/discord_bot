import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, select, button
from loguru import logger

from .embeds import attention_embed, symbols_list_embed
from regular_commands.regular_commands import command_error
from variables import LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE


class AttentionMessage(Modal):
    """Модальное окно для отправки важного сообщения."""
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title='Важное сообщение', timeout=None)
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи содержание сообщения',
                placeholder='Не более 4000 символов',
                max_length=4000
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            message: str = str(self.children[0].value)
            await self.channel.send(embed=attention_embed(value=message))
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(
                f'Пользователь {interaction.user.display_name} попытался сделать объявление '
                f'но получил ошибку {error}!'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def attention(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
) -> None:
    """
    Команда для отправки сообщения с пометкой 'Внимание!'.
    """
    await ctx.response.send_modal(AttentionMessage(channel=channel))
    logger.info(
        f'Команда "/attention" вызвана пользователем '
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Сообщение отправлено в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=3
    )


@attention.error
async def attention_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды attention.
    """
    await command_error(ctx, error, "attention")


class SetNewDescription(Modal):
    """Модальное окно для установки нового описания embed"""
    def __init__(self, message_id: int, channel: discord.TextChannel):
        super().__init__(title='Укажи новое описание embed', timeout=None)
        self.message_id = message_id
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи содержание сообщения',
                placeholder='Не более 4000 символов',
                max_length=4000
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            message: discord.Message = await self.channel.fetch_message(self.message_id)
            try:
                embed: discord.Embed = message.embeds[0]
            except Exception as error:
                logger.error(f'Ошибка при поиске embed! "{error}"')
            embed.description = self.children[0].value
            await message.edit(embed=embed)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(
                f'Пользователь {interaction.user.display_name} попытался изменить embed '
                f'но получил ошибку {error}!'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE)
async def edit_embed(
    ctx: discord.ApplicationContext,
    message_id: discord.Option(
        str,
        description='ID сообщения, которое нужно изменить',
        name_localizations={'ru':'id_сообщения'}
    )  # type: ignore
) -> None:
    """
    Команда для изменения embed description, написанное ботом.
    """
    try:
        await ctx.response.send_modal(SetNewDescription(
            message_id=int(message_id),
            channel=ctx.channel
        ))
        logger.info(
            f'Команда "/edit_embed" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/edit_embed"! '
            f'"{error}"'
        )


@edit_embed.error
async def edit_embed_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды edit_embed.
    """
    await command_error(ctx, error, "edit_embed")


class CreateOrEditSymbolsList(View):
    """
    Универсальное модальное окно для создания или
    редактирования списка за символы свершения
    """
    banner_list: str | None = None
    cape_list: str | None = None

    def __init__(
        self,
        timeout: float | None = None,
        lookup_message: discord.Message | None = None
    ) -> None:
        super().__init__(timeout=timeout)
        self.lookup_message = lookup_message

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=24,
        placeholder='Выбери игроков'
    )
    async def banner_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            select_value: list[discord.User] = select.values
            self.banner_list: str = '\n'.join(
                f"{number}. {user.name}" for number, user
                in enumerate(select_value, start=1)
            )
            select.disabled = True
            await interaction.respond('✅')
        except Exception as error:
            logger.error(
                f'При оформлении списка знамён вышла "{error}"'
            )

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=24,
        placeholder='Выбери игроков'
    )
    async def cape_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            select_value: list[discord.User] = select.values
            self.cape_list: str = '\n'.join(
                f"{number}. {user.name}" for number, user
                in enumerate(select_value, start=1)
            )
            select.disabled = True
            await interaction.respond('✅')
        except Exception as error:
            logger.error(
                f'При оформлении списка накидок вышла "{error}"'
            )

    @button(
        label='Создать',
        style=discord.ButtonStyle.green,
        emoji='📨'
    )
    async def create_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if self.lookup_message:
                embed: discord.Embed = self.lookup_message.embeds[0]
                banner_fieild: discord.EmbedField = embed.fields[0]
                cape_field = 
                await self.lookup_message.edit(
                    embed=symbols_list_embed(
                        banner_list=self.banner_list,
                        cape_list=self.cape_list
                    )
                )
            else:
                await interaction.channel.send(
                    embed=symbols_list_embed(
                        banner_list=self.banner_list,
                        cape_list=self.cape_list
                    )
                )
            await interaction.respond('✅')
        except Exception as error:
            logger.error(
                f'При создании списка знамён/накидок вышла "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE)
async def embed_manager(
    ctx: discord.ApplicationContext,
    message_id: discord.Option(
        str,
        description='ID сообщения, которое нужно изменить',
        name_localizations={'ru':'id_сообщения'},
        required=False
    ),  # type: ignore
) -> None:
    """
    Команда для создания или изменения списка за символы.
    """
    try:
        await ctx.defer(ephemeral=True)

        if message_id:
            try:
                lookup_message: discord.Message = await ctx.channel.fetch_message(int(message_id))
            except discord.NotFound:
                await ctx.respond('_Сообщение не найдено по этому ID_', delete_after=2)
                logger.warning(f'Не найдено сообщение по id = {message_id}')

            if not lookup_message.embeds[0]:
                await ctx.respond('_У этого сообщения нет embed!_', delete_after=2)

            await ctx.respond(view=CreateOrEditSymbolsList(lookup_message=lookup_message))
        else:
            await ctx.respond(view=CreateOrEditSymbolsList())
        await ctx.respond('✅')
        logger.info(
            f'Команда "/embed_manager" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/embed_manager"! '
            f'"{error}"'
        )


@embed_manager.error
async def embed_manager_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды embed_manager.
    """
    await command_error(ctx, error, "embed_manager")


def setup(bot: discord.Bot):
    bot.add_application_command(attention)
    bot.add_application_command(edit_embed)
    bot.add_application_command(embed_manager)
