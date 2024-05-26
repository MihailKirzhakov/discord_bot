import discord
import random

from decimal import Decimal
from discord.ext import commands
from discord.ui import View, Button

from .embeds import attention_embed, results_embed
from .functions import (
    convert_bid,
    label_count,
    convert_to_mention,
    convert_sorted_message
)
from variables import (
    ANSWERS_IF_NO_ROLE, CATCH_BUG_MESSAGE,
    MAX_BUTTON_VALUE, MIN_BID_VALUE, NOT_SOLD
)

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
        max_value=MAX_BUTTON_VALUE,
        description='Сколько кнопок с лотами будет запущено',
        name_localizations={'ru': 'количество_лотов'}
    ),  # type: ignore
    start_bid: discord.Option(
        int,
        min_value=MIN_BID_VALUE,
        description='Укажи начальную ставку',
        name_localizations={'ru': 'начальная_ставка'}
    ),  # type: ignore
    bid: discord.Option(
        int,
        description='Укажи шаг ставки',
        name_localizations={'ru': 'шаг_ставки'}
    )  # type: ignore
):
    """
    Команда для запуска аукциона.

    :param ctx: Контекст команды
    :param name: Название лотов
    :param count: Количество лотов
    :param start_bid: Начальная ставка
    :param bid: Шаг ставки
    :return: None
    """
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
        embed=attention_embed(
            user_mention=ctx.user.mention,
            name_auc=name,
            lot_count=count,
            first_bid=convert_bid(start_bid),
            next_bid=convert_bid(bid)
        ),
        view=button_manager
    )


# Обработка ошибок и вывод сообщения
# о запрете вызова команды без указанной роли
@go_auc.error
async def go_auc_error(ctx: discord.ApplicationContext, error: Exception):
    """
    Обработчик ошибок для команды go_auc

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
    """
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond(
            'Команду может вызвать только Аукционер!',
            ephemeral=True,
            delete_after=10
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=10
        )
    else:
        raise error


def bid_callback(button: discord.ui.Button, view: discord.ui.View, bid: int):
    """
    Функция для обработки нажатия на кнопку ставки

    :param button: Объект класса discord.ui.Button
    :param view: Объект класса discord.ui.View
    :param bid: Шаг ставки
    :return: inner() функция
    """
    async def inner(interaction: discord.Interaction):
        """
        Внутренняя функция, помощник

        :param interaction: Объект класса discord.Interaction
        :return: None
        """
        try:
            button.style = discord.ButtonStyle.blurple
            name = interaction.user.display_name
            mention = interaction.user.mention
            original_label = Decimal(button.label.split()[0][:-1])
            label_count(button, original_label, name, bid)
            button_mentions[name] = mention
            await interaction.response.edit_message(view=view)
        except discord.errors.NotFound:
            await interaction.respond(
                '_Сильно не торопись тыкать на кнопку, бот чутка запыхался 😥_',
                ephemeral=True,
                delete_after=10
            )
    return inner


# Callback для обработки кнопки остановки аукциона
def stop_callback(view: discord.ui.View, amount):
    """
    Функция для обработки нажатия на кнопку завершения аукциона

    :param view: Объект класса discord.ui.View
    :param amount: Количество объектов внутри менеджера кнопок
    :return: inner() функция
    """
    async def inner(interaction: discord.Interaction):
        """
        Внутренняя функция, помощник

        :param interaction: Объект класса discord.Interaction
        :return: None
        """
        try:
            if discord.utils.get(interaction.user.roles, name='Аукцион'):
                view.disable_all_items()
                label_values = [btn.label for btn in view.children[:amount]]
                convert_label_values = convert_to_mention(
                    label_values, button_mentions
                )
                count_not_bid = convert_label_values.count(NOT_SOLD)
                removed_not_bid = []
                for i in convert_label_values:
                    if i != NOT_SOLD:
                        removed_not_bid.append(i)
                sorted_list = sorted(
                    removed_not_bid,
                    key=convert_sorted_message,
                    reverse=True
                )
                for _ in range(count_not_bid):
                    sorted_list.append(NOT_SOLD)
                message = (
                    '\n'.join([f'{i+1}. {val}' for i, val in enumerate(
                        sorted_list
                    )])
                )
                await interaction.response.edit_message(view=view)
                await interaction.followup.send(
                    embed=results_embed(message)
                )
            else:
                random_amount = random.randint(1, 3)
                await interaction.response.send_message(
                    f'{ANSWERS_IF_NO_ROLE[str(random_amount)]}',
                    ephemeral=True,
                    delete_after=10
                )
                return inner
        except discord.errors.NotFound:
            await interaction.respond(
                CATCH_BUG_MESSAGE,
                ephemeral=True,
                delete_after=10
            )
    return inner


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
