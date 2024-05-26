import discord


from variables import ATTENTION, AUCTION_IMAGE_URL


def attention_embed(user_mention, name_auc, lot_count, first_bid, next_bid):
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
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed


def results_embed(results_message):
    """
    Создает встраиваемое сообщение с результатами аукциона.

    :param results_message: результаты аукциона в виде строки
    :return: встраиваемое сообщение
    """
    embed = discord.Embed(
        title='_**Результаты аукциона:**_',
        description=f'_{results_message}!_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed
