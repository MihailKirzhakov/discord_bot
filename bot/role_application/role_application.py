import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button
from loguru import logger

from variables import (
    ANSWER_IF_DUPLICATE_APP, ANSWER_IF_DUPLICATE_NICK, ANSWER_IF_CHEAT,
    ANSWER_IF_CLICKED_THE_SAME_TIME, LEADER_ROLE, OFICER_ROLE,
    TREASURER_ROLE, SERGEANT_ROLE, GUEST_ROLE, ANSWERS_IF_NO_ROLE
)
from .embeds import (
    access_embed, denied_embed, application_embed, start_app_embed
)
from .functions import character_lookup, has_required_role


app_list: list[str] = []  # Список для контроля дублирующих заявок


class RoleButton(View):
    """
    Класс кнопки роли для взаимодействия с пользователем в Discord.
    Создаёт 2 кнопки. Первая для выдачи роли,
    вторая для отказа в выдаче роли 'Старшина'.
    """

    def __init__(
            self,
            nickname: str,
            user: discord.Member | discord.User,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.nickname = nickname
        self.user = user

    @button(label='Выдать старшину', style=discord.ButtonStyle.green)
    async def callback_accept(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        """Кнопка выдачи роли 'Старшина'."""
        await interaction.response.defer(invisible=False, ephemeral=True)
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                delete_after=5
            )
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
                    delete_after=15
                )
            await self.user.edit(nick=self.nickname)
            await self.user.add_roles(role_sergeant)
            await self.user.remove_roles(role_guest)
            curent_embed = interaction.message.embeds[0]
            curent_embed.add_field(
                name='_Результат рассмотрения_ ✅',
                value=f'_{interaction.user.mention} выдал роль!_',
                inline=False
            )
            self.disable_all_items()
            self.clear_items()
            await interaction.message.edit(
                embed=curent_embed,
                view=self
            )
            try:
                await self.user.send(embed=access_embed())
            except discord.Forbidden:
                logger.warning(f'Пользователю "{self.user.display_name}" запрещено отправлять сообщения')
            await interaction.respond('✅', delete_after=1)
            logger.info(
                f'Пользователь {interaction.user.display_name} '
                f'выдал роль пользователю "{self.nickname}"!'
            )
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                    f'При попытке выдать роль '
                    f'пользователю "{self.nickname}" возникла ошибка '
                    f'"{error}"'
                )
        finally:
            app_list.remove(self.nickname)

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
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                ephemeral=True,
                delete_after=5
            )
        try:
            await interaction.response.send_modal(DeniedRoleModal(
                nickname=self.nickname,
                view=self,
                user=self.user,
                embed=self.embed
            ))
        except Exception as error:
            await interaction.respond('❌', ephemeral=True, delete_after=1)
            logger.error(
                f'При попытке вызвать модальное окно нажатием на кнопку '
                f'"{button.label}" возникла ошибка "{error}"'
            )


class DeniedRoleModal(Modal):
    """
    Класс модального окна для взаимодействия с пользователем в Discord.
    В данном случае, модальное окно используется для отказа в выдаче роли 'Старшина'.
    """

    def __init__(
        self,
        nickname: str,
        user: discord.Member,
        view: discord.ui.View,
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
        await interaction.response.defer(invisible=False, ephemeral=True)
        if self.nickname not in app_list:
            return await interaction.respond(
                ANSWER_IF_CLICKED_THE_SAME_TIME,
                delete_after=5
            )
        user = interaction.user
        value = self.children[0].value
        self.embed.add_field(
                name='_Результат рассмотрения_ ❌',
                value=f'_{interaction.user.mention} отказал в доступе!_',
                inline=False
            )
        try:
            app_list.remove(self.nickname)
            try:
                await self.user.send(embed=denied_embed(user, value))
            except discord.Forbidden:
                logger.warning(f'Пользователю "{self.user.display_name}" запрещено отправлять сообщения')
            self.view.disable_all_items()
            self.view.clear_items()
            await interaction.message.edit(embed=self.embed, view=self.view)
            await interaction.respond('✅', delete_after=1)
            logger.info(
                f'Пользователь {interaction.user.display_name} отказал в доступе '
                f'пользователю "{self.nickname}"!'
            )
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При попытке отправить форму после нажатия на кнопку в '
                f'модальном окне "Отказ в заявке" возникла ошибка "{error}"'
            )


