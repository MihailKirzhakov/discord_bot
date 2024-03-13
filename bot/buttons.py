import discord
from discord.ext import commands
from discord.ui import View
from discord.ui.item import Item


class AucButton(View):
    def __init__(
            self,
            *items: Item,
            timeout: float | None = None,
            disable_on_timeout: bool = False,
            count: int
    ):
        super().__init__(
            *items,
            timeout=timeout,
            disable_on_timeout=disable_on_timeout
        )
        self.count = count

    for i in range(self.count):
        @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary)
        async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
            button.label = interaction.user.display_name
            await interaction.response.edit_message(view=self)


@commands.slash_command()
async def go_auc(ctx: discord.ApplicationContext, count: int):
    await ctx.respond(view=AucButton(count=count))


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)
