from datetime import datetime, timedelta

import discord
from discord.ext import commands
from loguru import logger

from .functions import remind_message
from .embeds import technical_works_embed, attention_embed, remind_embed
from .randomaizer import RandomButton
from .rename_request import RenameButton
from variables import (
    LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE,
    CLOSED_JMURENSKAYA, CLOSED_ORTHODOX, CLOSED_TEAM_TAYP,
    CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT,
    BUHLOID_ID, IDOL_ID, TAYP_ID, KVAPA_ID, GOOSE_ID
)


async def command_error(
        ctx: discord.ApplicationContext, error: Exception, command_name: str
) -> None:
    """
    Обработчик ошибок для команд.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

        command_name: str
            Имя команды.

    Returns:
    --------
        None
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            f'Команду {command_name} может вызвать только '
            f'"Лидер", "Казначей" или "Офицер"!',
            ephemeral=True,
            delete_after=10
        )
        logger.info(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}"! '
            f'В результате возникло исключение "{error}"!'
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            f'Команду {command_name} нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=10
        )
        logger.info(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}" в лс! '
            f'В результате возникло исключение "{error}"!'
        )
    else:
        logger.error(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}"! '
            f'В результате возникло исключение "{error}"!'
        )
        raise error


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def technical_works(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    )  # type: ignore
) -> None:
    """
    Команда для отправки сообщения о технических работах.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        channel: discord.TextChannel
            Текстовый канал, в который нужно отправить сообщение.

    Returns:
    --------
        None
    """
    await channel.send(embed=technical_works_embed())
    logger.info(
        f'Команда "/technical_works" вызвана пользователем '
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Сообщение о тех работах отправлено в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=5
    )


@technical_works.error
async def technical_works_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды technical_works.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "technical_works")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def attention(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
    value: discord.Option(
        str,
        description='Введи текст сообщения',
        name_localizations={'ru':'текст'},
    )  # type: ignore
) -> None:
    """
    Команда для отправки сообщения с пометкой 'Внимание!'.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        channel: discord.TextChannel
            Канал, в который нужно отправить сообщение.

        value: str
            Текст сообщения.

    Returns:
    --------
        None
    """
    await channel.send(embed=attention_embed(value=value))
    logger.info(
        f'Команда "/attention" вызвана пользователем '
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Сообщение отправлено в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=5
    )


@attention.error
async def attention_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды attention.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "attention")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def random(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'},
    ), # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки рандомайзера.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст вызова команды.

        channel: discord.TextChannel
            Канал, в который нужно отправить кнопку.

    Returns:
    --------
        None
    """
    if message_id:
        message = ctx.channel.get_partial_message(int(message_id))
        await message.edit(view=RandomButton())
        await ctx.respond(
            f'_Кнопка рандомайзера обновлена и снова работает в канале {channel.mention}!_',
            ephemeral=True,
            delete_after=10
        )
    else:
        await channel.send(view=RandomButton())
        await ctx.respond(
            f'_Кнопка рандомайзера отправлена в канал {channel.mention}!_',
            ephemeral=True,
            delete_after=10
        )
    logger.info(
        f'Команда "/random" вызвана пользователем'
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )


