import discord
from discord.ext import commands
from discord.ui import View, Button
from discord.ui.item import Item


@commands.slash_command()
async def go_auc(ctx: discord.ApplicationContext, count: int):
    button_manager = View(timeout=None)
    for i in range(count):
        auc_button: discord.ui.Button = Button(label='300', style=discord.ButtonStyle.green)
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(auc_button, button_manager)
    stop_button:  discord.ui.Button = Button(label='Завершить аукцион', style=discord.ButtonStyle.red)
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(button_manager)
    await ctx.respond(view=button_manager)


def bid_callback(button: discord.ui.Button, view: discord.ui.View):
    async def inner(interaction: discord.Interaction):
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        thousand = 'K'
        million = 'M'
        original_label = button.label.split()
        current_label = float(original_label[0])
        if 300 <= current_label < 900:
            current_label += 100
            button.label = f'{int(current_label)} {thousand} {name}'
        elif current_label >= 900:
            current_label += 100
            current_label /= 1000
            button.label = f'{round(current_label)} {million} {name}'
        else:
            current_label += 0.1
            if current_label.is_integer():
                button.label = f'{round(current_label)} {million} {name}'
            else:
                button.label = f'{round(current_label, 1)} {million} {name}'
        await interaction.response.edit_message(view=view)
    return inner


def stop_callback(view: discord.ui.View):
    async def inner(interaction: discord.Interaction):
        # if interaction.guild_id
        view.disable_all_items()
        await interaction.response.edit_message(view=view)
    return inner
    

def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
