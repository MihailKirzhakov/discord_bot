import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button
from loguru import logger

from variables import (
    ANSWER_IF_DUPLICATE_APP, ANSWER_IF_DUPLICATE_NICK, ANSWER_IF_CHEAT,
    ANSWER_IF_CLICKED_THE_SAME_TIME, LEADER_ROLE, OFICER_ROLE,
    TREASURER_ROLE, SERGEANT_ROLE, GUEST_ROLE
)
from .embeds import (
    access_embed, denied_embed, application_embed, start_app_embed
)
from .functions import character_lookup, has_required_role, answer_if_no_role


app_list: list = []  # Список для контроля дублирующих заявок


class RoleButton(View):
    """
    Класс кнопки роли для взаимодействия с пользователем в Discord.
    Создаёт 2 кнопки. Первая для выдачи роли,
    вторая для отказа в выдаче роли 'Старшина'

    Attributes:
    -----------
        nickname: str
            Discord - псевдоним пользователя.

        embed: discord.Embed
            Embed объект, связанный с взаимодействием с пользователем.

        user: discord.Member | discord.User
            Пользователь, который взаимодействовал с модалкой.
    """

    def __init__(
            self,
            nickname: str,
            embed: discord.Embed,
            user: discord.Member | discord.User,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.nickname = nickname
        self.user = user
        self.embed = embed

    @button(label='Выдать старшину', style=discord.ButtonStyle.green)
    async def callback_accept(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        """Кнопка выдачи роли 'Старшина'."""
        if not has_required_role(interaction.user):
            await answer_if_no_role(interaction)
        role_sergeant = discord.utils.get(
            interaction.guild.roles, name=SERGEANT_ROLE
        )
        role_guest = discord.utils.get(
            interaction.guild.roles, name=GUEST_ROLE
        )
        try:
            if self.nickname not in app_list:
                await interaction.respond(
                    ANSWER_IF_CLICKED_THE_SAME_TIME,
                    ephemeral=True,
                    delete_after=15
                )
            else:
                await self.user.edit(nick=self.nickname)
                await self.user.add_roles(role_sergeant)
                await self.user.remove_roles(role_guest)
                self.embed.add_field(
                    name='_Результат рассмотрения_ ✔',
                    value=f'_{interaction.user.mention} выдал роль!_',
                    inline=False
                )
                self.disable_all_items()
                self.clear_items()
                await interaction.response.edit_message(
                    embed=self.embed,
                    view=self
                )
                await self.user.send(embed=access_embed())
                app_list.remove(self.nickname)
                logger.info(
                    f'Пользователь {interaction.user.display_name} '
                    f'выдал роль пользователю "{self.nickname}"!'
                )
        except Exception as error:
            logger.error(
                    f'При попытке выдать роль '
                    f'пользователю "{self.nickname}" возникла ошибка '
                    f'"{error}"'
                )

    @button(
        label='Отправить в ЛС, что не подходит',
        style=discord.ButtonStyle.red
    )
    async def callback_denied(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        """Кнопка отказа в выдаче выдачи роли 'Старшина'."""
        if not has_required_role(interaction.user):
            await answer_if_no_role(interaction)
        else:
            try:
                await interaction.response.send_modal(DeniedRoleModal(
                    nickname=self.nickname,
                    view=self,
                    user=self.user,
                    embed=self.embed
                ))
            except Exception as error:
                logger.error(
                    f'При попытке вызвать модальное окно нажатием на кнопку '
                    f'"{button.label}" возникла ошибка "{error}"'
                )


class DeniedRoleModal(Modal):
    """
    Класс модального окна для взаимодействия с пользователем в Discord.
    В данном случае, модальное окно используется для отказа в выдаче роли 'Старшина'.

    Attributes:
    -----------
        nickname: str
            Discord нинкнейм пользователя.

        user: discord.Member | discord.User
            Пользователь, провзаимодействоваший с кнопкой отказа в доступе.

        view: discord.ui.Button
            Кнопка.

        embed: discord.Embed
            Embed объект, связанный с взаимодействием с пользователем.

    """

    def __init__(
        self,
        nickname: str,
        user: discord.Member | discord.User,
        view: discord.ui.Button,
        embed: discord.Embed,
        *args,
        **kwargs
    ):
        super().__init__(
            *args, **kwargs, title='Комментарий к отказу', timeout=None
        )
        self.nickname = nickname
        self.user = user
        self.view = view
        self.embed = embed
        self.add_item(
                InputText(
                    style=discord.InputTextStyle.multiline,
                    label='Почему решил отказать в заявке',
                    placeholder=(
                        'Необязательно (если пусто, отправится дэфолт фраза)'
                    ),
                    max_length=400,
                    required=False
                )
            )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        value = self.children[0].value
        self.embed.add_field(
                name='_Результат рассмотрения_ ❌',
                value=f'_{interaction.user.mention} отказал в доступе!_',
                inline=False
            )
        if self.nickname not in app_list:
            await interaction.respond(
                ANSWER_IF_CLICKED_THE_SAME_TIME,
                ephemeral=True,
                delete_after=15
            )
        else:
            try:
                app_list.remove(self.nickname)
                await self.user.send(embed=denied_embed(user, value))
                self.view.disable_all_items()
                self.view.clear_items()
                await interaction.response.edit_message(embed=self.embed, view=self.view)
                logger.info(
                    f'Пользователь {interaction.user.display_name} отказал в доступе '
                    f'пользователю "{self.nickname}"!'
                )
            except Exception as error:
                logger.error(
                    f'При попытке отправить форму после нажатия на кнопку в '
                    f'модальном окне "Отказ в заявке" возникла ошибка "{error}"'
                )


class RoleApplication(Modal):
    """
    Класс модального окна для взаимодействия с пользователем в Discord.
    Используется для создания модального окна с полем для ввода никнейма.

    Attributes:
    -----------
        channel: discord.TextChannel
            Канал, в котором будет создано модальное окно.
    """

    def __init__(self, channel: discord.TextChannel, *args, **kwargs):
        super().__init__(
            *args, **kwargs, title='Заявка на выдачу роли', timeout=None
        )
        self.channel = channel

        self.add_item(
            InputText(
                label='Укажи свой игровой ник без пробелов',
                placeholder='Учитывай регистр (большие и маленькие буквы)'
            )
        )

    async def callback(self, interaction: discord.Interaction):
        nickname: str = self.children[0].value
        user = interaction.user
        member = discord.utils.get(interaction.guild.members, id=user.id)
        member_by_display_name = discord.utils.get(
            interaction.guild.members, display_name=nickname
        )
        role = discord.utils.get(interaction.guild.roles, name=GUEST_ROLE)
        player_parms = character_lookup(1, nickname)
        if not player_parms:
            return await interaction.respond(
                ANSWER_IF_CHEAT,
                ephemeral=True,
                delete_after=15
            )
        if nickname in app_list:
            return await interaction.respond(
                ANSWER_IF_DUPLICATE_APP,
                ephemeral=True,
                delete_after=10
            )
        if member_by_display_name:
            if role not in member_by_display_name.roles:
                return await interaction.respond(
                    ANSWER_IF_DUPLICATE_NICK,
                    ephemeral=True,
                    delete_after=10
                )
        description = (
            f'Профиль Discord: {user.mention}\n'
            f'Гильдия: {player_parms['guild']}'
        )
        if 'dragon_emblem' in player_parms:
            description += f'\nДраконий амулет: {player_parms['dragon_emblem']['name']}'
        try:
            await self.channel.send(
                view=RoleButton(
                    nickname=nickname,
                    user=user,
                    embed=application_embed(
                        description, nickname, member, player_parms
                    )
                ),
                embed=application_embed(
                    description, nickname, member, player_parms
                )
            )
            app_list.append(nickname)
            await interaction.respond(
                '👍\n_Твой запрос принят! Дождись выдачи роли_',
                ephemeral=True,
                delete_after=10
            )
            logger.info(
                    f'Пользователь {interaction.user.display_name} заполнил форму, '
                    f'она была отправлена в канал "{self.channel}"'
                )
        except Exception as error:
            logger.error(
                    f'При попытке отказать пользователю в выдаче роли '
                    f'пользователю "{nickname}" возникла ошибка '
                    f'"{error}"'
                )


class ApplicationButton(View):
    """
    Класс кнопки роли для взаимодействия с пользователем в Discord.
    Вызывает модальное окно для заполнения формы.'

    Attributes:
    -----------
        channel: discord.TextChannel.
            Канал, в котором будет создано модальное окно.
    """

    def __init__(
            self,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(
        label='Заполни форму', style=discord.ButtonStyle.green,
        emoji='📋', custom_id='Заявки'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.send_modal(RoleApplication(
                channel=self.channel
            ))
        except Exception as error:
            logger.error(
                f'При попытке вызвать модальное окно нажатием на кнопку '
                f'"{button.label}" возникла ошибка "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, TREASURER_ROLE, OFICER_ROLE)
async def role_application(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Выбери канал в который будут отправляться заявки',
        name_localizations={'ru': 'название_канала'}
    ),  # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    ),  # type: ignore
) -> None:
    """
    Команда для вызова кнопки, которая обрабатывает запросы на доступ.

    Parameters
    ----------
        ctx: discord.ApplicationContext.
            Контекст.

        channel: discord.TextChannel.
            Канал, в котором будет размещена кнопка.

    Returns
    -------
        None
    """
    try:
        if message_id:
            message = ctx.channel.get_partial_message(int(message_id))
            await message.edit(
                embed=start_app_embed(),
                view=ApplicationButton(channel=channel)
            )
            await ctx.respond(
                '_Кнопка подачи заявок обновлена, заявки снова работают!_',
                ephemeral=True,
                delete_after=10
            )
        else:
            await ctx.respond(
                embed=start_app_embed(),
                view=ApplicationButton(channel=channel)
            )
            await ctx.respond(
                '_Кнопка подачи заявок запущена!_',
                ephemeral=True,
                delete_after=10
            )
        logger.info(
            f'Команда "/role_application" вызвана пользователем '
            f'"{ctx.user.display_name}"! Кнопка была отправлена в канал '
            f'"{channel}"!'
        )
    except Exception as error:
        logger.error(
            f'При попытке вызвать команду /role_application'
            f'возникла ошибка "{error}". Команду попытался вызвать пользователь '
            f'"{ctx.user.display_name}". Канал для обработки заявок "{channel}"'
        )


@role_application.error
async def role_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обрабатывать ошибки, возникающие
    при выполнении команды запросов на выдачу доступа.

    Parameters
    ----------
        ctx: discord.ApplicationContext.
            Контекст.

        error: Exception
            Выбрасываемая ошибка.

    Returns
    -------
        None
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер", "Казначей" или "Офицер"!',
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
    bot.add_application_command(role_application)
