import discord

from .variables import (
    PLAYING_DICES_URL_ICON, TEСHNICAL_WORKS, WRENCH_IMAGE_URL
)
from role_application.variables import IRONBALLS_IMAGE_URL


def number_range(value, ranje):
    embed = discord.Embed(
        title='_Рандомайзер!_',
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
        title='_Рандомайзер!_',
        color=0x00ff00
    )
    embed.add_field(
        name='_Участники:_',
        value=value,
        inline=False
    )
    embed.set_thumbnail(url=PLAYING_DICES_URL_ICON)
    return embed


def technical_works_embed():
    embed = discord.Embed(
        title='_IronBot_',
        color=0xfffb00
    )
    embed.add_field(
        name='_Технические работы..._',
        value=TEСHNICAL_WORKS,
        inline=False
    )
    embed.set_thumbnail(url=WRENCH_IMAGE_URL)
    embed.set_image(url=IRONBALLS_IMAGE_URL)
    return embed
