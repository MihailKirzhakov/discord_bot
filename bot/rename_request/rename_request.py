import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .embeds import (
    rename_embed, changed_rename_embed,
    denied_rename_embed, denied_send_embed
)
from core import async_session_factory, LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE, LEADER_NICKNAME
from core.orm import rename_req_orm


class AccessDeniedView(View):
    """
    Кнопки для одобрения или отказа в ренейме.
    """
    def __init__(self, timeout: float | None = None):
        super().__init__(timeout=timeout)

    
    async def get_member_params(self, session: AsyncSession, interaction: discord.Interaction):
        old_nickname = interaction.message.embeds[0].author.name
        rename_req_obj = await rename_req_orm.get_rename_request_obj(session, old_nickname)
        if not rename_req_orm:
            return await interaction.respond('Ошибка в БД, не нашел пользователя! ❌')
        guild = interaction.guild
        member = await guild.fetch_member(rename_req_obj.user_id)

        return old_nickname, rename_req_obj, member

    
    @button(label='Сменить никнейм', custom_id='СменитьНикнейм', style=discord.ButtonStyle.green)
    async def callback_accept(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            async with async_session_factory() as session:
                await interaction.response.defer(invisible=False, ephemeral=True)
                old_nickname, rename_req_obj, member = await self.get_member_params(
                    session=session,
                    interaction=interaction
                )
                await member.edit(nick=rename_req_obj.new_nickname)
                self.disable_all_items()
                self.clear_items()
                await interaction.message.edit(
                    embed=changed_rename_embed(
                        old_nickname=old_nickname,
                        jump_url=member.jump_url,
                        new_nickname=rename_req_obj.new_nickname
                    ),
                    view=self
                )
                await rename_req_orm.delete_rename_request_data(session, old_nickname)
                await session.commit()
                await interaction.respond('✅', delete_after=1)
                logger.info(
                    f'Никнейм пользователя {old_nickname} изменён '
                    f'на {rename_req_obj.new_nickname}'
                )
        except Exception as error:
            await interaction.respond('❌', delete_after=3)
            logger.error(
                f'При попытке изменить никнейм возникла ошибка {error}'
            )

    @button(
        label='Отказать в ренейме, если не совпадает с игровым',
        custom_id='ОтказатьВренейме',
        style=discord.ButtonStyle.red
    )
    async def callback_denied(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            async with async_session_factory() as session:
                await interaction.response.defer(invisible=False, ephemeral=True)
                old_nickname, rename_req_obj, member = await self.get_member_params(
                    session=session,
                    interaction=interaction
                )
                try:
                    await member.send(
                        embed=denied_send_embed()
                    )
                except discord.Forbidden:
                    logger.warning(f'Пользователю "{old_nickname}" запрещено отправлять сообщения')
                self.disable_all_items()
                self.clear_items()
                await interaction.message.edit(
                    embed=denied_rename_embed(old_nickname=old_nickname, jump_url=member.jump_url),
                    view=self
                )
                await rename_req_orm.delete_rename_request_data(session, old_nickname)
                await session.commit()
                await interaction.respond('✅', delete_after=1)
                logger.info(f'Никнейм пользователя {old_nickname} НЕ изменён')
        except Exception as error:
            await interaction.respond('❌', delete_after=3)
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
            async with async_session_factory() as session:
                await interaction.response.defer(invisible=False, ephemeral=True)
                rename_req_obj = await rename_req_orm.get_rename_request_obj(session, user.display_name)
                if interaction.user.display_name == new_nickname:
                    return await interaction.respond(
                        '_Зачем менять никнейм на свой текущий? 🤔_',
                        delete_after=3
                    )
                if rename_req_obj:
                    await interaction.respond(
                        '_Ты уже отправил запрос на смену ника, ожидай! 👌_',
                        delete_after=3
                    )
                else:
                    await self.channel.send(
                        embed=rename_embed(
                            old_nickname=user.display_name,
                            jump_url=user.jump_url,
                            new_nickname=new_nickname
                        ),
                        view=AccessDeniedView()
                    )
                    await rename_req_orm.insert_rename_request_data(
                        session=session,
                        old_nickname=user.display_name,
                        new_nickname=new_nickname,
                        user_id=user.id
                    )
                    await session.commit()
                    await interaction.respond(
                        '_Запрос отправлен, погоди чутка! ✅_',
                        delete_after=3
                    )
                    logger.info(
                        f'Отправлен запрос на смену ника пользователем {user.display_name}'
                    )
        except Exception as error:
            await interaction.respond(
                '_Не получилось отправить запрос ❌\n\n'
                f'Код ошибки: **{error}**\n\n'
                f'Заскринь, отправь {LEADER_NICKNAME}, он разберётся!👌_'
            )
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


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rename(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'}
    ),  # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки рандомайзера.
    """
    if message_id:
        message = ctx.channel.get_partial_message(int(message_id))
        await message.edit(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера обновлена и снова работает!_',
            ephemeral=True,
            delete_after=3
        )
    else:
        await ctx.respond(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера запущена!_',
            ephemeral=True,
            delete_after=3
        )
    logger.info(
        f'Команда "/rename" вызвана пользователем'
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )


@rename.error
async def role_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обрабатывать ошибки, возникающие
    при выполнении команды запросов на ренейм.
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер, Кизначей или Офицер"!',
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
    bot.add_application_command(rename)
