import discord

from variables import (
    ATTENTION,
    GUILD_IMAGE_URL,
    PLAYING_DICES_URL_ICON,
    SMALL_GUILD_ICON_URL,
    TEСHNICAL_WORKS,
    WRENCH_IMAGE_URL,
    REMIND
)


def number_range(value, ranje):
    """
    Функция для создания вложения с рандомным числом в заданном диапазоне.

    :param value: рандомное число
    :param ranje: диапазон чисел
    :return: вложение с рандомным числом
    """
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
    """
    Функция для создания вложения с рандомным участником.

    :param value: рандомный участник
    :return: вложение с рандомным участником
    """
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
    """
    Функция для создания вложения с информацией о технических работах.

    :return: вложение с информацией о технических работах
    """
    embed = discord.Embed(
        title='_Kavo4avoBot_',
        color=0xfffb00
    )
    embed.add_field(
        name='_Технические работы..._',
        value=TEСHNICAL_WORKS,
        inline=False
    )
    embed.set_thumbnail(url=WRENCH_IMAGE_URL)
    embed.set_image(url=GUILD_IMAGE_URL)
    return embed


def attention_embed(value):
    """
    Функция для создания вложения с предупреждением.

    :param value: текст предупреждения
    :return: вложение с предупреждением
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=f'_**{value}!**_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed


def remind_embed(date, message):
    """
    Функция для создания вложения с предупреждением.

    :param value: текст предупреждения
    :return: вложение с предупреждением
    """
    embed = discord.Embed(
        title=REMIND,
        description=f'_Ты просил в {date} тебе чиркануть!\nТекст напоминания: **"{message}"**!_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed
