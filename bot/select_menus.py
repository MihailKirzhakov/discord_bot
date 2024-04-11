import discord

from discord.ext import commands
from discord.ui import Modal, InputText, View, button
from discord.ui.item import Item


class DominionApplication(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Заявка на РЧД')

        self.add_item(
            InputText(
                label='Укажи, сколько чести сейчас?',
                placeholder='350'
            )
        )

        self.add_item(
            InputText(
                label='На каком классе можешь отыграть?',
                placeholder='шаман/жрец'
            )
        )

        self.add_item(
            InputText(
                label='Какая накидка сейчас на тебе?',
                placeholder='красная'
            )
        )

    async def callback(self, interaction: discord.Interaction):
        name = interaction.user.mention
        honor = self.children[0].value
        class_name = self.children[1].value
        clothing = self.children[2].value

        await interaction.response.send_message(
            f'**принял заявку на РЧД**\n'
            f'{name} _**записался на РЧД**_\n'
            f'**ЧЕСТЬ**: {honor}\n'
            f'**КЛАСС/КЛАССЫ**: {class_name}\n'
            f'**НАКИДКА**: {clothing}'
        )


class ApplicationView(View):
    def __init__(self, timeout: float | None = 180):
        super().__init__(timeout=timeout)


    @button(label='Записаться на РЧД', style=discord.ButtonStyle.green, emoji='📋')
    async def callback(self, button: discord.ui.Button, interaction: discord.Integration):
        await interaction.response.send_modal(DominionApplication())


@commands.slash_command()
@commands.has_any_role('📣Казначей📣', '🛡️Офицер🛡️')
async def rcd(ctx: discord.ApplicationContext):
    """Команда для запуска кнопки заявки на РЧД"""
    await ctx.respond('**Форма для заполнения заявки на РЧД**', view=ApplicationView())


@rcd.error
async def go_auc_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond('Команду может вызвать только руководство!')
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond('Команду нельзя вызывать в личные сообщения бота!')
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(rcd)
