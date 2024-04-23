import discord

from discord.ui import Modal, InputText, View, button

from regular_commands.embeds import number_range, nickname_range
from regular_commands.functions import rand_choice
from regular_commands.variables import DEAFAULT_RANDOMISE_VALUE, WRONG_PARMS


class RoleApplication(Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Рандомайзер')

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Параметры для рандомайзера',
                placeholder='Необязательно(если пусто то, рандом число 1-100)',
                max_length=1000,
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        if len(self.children[0].value) == 0:
            if rand_choice(DEAFAULT_RANDOMISE_VALUE) is None:
                return await interaction.respond(
                    WRONG_PARMS,
                    ephemeral=True,
                    delete_after=15
                )
            return await interaction.respond(
                embed=number_range(
                    rand_choice(DEAFAULT_RANDOMISE_VALUE),
                    DEAFAULT_RANDOMISE_VALUE
                ),
                delete_after=30
            )
        else:
            if rand_choice(self.children[0].value) is None:
                return await interaction.respond(
                    WRONG_PARMS,
                    ephemeral=True,
                    delete_after=15
                )
            if not isinstance(rand_choice(self.children[0].value), int):
                return await interaction.respond(
                    embed=nickname_range(rand_choice(self.children[0].value)),
                    delete_after=30
                )
            return await interaction.respond(
                embed=number_range(
                    rand_choice(self.children[0].value),
                    self.children[0].value
                ),
                delete_after=30
            )


class ApplicationButton(View):

    def __init__(
            self,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(label='Рандомайзер', style=discord.ButtonStyle.green, emoji='🎲')
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.response.send_modal(RoleApplication())
