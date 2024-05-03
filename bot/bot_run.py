import discord
import os
from dotenv import load_dotenv

# Подгружаем файл с переменными из .env
load_dotenv()

bot = discord.Bot()
if os.getenv('DEBUG_SERVER_ID'):
    bot = discord.Bot(debug_guilds=[int(os.getenv('DEBUG_SERVER_ID'))])


@bot.event
async def on_ready():
    """Событие запуска бота"""
    print("Бот подключился к Discord API")


@bot.command()
async def reload_extention(ctx: discord.ApplicationContext):
    """Команда перезагружает остальные команды после внесенных изменений"""
    bot.reload_extension('regular_commands.regular_commands')
    bot.reload_extension('auc_buttons.auc_buttons')
    bot.reload_extension('role_application.role_application')
    await ctx.respond('Extension reloaded')

bot.load_extension('regular_commands.regular_commands')
bot.load_extension('auc_buttons.auc_buttons')
bot.load_extension('role_application.role_application')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
