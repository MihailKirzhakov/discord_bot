import discord

from discord.ext import commands

from regular_commands.randomaizer import ApplicationButton


@commands.slash_command()
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def gogo(ctx: discord.ApplicationContext):
    """Команда для проверки бота"""
    await ctx.respond('This is a regular command')


@gogo.error
async def gogo_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Казначей" или "Офицер"!',
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
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def random(
    ctx: discord.ApplicationContext
):
    """
    Команда вызывающая рандомайзер. По дэфолту диапазон чисел 1-100.
    """
    await ctx.respond(view=ApplicationButton())

@random.error
async def random_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Казначей" или "Офицер"!',
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
async def greet(ctx: discord.ApplicationContext, name: str):
    """Команда для теста"""
    await ctx.respond(f'Ну привет, {name}! Тестим')


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
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def clear_all(ctx: discord.ApplicationContext):
    await ctx.channel.purge(
        bulk=False
    )


@clear_all.error
async def clear_all_error(
    ctx: discord.ApplicationContext,
    error: Exception
):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Казначей" или "Офицер"!',
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
    bot.add_application_command(gogo)
    bot.add_application_command(greet)
    bot.add_application_command(random)
    bot.add_application_command(clear_all)
