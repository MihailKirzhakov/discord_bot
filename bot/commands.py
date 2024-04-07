import discord
from discord.ext import commands
from functions import rand_choice


@commands.slash_command()
async def gogo(ctx: discord.ApplicationContext):
    """Команда для проверки бота"""
    await ctx.respond('This is a regular command')


@commands.slash_command()
@commands.has_role('Казначей', 'Офицер', 'Лидер гильдии', 'Ветеран', 'Старшина')
async def random(ctx: discord.ApplicationContext, nicknames: discord.Option(
    str,
    description='Укажи ники через "-", или диапазон в формате "1-100", или оставь поле пустым',
    name_localizations={'ru': 'среди_чего_выбрать'}
)='1-100'): # type: ignore
    """Команда вызывающая рандомайзер"""
    await ctx.respond(rand_choice(nicknames))

@random.error
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.respond('Эта команда не может быть вызвана через ЛС')
    elif isinstance(error, commands.errors.MissingRole):
        await ctx.respond(f'{ctx.author.mention} ты, дружочек, не достоин просить меня это сделать!')
    else:
        return error


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
        await ctx.respond(f'{ctx.author.mention} ты, дружочек, не достоин просить меня это сделать!')
    else:
        return error


def setup(bot: discord.Bot):
    bot.add_application_command(gogo)
    bot.add_application_command(greet)
    bot.add_application_command(random)
