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
    ),  # type: ignore
    bid: discord.Option(
        int,
        description='Укажи шаг ставки',
        name_localizations={'ru': 'шаг_ставки'}
    )  # type: ignore
):
    """Команда создания аукциона"""
    convert_start_bid = (
        f'{Decimal(start_bid) / Decimal('1000')}K' if 100000 <= start_bid
        <= 900000 else f'{Decimal(start_bid) / Decimal('1000000')}M'
    )
    button_manager = View(timeout=None)
    for _ in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_start_bid),
            style=discord.ButtonStyle.green
        )
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(auc_button, button_manager, bid)
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(button_manager, count)
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


def bid_callback(button: discord.ui.Button, view: discord.ui.View, bid_step: int):
    async def inner(interaction: discord.Interaction):
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        original_label = Decimal(button.label.split()[0][:-1])
        if len(button.label.split()) == 1:
            if 'K' in button.label:
                button.label = f'{original_label}K {name}'
            else:
                button.label = f'{original_label}M {name}'
        else:    
            if 'K' in button.label:
                if original_label < 900:
                    button.label = f'{original_label + (Decimal(bid_step) / Decimal('1000'))}K {name}'
                else:
                    button.label = f'{(original_label + (Decimal(bid_step) / Decimal('1000'))) / Decimal('1000')}M {name}'
            else:
                button.label = f'{original_label + (Decimal(bid_step) / Decimal('1000000'))}M {name}'
        await interaction.response.edit_message(view=view)
    return inner


def stop_callback(view: discord.ui.View, amount):
    async def inner(interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, name='Аукционер'):
            view.disable_all_items()
            label_values = [btn.label for btn in view.children[:amount]]
            label_values.sort()
            message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(label_values)])
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(content=message)
        else:
            answer = random.randint(1, 3)
            await interaction.response.send_message(
                f'{interaction.user.mention} {os.getenv(str(answer))}'
            )
            return inner
    return inner


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
