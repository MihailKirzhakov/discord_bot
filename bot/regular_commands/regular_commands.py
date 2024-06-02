import discord
import logging
from discord.ext import commands

from .embeds import technical_works_embed, attention_embed
from .randomaizer import ApplicationButton

from variables import LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE

logger = logging.getLogger('regular_commands')
logger.setLevel(logging.DEBUG)

log_file_handler = logging.FileHandler(
    filename='discord_bot.log', mode='a',
    encoding='utf-8', errors='backslashreplace'
)

formatter = logging.Formatter(
    '%(asctime)s | [%(filename)s:%(name)s:%(lineno)d] | %(levelname)s = %(message)s'
)
log_file_handler.setFormatter(formatter)

logger.addHandler(log_file_handler)


async def command_error(
        ctx: discord.ApplicationContext, error: Exception, command_name
):
    """
    Обработчик ошибок для команд.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :param command_name: Имя команды.
    :return: None
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
):
    """
    Команда для отправки сообщения о технических работах.

    :param ctx: Контекст команды.
    :param channel: Текстовый канал, в который нужно отправить сообщение.
    :return: None
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
):
    """
    Обработчик ошибок для команды technical_works.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
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
):
    """
    Команда для отправки сообщения с пометкой 'Внимание!'.

    :param ctx: контекст вызова команды
    :param channel: канал, в который нужно отправить сообщение
    :param value: текст сообщения
    :return: None
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
):
    """
    Обработчик ошибок для команды attention.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
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
    )  # type: ignore
):
    """
    Команда для отправки кнопки рандомайзера.

    :param ctx: контекст вызова команды
    :param channel: канал, в который нужно отправить кнопку
    :return: None
    """
    await channel.send(view=ApplicationButton())
    logger.info(
        f'Команда "/random" вызвана пользователем'
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Кнопка рандомайзера отправлена в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=10
    )


@random.error
async def random_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    """
    Обработчик ошибок для команды random.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
    """
    await command_error(ctx, error, "random")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def greet(
    ctx: discord.ApplicationContext,
    value: discord.Option(
        str,
        description='Впиши любое слово',
        name_localizations={'ru':'что_угодно'},
    )  # type: ignore
):
    """
    Команда для тестирования отправки сообщений и тэгов.

    :param ctx: контекст вызова команды
    :param channel: канал, в который нужно отправить кнопку
    :return: None
    """
    await ctx.respond(
        f'Ну привет {ctx.user.mention}!\n{value} - что означает?'
    )
    logger.info(
        f'Команда "/attention" вызвана пользователем '
        f'"{ctx.user.display_name}"!'
    )


@greet.error
async def greet_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    """
    Обработчик ошибок для команды greet.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
    """
    await command_error(ctx, error, "greet")


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
):
    """
    Команда для удаления сообщений в текстовом канале.

    :param ctx: контекст вызова команды
    :param channel: канал, в котором нужно удалить сообщения
    :param limit: кол-во сообщений, для удаления с конца
    :return: None
    """
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


@clear_all.error
async def clear_all_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    """
    Обработчик ошибок для команды clear_all.

    :param ctx: Контекст команды.
    :param error: Исключение, возникшее при выполнении команды.
    :return: None
    """
    await command_error(ctx, error, "clear_all")


def setup(bot: discord.Bot):
    bot.add_application_command(technical_works)
    bot.add_application_command(attention)
    bot.add_application_command(greet)
    bot.add_application_command(random)
    bot.add_application_command(clear_all)
