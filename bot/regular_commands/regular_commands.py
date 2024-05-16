import discord

from discord.ext import commands

from .randomaizer import ApplicationButton
from .embeds import technical_works_embed, attention_embed


@commands.slash_command()
@commands.has_any_role('🌀Лидер гильдии🌀', '📣Казначей📣', '🛡️Офицер🛡️')
async def technical_works(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    )  # type: ignore
):
    """Команда для отправки сообщения о тех. работах"""
    await channel.send(embed=technical_works_embed())
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
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер", "Казначей" или "Офицер"!',
            ephemeral=True,
            delete_after=15
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=15
        )
    else:
        raise error


@commands.slash_command()
@commands.has_any_role('🌀Лидер гильдии🌀', '📣Казначей📣', '🛡️Офицер🛡️')
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
    """Команда для отправки сообщения с пометкой 'Внимание!'"""
    await channel.send(embed=attention_embed(value=value))
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
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер", "Казначей" или "Офицер"!',
            ephemeral=True,
            delete_after=15
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=15
        )
    else:
        raise error


@commands.slash_command()
@commands.has_any_role('🌀Лидер гильдии🌀', '📣Казначей📣', '🛡️Офицер🛡️')
async def random(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'},
    )  # type: ignore
):
    """
    Команда вызывающая рандомайзер. По дэфолту диапазон чисел 1-100.
    """
    await channel.send(view=ApplicationButton())
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
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер", "Казначей" или "Офицер"!',
            ephemeral=True,
            delete_after=15
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=15
        )
    else:
        raise error


@commands.slash_command()
@commands.has_role('Аукцион')
async def greet(
    ctx: discord.ApplicationContext,
    value: discord.Option(
        str,
        description='Впиши любое слово',
        name_localizations={'ru':'что_угодно'},
    )  # type: ignore
):
    """Команда для теста"""
    await ctx.respond(f'Ну привет {ctx.user.mention}!\n{value} - что означает?')


@greet.error
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.respond('Эта команда не может быть вызвана через ЛС')
    elif isinstance(error, commands.errors.MissingRole):
        await ctx.respond(
            f'{ctx.author.mention} ты, дружочек, '
            f'не достоин просить меня это сделать!'
        )
    else:
        return error


@commands.slash_command()
@commands.has_any_role('🌀Лидер гильдии🌀', '📣Казначей📣', '🛡️Офицер🛡️')
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
    """Команда для удаления сообщений в текстовых каналах"""
    await channel.purge(
        limit=limit,
        bulk=True
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
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер", "Казначей" или "Офицер"!',
            ephemeral=True,
            delete_after=15
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=15
        )
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(technical_works)
    bot.add_application_command(attention)
    bot.add_application_command(greet)
    bot.add_application_command(random)
    bot.add_application_command(clear_all)
