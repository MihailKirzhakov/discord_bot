import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable

import discord
import random
from discord.ext import commands
from discord.ui import View, Button
from loguru import logger

from .embeds import start_auc_embed, results_embed, outbid_embed
from .functions import (
    convert_bid,
    label_count,
    convert_to_mention,
    convert_sorted_message,
    seconds_until_date
)
from variables import (
    ANSWERS_IF_NO_ROLE,
    MAX_BUTTON_VALUE, MIN_BID_VALUE, NOT_SOLD
)


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
        description='Укажи дату и время в формате ДД.ММ ЧЧ:ММ:СС',
        name_localizations={'ru': 'дата_время'}
    )  # type: ignore
) -> None:
    """
    Команда для запуска аукциона.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        name_auc: str
            Название лотов.

        count: int
            Количество лотов.

        start_bid: int
            Начальная ставка.

        bid: int
            Шаг ставки.

        target_date_time: str
            Дата и время окончания аукциона. Формат "ДД-ММ ЧЧ:ММ:СС".

    Returns:
    --------
        None.
    """
    button_mentions: dict[
        discord.abc.User.display_name, discord.abc.User.mention
    ] = {}
    final_time: dict[str, datetime] = {}
    today: datetime = datetime.now()
    stop_time: datetime = today + timedelta(
        seconds=seconds_until_date(target_date_time)
    )
    final_time['stop_time'] = stop_time
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
            final_time=final_time,
            button_mentions=button_mentions
        )
    stop_button:  discord.ui.Button = Button(
        label='Завершить аукцион', style=discord.ButtonStyle.red
    )
    button_manager.add_item(stop_button)
    stop_button.callback = stop_callback(
        ctx=ctx,
        view=button_manager,
        user_mention=user_mention,
        name_auc=name_auc,
        count=count,
        final_time=final_time,
        button_mentions=button_mentions
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
        await discord.utils.sleep_until(stop_time - timedelta(seconds=60))
        if final_time['stop_time']:
            await check_timer(
                ctx=ctx,
                view=button_manager,
                user_mention=user_mention,
                name_auc=name_auc,
                count=count,
                final_time=final_time,
                button_mentions=button_mentions
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
async def go_auc_error(
    ctx: discord.ApplicationContext, error: Exception
) -> None:
    """
    Обработчик ошибок для команды go_auc.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: error
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None.
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


async def check_timer(
    ctx: discord.ApplicationContext,
    view: discord.ui.View,
    user_mention: discord.abc.User.mention,
    name_auc: str,
    count: int,
    final_time: dict,
    button_mentions: dict
) -> None:
    """
    Функция для полинга таймера, которая автоматически завершает аукцион.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        view: discord.ui.View
            Объект класса View.

        user_mention: discord.abc.User.mention
            Тэг юзера.

        name_auc: str
            Название аукциона.

        count: int
            Количество лотов.

        final_time: dict
            Словарь с временем завершения аукциона.

        button_mentions: dict
            Словарь с тэгами юзеров в кнопках.

    Returns:
    --------
        None.
    """
    while True:
        if not final_time['stop_time']:
            break
        if final_time['stop_time'] > datetime.now():
            await asyncio.sleep(0.5)
        else:
            await auto_stop_auc(
                ctx=ctx,
                view=view,
                user_mention=user_mention,
                name_auc=name_auc,
                count=count,
                button_mentions=button_mentions
            )
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
        final_time: dict,
        button_mentions: dict
) -> Callable:
    """
    Функция для обработки нажатия на кнопку ставки.

    Parametrs:
    ----------
        button: discord.ui.Button
            Кнопка.

        view: discord.ui.View
            Объект класса View.

        bid: int
            Шаг ставки.

        start_auc_user: discord.ApplicationContext.user
            Никнейм пользователя, начавшего аукцион.

        stop_time: datetime
            Время завершения аукциона.

        user_mention: discord.abc.User.mention
            Тэг юзера.

        count: int
            Количество лотов.

        name_auc: str
            Название аукциона.

        final_time: dict
            Словарь с временем завершения аукциона.

        button_mentions: dict
            Словарь с тэгами юзеров в кнопках.

    Returns:
    --------
        inner: Callable
            Вспомогательная функция inner().
    """
    async def inner(interaction: discord.Interaction):
        nowtime: datetime = datetime.now()
        secondstime: timedelta = timedelta(seconds=60)
        plus_minute: datetime = nowtime + secondstime
        reserve_view: discord.ui.View = view
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        mention = interaction.user.mention
        original_label: Decimal = Decimal(button.label.split()[0][:-1])
        befor_button_label = button.label
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
                if (stop_time - nowtime) < secondstime:
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
                    final_time['stop_time'] = plus_minute
                else:
                    await interaction.response.edit_message(view=view)
                if 'K' != befor_button_label[-1] and 'M' != befor_button_label[-1] and interaction.user.display_name not in befor_button_label:
                    time_of_bid = None
                    url = interaction.message.jump_url
                    take_nick = befor_button_label.split()
                    member = discord.utils.get(interaction.guild.members, nick=take_nick[1])
                    if (datetime.now() + timedelta(seconds=60)) > final_time['stop_time'] > datetime.now():
                        time_of_bid = plus_minute
                    else:
                        time_of_bid = stop_time
                    await member.send(
                        embed=outbid_embed(url=url, stop_time=time_of_bid),
                        delete_after=3600
                    )
        except Exception as error:
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )
    return inner


def stop_callback(
    ctx: discord.ApplicationContext,
    view: discord.ui.View,
    user_mention: discord.abc.User.mention,
    name_auc: str,
    count: int,
    button_mentions: dict,
    final_time: dict
) -> Callable:
    """
    Функция для обработки нажатия на кнопку завершения аукциона.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        view: discord.ui.View
            Объект класса View.

        user_mention: discord.abc.User.mention
            Тэг юзера.

        name_auc: str
            Название аукциона.

        count: int
            Количество лотов.

        button_mentions: dict
            Словарь с тэгами юзеров в кнопках.

        final_time: dict
            Словарь с временем завершения аукциона.

    Returns:
    --------
        inner: Callable
            Вспомогательная функция inner().
    """
    async def inner(interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, name='Аукцион'):
            final_time['stop_time'] = False
            await auto_stop_auc(
                ctx=ctx,
                view=view,
                user_mention=user_mention,
                name_auc=name_auc,
                count=count,
                button_mentions=button_mentions
            )
            logger.info(
                f'Пользователь {interaction.user.display_name} '
                f'досрочно завершил аукцион!'
            )
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
        count: int,
        button_mentions: dict
) -> None:
    """
    Функция для автозавершения аукциона.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды

        view: discord.ui.View
            Объект класса View

        user_mention: discord.abc.User.mention
            Тэг юзера

        name_auc: str
            Название аукциона

        count: int
            Количество лотов

    Returns:
    --------
        None.
    """
    view.disable_all_items()
    label_values = [btn.label for btn in view.children[:count]]
    convert_label_values = convert_to_mention(
        label_values, button_mentions
    )
    count_not_bid = convert_label_values.count(NOT_SOLD)
    removed_not_bid: list = []
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
            'Аукцион успешно завершён!'
        )
    except Exception as error:
        logger.error(
            f'При автоматическом завершении аукциона возникла ошибка '
            f'"{error}"'
        )


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
