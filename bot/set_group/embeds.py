import discord


def set_group_embed() -> discord.Embed:
    """
    Функция для создания вложения с информацией о группе.
    """
    embed = discord.Embed(
        title='КП лидер',
        description='',
        color=0x55ffff
    )
    embed.add_field(
        name='Состав:\n',
        value='',
    )
    return embed


def set_group_discription_embed() -> discord.Embed:
    """
    Функция для создания вложения с информацией о создании группы в канале
    """
    embed = discord.Embed(
        title='Инструкция по созданию группы в канале 🙌',
        description=(
            '_Для создания группы необходимо нажать на кнопку и '
            'заполнить поля в модальном окне. Если группа неполная, можно '
            'оставить поле пустым. 👌_'
        ),
        color=0x55ffff
    )
    return embed
