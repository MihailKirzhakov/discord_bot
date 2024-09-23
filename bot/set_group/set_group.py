import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button, select
from loguru import logger

from variables import (
    LEADER_ROLE, TREASURER_ROLE, OFICER_ROLE,
    VETERAN_ROLE, SERGEANT_ROLE, LEADER_ID
)
from .embeds import set_group_embed, set_group_discription_embed


class EditGroupButton(View):
    def __init__(
        self,
    ):
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
            guild_leader = discord.utils.get(interaction.guild.members, id=int(LEADER_ID))
            interaction_message_embed: discord.Embed = interaction.message.embeds[0]

            if (
                interaction.user.mention in interaction_message_embed.description
                or interaction.user == guild_leader
            ):
                return await interaction.response.send_modal(SetGroupModal(if_edit=True))

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


class LeaderSetGroup(View):
    """Модальное окно для админа, чтобы создать КПла"""
    def __init__(self):
        super().__init__(timeout=None)

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=6,
        placeholder='Выбери КПла'
    )
    async def callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            group_leader: discord.User = select.values[0]
            embed: discord.Embed = set_group_embed()
            embed.description += f'1. {group_leader.mention}'

            for i, child in enumerate(select.values, start=2):
                user_nick: child.value
                user_mention: str = user_nick.mention if user_nick else 'Вакансия'
                embed.fields[0].value += f'{i}. {user_mention}\n'

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


class SetGroupModal(Modal):
    """Модальное окно для указания игроков"""
    def __init__(self, if_edit: bool = False):
        super().__init__(
            title='Впиши никнеймы своих соКП, себя НЕ надо!',
            timeout=None
        )
        self.if_edit = if_edit

        for i in range(5):
            self.add_item(
                    InputText(
                        style=discord.InputTextStyle.short,
                        label=f'{i + 2} игрок',
                        placeholder='Длина никнейма как в игре 3-14 символов',
                        min_length=3,
                        max_length=14,
                        required=False
                    )
                )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            group_leader: discord.User = interaction.user
            embed: discord.Embed = set_group_embed()
            embed.description += f'1. {group_leader.mention}'

            if self.if_edit:
                embed: discord.Embed = interaction.message.embeds[0]
                embed.fields[0].value = ''

            for i, child in enumerate(self.children, start=2):
                user_nick: discord.User = discord.utils.get(interaction.guild.members, display_name=child.value)
                user_mention: str = user_nick.mention if user_nick else 'Вакансия'
                embed.fields[0].value += f'{i}. {user_mention}\n'

            if self.if_edit:
                await interaction.message.edit(embed=embed)
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
            if interaction.user.id == int(LEADER_ID):
                await interaction.respond(
                    view=LeaderSetGroup(), ephemeral=True
                )
            await interaction.response.send_modal(SetGroupModal())
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
