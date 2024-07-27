import discord

from variables import (
    ACCESS_IMAGE_URL, ACCESS_VALUE, DENIED_IMAGE_URL,
    GUILD_IMAGE_URL, GUILD_NAME, SMALL_GUILD_ICON_URL
)


def access_embed() -> discord.Embed:
    """
    Функция для создания вложения с информацией о выдаче доступа.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title='_Приветствую!_',
        description=f'_Тебе выдан доступ на сервер гильдии {GUILD_NAME}!_',
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


def denied_embed(user: discord.abc.User, reason: str) -> discord.Embed:
    """
    Функция для создания вложения с информацией об отказе в доступе.

    Parametrs:
    ----------
        user: discord.abc.User
            Класс юзера, который взаимодействует с кнопкой.

        reason: str
            Причина отказа в доступе.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title='_Приветствую!_',
        description=(
            f'_{user.display_name} отказал тебе '
            f'в доступе на сервер гильдии {GUILD_NAME}!_'
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


def application_embed(
        description: str,
        nickname: str,
        member: discord.abc.User,
        player_parms: dict | None
) -> discord.Embed:
    """
    Функция для создания вложения с информацией об игроке.

    Parametrs:
    ----------
        description: str
            Информация о профиле и гильдии.

        nickname: str
            Никнейм пользователя из модального окна.

        member: discord.abc.User
            Пользователь из discord.utils.get()

        player_parms: dict | None
            Параметры игрока.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
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


def start_app_embed() -> discord.Embed:
    """
    Функция для создания вложения с просьбой заполнить форму.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title='_**Привет, друг! 👋**_',
        description='_Заполни форму для получения доступа!\n\nТыкай кнопку 👇_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed
