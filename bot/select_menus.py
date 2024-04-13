import discord

from discord.ext import commands
from discord.ui import Modal, InputText, View, button



class RoleButton(View):

    def __init__(self, user, channel: discord.TextChannel, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.user = user
        self.channel = channel

    @button(label='Выдать старшину', style=discord.ButtonStyle.green)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, id=1222655185055252581)
        self.disable_all_items()
        await self.user.add_roles(role)
        await interaction.response.edit_message(
            view=self
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
        nickname = self.children[0].value
        embed = discord.Embed(
            title=f'Заявка на доступ',
            description='Думаю над текстом',
            color=0x6e00ff
        )
        embed.set_author(name=member.display_name, icon_url='https://avatars.mds.yandex.net/i?id=25468a149adb4b493e2ec75c6dfc0f6a7b318532-7664914-images-thumbs&n=13')
        embed.add_field(name='Текущий класс', value='Здесь будет отображаться спарсеный класс', inline=True),
        embed.add_field(name='Текущий ГС', value='Здесь будет отображаться спарсеный ГС', inline=True),
        embed.add_field(name='Текущий уровень наследия богов', value='Здесь будет отображаться лвл НБ', inline=True),
        embed.set_thumbnail(url=member.avatar)
        await interaction.respond(
            '_Твой запрос принят! Дождись выдачи роли_',
            ephemeral=True
        )
        await user.edit(nick=nickname)
        await self.channel.send(
            view=RoleButton(user=user, channel=self.channel),
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


def setup(bot: discord.Bot):
    bot.add_application_command(role_application)
