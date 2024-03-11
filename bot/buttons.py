import discord
from discord.ext import commands
from discord.ui import button, View


class AucButton(View):

    def __init__(
            self,
            timeout: float | None = None,
    ):
        super().__init__(
            timeout=timeout,
        )

    @button(label='300', style=discord.ButtonStyle.green)
    async def callback(self, button, interaction: discord.Interaction):
        button.label = '400'
        button.style = discord.ButtonStyle.blurple
        await interaction.respond('Test')


@commands.slash_command()
async def go_auc(ctx: discord.ApplicationContext):
    await ctx.respond(view=AucButton())


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
