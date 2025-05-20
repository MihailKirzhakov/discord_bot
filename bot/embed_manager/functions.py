import discord

from variables import VETERAN_ROLE, OFICER_ROLE


async def validate_amount(
    value: str,
    interaction: discord.Interaction,
    is_banner: bool = True
):
    error_message = (
        f'❌\n_Значение должно быть числом от 1 до {30 if is_banner else 10}!_'
    )

    max_value = 30 if is_banner else 10
    if value.isdigit():
        amount = int(value)
        if 0 < amount < max_value:
            return amount
    return await interaction.respond(error_message, delete_after=3)


async def generate_member_list(
    nicknames: list,
    interaction: discord.Interaction
) -> str:
    member_list = '_'
    members: list[discord.Member] = interaction.guild.members
    roles: list[discord.Role] = interaction.guild.roles
    veteran_role: discord.Role | None = discord.utils.get(
        roles, name=VETERAN_ROLE
    )
    oficer_role: discord.Role | None = discord.utils.get(
        roles, name=OFICER_ROLE
    )
    miss_count = 0

    for index, nickname in enumerate(nicknames, start=1):
        member: discord.Member | None = discord.utils.get(
            members,
            display_name=nickname
        )
        if member:
            if (
                veteran_role in member.roles
                or oficer_role in member.roles
                and nickname != 'СашаЖмуров'
            ):
                miss_count += 1
                continue
        member_list += f'{index - miss_count}. {nickname}'
        miss_count = 0
        if member:
            member_list += f' | Discord: {member.mention}'
        member_list += '\n'
    member_list += '_'

    return member_list
