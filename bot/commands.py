import discord
from discord.ext import commands


@commands.slash_command()
async def gogo(ctx: discord.ApplicationContext):
    await ctx.respond('This is a regular command')


@commands.slash_command()
@commands.has_role(1216045585166237836)
async def greet(ctx: discord.ApplicationContext, name: str):
    await ctx.respond(f'Hello, {name}!')


@greet.error
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.respond('Эта команда не может быть вызвана через ЛС')
    elif isinstance(error, commands.errors.MissingRole):
        await ctx.respond(f'{ctx.author.mention} ты дружочек не достоин просить меня это сделать!')
    else:
        return error


def setup(bot: discord.Bot):
    bot.add_application_command(gogo)
    bot.add_application_command(greet)
