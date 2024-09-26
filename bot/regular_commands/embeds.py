import discord

from variables import (
    ATTENTION, GUILD_IMAGE_URL,
    SMALL_GUILD_ICON_URL, TEСHNICAL_WORKS, WRENCH_IMAGE_URL,
    REMIND, REMIND_IMAGE_URL, TO_REMIND,
)


def technical_works_embed() -> discord.Embed:
    """
    Функция для создания вложения с информацией о технических работах.
    """
    embed = discord.Embed(
        title='_Kavo4avoBot_',
        color=0xfffb00
    )
    embed.add_field(
        name='_Технические работы..._',
        value=TEСHNICAL_WORKS,
        inline=False
    )
    embed.set_thumbnail(url=WRENCH_IMAGE_URL)
    embed.set_image(url=GUILD_IMAGE_URL)
    return embed








def removed_role_list_embed() -> discord.Embed:
    """
    Функция для создания вложения почищеных ролей.
    """
    embed = discord.Embed(
        title=ATTENTION,
        description='_**Список пользователей, у которых забрали роль старшина:**_\n\n',
        color=0xfffb00
    )
    embed.set_thumbnail(url=SMALL_GUILD_ICON_URL)
    return embed
