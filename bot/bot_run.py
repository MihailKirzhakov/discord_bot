import discord
from loguru import logger

from core import settings
from core.orm import async_orm, role_app_orm
from randomaizer.randomaizer import RandomButton
from rename_request.rename_request import RenameButton, AccessDeniedView
from role_application.role_application import (
    ApplicationButton, has_required_role
)
from rcd_aplication.rcd_aplication import (
    StartRCDButton, CreateRCDList, AddMemberToListButton, PrivateMessageView
)
from role_application.role_application import RoleButton
from set_group.set_group import SetGroupButton, EditGroupButton
from core import APPLICATION_CHANNEL_ID, ANSWERS_IF_NO_ROLE, INDEX_CLASS_ROLE


logger.remove()
logger.add(
    sink='discord_bot.log', level=10, rotation='5 MB', mode='a'
)

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)
if settings.debug_server_id:
    bot = discord.Bot(intents=intents, debug_guilds=[settings.debug_server_id])


@bot.event
async def on_ready() -> None:
    """Событие запуска бота"""

    await async_orm.create_tables()
    app_channel = await bot.fetch_channel(APPLICATION_CHANNEL_ID)
    bot.add_view(RandomButton())
    bot.add_view(RenameButton(channel=app_channel))
    bot.add_view(ApplicationButton(channel=app_channel))
    bot.add_view(AccessDeniedView())
    bot.add_view(SetGroupButton())
    bot.add_view(EditGroupButton())
    bot.add_view(StartRCDButton())
    bot.add_view(PrivateMessageView())
    create_rcd_list_view = CreateRCDList()
    for index, role in INDEX_CLASS_ROLE.items():
        create_rcd_list_view.add_item(AddMemberToListButton(
            label=f'Редактировать "{role[:-2]}ов"',
            custom_id=f'{index}КнопкаДобавления'
        ))
    bot.add_view(create_rcd_list_view)
    cstm_btn_ids = await role_app_orm.get_btn_cstm_ids()
    for id in cstm_btn_ids:
        acc_btn_cstm_id, den_btn_cstm_id = id
        bot.add_view(RoleButton(acc_btn_cstm_id, den_btn_cstm_id))
    logger.info('Бот запущен и готов к работе!')


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
bot.load_extension('build_embeds.embed_manager')
bot.load_extension('rcd_aplication.rcd_aplication')
bot.load_extension('reminder.reminder')
bot.load_extension('randomaizer.randomaizer')
bot.load_extension('auction.auc_buttons')
bot.load_extension('role_application.role_application')
bot.load_extension('set_group.set_group')
logger.info('Приложения запущены')


if __name__ == '__main__':
    bot.run(settings.token)
