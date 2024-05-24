import discord


from bot.variables import ATTENTION, AUCTION_IMAGE_URL


def attention_embed(user_mention, name_auc, lot_count, first_bid, next_bid):
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
    embed = discord.Embed(
        title='_**Результаты аукциона:**_',
        description=f'_{results_message}!_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=AUCTION_IMAGE_URL)
    return embed
