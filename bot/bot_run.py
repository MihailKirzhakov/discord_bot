import os
from datetime import datetime

import discord
from dotenv import load_dotenv
from loguru import logger

from reminder.functions import send_reminders, cursor
from randomaizer.randomaizer import RandomButton
from rename_request.rename_request import RenameButton
from role_application.role_application import (
    ApplicationButton, has_required_role
)
from set_group.set_group import SetGroupButton, EditGroupButton
from variables import APPLICATION_CHANNEL_ID, ANSWERS_IF_NO_ROLE

load_dotenv()

logger.remove()
logger.add(
    sink='discord_bot.log', level=10, rotation='5 MB', mode='a'
)

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)
if os.getenv('DEBUG_SERVER_ID'):
    bot = discord.Bot(intents=intents, debug_guilds=[int(os.getenv('DEBUG_SERVER_ID'))])


@bot.event
async def on_ready() -> None:
    """Событие запуска бота"""
    app_channel = await bot.fetch_channel(APPLICATION_CHANNEL_ID)
    bot.add_view(RandomButton())
    bot.add_view(RenameButton(channel=app_channel))
    bot.add_view(ApplicationButton(channel=app_channel))
    bot.add_view(SetGroupButton())
    bot.add_view(EditGroupButton())
    logger.info('Бот запущен и готов к работе!')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS date_info
        (date_name TEXT UNIQUE, date TEXT)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rcd_application
        (message_name TEXT UNIQUE, message_id INTEGER)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notice_list
        (action TEXT, role TEXT, members_id TEXT, UNIQUE (action, role) ON CONFLICT REPLACE)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminds
        (user_id INTEGER, message TEXT UNIQUE, remind_date TEXT)
    ''')
    await send_reminders(bot, cursor, logger)


@bot.command()
async def reload_extentions(ctx: discord.ApplicationContext):
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
    if not has_required_role(ctx.user):
        return await ctx.respond(
            ANSWERS_IF_NO_ROLE,
            ephemeral=True,
            delete_after=15
        )
    bot.reload_extension('regular_commands.regular_commands')
    bot.reload_extension('rename_request.rename_request')
    bot.reload_extension('embed_manager.embed_manager')
    bot.reload_extension('randomaizer.randomaizer')
    bot.reload_extension('reminder.reminder')
    bot.reload_extension('rcd_aplication.rcd_aplication')
    bot.reload_extension('auc_buttons.auc_buttons')
    bot.reload_extension('role_application.role_application')
    bot.reload_extension('set_group.set_group')
    await ctx.respond(
        '_Расширения перезагружены!_',
        ephemeral=True,
        delete_after=10
    )
    logger.info('Расширения перезагружены')


bot.load_extension('regular_commands.regular_commands')
bot.load_extension('rename_request.rename_request')
bot.load_extension('embed_manager.embed_manager')
bot.load_extension('rcd_aplication.rcd_aplication')
bot.load_extension('reminder.reminder')
bot.load_extension('randomaizer.randomaizer')
bot.load_extension('auc_buttons.auc_buttons')
bot.load_extension('role_application.role_application')
bot.load_extension('set_group.set_group')
logger.info('Приложения запущены')


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
