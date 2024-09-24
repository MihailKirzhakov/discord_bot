import discord
from discord.ext import commands
from discord.ui import View, button, select
from loguru import logger

from variables import (
    LEADER_ROLE, TREASURER_ROLE, OFICER_ROLE,
    VETERAN_ROLE, SERGEANT_ROLE, LEADER_ID
)
from .embeds import set_group_embed, set_group_discription_embed


class EditGroupButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(
        label='Редактировать группу', style=discord.ButtonStyle.blurple,
        emoji='🔁', custom_id='РедактированиеГруппы'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            interaction_message_embed: discord.Embed = interaction.message.embeds[0]
            interaction_message: discord.Message = interaction.message

            if (
                interaction.user.mention in interaction_message_embed.description
                or interaction.user.id == int(LEADER_ID)
            ):
                return await interaction.respond(
                    view=SetGroup(
                        if_edit=True,
                        message_embed=interaction_message_embed,
                        interaction_message=interaction_message
                    ),
                    ephemeral=True,
                    delete_after=60
                )

            await interaction.respond(
                '_Редактировать группу может только КПЛ ❌_',
                ephemeral=True,
                delete_after=2
            )
        except Exception as error:
            logger.error(
                f'При попытке вызвать модальное окно нажатием на кнопку '
                f'"{button.label}" возникла ошибка "{error}"'
            )


class SetGroup(View):
    """Модальное окно для админа, чтобы создать КПла"""
    def __init__(
        self, if_edit: bool = False,
        message_embed: discord.Embed = None,
        interaction_message: discord.Message = None
    ):
        super().__init__(timeout=None)
        self.if_edit = if_edit
        self.message_embed = message_embed
        self.interaction_message = interaction_message

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=6,
        placeholder='Выбери игроков'
    )
    async def callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            embed: discord.Embed = set_group_embed()
            if self.if_edit:
                embed: discord.Embed = self.message_embed
                embed.fields[0].value = ''

            if not self.if_edit:
                group_leader: discord.User = (
                    select.values[0] if interaction.user.id == int(LEADER_ID) else interaction.user
                )
                embed.description += f'1. {group_leader.mention}'

            members = [
                value.mention for value in (
                    select.values[1:] if interaction.user.id == int(LEADER_ID)
                    and not self.if_edit else select.values
                )
            ]

            member_list = '\n'.join(f'{i+2}. {member}' for i, member in enumerate(members))
            embed.fields[0].value += member_list

            if self.if_edit:
                await self.interaction_message.edit(embed=embed)
            else:
                await interaction.channel.send(
                    view=EditGroupButton(),
                    embed=embed
                )

            await interaction.respond('✅', delete_after=1)
            logger.info(
                f'Группа создана пользователем {interaction.user.display_name}'
            )
        except Exception as error:
            logger.error(
                f'При попытке создания группы пользователем {interaction.user.display_name} '
                f'возникла ошибка {error}'
            )


class SetGroupButton(View):
    """Кнопка для создания группы"""
    def __init__(self):
        super().__init__(timeout=None)

    @button(
        label='Создать группу', style=discord.ButtonStyle.green,
        emoji='📋', custom_id='СозданиеГруппы'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.respond(view=SetGroup(), ephemeral=True)
        except Exception as error:
            logger.error(
                f'При попытке вызвать модальное окно нажатием на кнопку '
                f'"{button.label}" возникла ошибка "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(
    LEADER_ROLE, TREASURER_ROLE, OFICER_ROLE,
    VETERAN_ROLE, SERGEANT_ROLE
)
async def set_group(ctx: discord.ApplicationContext) -> None:
    """
    Команда для вызова кнопки, которая создаёт группу.
    """
    try:
        await ctx.respond(
            embed=set_group_discription_embed(),
            view=SetGroupButton()
        )
        await ctx.respond(
            '_Кнопка подачи заявок запущена!_',
            ephemeral=True,
            delete_after=2
        )
        logger.info(
            f'Команда "/set_group" вызвана пользователем '
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'При попытке вызвать команду /set_group'
            f'возникла ошибка "{error}". Команду попытался вызвать пользователь '
            f'"{ctx.user.display_name}".'
        )


@set_group.error
async def role_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обрабатывать ошибки, возникающие
    при выполнении команды запросов на выдачу доступа.
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Согильдеец"!',
            ephemeral=True,
            delete_after=10
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=10
        )
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(set_group)
