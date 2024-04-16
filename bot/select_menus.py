import discord
import random

from discord.ext import commands
from discord.ui import Modal, InputText, View, button

from answers import answers_for_application
from constants import ANSWER_IF_CHEAT
from functions import character_lookup


class RoleButton(View):

    def __init__(
            self,
            user: discord.Interaction.user,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)
        self.user = user
        self.channel = channel

    @button(label='Выдать старшину', style=discord.ButtonStyle.green)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, name='📣Казначей📣') or
            discord.utils.get(interaction.user.roles, name='🛡️Офицер🛡️')
        ):
            role_sergeant = discord.utils.get(interaction.guild.roles, id=1182428098256457819)
            role_guest = discord.utils.get(interaction.guild.roles, id=1173570849467551744)
            self.disable_all_items()
            await self.user.add_roles(role_sergeant)
            await self.user.remove_roles(role_guest)
            await interaction.response.edit_message(
                view=self
            )
            await interaction.respond(
                f'{interaction.user.mention} __выдал__ '
                f'роль игроку __{self.user.display_name}__!'
            )
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{answers_for_application[str(random_amount)]}',
                ephemeral=True
            )


class DeniedRoleModal(Modal):
    def __init__(self, nickname: str, user, view: discord.ui.Button,  *args, **kwargs):
        super().__init__(*args, **kwargs, title='Комментарий к отказу')
        self.nickname = nickname
        self.user = user
        self.view = view

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
        comments = (
            f'_**Приветствую!**_\n'
            f'_Офицер гильдии "Айронболз" {user.display_name} не согласовал приём в гильдию_!\n'

        )
        if len(self.children[0].value) > 0:
            comments += (
                f'_Комментарии:\n{self.children[0].value}_'
            )
        await self.user.send(comments)
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(
            f'{interaction.user.mention} __отказал__ '
            f'в доступе игроку __{self.nickname}__!'
        )


class DeniedButton(RoleButton):

    def __init__(
            self,
            nickname: str,
            user: discord.Interaction.user,
            channel: discord.TextChannel,
            timeout: float | None = None
    ):
        super().__init__(user=user, channel=channel, timeout=timeout)
        self.nickname = nickname


    @button(label='Отправить в ЛС, что не подходит', style=discord.ButtonStyle.red)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, name='📣Казначей📣') or
            discord.utils.get(interaction.user.roles, name='🛡️Офицер🛡️')
        ):
            self.disable_all_items()
            await interaction.response.send_modal(DeniedRoleModal(
                nickname=self.nickname, view=self, user=self.user
            ))
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{answers_for_application[str(random_amount)]}',
                ephemeral=True
            )


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
        player_parms = character_lookup(1, nickname)
        if not player_parms:
            await interaction.respond(
                ANSWER_IF_CHEAT,
                ephemeral=True
            )
            return None

        description = f'Гильдия: {player_parms['guild']}'

        if 'dragon_emblem' in player_parms:
            description += f'\nДраконий амулет: {player_parms['dragon_emblem']['name']}'

        embed = discord.Embed(
            title='Заявка на доступ',
            description=description,
            color=0x6e00ff
        )
        embed.set_author(name=nickname, icon_url=member.avatar)
        embed.add_field(name='Гирскор', value=player_parms['gear_score'], inline=True)
        art_lvl = 'Нет'
        if 'artifact' in player_parms:
            art_lvl = player_parms['artifact']['level']
        embed.add_field(name='Уровень НБ', value=art_lvl, inline=True)
        embed.set_thumbnail(url=player_parms['class_icon'])
        if 'emblem' in player_parms:
            embed.set_image(url=player_parms['emblem']['image_url'])
        await interaction.respond(
            '_Твой запрос принят! Дождись выдачи роли_',
            ephemeral=True
        )
        await user.edit(nick=nickname)
        await self.channel.send(
            view=DeniedButton(nickname=nickname, user=user, channel=self.channel),
            embed=embed
        )


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
        await ctx.respond('Команду может вызвать только "Казначей" или "Офицер"!', ephemeral=True)
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!', ephemeral=True)
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(role_application)
