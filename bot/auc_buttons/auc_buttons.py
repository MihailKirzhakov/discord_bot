import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable

import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, InputText
from loguru import logger

from .embeds import (
    start_auc_embed, results_embed, outbid_embed,
    end_auc_notification_embed
)
from .functions import (
    convert_bid,
    label_count,
    convert_to_mention,
    convert_sorted_message,
    seconds_until_date
)
from variables import (
    MAX_BUTTON_VALUE, MIN_BID_VALUE, NOT_SOLD, LEADER_NICKNAME
)


final_time: dict[str, datetime] = {}
channel_last_message: dict[str, discord.Message] = {}


class StartAucModal(Modal):
    """
    Модальное окно для ввода данных для старта аукциона.

    Parametrs:
    ----------
        channel: discord.TextChannel
            Текстовый канал, в который отправляется запрос.

    Returns:
    --------
        None
    """
    def __init__(
            self,
            channel: discord.TextChannel
    ):
        super().__init__(title='Параметры аукциона', timeout=None)
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи название аукциона',
                placeholder='название лотов для розыгрыша'
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи количество разыгрываемых лотов',
                placeholder='кол-во лотов может быть от 1 до 25',
                min_length=1,
                max_length=MAX_BUTTON_VALUE
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи начальную ставку',
                placeholder=f'минимальная ставка {MIN_BID_VALUE}',
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи шаг ставки',
                placeholder='рекомендовано по дефолту 100000'
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи дату и время в формате ДД.ММ ЧЧ:ММ',
                placeholder='ДД.ММ ЧЧ:ММ',
                max_length=11
            )
        )

    async def callback(self, interaction: discord.Interaction):
        name_auc: str = str(self.children[0].value)
        count: int = int(self.children[1].value)
        start_bid: int = int(self.children[2].value)
        bid: int = int(self.children[3].value)
        target_date_time: str = str(self.children[4].value)
        if count < 1 or count > 25:
            return await interaction.respond(
                '_Количество лотов должно быть от 1 до 24_',
                ephemeral=True,
                delete_after=10
            )
        if final_time.get(name_auc) or channel_last_message.get(name_auc):
            name_auc += ' 😊'
        button_mentions: dict[str, str] = {}
        today: datetime = datetime.now()
        try:
            stop_time: datetime = today + timedelta(
                seconds=seconds_until_date(target_date_time)
            )
        except Exception as error:
            await interaction.respond(
                'Неверный формат. Ожидался ДД.ММ ЧЧ:ММ'
            )
            logger.error(
                f'При вводе даты в команду аукциона возникла ошибка {error}'
            )
        final_time[name_auc] = stop_time
        start_auc_user = interaction.user
        user_mention = interaction.user.mention
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
        try:
            await self.channel.send(
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
            channel_last_message[name_auc] = self.channel.last_message
            await interaction.respond(
                f'_Аукцион запущен в канале {self.channel.mention}_',
                ephemeral=True,
                delete_after=10
            )
            logger.info(
                f'Команда /go_auc запущена пользователем "{interaction.user.display_name}"'
            )
            await discord.utils.sleep_until(stop_time - timedelta(seconds=60))
            await self.channel.send(
                embed=end_auc_notification_embed(),
                delete_after=10
            )
            await check_timer(
                channel_last_message=channel_last_message.get(name_auc),
                view=button_manager,
                user_mention=user_mention,
                name_auc=name_auc,
                count=count,
                final_time=final_time,
                button_mentions=button_mentions
            )
        except Exception as error:
            await interaction.respond(
                f'Не вышло, вот ошибка: {error}',
                ephemeral=True
            )
            logger.error(
                f'При попытке запустить аукцион модальным окном '
                f'возникло исключение "{error}"'
            )


@commands.slash_command()
@commands.has_role('Аукцион')
async def go_auc(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Текстовый канал в котором будет аукцион',
        name_localizations={'ru': 'канал'}
    ),  # type: ignore
) -> None:
    """
    Команда для запуска аукциона.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        channel: discord.TextChannel
            Канал, в котором лежит сообщение для редактирования Embed'а

    Returns:
    --------
        None.
    """
    try:
        await ctx.response.send_modal(StartAucModal(channel=channel))
    except Exception as error:
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
    channel_last_message: discord.Message,
    view: discord.ui.View,
    user_mention: str,
    name_auc: str,
    count: int,
    final_time: dict,
    button_mentions: dict
) -> None:
    """
    Функция для полинга таймера, которая автоматически завершает аукцион.

    Parametrs:
    ----------
        channel_last_message: discord.Message
            Последнее сообщение в текстовом канале.

        view: discord.ui.View
            Объект класса View.

        user_mention: str
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
        if final_time.get(name_auc) > datetime.now():
            await asyncio.sleep(0.5)
        else:
            await auto_stop_auc(
                channel_last_message=channel_last_message,
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
        start_auc_user: discord.Member | discord.User,
        stop_time: datetime,
        user_mention: str,
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

        start_bid: int
            Начальная ставка.

        bid: int
            Шаг ставки.

        start_auc_user: discord.Member | discord.User
            Никнейм пользователя, начавшего аукцион.

        stop_time: datetime
            Время завершения аукциона.

        user_mention: str
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
        await interaction.response.defer()
        nowtime: datetime = datetime.now()
        secondstime: timedelta = timedelta(seconds=60)
        plus_minute: datetime = nowtime + secondstime
        reserve_view: discord.ui.View = view
        button.style = discord.ButtonStyle.blurple
        name = interaction.user.display_name
        mention = interaction.user.mention
        original_label: Decimal = Decimal(button.label.split()[0][:-1])
        before_button_label = button.label
        try:
            label_count(button, original_label, name, bid)
            logger.debug(
                f'Кнопка изменилась, функция "label_count" отработала, '
                f'результат "{button.label}"'
            )
            button_mentions[name] = mention
            if len(view.children) == 0:
                await interaction.message.edit(view=reserve_view)
                await interaction.followup.send(
                    f'В момент обработки, сделанной ставки возникла ошибка!'
                    f'Бот не сломался, попробуй сделать ставку снова. Если '
                    f'данное сообщение появляется снова, обратись к '
                    f'{LEADER_NICKNAME}, для скорейшего решения проблемы!',
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
                    await interaction.message.edit(
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
                    final_time[name_auc] = plus_minute
                else:
                    await interaction.message.edit(view=view)
                if 'K' != before_button_label[-1] and 'M' != before_button_label[-1] and interaction.user.display_name not in before_button_label:
                    time_of_bid = None
                    url = interaction.message.jump_url
                    take_nick = before_button_label.split()
                    member: discord.Member = discord.utils.get(interaction.guild.members, nick=take_nick[1])
                    if (datetime.now() + timedelta(seconds=60)) > final_time.get(name_auc) > datetime.now():
                        time_of_bid = plus_minute
                        delete_after = 60
                    else:
                        time_of_bid = stop_time
                        delete_after = 1800
                    await member.send(
                        embed=outbid_embed(
                            url=url, stop_time=time_of_bid,
                            delete_after=delete_after
                        ),
                        delete_after=delete_after
                    )
                    logger.info(
                        f'Ставку "{member.display_name}" перебил "{interaction.user.display_name}"!'
                    )
        except Exception as error:
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )
    return inner


async def auto_stop_auc(
        channel_last_message: discord.Message,
        view: discord.ui.View,
        user_mention: str,
        name_auc: str,
        count: int,
        button_mentions: dict
) -> None:
    """
    Функция для автозавершения аукциона.

    Parametrs:
    ----------
        channel_last_message: discord.Message
            Последнее сообщение в текстовом канале.

        view: discord.ui.View
            Объект класса View

        user_mention: str
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
    label_values = [btn.label for btn in view.children]
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
        await channel_last_message.edit(
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
