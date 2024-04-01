import discord
import os
import random
from decimal import Decimal
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

load_dotenv()
button_mentions = dict()

@commands.slash_command()
# Проверка роли по названию
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
    # Конвертирование параметра начальной ставки в вид ("300K" или "1M")
    convert_start_bid = (
        f'{Decimal(start_bid) / Decimal('1000')}K' if 100000 <= start_bid
        <= 900000 else f'{Decimal(start_bid) / Decimal('1000000')}M'
    )
    convert_bid = (
        f'{Decimal(bid) / Decimal('1000')}K' if 100000 <= bid
        <= 900000 else f'{Decimal(bid) / Decimal('1000000')}M'
    )
    button_manager = View(timeout=None)
    # Создаём кнопки для каждго лота
    for _ in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_start_bid),
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
        f'Начальная ставка: {convert_start_bid}.\n'
        f'Шаг ставки: {convert_bid}.'
    )
    await ctx.send_followup(view=button_manager)


# Обработка ошибок и вывод сообщения о запрете вызова команды без указанной роли
@go_auc.error
async def go_auc_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('Команду может вызвать только Аукционер!')
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!')
    else:
        raise error


# Callback для обработки на нажатие кнопок с лотами
def bid_callback(button: discord.ui.Button, view: discord.ui.View, bid_step: int):
    async def inner(interaction: discord.Interaction):
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        mention = interaction.user.mention
        original_label = Decimal(button.label.split()[0][:-1])
        if len(button.label.split()) == 1:
            if 'K' in button.label:
                button.label = f'{original_label}K {name}'
            else:
                button.label = f'{original_label}M {name}'
        else:    
            if 'K' in button.label:
                if original_label < 900 and (original_label + (Decimal(bid_step) / Decimal('1000'))) < 1000:
                    button.label = f'{original_label + (Decimal(bid_step) / Decimal('1000'))}K {name}'
                else:
                    button.label = f'{(original_label + (Decimal(bid_step) / Decimal('1000'))) / Decimal('1000')}M {name}'
            else:
                button.label = f'{original_label + (Decimal(bid_step) / Decimal('1000000'))}M {name}'
        button_mentions[name] = mention
        await interaction.response.edit_message(view=view)
    return inner


# Callback для обработки кнопки остановки аукциона
def stop_callback(view: discord.ui.View, amount):
    async def inner(interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, name='Аукционер'):
            view.disable_all_items()
            label_values = [btn.label for btn in view.children[:amount]]
            def convert_to_mention(values):
                result = []
                for value in values:
                    split_value = value.split()
                    if len(split_value) > 1:
                        split_value[-1] = button_mentions[split_value[-1]]
                        result.append(' '.join(split_value))
                    else:
                        result.append('Лот не был выкуплен')
                return result
            convert_label_values = convert_to_mention(label_values)
            sorted_values = sorted(convert_label_values, reverse=False)
            result = []
            check = 0
            for i in range(0, len(sorted_values)):
                if 'M' in sorted_values[i]:
                    result.insert(0, sorted_values[i])
                    check += 1
                elif 'K' in sorted_values[i]:
                    result.insert(check, sorted_values[i])
                else:
                    result.append(sorted_values[i])
            message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(result)])
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
