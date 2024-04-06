import discord
import os
import random
from decimal import Decimal
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
from answers import answers
from functions import (
    convert_bid,
    label_count,
    convert_to_mention,
    convert_sorted_message
)

load_dotenv()
button_mentions = dict()

@commands.slash_command()
# Проверка роли по названию
@commands.has_role('Аукцион')
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
    button_manager = View(timeout=None)
    # Создаём кнопки для каждго лота
    for _ in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_bid(start_bid)),
            style=discord.ButtonStyle.green
        )
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(auc_button, button_manager, bid)
    # Создаём кнопку для завершения аукциона
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(button_manager, count)
    await ctx.respond(
        f'{ctx.user.mention} начал аукцион "{name}"!\n'
        f'Количество лотов: {count}.\n'
        f'Начальная ставка: {convert_bid(start_bid)}.\n'
        f'Шаг ставки: {convert_bid(bid)}.'
    )
    await ctx.send_followup(view=button_manager)


# Обработка ошибок и вывод сообщения
# о запрете вызова команды без указанной роли
@go_auc.error
async def go_auc_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('Команду может вызвать только Аукционер!')
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!')
    else:
        raise error


# Callback для обработки на нажатие кнопок с лотами
def bid_callback(button: discord.ui.Button, view: discord.ui.View, bid: int):
    async def inner(interaction: discord.Interaction):
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        mention = interaction.user.mention
        original_label = Decimal(button.label.split()[0][:-1])
        label_count(button, original_label, name, bid)
        button_mentions[name] = mention
        await interaction.response.edit_message(view=view)
    return inner


# Callback для обработки кнопки остановки аукциона
def stop_callback(view: discord.ui.View, amount):
    async def inner(interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, name='Аукцион'):
            view.disable_all_items()
            label_values = [btn.label for btn in view.children[:amount]]
            convert_label_values = convert_to_mention(label_values, button_mentions)
            sorted_values = sorted(convert_label_values, reverse=False)
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(content=convert_sorted_message(sorted_values))
        else:
            random_amount = random.randint(1, 4)
            await interaction.response.send_message(
                f'{interaction.user.mention} {answers[str(random_amount)]}'
            )
            return inner
    return inner


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
