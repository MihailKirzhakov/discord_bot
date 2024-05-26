import discord
import os

from dotenv import load_dotenv

from role_application.role_application import (
     has_required_role, answer_if_no_role
)

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
async def reload_extentions(ctx: discord.ApplicationContext):
    """
    Команда для перезагрузки расширений.

    :param ctx: Контекст команды.
    :param channel: Текстовый канал, в который нужно отправить сообщение.
    :return: None
    """
    if has_required_role(ctx.user):
        bot.reload_extension('regular_commands.regular_commands')
        bot.reload_extension('auc_buttons.auc_buttons')
        bot.reload_extension('role_application.role_application')
        await ctx.respond(
            'Расширения перезагружены',
            ephemeral=True,
            delete_after=10
        )
    else:
        await answer_if_no_role(ctx)


bot.load_extension('regular_commands.regular_commands')
bot.load_extension('auc_buttons.auc_buttons')
bot.load_extension('role_application.role_application')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
