import discord
from discord.ui import Modal, InputText, View, button

from .embeds import number_range, nickname_range
from .functions import rand_choice
from variables import DEAFAULT_RANDOMISE_VALUE, WRONG_PARMS


class RandomModal(Modal):
    """
    Модальное окно для ввода значения,
    диапазон чисел или никнеймы через разделитель.

    Returns:
    --------
        None
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Рандомайзер', timeout=None)

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
            if not rand_choice(DEAFAULT_RANDOMISE_VALUE):
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
            if not rand_choice(self.children[0].value):
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


class RandomButton(View):
    """
    Кнопка для запуска модального окна рандомайзера.

    Returns:
    --------
        None
    """
    def __init__(
            self,
            timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
        label='Рандомайзер', style=discord.ButtonStyle.green,
        emoji='🎲', custom_id='Рандомайзер'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.response.send_modal(RandomModal())
