import asyncio
from datetime import datetime, timedelta
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
    convert_sorted_message,
    minutes_until_date
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
    name_auc: discord.Option(
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
    target_date_time: discord.Option(
        str,
        description='Укажи дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ',
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
    :param stop_time_str: Дата и время окончания аукциона. Формат "2022-07-25 14:30:00"
    :return: None
    """
    final_time: list = []
    today = datetime.now()
    stop_time = today + timedelta(minutes=minutes_until_date(target_date_time))
    final_time.append(stop_time)
    start_auc_user = ctx.user
    user_mention = ctx.user.mention
    button_manager = View(timeout=None)
    for _ in range(count):
        auc_button: discord.ui.Button = Button(
            label=str(convert_bid(start_bid)),
            style=discord.ButtonStyle.green
        )
        button_manager.add_item(auc_button)
        auc_button.callback = bid_callback(
            button=auc_button,
            view=button_manager,
            start_bid=start_bid,
            bid=bid,
            start_auc_user=start_auc_user,
            stop_time=stop_time,
            user_mention=user_mention,
            count=count,
            name_auc=name_auc,
            final_time=final_time
        )
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(
        final_time=final_time
    )
    try:
        await ctx.respond(
            embed=start_auc_embed(
                user_mention=user_mention,
                name_auc=name_auc,
                stop_time=stop_time,
                lot_count=count,
                first_bid=convert_bid(start_bid),
                next_bid=convert_bid(bid)
            ),
            view=button_manager
        )
        logger.info(
            f'Команда /go_auc запущена пользователем "{ctx.user.display_name}"'
        )
        await check_timer(
            ctx=ctx,
            view=button_manager,
            user_mention=user_mention,
            name_auc=name_auc,
            count=count,
            final_time=final_time
        )
    except Exception as error:
        await ctx.respond(
            f'Не вышло, вот ошибка: {error}',
            ephemeral=True
        )
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


async def check_timer(ctx, view, user_mention, name_auc, count, final_time):
    while True:
        if final_time[0] > datetime.now():
            await asyncio.sleep(1)
        else:
            await auto_stop_auc(ctx, view, user_mention, name_auc, count)
            break


def bid_callback(
        button: discord.ui.Button,
        view: discord.ui.View,
        start_bid: int,
        bid: int,
        start_auc_user: discord.ApplicationContext.user,
        stop_time: datetime,
        user_mention: discord.abc.User.mention,
        count: int,
        name_auc: str,
        final_time: list,
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
        nowtime = datetime.now()
        minutetime = timedelta(minutes=1)
        plus_minute = nowtime + minutetime
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
                if (stop_time - nowtime) < minutetime:
                    await interaction.response.edit_message(
                        view=view,
                        embed=start_auc_embed(
                            user_mention=user_mention,
                            name_auc=name_auc,
                            stop_time=plus_minute,
                            lot_count=count,
                            first_bid=convert_bid(start_bid),
                            next_bid=convert_bid(bid)
                        )
                    )
                    final_time[0] = plus_minute
                else:
                    await interaction.response.edit_message(view=view)
        except Exception as error:
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )
    return inner


def stop_callback(
        final_time: list
):
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
            final_time[0] = datetime.now()
        else:
            random_amount = random.randint(1, 3)
            await interaction.response.send_message(
                f'{ANSWERS_IF_NO_ROLE[str(random_amount)]}',
                ephemeral=True,
                delete_after=10
            )
    return inner


async def auto_stop_auc(
        ctx: discord.ApplicationContext,
        view: discord.ui.View,
        user_mention: discord.abc.User.mention,
        name_auc: str,
        count: int
):
    """
    Внутренняя функция, помощник

    :param interaction: Объект класса discord.Interaction
    :return: None
    """
    view.disable_all_items()
    label_values = [btn.label for btn in view.children[:count]]
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
    view.clear_items()
    try:
        await ctx.edit(
            view=view,
            embed=results_embed(
                results_message=message,
                user_mention=user_mention,
                name_auc=name_auc,
                count=count
            )
        )
        logger.info(
            'Аукцион успешно завершён автоматически!'
        )
    except Exception as error:
        logger.error(
            f'При автоматическом завершении аукциона возникла ошибка '
            f'"{error}"'
        )


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
