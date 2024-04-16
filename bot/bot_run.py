import discord
import os
from dotenv import load_dotenv

# Подгружаем файл с переменными из .env
load_dotenv()

# bot = discord.Bot(debug_guilds=[1126110667666108487])
bot = discord.Bot()


@bot.event
async def on_ready():
    """Событие запуска бота"""
    print("Бот подключился к Discord API")


@bot.command()
async def reload_extention(ctx: discord.ApplicationContext):
    """Команда перезагружает остальные команды после внесенных изменений"""
    bot.reload_extension('commands')
    bot.reload_extension('buttons')
    await ctx.respond('Extension reloaded')

bot.load_extension('commands')
bot.load_extension('buttons')
bot.load_extension('select_menus')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
