import discord

from variables import DENIED_IMAGE_URL, ACCESS_IMAGE_URL, RENAME_IMAGE_URL

def rename_embed(user: str, nickname: str) -> discord.Embed:
    """
    Функция для создания вложения с переименованием.
    """
    embed = discord.Embed(
        title='_**ЗАПРОС НА СМЕНУ НИКА**_',
        description=(
            f'_**{user}** просит изменить никнейм на **{nickname}**!\n'
            f'**УБЕДИТЕЛЬНАЯ** просьба проверить сперва его ренейм в игре!\n'
            f'Если не совпадает, то отказываем, пока не поменяет в игре!_'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=RENAME_IMAGE_URL)
    return embed


def changed_rename_embed(user, nickname) -> discord.Embed:
    """
    Функция для создания вложения с выполненным переименованием.
    """
    embed = discord.Embed(
        title='_**Никнейм ИЗМЁНЕН**_',
        description=(
            f'_**{user}** изменил никнейм на **{nickname}**!_\n'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=ACCESS_IMAGE_URL)
    return embed


def denied_rename_embed(user: str) -> discord.Embed:
    """
    Функция для создания вложения с отказом в ренейме.
    """
    embed = discord.Embed(
        title='_**Никнейм НЕ ИЗМЁНЕН**_',
        description=(
            f'_**{user}** НЕ изменил ник в игре, ожидаем!_\n'
        ),
        color=0xfffb00
    )
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
