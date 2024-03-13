#         user_name = interaction.user.display_name
#         thousand = 'K'
#         million = 'M'
#         original_label = button.label.split()
#         current_label = float(original_label[0])
#         if 300 <= current_label < 900:
#             current_label += 100
#             button.label = f'{int(current_label)} {thousand} {user_name}'
#         elif current_label == 900:
#             current_label += 100
#             current_label /= 1000
#             button.label = f'{round(current_label)} {million} {user_name}'
#         else:
#             current_label += 0.1
#             if current_label.is_integer():
#                 button.label = f'{round(current_label)} {million} {user_name}'
#             else:
#                 button.label = f'{round(current_label, 1)} {million} {user_name}'
#         button.style = discord.ButtonStyle.blurple
#         await interaction.response.edit_message(view=self)