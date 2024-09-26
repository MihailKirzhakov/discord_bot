import discord

from variables import REMIND, SMALL_GUILD_ICON_URL, REMIND_IMAGE_URL, TO_REMIND


def remind_embed(date: str, message: str) -> discord.Embed:
    """
    Функция для создания вложения с инфой о готовности напоминания.
    """
    embed = discord.Embed(
        title=TO_REMIND,
        description=(
            f'_Сообщение отправится в {date}'
            f'\nтебе в личные сообщения 📨.\n'
            f'Содержание сообщения:\n\n**"{message}"**_'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=REMIND_IMAGE_URL)
    return embed


def remind_send_embed(date: str, message: str) -> discord.Embed:
    """
    Функция для создания вложения для отправки пользователю о напоминании.
    """
    embed = discord.Embed(
        title=REMIND,
        description=(
            f'_Ты просил в {date}\nтебе чиркануть и напомнить о: '
            f'\n\n**"{message}"**_\n\n'
            f'-# Данное сообщение будет удалено через 5 минут!'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed
