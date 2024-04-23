import discord

from regular_commands.variables import PLAYING_DICES_URL_ICON


def number_range(value, ranje):
    embed = discord.Embed(
        title='_Рандомайзер Айронболз!_',
        description=f'_Диапазон чисел {ranje}._',
        color=0x00ff00
    )
    embed.add_field(
        name='_Твоё рандомное число:_',
        value=value,
        inline=False
    )
    embed.set_thumbnail(url=PLAYING_DICES_URL_ICON)
    return embed


def nickname_range(value):
    embed = discord.Embed(
        title='_Рандомайзер Айронболз!_',
        color=0x00ff00
    )
    embed.add_field(
        name='_Участники:_',
        value=value,
        inline=False
    )
    embed.set_thumbnail(url=PLAYING_DICES_URL_ICON)
    return embed
