
button.style = discord.ButtonStyle.blurple
name = interaction.user.display_name
original_label = button.label.split()
current_label = Decimal(original_label[0])
if Decimal('100') <= current_label < Decimal('900'):
    current_label += Decimal('100')
    button.label = f'{current_label} K {name}'
elif current_label >= Decimal('900'):
    current_label += Decimal('100')
    current_label /= Decimal('1000')
    button.label = f'{round(current_label)} M {name}'
else:
    current_label += Decimal('0.1')
    button.label = f'{current_label} M {name}'
await interaction.response.edit_message(view=view)