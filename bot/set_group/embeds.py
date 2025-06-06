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


def set_group_discription_embed(guild_leader: str) -> discord.Embed:
    """
    Функция для создания вложения с информацией о создании группы в канале
    """
    embed = discord.Embed(
        title='Инструкция по созданию группы в канале 🙌',
        description=(
            '_- Для создания группы необходимо нажать на кнопку и '
            'выбрать игроков из списка. Найти нужных игроков можно с помощью '
            'поиска, просто начни вводить никнейм игрока. **СЕБЯ ПРИ ЭТОМ ВЫБИРАТЬ НЕ НУЖНО!**\n'
            '- Важно накликать сразу всех игроков, ибо если ты нажмешь '
            'в любое другое место группа создастся с недостоящими игроками '
            'и придется её редактировать 🤷‍♂️\n'
            '- Для редактирования 🔁 или удаления ❎ группы необходимо нажать на '
            'соответсвующие кнопки, появившееся поле будет действительно 60 секунд, '
            'если не успели, начните заново!\n'
            '- Cообщение для создания или '
            'редактирования группы видит только тот, кто нажал на кнопку, если '
            'вы закончили создание группы, то можете скрыть это сообщение, '
            'нажав ниже на синий текст, или дождаться окончания минуты.'
            '-Редактировать или удалять группы могут только КПлы\n'
            '- Если в группе не хватает игроков, то при редактировании или '
            'создании группы бот дозаполнит слоты пустыми полями 👌_\n\n'
            f'_По любым вопросам или ошибкам обращаться сразу к {guild_leader}!_'
        ),
        color=0x55ffff
    )
    return embed


def group_create_instruction_embed() -> discord.Embed:
    """
    Функция для создания вложения с подсказкой к созданию группы
    """
    embed = discord.Embed(
        title='_Памятка_ 😊',
        description=(
            '_Найти нужных игроков можно с помощью '
            'поиска, просто начни вводить никнейм игрока. При этом '
            'необходимо накликать сразу всех игроков, ибо если ты нажмешь '
            'в любое другое место группа создастся с недостоящими игроками '
            'и придется её редактировать_ 🤷‍♂️\n\n'
            '-# Данное сообщение пропадёт через 60 секунд! Если не успел '
            'заполнить, нажми на кнопку еще раз и повтори.'
        ),
        color=0x55ffff
    )
    return embed
