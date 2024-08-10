import discord

from variables import (
    ATTENTION, GUILD_IMAGE_URL, PLAYING_DICES_URL_ICON,
    SMALL_GUILD_ICON_URL, TEСHNICAL_WORKS, WRENCH_IMAGE_URL,
    REMIND, DENIED_IMAGE_URL, ACCESS_IMAGE_URL, RENAME_IMAGE_URL,
    REMIND_IMAGE_URL, TO_REMIND, CROSSED_SWORDS_IMAGE_URL,
    RCD_LIST_IMAGE_URL, QUESTION_IMAGE_URL
)


def number_range(value: str, ranje: str) -> discord.Embed:
    """
    Функция для создания вложения с рандомным числом в заданном диапазоне.

    Parametrs:
    ----------
        value: str
            Значение, которое будет возвращено в вложении.

        ranje: str
            Диапазон чисел в виде строки через дефис.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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


def nickname_range(value: str) -> discord.Embed:
    """
    Функция для создания вложения с рандомным участником.

    Parametrs:
    ----------
        value: str
            Значение, которое будет возвращено в вложении.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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


def technical_works_embed() -> discord.Embed:
    """
    Функция для создания вложения с информацией о технических работах.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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


def attention_embed(value: str) -> discord.Embed:
    """
    Функция для создания вложения с предупреждением.

    Parametrs:
    ----------
        value: str
            Значение, которое будет возвращено в вложении.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=f'_**{value}!**_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed


def remind_embed(date: str, message: str) -> discord.Embed:
    """
    Функция для создания вложения с инфой о готовности напоминания.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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
    Функция для создания вложения с предупреждением.

    Parametrs:
    ----------
        date: str
            Отформатированная строка даты и времени.

        message: str
            Значение, которое будет возвращено в вложении.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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


def rename_embed(user: str, nickname: str) -> discord.Embed:
    """
    Функция для создания вложения с предупреждением.

    Parametrs:
    ----------
        user: str
            Никнейм юзера, котоырй делает запрос.

        nickname: str
            Никнейм в который планирует ренеймнуться.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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
    Функция для создания вложения с предупреждением.

    Parametrs:
    ----------
        user: str
            Отформатированная строка даты и времени.

        nickname: str
            Значение, которое будет возвращено в вложении.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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
    Функция для создания вложения с предупреждением.

    Parametrs:
    ----------
        user: str
            Отформатированная строка даты и времени.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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
    Функция для создания вложения с предупреждением.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
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


def start_rcd_embed(date: str) -> discord.Embed:
    """
    Функция для создания вложения о старте РЧД заявок.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=f'_**Заявки на РЧД {date}**_',
        description=(
            '_Тыкай на кнопку ниже ⬇️\n\n'
            'Обрати внимание на то, что список внизу, '
            'это не финальный состав рейда, а просто поданные заявки!_'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=CROSSED_SWORDS_IMAGE_URL)
    return embed


def rcd_list_embed(date: str) -> discord.Embed:
    """
    Функция для создания вложения о списке поданных РЧД заявок.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=f'_**Список поданных заявок {date}**_',
        color=0xfffb00
    )
    embed.add_field(
        name='------------------------------',
        value='Ветераны:\n',
        inline=False
    )
    embed.add_field(
        name='------------------------------',
        value='Старшины:\n',
        inline=False
    )
    embed.set_thumbnail(url=RCD_LIST_IMAGE_URL)
    return embed


def ask_veteran_embed(member: discord.Member,date: str) -> discord.Embed:
    """
    Функция для создания вложения всем ветеранам.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description=(
            f'_Рассылка от пользователя {member.display_name}\n\n'
            f'Вопрос - можешь пойти на РЧД {date}?\n'
            f'Если да, заполни пожалуйста заявку на РЧД 😊_!\n\n'
            f'-# Сообщение автоматически удалится через 3 часа, если не ответить!'
        ),
        color=0xfffb00
    )
    embed.set_thumbnail(url=QUESTION_IMAGE_URL)
    return embed


def final_rcd_list_embed(date: str) -> discord.Embed:
    """
    Функция для создания вложения о списке РЧД.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    index_class_role = {
        0: 'Воины:',
        1: 'Паладины:',
        2: 'Инженеры:',
        3: 'Жрецы:',
        4: 'Шаманы:',
        5: 'Мистики:',
        6: 'Лучники:',
        7: 'Маги:',
        8: 'Некроманты:',
        9: 'Барды:',
        10: 'Демоны:'
    }
    embed = discord.Embed(
        title=f'_**Список РЧД {date}**_',
        color=0xfffb00
    )
    for role in index_class_role.values():
        embed.add_field(
            name=role,
            value='',
            inline=False
        )
    embed.set_thumbnail(url=RCD_LIST_IMAGE_URL)
    return embed


def removed_role_list_embed() -> discord.Embed:
    """
    Функция для создания вложения почищеных ролей.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description='_**Список пользователей, у которых забрали роль старшина:**_\n\n',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed


def publish_rcd_embed(date: str) -> discord.Embed:
    """
    Функция для создания вложения о старте РЧД заявок.

    Returns:
    --------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    embed = discord.Embed(
        title=f'_**Список РЧД {date}**_',
        color=0xfffb00
    )
    embed.set_thumbnail(url=CROSSED_SWORDS_IMAGE_URL)
    return embed
