from datetime import datetime

import discord


from variables import ATTENTION, AUCTION_IMAGE_URL


def start_auc_embed(
        user_mention, name_auc, stop_time,
        lot_count, first_bid, next_bid
):
    """
    Создает встраиваемое сообщение об открытии аукциона.

    :param user_mention: упоминание пользователя, открывшего аукцион
    :param name_auc: название аукциона
    :param lot_count: количество лотов в аукционе
    :param first_bid: начальная ставка
    :param next_bid: шаг ставки
    :return: встраиваемое сообщение
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=(
            f'_**{user_mention} начал аукцион "{name_auc}"!**\n\n'
            f'Количество лотов: {lot_count}.\n'
            f'Начальная ставка: {first_bid}.\n'
            f'Шаг ставки: {next_bid}._'
        ),
        color=0xfffb00
    )
    embed.add_field(
        name='_**Аукцион закончится**_',
        value=f'_**<t:{int(stop_time.timestamp())}:R>!**_'
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed


def results_embed(results_message, user_mention, name_auc, count):
    """
    Создает встраиваемое сообщение с результатами аукциона.

    :param results_message: результаты аукциона в виде строки
    :return: встраиваемое сообщение
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
