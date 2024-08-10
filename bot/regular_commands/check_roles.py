import discord
from discord.ui import View, button
from .embeds import removed_role_list_embed
from loguru import logger


removed_role_members: list[str] = []
embed: discord.Embed = removed_role_list_embed()


class CheckRoleButton(View):
    """
    Кнопка для дальнейшей чистки ролей.

    Attributes:
    ----------
        embed: discord.Embed
            Встраиваемое сообщение.
    """
    def __init__(
        self,
        members: list[discord.Member],
        sergaunt_role: discord.Role,
        guest_role: discord.Role,
        guild_member_list: list[str]
    ):
        super().__init__(timeout=None)
        self.members = members
        self.sergaunt_role = sergaunt_role
        self.guest_role = guest_role
        self.guild_member_list = guild_member_list

    @button(label='Почистить роли', style=discord.ButtonStyle.green)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            for member in self.members:
                if self.sergaunt_role in member.roles and member.display_name not in self.guild_member_list:
                    removed_role_members.append(member.display_name)
                    await member.remove_roles(self.sergaunt_role)
                    await member.add_roles(self.guest_role)
                logger.info(f'У пользователя {member.display_name} забрали старшину!')
            embed.description += '\n_'.join(f'_{member}_' for member in removed_role_members)
            await interaction.respond(embed=embed, ephemeral=True)
        except Exception as error:
            logger.error(f'Ошибка при вводе данных по поводу чистки ролей! "{error}"')
