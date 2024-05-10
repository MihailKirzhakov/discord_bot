import discord

from .variables import (
    ACCESS_VALUE,
    ACCESS_IMAGE_URL,
    GUILD_IMAGE_URL,
    DENIED_IMAGE_URL
)


def access_embed():
    embed = discord.Embed(
        title='_Приветствую!_',
        description='_Тебе выдан доступ на сервер гильдии Ревенжерс!_',
        color=0x00ff00
    )
    embed.add_field(
        name='_Полезное:_',
        value=ACCESS_VALUE,
        inline=False
    )
    embed.set_thumbnail(url=ACCESS_IMAGE_URL)
    embed.set_image(url=GUILD_IMAGE_URL)
    return embed


def denied_embed(user, reason):
    embed = discord.Embed(
        title='_Приветствую!_',
        description=(
            f'_Офицер {user.display_name} отказал тебе '
            f'в доступе на сервер гильдии Ревенжерс!_'
        ),
        color=0xff0000
    )
    embed.set_thumbnail(url=DENIED_IMAGE_URL)
    embed.set_image(url=GUILD_IMAGE_URL)
    if len(reason) > 0:
        embed.add_field(
            name='_Комментарии:_',
            value=f'_{reason}_',
            inline=False
        )
    return embed


def application_embed(description, nickname, member, player_parms):
    embed = discord.Embed(
        title='Заявка на доступ',
        description=description,
        color=0x6e00ff
    )
    embed.set_author(
        name=nickname,
        icon_url=member.avatar
    )
    embed.add_field(
        name='Гирскор',
        value=player_parms['gear_score'],
        inline=True
    )
    art_lvl = 'Нет'
    if 'artifact' in player_parms:
        art_lvl = player_parms['artifact']['level']
    embed.add_field(name='Уровень НБ', value=art_lvl, inline=True)
    embed.set_thumbnail(url=player_parms['class_icon'])
    if 'emblem' in player_parms:
        embed.set_image(url=player_parms['emblem']['image_url'])
    return embed
