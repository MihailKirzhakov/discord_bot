import discord
import os
import logging
# from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from role_application.role_application import (
     has_required_role, answer_if_no_role
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    encoding='utf-8',
    format=(
        '%(asctime)s | [%(filename)s:%(name)s:%(lineno)d] | %(levelname)s = %(message)s'
    ),
)

main_logger = logging.getLogger('main')
# main_logger.setLevel(logging.INFO)
# format = (
#         '%(asctime)s | [%(filename)s:%(name)s:%(lineno)d] | %(levelname)s = %(message)s'
#     )
# handler = RotatingFileHandler(
#     'main.log', maxBytes=50000000,
#     backupCount=5, encoding='utf-8', errors='backslashreplace'
# )
# handler.setFormatter(logging.Formatter(format))
# main_logger.addHandler(handler)

bot = discord.Bot()
if os.getenv('DEBUG_SERVER_ID'):
    bot = discord.Bot(debug_guilds=[int(os.getenv('DEBUG_SERVER_ID'))])


@bot.event
async def on_ready():
    """Событие запуска бота"""
    main_logger.info('Бот запущен и готов к работе!')


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
        main_logger.info('Расширения перезагружены')
    else:
        await answer_if_no_role(ctx)
        main_logger.error(
            f'{ctx.user.display_name} попытался '
            'использовать команду /reload_extentions!'
        )


bot.load_extension('regular_commands.regular_commands')
bot.load_extension('auc_buttons.auc_buttons')
bot.load_extension('role_application.role_application')
main_logger.info('Приложения запущены')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
