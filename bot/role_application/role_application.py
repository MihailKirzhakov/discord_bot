import discord

from discord.ext import commands
from discord.ui import Modal, InputText, View, button

from variables import (
    ANSWER_IF_DUPLICATE_APP,
    ANSWER_IF_DUPLICATE_NICK,
    ANSWER_IF_CHEAT,
    ANSWER_IF_CLICKED_THE_SAME_TIME,
    CATCH_BUG_MESSAGE,
    LEADER_ROLE,
    OFICER_ROLE,
    TREASURER_ROLE
)
from .embeds import (
    access_embed, denied_embed, application_embed, start_app_embed
)
from .functions import character_lookup, has_required_role, answer_if_no_role


app_list: list = []


class RoleButton(View):
    """Класс кнопки роли для взаимодействия с пользователем в Discord.
    Создаёт 2 кнопки. Первая для выдачи роли,
    вторая для отказа в выдаче роли 'Старшина'

    Attributes:
        nickname: Discord - псевдоним пользователя.
        embed: Embed объект, связанный с взаимодействием с пользователем.
        user: User объект из discord.Interaction.
    """

    def __init__(
            self,
            nickname: str,
            embed: discord.Embed,
            user: discord.Interaction.user,
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
            interaction.guild.roles, name='Старшина'
        )
        role_guest = discord.utils.get(
            interaction.guild.roles, name='Гость'
        )

        # try для попытки отловить пока непонятную для меня ошибку
        try:
            # Защита от одновременного нажатия
            # на кнопку 2-мя и более пользователями
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
                # Сперва была задумка просто disablить кнопки и выводить их,
                # но потом решил сделать так,
                # чтобы кнопки убирались после выдачи роли
                self.disable_all_items()
                self.clear_items()
                await interaction.response.edit_message(
                    embed=self.embed,
                    view=self
                )
                await self.user.send(embed=access_embed())
                app_list.remove(self.nickname)
        # та самая ошибка, появлялась неожиданно и редко (причина не ясна)
        except discord.errors.NotFound:
            await interaction.respond(
                CATCH_BUG_MESSAGE,
                ephemeral=True,
                delete_after=10
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
        try:
            await interaction.response.send_modal(DeniedRoleModal(
                nickname=self.nickname,
                view=self,
                user=self.user,
                embed=self.embed
            ))
        except discord.errors.NotFound:
            await interaction.respond(
                CATCH_BUG_MESSAGE,
                ephemeral=True,
                delete_after=10
            )


class DeniedRoleModal(Modal):
    """Класс модального окна для взаимодействия с пользователем в Discord.
    В данном случае, модальное окно используется для отказа в выдаче роли 'Старшина'.

    Attributes:
        nickname: Discord нинкнейм пользователя.
        user: User объект из discord.Interaction.
        view: View объект из discord.ui.Button.
        embed: Embed объект, связанный с взаимодействием с пользователем.
    """

    def __init__(
        self,
        nickname: str,
        user: discord.Interaction.user,
        view: discord.ui.Button,
        embed: discord.Embed,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs, title='Комментарий к отказу')
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
            app_list.remove(self.nickname)
            await self.user.send(embed=denied_embed(user, value))
            self.view.disable_all_items()
            self.view.clear_items()
            await interaction.response.edit_message(embed=self.embed, view=self.view)


class RoleApplication(Modal):
    """Класс модального окна для взаимодействия с пользователем в Discord.
    Используется для создания модального окна с полем для ввода никнейма.

    Attributes:
        channel: Объект discord.TextChannel.
    """

    def __init__(self, channel: discord.TextChannel, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Заявка на выдачу роли')
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
        role = discord.utils.get(interaction.guild.roles, name='Гость')
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

        await interaction.respond(
            '👍\n_Твой запрос принят! Дождись выдачи роли_',
            ephemeral=True,
            delete_after=10
        )
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


class ApplicationButton(View):
    """Класс кнопки роли для взаимодействия с пользователем в Discord.
    Создаёт 2 кнопки. Первая для выдачи роли,
    вторая для отказа в выдаче роли 'Старшина'

    Attributes:
        channel: Объект discord.TextChannel.
    """

    def __init__(
            self,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(label='Заполни форму', style=discord.ButtonStyle.green, emoji='📋')
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.response.send_modal(RoleApplication(
            channel=self.channel
        ))


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, TREASURER_ROLE, OFICER_ROLE)
async def role_application(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Выбери канал в который будут отправляться заявки',
        name_localizations={'ru': 'название_канала'}
    )  # type: ignore
):
    """Команда для вызова кнопки, которая обрабатывает запросы на доступ.

    Args:
        ctx: Контекст из discord.ApplicationContext.
        channel: Объект discord.TextChannel.
    """
    await ctx.respond(
        embed=start_app_embed(),
        view=ApplicationButton(channel=channel)
    )


# Обработка ошибок и вывод сообщения
# о запрете вызова команды без указанной роли
@role_application.error
async def role_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    """Обрабатывать ошибки, возникающие
    при выполнении команды запросов на выдачу доступа.

    Args:
        ctx: Контекст из discord.ApplicationContext.
        error: Выбрасываемая ошибка.
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
