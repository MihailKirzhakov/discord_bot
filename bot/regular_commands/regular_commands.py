from datetime import datetime
import re

import discord
from discord.ext import commands
from discord.ui import InputText, Modal
from loguru import logger

from .functions import add_remind_to_db, delete_remind_from_db
from .embeds import (
    technical_works_embed, attention_embed, remind_embed,
    remind_send_embed, removed_role_list_embed
)
from .randomaizer import RandomButton
from .rename_request import RenameButton
from .rcd_aplication import RcdDate
from variables import (
    LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE,
    CLOSED_JMURENSKAYA, CLOSED_ORTHODOX,
    CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT,
    BUHLOID_ID, IDOL_ID, KVAPA_ID, GOOSE_ID,
    SERGEANT_ROLE, VETERAN_ROLE, GUEST_ROLE
)


class StartRemindModal(Modal):
    """
    Модальное окно для ввода данных напоминания.
    """
    def __init__(self):
        super().__init__(title='Параметры напоминания', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи содержание сообщения',
                placeholder='Не более 500 символов',
                max_length=500
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи дату отправки в формате "ДД.ММ"',
                placeholder='ДД.ММ',
                max_length=5
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи время отправки в формате "ЧЧ:ММ"',
                placeholder='ЧЧ:ММ',
                max_length=5
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=False, ephemeral=True)
        message: str = str(self.children[0].value)
        date_str: str = str(self.children[1].value)
        time_str: str = str(self.children[2].value)

        # Регулярное выражение для проверки даты в формате ДД.ММ
        date_pattern = r'^([0-2][0-9]|3[0-1])[.,/](0[1-9]|1[0-2])$'
        date_match = re.match(date_pattern, date_str)

        # Регулярное выражение для проверки времени в формате ЧЧ:ММ
        time_pattern = r'^([0-1][0-9]|2[0-3])[:;]([0-5][0-9])$'
        time_match = re.match(time_pattern, time_str)

        if not date_match:
            return await interaction.respond(
                'Неправильный формат даты. Пожалуйста, используйте формат ДД.ММ',
                delete_after=10
            )

        if not time_match:
            return await interaction.respond(
                'Неправильный формат времени. Пожалуйста, используйте формат ЧЧ:ММ',
                delete_after=10
            )

        try:
            day, month = map(int, date_match.groups())
            hour, minute = map(int, time_match.groups())
            current_year = datetime.now().year
            remind_date = datetime(
                year=current_year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
            )
            if remind_date < datetime.now():
                remind_date = remind_date.replace(year=current_year + 1)
            convert_remind_date = discord.utils.format_dt(remind_date, style="F")
            add_remind_to_db(interaction.user.id, message, remind_date)
            await interaction.respond(
                embed=remind_embed(convert_remind_date, message),
                delete_after=20
            )
            logger.info(
                f'Пользователь {interaction.user.display_name} создал напоминалку'
                f'на {remind_date}!'
            )
            await discord.utils.sleep_until(remind_date)
            try:
                await interaction.user.send(
                    embed=remind_send_embed(convert_remind_date, message),
                    delete_after=300
                )
                logger.info(
                    f'Пользователь {interaction.user.display_name} получил напоминалку!'
                )
            except discord.Forbidden:
                logger.warning(f'Пользователю "{interaction.user.display_name}" запрещено отправлять сообщения')
            delete_remind_from_db(interaction.user.id, remind_date)
        except Exception as error:
            await interaction.respond(
                f'Произошла ошибка при создании напоминания. {error}',
                ephemeral=True
            )
            logger.error(
                f'Пользователь {interaction.user.display_name} попытался сделать напоминание '
                f'но получил ошибку {error}!'
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
async def attention(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить сообщение?',
        name_localizations={'ru':'текстовый_канал'},
    ),  # type: ignore
    value: discord.Option(
        str,
        description='Введи текст сообщения',
        name_localizations={'ru':'текст'},
    )  # type: ignore
) -> None:
    """
    Команда для отправки сообщения с пометкой 'Внимание!'.
    """
    await channel.send(embed=attention_embed(value=value))
    logger.info(
        f'Команда "/attention" вызвана пользователем '
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )
    await ctx.respond(
        f'_Сообщение отправлено в канал {channel.mention}!_',
        ephemeral=True,
        delete_after=3
    )


@attention.error
async def attention_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды attention.
    """
    await command_error(ctx, error, "attention")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def random(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'}
    ), # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки рандомайзера.
    """
    try:
        if message_id:
            message = ctx.channel.get_partial_message(int(message_id))
            await message.edit(view=RandomButton())
            await ctx.respond(
                f'_Кнопка рандомайзера обновлена и снова работает в '
                f'канале {channel.mention}!_',
                ephemeral=True,
                delete_after=3
            )
        else:
            await channel.send(view=RandomButton())
            await ctx.respond(
                f'_Кнопка рандомайзера отправлена в канал '
                f'{channel.mention}!_',
                ephemeral=True,
                delete_after=3
            )
        logger.info(
            f'Команда "/random" вызвана пользователем'
            f'"{ctx.user.display_name}" в канал "{channel}"!'
        )
    except Exception as error:
        await ctx.respond(
            'Неверные данные, попробуй снова!',
            ephemeral=True,
            delete_after=3
        )
        logger.error(
            f'При запуске команды /random возникла ошибка '
            f'"{error}"!'
        )