class RoleApplication(Modal):
    """
    Класс модального окна для взаимодействия с пользователем в Discord.
    Используется для создания модального окна с полем для ввода никнейма.
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
        await interaction.response.defer(invisible=False, ephemeral=True)
        nickname: str = self.children[0].value
        user = interaction.user
        member = discord.utils.get(interaction.guild.members, id=user.id)
        member_by_display_name = discord.utils.get(interaction.guild.members, display_name=nickname)
        role = discord.utils.get(interaction.guild.roles, name=GUEST_ROLE)

        try:
            player_parms = character_lookup(1, nickname)
            if player_parms == 'Bad site work':
                await self.handle_bad_site_work(interaction, nickname, user, member)
                return

            if not player_parms:
                return await self.respond_with_message(interaction, ANSWER_IF_CHEAT, 15)

            if nickname in app_list:
                return await self.respond_with_message(interaction, ANSWER_IF_DUPLICATE_APP, 10)

            if member_by_display_name and role not in member_by_display_name.roles:
                return await self.respond_with_message(interaction, ANSWER_IF_DUPLICATE_NICK, 10)

            description = self.build_description(player_parms, user)
            await self.send_application(interaction, nickname, user, member, player_parms, description)
            logger.info(
                f'Пользователь {interaction.user.display_name} заполнил форму, '
                f'она была отправлена в канал "{self.channel}"'
            )

        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При попытке отказать пользователю в выдаче роли '
                f'пользователю "{nickname}" возникла ошибка '
                f'"{error}"'
            )

    async def handle_bad_site_work(self, interaction, nickname, user, member):
        description = f'Профиль Discord: {user.mention}\n'
        await self.channel.send(
            view=RoleButton(nickname=nickname, user=user),
            embed=application_embed(description, nickname, member, player_parms=None)
        )
        app_list.append(nickname)
        await self.respond_with_message(interaction, '👍\n_Твой запрос принят! Дождись выдачи роли_', 5)
        logger.info(
            f'Пользователь {interaction.user.display_name} заполнил форму, '
            f'она была отправлена в канал "{self.channel}"'
        )

    async def respond_with_message(self, interaction, message, delete_after):
        await interaction.respond(message, delete_after=delete_after)

    def build_description(self, player_parms, user):
        description = (
            f'Профиль Discord: {user.mention}\n'
            f'Гильдия: {player_parms["guild"]}'
        )
        if 'dragon_emblem' in player_parms:
            description += f'\nДраконий амулет: {player_parms["dragon_emblem"]["name"]}'
        return description

    async def send_application(self, interaction, nickname, user, member, player_parms, description):
        await self.channel.send(
            view=RoleButton(nickname=nickname, user=user),
            embed=application_embed(description, nickname, member, player_parms=player_parms)
        )
        app_list.append(nickname)
        await self.respond_with_message(interaction, '👍\n_Твой запрос принят! Дождись выдачи роли_', 5)
        logger.info(
            f'Пользователь {interaction.user.display_name} заполнил форму, '
            f'она была отправлена в канал "{self.channel}"'
        )


class ApplicationButton(View):
    """
    Класс кнопки роли для взаимодействия с пользователем в Discord.
    Вызывает модальное окно для заполнения формы.
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
            await interaction.response.send_modal(RoleApplication(channel=self.channel))
        except Exception as error:
            await interaction.respond('❌', ephemeral=True, delete_after=1)
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
        description='ID сообщения, в котором есть кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    ),  # type: ignore
) -> None:
    """
    Команда для вызова кнопки, которая обрабатывает запросы на доступ.
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
        await ctx.respond('❌', ephemeral=True, delete_after=1)
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
