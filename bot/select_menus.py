import discord
import random

from discord.ext import commands
from discord.ui import Modal, InputText, View, button

from answers import answers_for_application
from constants import (
    ANSWER_IF_CHEAT,
    ANSWER_IF_DUPLICATE_APP,
    ANSWER_IF_DUPLICATE_NAME,

)
from embeds.embeds import access_embed, denied_embed, application_embed
from functions import character_lookup


app_list: list = []


class RoleButton(View):

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
    async def callback_accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, name='📣Казначей📣') or
            discord.utils.get(interaction.user.roles, name='🛡️Офицер🛡️')
        ):
            role_sergeant = discord.utils.get(interaction.guild.roles, id=1182428098256457819)  # Старшина 1182428098256457819, Выдать 1222655185055252581
            role_guest = discord.utils.get(interaction.guild.roles, id=1173570849467551744)  # Гость 1173570849467551744, Убрать 1230178082346762240
            self.disable_all_items()
            self.embed.add_field(
                name='_Результат рассмотрения_ ✔',
                value=f'_{interaction.user.mention} выдал роль!_',
                inline=False
            )
            await self.user.add_roles(role_sergeant)
            await self.user.remove_roles(role_guest)
            await interaction.response.edit_message(
                embed=self.embed,
                view=self
            )
            await self.user.send(embed=access_embed())
            app_list.remove(self.nickname)
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{answers_for_application[str(random_amount)]}',
                ephemeral=True,
                delete_after=15
            )

    @button(label='Отправить в ЛС, что не подходит', style=discord.ButtonStyle.red)
    async def callback_denied(self, button: discord.ui.Button, interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, name='📣Казначей📣') or
            discord.utils.get(interaction.user.roles, name='🛡️Офицер🛡️')
        ):
            self.disable_all_items()
            await interaction.response.send_modal(DeniedRoleModal(
                nickname=self.nickname, view=self, user=self.user, embed=self.embed
            ))
            app_list.remove(self.nickname)
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{answers_for_application[str(random_amount)]}',
                ephemeral=True,
                delete_after=15
            )


class DeniedRoleModal(Modal):
    def __init__(self, nickname: str, user, view: discord.ui.Button, embed: discord.Embed,  *args, **kwargs):
        super().__init__(*args, **kwargs, title='Комментарий к отказу')
        self.nickname = nickname
        self.user = user
        self.view = view
        self.embed = embed
        self.add_item(
                InputText(
                    style=discord.InputTextStyle.multiline,
                    label='Почему решил отказать в заявке',
                    placeholder='Необязательно (если пусто, отправится дэфолт фраза)',
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
        await self.user.send(embed=denied_embed(user, value))
        await interaction.response.edit_message(embed=self.embed, view=self.view)


class RoleApplication(Modal):

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
        user = interaction.user
        member = discord.utils.get(interaction.guild.members, id=user.id)
        nickname: str = self.children[0].value
        display_names = [name.display_name for name in interaction.guild.members]
        global_names = [name.global_name for name in interaction.guild.members]
        player_parms = character_lookup(1, nickname)
        if not player_parms:
            return await interaction.respond(
                ANSWER_IF_CHEAT,
                ephemeral=True,
                delete_after=30
            )
        if nickname in display_names or nickname in global_names:
            return await interaction.respond(
                ANSWER_IF_DUPLICATE_NAME,
                ephemeral=True,
                delete_after=15
            )
        if nickname in app_list:
            return await interaction.respond(
                ANSWER_IF_DUPLICATE_APP,
                ephemeral=True,
                delete_after=15
            )

        description = (
            f'Профиль: {user.mention}\n'
            f'Гильдия: {player_parms['guild']}'
        )

        if 'dragon_emblem' in player_parms:
            description += f'\nДраконий амулет: {player_parms['dragon_emblem']['name']}'

        await interaction.respond(
            '_Твой запрос принят! Дождись выдачи роли_',
            ephemeral=True,
            delete_after=15
        )
        await user.edit(nick=nickname)
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

    def __init__(self, channel: discord.TextChannel, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.channel = channel

    @button(label='Заполни форму', style=discord.ButtonStyle.green, emoji='📋')
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleApplication(channel=self.channel))


@commands.slash_command()
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def role_application(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Выбери канал в который будут отправляться заявки',
        name_localizations={'ru': 'название_канала'}
    )  # type: ignore
):
    """Команда для вызова кнопки, которая обрабатывает запросы на доступ"""
    await ctx.respond(
        '_**Привет!\n Заполни форму для получения доступа**_',
        view=ApplicationButton(channel=channel)
    )


# Обработка ошибок и вывод сообщения
# о запрете вызова команды без указанной роли
@role_application.error
async def role_application_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond('Команду может вызвать только "Казначей" или "Офицер"!', ephemeral=True, delete_after=15)
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!', ephemeral=True, delete_after=15)
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(role_application)
