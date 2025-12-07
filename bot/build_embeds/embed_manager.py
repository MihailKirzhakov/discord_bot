import json

import chardet
import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, select, button
from loguru import logger

from .functions import (
    validate_amount, generate_member_list, handle_selection,
    sort_nicknames_by_role
)
from .embeds import attention_embed, symbols_list_embed
from regular_commands.regular_commands import command_error
from core import LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE


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
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def edit_embed_description(
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
            f'Команда "/edit_embed_description" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/edit_embed_description"! '
            f'"{error}"'
        )


@edit_embed_description.error
async def edit_embed_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды edit_embed_description.
    """
    await command_error(ctx, error, "edit_embed_description")


class CreateOrEditSymbolsList(View):
    """
    Универсальное модальное окно для создания или
    редактирования списка за символы свершения
    """
    banner_list: str | None = None
    cape_list: str | None = None
    select_type: discord.ComponentType = discord.ComponentType.user_select
    min_values: int = 1
    max_values: int = 24
    placeholder: str = 'Выбери игроков'

    def __init__(
        self,
        lookup_message: discord.Message | None = None
    ) -> None:
        super().__init__(timeout=None)
        self.lookup_message = lookup_message

    @select(
        select_type=select_type,
        min_values=min_values,
        max_values=max_values,
        placeholder=placeholder
    )
    async def banner_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        await handle_selection(self, select, interaction, 'banner')

    @select(
        select_type=select_type,
        min_values=min_values,
        max_values=max_values,
        placeholder=placeholder
    )
    async def cape_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        await handle_selection(self, select, interaction, 'cape')

    @button(
        label='Опубликовать',
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
                banner_field: discord.EmbedField = embed.fields[0]
                cape_field: discord.EmbedField = embed.fields[1]
                banner_field.value = self.banner_list
                cape_field.value = self.cape_list
                await self.lookup_message.edit(embed=embed)
            else:
                await interaction.channel.send(
                    embed=symbols_list_embed(
                        banner_list=self.banner_list,
                        cape_list=self.cape_list
                    )
                )
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(
                f'При создании списка знамён/накидок вышла "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def symbols_list(
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
                lookup_message: discord.Message = (
                    await ctx.channel.fetch_message(int(message_id))
                )
            except discord.NotFound:
                await ctx.respond(
                    '_Сообщение не найдено по этому ID_', delete_after=2
                )
                logger.warning(f'Не найдено сообщение по id = {message_id}')

            if not lookup_message.embeds[0]:
                await ctx.respond(
                    '_У этого сообщения нет embed!_', delete_after=2
                )

            await ctx.respond(
                view=CreateOrEditSymbolsList(lookup_message=lookup_message)
            )
        else:
            await ctx.respond(view=CreateOrEditSymbolsList())
        logger.info(
            f'Команда "/embed_manager" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/embed_manager"! '
            f'"{error}"'
        )


@symbols_list.error
async def embed_manager_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды symbols_list.
    """
    await command_error(ctx, error, "symbols_list")


class ChooseSimbolsAmount(Modal):
    """Модальное окно для выбора количества топ за символы."""
    def __init__(
        self,
        ctx: discord.ApplicationContext,
        message_id: str,
        channel: discord.TextChannel
    ):
        super().__init__(
            title='Укажи сколько знамён и чемпионок',
            timeout=None
        )
        self.ctx = ctx
        self.message_id = message_id
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи количество победителей для знамён',
                placeholder='Не более 30',
                max_length=2
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи количество победителей для чемпионок',
                placeholder='Не более 10',
                max_length=2,
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            checking_message: discord.Message = (
                await self.ctx.channel.fetch_message(int(self.message_id))
            )
            attachment = checking_message.attachments[0]
            bytes_data = await attachment.read()
            detected = chardet.detect(bytes_data)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            try:
                content = bytes_data.decode(encoding)
            except UnicodeDecodeError:
                try:
                    content = bytes_data.decode('windows-1251')
                except UnicodeDecodeError as e:
                    logger.error(f"Ошибка декодирования файла: {e}")
                    await interaction.respond("Ошибка: файл не может быть прочитан. Проверьте кодировку файла.")
                    return
            data_start = content.find('[')  # Находим начало JSON-данных
            data_end = content.rfind(']') + 1  # Находим конец JSON-данных
            json_data = content[data_start:data_end]
            data_list = json.loads(json_data)
            members: list[discord.Member] = interaction.guild.members
            roles: list[discord.Role] = interaction.guild.roles
            banner_amount: str | None = self.children[0].value
            cape_amount: str | None = self.children[1].value
            result: list[str] = [item['name'] for item in data_list]
            sorted_result: list[str] = await sort_nicknames_by_role(
                members, roles, result
            )

            # Валидируем вводимое значение пользователем для знамён
            validated_banner_amount = await validate_amount(
                value=banner_amount,
                interaction=interaction
            )
            # Генерируем список знамён
            banner_list = await generate_member_list(
                sorted_result[:validated_banner_amount],
                interaction=interaction
            )
            # Валидируем вводимое значение пользователем для накидок
            if cape_amount:
                validated_cape_amount = await validate_amount(
                    value=cape_amount,
                    interaction=interaction,
                    is_banner=False
                )
                # Генерируем список накидок, если нужно
                cape_list = await generate_member_list(
                    sorted_result[
                        validated_banner_amount:validated_cape_amount
                        + validated_banner_amount
                    ],
                    interaction=interaction
                )

            await self.channel.send(
                embed=symbols_list_embed(
                    banner_list=banner_list,
                    cape_list=cape_list if cape_amount else None
                )
            )
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(
                f'Пользователь {interaction.user.display_name} попытался выбрать кол-во '
                f'за накидки/чемпы, но получил ошибку {error}!'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def auto_simbols_list(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть файл',
        name_localizations={'ru':'id_сообщения'}
    )  # type: ignore
) -> None:
    """
    Команда для автоматического вывода списка топ за символы.
    """
    try:
        if not message_id.isdigit():
            ctx.respond('❌\n_Введи ID сообщения с файлом!_')
        await ctx.response.send_modal(ChooseSimbolsAmount(
            ctx=ctx, message_id=message_id, channel=channel
        ))
        logger.info(
            'Команда "/auto_simbols_list" вызвана пользователем '
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        await ctx.respond(f'_Ошибка ❌: {error}_')
        logger.error(f'Ошибка при вызове команды "/auto_simbols_list"! "{error}"')


@auto_simbols_list.error
async def auto_simbols_list_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды auto_simbols_list.
    """
    await command_error(ctx, error, "auto_simbols_list")


def setup(bot: discord.Bot):
    bot.add_application_command(attention)
    bot.add_application_command(edit_embed_description)
    bot.add_application_command(symbols_list)
    bot.add_application_command(auto_simbols_list)
