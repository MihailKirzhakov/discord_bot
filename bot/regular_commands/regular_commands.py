import re

import discord
from discord.ext import commands
from loguru import logger

from core.orm import AsyncORM
from .embeds import technical_works_embed, removed_role_list_embed
from rcd_aplication.functions import clear_rcd_data
from variables import (
    LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE,
    CLOSED_TOP_4_ICD, CLOSED_MOTHERS, AMARELLA_ID,
    CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT,
    IDOL_ID, KVAPA_ID, GOOSE_ID,
    SERGEANT_ROLE, VETERAN_ROLE, GUEST_ROLE,
    DOBRYAK_ID, CLOSED_ON_GOOD_MOVEMENTS
)


async def command_error(
        ctx: discord.ApplicationContext, error: Exception, command_name: str
) -> None:
    """
    Обработчик ошибок для команд.
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            f'_Команду {command_name} может вызвать только '
            f'"Лидер", "Казначей" или "Офицер"! ❌_',
            ephemeral=True,
            delete_after=10
        )
        logger.info(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}"! '
            f'В результате возникло исключение "{error}"!'
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            f'Команду {command_name} нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=5
        )
        logger.info(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}" в лс! '
            f'В результате возникло исключение "{error}"!'
        )
    else:
        logger.error(
            f'Пользователь "{ctx.user.display_name}" '
            f'пытался вызвать команду "{command_name}"! '
            f'В результате возникло исключение "{error}"!'
        )
        raise error


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def technical_works(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    )  # type: ignore
) -> None:
    """
    Команда для отправки сообщения о технических работах.
    """
    await channel.send(embed=technical_works_embed())
    logger.info(
        f'Команда "/technical_works" вызвана пользователем '
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Сообщение о тех работах отправлено в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=3
    )


@technical_works.error
async def technical_works_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды technical_works.
    """
    await command_error(ctx, error, "technical_works")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def clear_all(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Канал для очистки',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
    limit: discord.Option(
        int,
        description='Кол-во сообщений для удаления',
        name_localizations={'ru':'сколько_удалить'},
        default=100,
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для удаления сообщений в текстовом канале.
    """
    try:
        await ctx.defer(ephemeral=True)
        await channel.purge(
            limit=limit,
            bulk=True
        )
        logger.info(
            f'Команда "/clear_all" вызвана пользователем '
            f'"{ctx.user.display_name}" в канале "{channel}"!'
        )
        await ctx.respond(
            f'_Сообщения удалены в канале {channel.mention}!_',
            delete_after=3
        )
    except Exception as error:
        logger.error(
            f'_При использовании команды "clear_all" в канале '
            f'{channel} возникла ошибка: "{error}"!_'
        )


@clear_all.error
async def clear_all_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды clear_all.
    """
    await command_error(ctx, error, "clear_all")


@commands.slash_command()
@commands.has_any_role(
    CLOSED_TOP_4_ICD, CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT, CLOSED_MOTHERS
)
async def give_role_to(
    ctx: discord.ApplicationContext,
    member: discord.Option(
        discord.Member,
        description='Пользователь дискорда, кому нужна роль',
        name_localizations={'ru':'выбери_пользователя'}
    )  # type: ignore
) -> None:
    """
    Команда для выдачи роли.
    """
    closed_top_4_ICD = discord.utils.get(
            ctx.guild.roles, name=CLOSED_TOP_4_ICD)
    closed_goose_home = discord.utils.get(
            ctx.guild.roles, name=CLOSED_GOOSE_HOME)
    closed_on_the_mind_aspect = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ON_THE_MIND_ASPECT)
    closed_on_good_movements = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ON_GOOD_MOVEMENTS)
    closed_mothers = discord.utils.get(
            ctx.guild.roles, name=CLOSED_MOTHERS)
    check_group_leaders = {
        IDOL_ID: closed_top_4_ICD,
        GOOSE_ID: closed_goose_home,
        KVAPA_ID: closed_on_the_mind_aspect,
        DOBRYAK_ID: closed_on_good_movements,
        AMARELLA_ID: closed_mothers
    }
    try:
        if str(ctx.user.id) in check_group_leaders:
            await member.add_roles(check_group_leaders.get(str(ctx.user.id)))
            await ctx.respond(
                f'_**Роль**\n{check_group_leaders.get(str(ctx.user.id)).mention}\n'
                f'**выдана**\n{member.mention}!_',
                ephemeral=True,
                delete_after=5
            )
            logger.info(
                f'Команда "/give_role_to" вызвана пользователем'
                f'"{ctx.user.display_name}", роль выдана "{member.display_name}"!'
            )
        else:
            await ctx.respond(
                '_У тебя нет доступа к этой команде!_',
                ephemeral=True,
                delete_after=3
            )
    except Exception as error:
        logger.error(f'Ошибка при вызове команды "/give_role_to": {error}')


