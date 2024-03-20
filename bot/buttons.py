import discord
from discord.ext import commands
from discord.ui import View, Button
from discord.ui.item import Item


@commands.slash_command()
async def go_auc(ctx: discord.ApplicationContext, count: int):
    button_manager = View()
    for i in range(count):
        auc_button: discord.ui.Button = Button(label='300')
        button_manager.add_item(auc_button)
        auc_button.callback = button_callback(auc_button, button_manager)
    await ctx.respond(view=button_manager)


def button_callback(button: discord.ui.Button, view):
    async def inner(interaction: discord.Interaction):
        button.label = interaction.user.display_name
        await interaction.response.edit_message(view=view)
    return inner

    

def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
