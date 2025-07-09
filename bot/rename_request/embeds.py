import discord

from core import DENIED_IMAGE_URL, ACCESS_IMAGE_URL, RENAME_IMAGE_URL


def rename_embed(
    old_nickname: str,
    jump_url: str,
    new_nickname: str
) -> discord.Embed:
    """
    Функция для создания вложения с переименованием.
    """
    embed = discord.Embed(
        description=(
            f'_Просит изменить никнейм на **{new_nickname}**!\n'
            f'**УБЕДИТЕЛЬНАЯ** просьба проверить сперва его ренейм в игре!\n'
            f'Если не совпадает, то отказываем, пока не поменяет в игре!_'
        ),
        color=0xfffb00
    )
    embed.set_author(name=old_nickname, url=jump_url)
    embed.set_thumbnail(url=RENAME_IMAGE_URL)
    return embed


def changed_rename_embed(
    old_nickname: str,
    jump_url: str,
    new_nickname: str
) -> discord.Embed:
    """
    Функция для создания вложения с выполненным переименованием.
    """
    embed = discord.Embed(
        description=(
            f'_изменил никнейм на **{new_nickname}**!_\n'
        ),
        color=0xfffb00
    )
    embed.set_author(name=old_nickname, url=jump_url)
    embed.set_thumbnail(url=ACCESS_IMAGE_URL)
    return embed


def denied_rename_embed(old_nickname: str, jump_url: str) -> discord.Embed:
    """
    Функция для создания вложения с отказом в ренейме.
    """
    embed = discord.Embed(
        description=(
            f'_**НЕ** изменил ник в игре, ожидаем!_\n'
        ),
        color=0xfffb00
    )
    embed.set_author(name=old_nickname, url=jump_url)
    embed.set_thumbnail(url=DENIED_IMAGE_URL)
    return embed


def denied_send_embed() -> discord.Embed:
    """
    Функция для создания вложения для отправки отказа в ренейме.
    """
    embed = discord.Embed(
        title='_**Никнейм НЕ ИЗМЁНЕН**_',
        description=(
            '_Тебе отказали в смене ника, скорее всего ты попытался'
            ' сменить ник в дискорде, не изменив его в самой игре!\n'
            'Как поменяешь ник в игре, чиркани запрос снова_ 👌'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=DENIED_IMAGE_URL)
    return embed