@give_role_to.error
async def give_role_to_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды random.
    """
    await command_error(ctx, error, "give_role_to")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE)
async def check_roles(
    ctx: discord.ApplicationContext,
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть файл',
        name_localizations={'ru':'id_сообщения'}
    )  # type: ignore
) -> None:
    """
    Команда для проверки ролей на сервере.
    """
    guild_member_list: list[str] = []
    removed_role_members: list[str] = []
    embed: discord.Embed = removed_role_list_embed()
    try:
        await ctx.defer(ephemeral=True)
        members: list[discord.Member] = await ctx.guild.fetch_members(limit=None).flatten()
        checking_message: discord.Message = await ctx.channel.fetch_message(int(message_id))
        attachment = checking_message.attachments[0]
        try:
            lines = (await attachment.read()).decode('windows-1251').splitlines()
        except UnicodeDecodeError as e:
            logger.error(f"Ошибка декодирования файла: {e}")
            return await ctx.respond("Ошибка: файл не может быть прочитан. Проверьте кодировку файла.")
        sergaunt_role: discord.Role = discord.utils.get(ctx.guild.roles, name=SERGEANT_ROLE)
        guest_role: discord.Role = discord.utils.get(ctx.guild.roles, name=GUEST_ROLE)
        veteran_role: discord.Role = discord.utils.get(ctx.guild.roles, name=VETERAN_ROLE)
        for line in lines:
            parts = line.split(';')
            if len(parts) > 2:
                guild_member_list.append(parts[2])
        for member in members:
            if (
                (sergaunt_role in member.roles or veteran_role in member.roles)
                and re.sub(r'[^a-zA-Zа-яА-ЯеЕёЁ0-9]', '', member.display_name)
                not in guild_member_list
            ):
                removed_role_members.append(member.display_name)
                await member.remove_roles(sergaunt_role)
                await member.remove_roles(veteran_role)
                await member.add_roles(guest_role)
                logger.info(f'У пользователя {member.display_name} забрали старшину!')
        embed.description += '\n'.join(f'_{member}_' for member in removed_role_members)
        await ctx.respond(embed=embed)
    except Exception as error:
        logger.error(f'Ошибка при вызове команды "/check_roles"! "{error}"')


@check_roles.error
async def check_roles_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды check_roles.
    """
    await command_error(ctx, error, "check_roles")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def clear_db_data(ctx: discord.ApplicationContext) -> None:
    """
    Команда для очистки базы данных.
    """
    await ctx.defer(ephemeral=True)
    try:
        await AsyncORM.delete_roleapp_data()
        clear_rcd_data()
        await ctx.respond('_Почистил_ ✅', delete_after=2)
        logger.info(
            'Команда "/clear_db_data" вызвана пользователем '
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        await ctx.respond(f'_Ошибка ❌: {error}_')
        logger.error(f'Ошибка при вызове команды "/clear_db_datas"! "{error}"')


@clear_db_data.error
async def clear_db_data_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды clear_db_data.
    """
    await command_error(ctx, error, "clear_db_data")


def setup(bot: discord.Bot):
    bot.add_application_command(technical_works)
    bot.add_application_command(clear_all)
    bot.add_application_command(give_role_to)
    bot.add_application_command(check_roles)
    bot.add_application_command(clear_db_data)