@random.error
async def random_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды random.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "random")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def clear_all(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Канал для очистки',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
    limit: discord.Option(
        int,
        description='Кол-во сообщений для удаления',
        name_localizations={'ru':'сколько_удалить'},
        default=100,
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для удаления сообщений в текстовом канале.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст вызова команды.

        channel: discord.TextChannel
            Канал, в который нужно отправить кнопку.

        limit: int
            Количество сообщений для удаления с конца.

    Returns:
    --------
        None
    """
    try:
        await channel.purge(
            limit=limit,
            bulk=True
        )
        logger.info(
            f'Команда "/clear_all" вызвана пользователем '
            f'"{ctx.user.display_name}" в канале "{channel}"!'
        )
        await ctx.respond(
            f'_Сообщения удалены в канале {channel.mention}!_',
            ephemeral=True,
            delete_after=10
        )
    except Exception as error:
        await ctx.respond(
            f'_При использовании команды "clear_all" в канале '
            f'{channel} возникла ошибка: "{error}"!_'
        )
        logger.error(
            f'_При использовании команды "clear_all" в канале '
            f'{channel} возникла ошибка: "{error}"!_'
        )


@clear_all.error
async def clear_all_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды clear_all.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "clear_all")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def remind(
    ctx: discord.ApplicationContext,
    message: discord.Option(
        str,
        description='Укажи сообщение',
        name_localizations={'ru': 'строка'}
    ),  # type: ignore
    date_time_time_str: discord.Option(
        str,
        description='Укажи дату и время "ГГГГ-ММ-ДД ЧЧ:ММ"',
        name_localizations={'ru': 'дата_время'}
    ),  # type: ignore
) -> None:
    """
    Команда для отправки сообщения с напоминанием.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        date_time_time_str: str
            Строка в формате "ГГГГ-ММ-ДД ЧЧ:ММ".

    Returns:
    --------
        None
    """
    date_time_time_str_split = date_time_time_str.replace(
        '-', ' '
    ).replace('_', ' ').replace(':', ' ').split()
    remind_date = datetime(
        year=int(date_time_time_str_split[0]),
        month=int(date_time_time_str_split[1]),
        day=int(date_time_time_str_split[2]),
        hour=int(date_time_time_str_split[3]),
        minute=int(date_time_time_str_split[4]),
    )
    convert_remind_date = discord.utils.format_dt(remind_date, style="F")
    await ctx.respond(
        remind_message(convert_remind_date, message),
        ephemeral=True,
        delete_after=10
    )
    await discord.utils.sleep_until(remind_date)
    await ctx.user.send(embed=remind_embed(convert_remind_date, message))


@remind.error
async def remind_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды remind.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "remind")


@commands.slash_command()
@commands.has_any_role(
    CLOSED_JMURENSKAYA, CLOSED_ORTHODOX, CLOSED_TEAM_TAYP,
    CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT
)
async def give_role_to(
    ctx: discord.ApplicationContext,
    member: discord.Option(
        discord.Member,
        description='Пользователь дискорда, кому нужна роль',
        name_localizations={'ru':'выбери_пользователя'}
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки на выдачу роли.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        member: discord.Member
            Пользователь дискорда, кому нужна роль.

    Returns:
    --------
        None
    """
    closed_jmurenskaya = discord.utils.get(
            ctx.guild.roles, name=CLOSED_JMURENSKAYA)
    closed_orthodox = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ORTHODOX)
    closed_team_tayp = discord.utils.get(
            ctx.guild.roles, name=CLOSED_TEAM_TAYP)
    closed_goose_home = discord.utils.get(
            ctx.guild.roles, name=CLOSED_GOOSE_HOME)
    closed_on_the_mind_aspect = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ON_THE_MIND_ASPECT)
    check_group_leaders = {
        BUHLOID_ID: closed_jmurenskaya,
        IDOL_ID: closed_orthodox,
        TAYP_ID: closed_team_tayp,
        GOOSE_ID: closed_goose_home,
        KVAPA_ID: closed_on_the_mind_aspect
    }
    try:
        if str(ctx.user.id) in check_group_leaders:
            await member.add_roles(check_group_leaders.get(str(ctx.user.id)))
            await ctx.respond(
                f'_**Роль**\n{check_group_leaders.get(str(ctx.user.id)).mention}\n'
                f'**выдана**\n{member.mention}!_',
                ephemeral=True,
                delete_after=10
            )
            logger.info(
                f'Команда "/give_role_to" вызвана пользователем'
                f'"{ctx.user.display_name}", роль выдана "{member.display_name}"!'
            )
        else:
            await ctx.respond(
                '_У тебя нет доступа к этой команде!_',
                ephemeral=True,
                delete_after=10
            )
    except Exception as error:
        logger.error(f'Ошибка при вызове команды "/give_role_to": {error}')


@give_role_to.error
async def give_role_to_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды random.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "give_role_to")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rename(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'},
    ), # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки рандомайзера.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        channel: discord.TextChannel
            Канал, в который нужно отправить кнопку.

        message_id: str
            ID сообщения, в котором есть кнопка кнопка

    Returns:
    --------
        None
    """
    if message_id:
        message = ctx.channel.get_partial_message(int(message_id))
        await message.edit(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера обновлена и снова работает!_',
            ephemeral=True,
            delete_after=10
        )
    else:
        await ctx.respond(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера запущена!_',
            ephemeral=True,
            delete_after=10
        )
    logger.info(
        f'Команда "/rename" вызвана пользователем'
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )


@rename.error
async def rename_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды rename.

    Parametrs:
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

        error: Exception
            Исключение, возникшее при выполнении команды.

    Returns:
    --------
        None
    """
    await command_error(ctx, error, "rename")


def setup(bot: discord.Bot):
    bot.add_application_command(technical_works)
    bot.add_application_command(attention)
    bot.add_application_command(random)
    bot.add_application_command(clear_all)
    bot.add_application_command(remind)
    bot.add_application_command(give_role_to)
    bot.add_application_command(rename)
