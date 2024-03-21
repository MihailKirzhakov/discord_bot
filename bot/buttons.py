import discord
import os
import random
from decimal import Decimal
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

load_dotenv()

@commands.slash_command()
@commands.has_role('Аукционер')
async def go_auc(
    ctx: discord.ApplicationContext,
    name: discord.Option(
        str,
        description='Что разыгрываем?',
        name_localizations={'ru': 'название_лотов'}
    ),  # type: ignore
    count: discord.Option(
        int,
        max_value=24,
        description='Сколько кнопок с лотами будет запущено',
        name_localizations={'ru': 'количество_лотов'}
    ),  # type: ignore
    start_bid: discord.Option(
        int,
        min_value=100000,
        description='Укажи начальную ставку',
        name_localizations={'ru': 'начальная_ставка'}
    )  # type: ignore
):
    """Команда создания аукциона"""
    convert_start_bid = (
        f'{Decimal(start_bid) / Decimal('1000')} K' if 100000 <= start_bid
        <= 900000 else f'{Decimal(start_bid) / Decimal('1000000')} M'
    )
    button_manager = View(timeout=None)
    for i in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_start_bid),
            style=discord.ButtonStyle.green
        )
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(auc_button, button_manager)
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(button_manager)
    await ctx.respond(f'{ctx.user.mention} начал аукцион {name}!')
    await ctx.send_followup(view=button_manager)


@go_auc.error
async def go_auc_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('Команду может вызвать только Аукционер!')
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!')
    else:
        raise error


def bid_callback(button: discord.ui.Button, view: discord.ui.View):
    async def inner(interaction: discord.Interaction):
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        original_label = button.label.split()
        current_label = Decimal(original_label[0])
        if Decimal('100') <= current_label < Decimal('900'):
            current_label += Decimal('100')
            button.label = f'{current_label} K {name}'
        elif current_label >= Decimal('900'):
            current_label += Decimal('100')
            current_label /= Decimal('1000')
            button.label = f'{round(current_label)} M {name}'
        else:
            current_label += Decimal('0.1')
            button.label = f'{current_label} M {name}'
        await interaction.response.edit_message(view=view)
    return inner


def stop_callback(view: discord.ui.View):
    async def inner(interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, name='Аукционер'):
            view.disable_all_items()
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(content='Аукцион был остановлен.')
        else:
            answer = random.randint(1, 3)
            await interaction.response.send_message(
                f'{interaction.user.mention} {os.getenv(str(answer))}'
            )
            return inner
    return inner


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
