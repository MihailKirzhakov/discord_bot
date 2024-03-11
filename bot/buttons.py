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
        user_name = interaction.user.display_name
        current_label = float(button.label.split()[0])
        if 300 <= current_label < 900:
            current_label += 100
            button.label = f'{current_label} K {user_name}'
        elif current_label == 900:
            current_label += 100
            button.label = f'{current_label / 1000} M {user_name}'
        else:
            current_label *= 1000
            current_label += 100
            button.label = f'{current_label / 1000} M {user_name}'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=self)


@commands.slash_command()
async def go_auc(ctx: discord.ApplicationContext):
    await ctx.respond(view=AucButton())


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
