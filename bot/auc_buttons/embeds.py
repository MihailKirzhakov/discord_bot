from datetime import datetime

import discord

from variables import ATTENTION, AUCTION_IMAGE_URL


def start_auc_embed(
    user_mention: discord.abc.User.mention,
    name_auc: str,
    stop_time: datetime,
    lot_count: int,
    first_bid: str,
    next_bid: str
) -> discord.Embed:
    """
    Создает встраиваемое сообщение об открытии аукциона.

    Parametrs:
    ----------
        user_mention: discord.abc.User.mention
            Упоминание пользователя, открывшего аукцион

        name_auc: str
            Название аукциона

        stop_time: datetime
            Время окончания аукциона

        lot_count: int
            Количество лотов в аукционе

        first_bid: str
            Начальная ставка

        next_bid: str
            Шаг ставки

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=(
            f'_**{user_mention} начал аукцион "{name_auc}"!**\n\n'
            f'Количество лотов: {lot_count}.\n'
            f'Начальная ставка: {first_bid}.\n'
            f'Шаг ставки: {next_bid}.\n\n'
            f'**Аукцион закончится\n'
            f'<t:{int(stop_time.timestamp())}:R>!**_'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed


def results_embed(
        results_message: str,
        user_mention: discord.abc.User.mention,
        name_auc: str,
        count: int
) -> discord.Embed:
    """
    Создает встраиваемое сообщение с результатами аукциона.

    Parametrs:
    ----------
        results_message: str
            Результаты аукциона в виде строки.

        user_mention: discord.abc.User.mention
            Упоминание пользователя, открывшего аукцион.

        name_auc: str
            Название аукциона.

        count: int
            Количество лотов в аукционе.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=(
            f'_**{user_mention} провёл аукцион "{name_auc}"!\n\n'
            f'Аукцион был завершён в {discord.utils.format_dt(datetime.now(), style="F")}!**\n\n'
            f'Количество лотов: {count}.\n\n'
            f'**Результаты аукциона:**\n'
            f'{results_message}_'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed


def outbid_embed(url: str, stop_time: datetime, delete_after: int) -> discord.Embed:
    """
    Создает встраиваемое сообщение с результатами аукциона.

    Parametrs:
    ----------
        url: str
            Ссылка на сообщение.

        stop_time: datetime
            Ссылка на сообщение.

        delete_after: int
            Время жизни сообщения.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=(
            f'_**Твоя ставка на аукционе была перебита!\n'
            f'Аукцион закончится <t:{int(stop_time.timestamp())}:R>\n\n'
            f'{url}**\n\n'
            f'данное сообщение автоматически удалится через '
            f'{"минуту" if delete_after == 60 else "30 минут"}._'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed
