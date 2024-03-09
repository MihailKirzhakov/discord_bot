import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Подгружаем файл с переменными из .env
load_dotenv()

bot = discord.Bot(debug_guilds=[1214866204309725244])


@bot.event
async def on_ready():
    """Событие запуска бота"""
    print("Бот подключился к Discord API")


@bot.command()
async def reload_extention(ctx: discord.ApplicationContext):
    bot.reload_extension('commands')
    await ctx.respond('Extension reloaded')


bot.load_extension('commands')
bot.run(os.getenv('TOKEN'))
