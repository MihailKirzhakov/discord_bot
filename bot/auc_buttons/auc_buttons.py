from decimal import Decimal

import discord
import random
from discord.ext import commands
from discord.ui import View, Button
from loguru import logger

from .embeds import start_auc_embed, results_embed
from .functions import (
    convert_bid,
    label_count,
    convert_to_mention,
    convert_sorted_message
)
from variables import (
    ANSWERS_IF_NO_ROLE,
    MAX_BUTTON_VALUE, MIN_BID_VALUE, NOT_SOLD
)


button_mentions = dict()


@commands.slash_command()
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
    ),  # type: ignore
    stop_time_str: discord.Option(
        str,
        description='Укажи дату и время окончания аука',
        name_localizations={'ru': 'дата_время'}
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
    start_auc_user = ctx.user
    button_manager = View(timeout=None)
    for _ in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_bid(start_bid)),
            style=discord.ButtonStyle.green
        )
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(auc_button, button_manager, bid, start_auc_user)
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(button_manager, count)
    try:
        await ctx.respond(
            embed=start_auc_embed(
                user_mention=ctx.user.mention,
                name_auc=name,
                stop_time_str=stop_time_str,
                lot_count=count,
                first_bid=convert_bid(start_bid),
                next_bid=convert_bid(bid)
            ),
            view=button_manager
        )
        logger.info(
            f'Команда /go_auc запущена пользователем "{ctx.user.display_name}"'
        )
    except Exception as error:
        logger.error(
            f'При попытке запустить аукцион командой /go_auc '
            f'возникло исключение "{error}"'
        )


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


def bid_callback(
        button: discord.ui.Button,
        view: discord.ui.View,
        bid: int,
        start_auc_user: discord.ApplicationContext.user
):
    """
    Функция для обработки нажатия на кнопку ставки

    :param button: Объект класса discord.ui.Button
    :param view: Объект класса discord.ui.View
    :param bid: Шаг ставки
    :param start_auc_user: Пользователь, начавший аукцион discord.ApplicationContext.user
    :return: inner() функция
    """
    async def inner(interaction: discord.Interaction):
        """
        Внутренняя функция, помощник

        :param interaction: Объект класса discord.Interaction
        :return: None
        """
        reserve_view = view
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        mention = interaction.user.mention
        original_label = Decimal(button.label.split()[0][:-1])
        try:
            label_count(button, original_label, name, bid)
            logger.debug(
                f'Кнопка изменилась, функция "label_count" отработала, '
                f'результат "{button.label}"'
            )
            button_mentions[name] = mention
            if len(view.children) == 0:
                await interaction.response.edit_message(view=reserve_view)
                await interaction.followup.send(
                    'В момент обработки, сделанной ставки возникла ошибка!'
                    'Бот не сломался, попробуй сделать ставку снова. Если '
                    'данное сообщение появляется снова, обратись к '
                    'СтопарьВоды, для скорейшего решения проблемы!',
                    ephemeral=True,
                    delete_after=10
                )
                await start_auc_user.send(
                    f'Сигнал об ошибке во время аукциона! '
                    f'При попытке пользователя "{interaction.user.display_name}" '
                    f'сделать ставку, произошла неизвестная ошибка! '
                    f'Отработала резервная view.'
                )
                logger.error(
                    f'При попытке сделать ставку пользователем '
                    f'"{interaction.user.mention}" возникла неизвестная ошибка, '
                    f'которая сносит кнопки. Во "view" сложили резервную копию.'
                )
            else:
                await interaction.response.edit_message(view=view)
        except Exception as error:
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )
    return inner


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
            try:
                await interaction.response.edit_message(view=view)
                await interaction.followup.send(
                    embed=results_embed(message)
                )
                logger.info(
                    f'Аукцион успешно завершён пользователем "{interaction.user.display_name}"'
                )
            except Exception as error:
                logger.error(
                    f'При завершении аукциона пользователем '
                    f'"{interaction.user.display_name}" возникла ошибка '
                    f'"{error}"'
                )
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{ANSWERS_IF_NO_ROLE[str(random_amount)]}',
                ephemeral=True,
                delete_after=10
            )
    return inner


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
