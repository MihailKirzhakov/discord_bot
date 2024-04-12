import discord

from discord.ext import commands
from discord.ui import Modal, InputText, View, Button, button


class ApplicationButton(View):

    @button(label='Заполни форму', style=discord.ButtonStyle.green, emoji='📋')
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleApplication())


class RoleButton(View):

    @button(label='Выдать старшину', style=discord.ButtonStyle.green)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        await interaction.response

# def access_button(user):
#     button_manager = View(timeout=None)
#     button: discord.ui.Button = Button(
#         label='Выдать старшину',
#         style=discord.ButtonStyle.green
#     )

#     async def button_callback(interaction: discord.Interaction):
#         guild = interaction.guild
#         role = guild.get_role(1227886432002117734)
#         await user.add_roles(role)
#     button.callback = button_callback
#     button_manager.add_item(button)



class RoleApplication(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Заявка на выдачу роли')

        self.add_item(
            InputText(
                label='Укажи свой игровой ник без пробелов',
                placeholder='Учитывай регистр (большие и маленькие буквы)'
            )
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        nickname = self.children[0].value
        await interaction.respond(
            'Твой запрос принят! Дождись выдачи роли',
            empheral=True
        )
        await interaction.respond(
            f'Принял запрос!\n'
            f'{user.mention} просит выдать роль\n'
            f'Игровой ник: {nickname}'
        )


@commands.slash_command()
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def role_application(ctx: discord.ApplicationContext):
    await ctx.respond(
        'Привет!\n Заполни форму для получения доступа',
        view=ApplicationButton()
    )


def setup(bot: discord.Bot):
    bot.add_application_command(role_application)
