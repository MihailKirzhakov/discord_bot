import os
from datetime import datetime

import discord
from dotenv import load_dotenv
from loguru import logger

from regular_commands.embeds import remind_send_embed
from regular_commands.functions import delete_remind_from_db, cursor
from regular_commands.randomaizer import RandomButton
from regular_commands.rename_request import RenameButton
from role_application.role_application import (
    ApplicationButton, has_required_role, answer_if_no_role
)
from variables import APPLICATION_CHANNEL_ID

load_dotenv()

logger.remove()
logger.add(
    sink='discord_bot.log', level=10, rotation='5 MB', mode='a'
)

bot = discord.Bot()
if os.getenv('DEBUG_SERVER_ID'):
    bot = discord.Bot(debug_guilds=[int(os.getenv('DEBUG_SERVER_ID'))])


@bot.event
async def on_ready() -> None:
    """Событие запуска бота"""
    app_channel = await bot.fetch_channel(APPLICATION_CHANNEL_ID)
    bot.add_view(RandomButton())
    bot.add_view(RenameButton(channel=app_channel))
    bot.add_view(ApplicationButton(channel=app_channel))
    logger.info('Бот запущен и готов к работе!')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminds
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, remind_date TEXT)
    ''')
    cursor.execute('SELECT * FROM reminds ORDER BY remind_date ASC')
    reminds = cursor.fetchall()

    for remind in reminds:
        _, user_id, message, remind_date = remind
        remind_date = datetime.strptime(remind_date, '%Y-%m-%d %H:%M:%S')
        if remind_date < datetime.now():
            remind_date = remind_date.replace(year=(datetime.now().year) + 1)
        await discord.utils.sleep_until(remind_date)
        user = await bot.fetch_user(user_id)
        if user:
            await user.send(
                embed=remind_send_embed(
                    discord.utils.format_dt(remind_date, style="F"), message
                ),
                delete_after=300
            )
            logger.info(
                f'Напоминание отправлено пользователю {user.display_name} '
                f'после проверки БД.'
            )
            delete_remind_from_db(user_id, remind_date)
        else:
            logger.error(f'Пользователь с данным ID {user_id} не найден')


@bot.command()
async def reload_extentions(ctx: discord.ApplicationContext) -> None:
    """
    Команда для перезагрузки расширений.

    Parameters
    ----------
        ctx: discord.ApplicationContext
            Контекст команды.

    Returns
    -------
        None
    """
    if has_required_role(ctx.user):
        bot.reload_extension('regular_commands.regular_commands')
        bot.reload_extension('auc_buttons.auc_buttons')
        bot.reload_extension('role_application.role_application')
        await ctx.respond(
            '_Расширения перезагружены!_',
            ephemeral=True,
            delete_after=10
        )
        logger.info('Расширения перезагружены')
    else:
        await answer_if_no_role(ctx)
        logger.error(
            f'_{ctx.user.display_name} попытался '
            'использовать команду /reload_extentions!_'
        )


bot.load_extension('regular_commands.regular_commands')
bot.load_extension('auc_buttons.auc_buttons')
bot.load_extension('role_application.role_application')
logger.info('Приложения запущены')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