@random.error
async def random_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды random.
    """
    await command_error(ctx, error, "random")


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
        await ctx.respond(
            f'_При использовании команды "clear_all" в канале '
            f'{channel} возникла ошибка: "{error}"!_',
            ephemeral=True
        )
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
    LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE, SERGEANT_ROLE, VETERAN_ROLE
)
async def remind(ctx: discord.ApplicationContext) -> None:
    """
    Команда для отправки сообщения с напоминанием.
    """
    try:
        await ctx.response.send_modal(StartRemindModal())
    except Exception as error:
        logger.error(
                f'При попытке запустить аукцион командой /remind '
                f'возникло исключение "{error}"'
            )


@remind.error
async def remind_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды remind.
    """
    await command_error(ctx, error, "remind")


@commands.slash_command()
@commands.has_any_role(
    CLOSED_JMURENSKAYA, CLOSED_ORTHODOX,
    CLOSED_GOOSE_HOME, CLOSED_ON_THE_MIND_ASPECT
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
    Команда для отправки кнопки на выдачу роли.
    """
    closed_jmurenskaya = discord.utils.get(
            ctx.guild.roles, name=CLOSED_JMURENSKAYA)
    closed_orthodox = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ORTHODOX)
    closed_goose_home = discord.utils.get(
            ctx.guild.roles, name=CLOSED_GOOSE_HOME)
    closed_on_the_mind_aspect = discord.utils.get(
            ctx.guild.roles, name=CLOSED_ON_THE_MIND_ASPECT)
    check_group_leaders = {
        BUHLOID_ID: closed_jmurenskaya,
        IDOL_ID: closed_orthodox,
        GOOSE_ID: closed_goose_home,
        KVAPA_ID: closed_on_the_mind_aspect
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
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rename(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Куда отправить кнопку?',
        name_localizations={'ru':'текстовый_канал'}
    ),  # type: ignore
    message_id: discord.Option(
        str,
        description='ID сообщения, в котором есть кнопка кнопка',
        name_localizations={'ru':'id_сообщения'},
        required=False
    )  # type: ignore
) -> None:
    """
    Команда для отправки кнопки рандомайзера.
    """
    if message_id:
        message = ctx.channel.get_partial_message(int(message_id))
        await message.edit(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера обновлена и снова работает!_',
            ephemeral=True,
            delete_after=3
        )
    else:
        await ctx.respond(view=RenameButton(channel=channel))
        await ctx.respond(
            '_Кнопка ренеймера запущена!_',
            ephemeral=True,
            delete_after=3
        )
    logger.info(
        f'Команда "/rename" вызвана пользователем'
        f'"{ctx.user.display_name}" в канал "{channel}"!'
    )


@rename.error
async def rename_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды rename.
    """
    await command_error(ctx, error, "rename")


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rcd_application(ctx: discord.ApplicationContext) -> None:
    """
    Команда для запуска кнопки старта РЧД заявок.
    """
    try:
        await ctx.response.send_modal(RcdDate())
        logger.info(
            f'Команда "/rcd_application" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/rcd_application"! '
            f'"{error}"'
        )


@rcd_application.error
async def rcd_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обработчик ошибок для команды rcd_application.
    """
    await command_error(ctx, error, "rcd_application")


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
        lines = (await attachment.read()).decode('windows-1251').splitlines()
        sergaunt_role: discord.Role = discord.utils.get(ctx.guild.roles, name=SERGEANT_ROLE)
        guest_role: discord.Role = discord.utils.get(ctx.guild.roles, name=GUEST_ROLE)
        veteran_role: discord.Role = discord.utils.get(ctx.guild.roles, name=VETERAN_ROLE)
        for line in lines:
            parts = line.split(';')
            if len(parts) > 2:
                guild_member_list.append(parts[2])
        for member in members:
            if (sergaunt_role in member.roles or veteran_role in member.roles) and re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9]', '', member.display_name) not in guild_member_list:
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


def setup(bot: discord.Bot):
    bot.add_application_command(technical_works)
    bot.add_application_command(attention)
    bot.add_application_command(random)
    bot.add_application_command(clear_all)
    bot.add_application_command(remind)
    bot.add_application_command(give_role_to)
    bot.add_application_command(rename)
    bot.add_application_command(rcd_application)
    bot.add_application_command(check_roles)
