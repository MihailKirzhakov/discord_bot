import os

import discord
from dotenv import load_dotenv
from loguru import logger

from role_application.role_application import (
    ApplicationButton, has_required_role, answer_if_no_role
)
from regular_commands.randomaizer import RandomButton
from regular_commands.rename_request import RenameButton
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
    get_channel_object = await bot.fetch_channel(APPLICATION_CHANNEL_ID)
    bot.add_view(RandomButton())
    bot.add_view(RenameButton(channel=get_channel_object))
    bot.add_view(ApplicationButton(channel=get_channel_object))
    logger.info('Бот запущен и готов к работе!')


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
