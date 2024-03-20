class AucButton(discord.ui.View):
    def __init__(self, count, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _ in range(count):
            btn = discord.ui.Button(label="Click me!")
            btn.callback = self.custom_callback(btn)
            self.add_item(btn)

    @staticmethod
    def custom_callback(button: discord.ui.Button):
        async def inner(interaction: discord.Interaction):
            button.label = interaction.user.display_name
            await interaction.edit_original_message(view=button.view)
        return inner