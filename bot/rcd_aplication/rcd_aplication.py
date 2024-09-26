from datetime import datetime
import re

import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, button, select
from loguru import logger

from .embeds import (
    start_rcd_embed, rcd_list_embed, ask_veteran_embed,
    final_rcd_list_embed, publish_rcd_embed, rcd_notification_embed,
    second_final_rcd_list_embed, publish_rcd_second_embed
)
from role_application.functions import has_required_role
from variables import (
    VETERAN_ROLE, ANSWERS_IF_NO_ROLE, INDEX_CLASS_ROLE,
    SERGEANT_ROLE, LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE
)


ask_member_list: list[int] = []
member_list: list = []
rcd_date_list: dict[str, str] = {}
embed: dict[str, discord.Embed] = {}
last_message_to_finish: dict[str, discord.Message] = {}
rcd_application_channel: dict[str, discord.TextChannel] = {}
publish_embed: dict[str, discord.Embed] = {}
members_by_roles_attack: dict[str, set[discord.Member]] = {}
members_by_roles_deff: dict[str, set[discord.Member]] = {}
rcd_application_last_message: dict[str, discord.Message] = {}
pub_info: dict[str, bool] = {}


class RcdDate(Modal):
    """
    Модальное окно для ввода даты РЧД.
    """
    def __init__(self):
        super().__init__(title='Введи дату проведения РЧД', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи дату в формате ДД.ММ',
                placeholder='ДД.ММ',
                max_length=5
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=False, ephemeral=True)
        date_str: str = str(self.children[0].value)
        date_pattern = r'^([0-2][0-9]|3[0-1])[.,/](0[1-9]|1[0-2])$'
        date_match = re.match(date_pattern, date_str)

        if not date_match:
            return await interaction.respond(
                '_Неправильный формат даты. Пожалуйста, используйте формат ДД.ММ_',
                delete_after=5
            )

        try:
            day, month = map(int, date_match.groups())
            current_year = datetime.now().year
            rcd_date = datetime(
                year=current_year,
                month=month,
                day=day)
            if rcd_date < datetime.now():
                rcd_date = rcd_date.replace(year=current_year + 1)
            convert_rcd_date = discord.utils.format_dt(rcd_date, style="D")
            rcd_date_list['convert_rcd_date'] = convert_rcd_date
            embed['final_rcd_list_embed'] = final_rcd_list_embed(convert_rcd_date)
            embed['second_final_rcd_list_embed'] = second_final_rcd_list_embed(convert_rcd_date)
            embed['rcd_list_embed'] = rcd_list_embed(convert_rcd_date)
            await interaction.channel.send(embed=rcd_list_embed(convert_rcd_date), view=StartRCDButton())
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При вводе даты РЧД возникла ошибка "{error}"'
            )


class RaidChampionDominionApplication(Modal):
    """
    Модальное окно для ввода данных на заявку РЧД.
    """
    def __init__(self):
        super().__init__(title='Заявка на РЧД', timeout=None)

        self.add_item(
            InputText(
                style=discord.InputTextStyle.multiline,
                label='Укажи количество чести',
                placeholder='0-500',
                max_length=3
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи классы, на которых хочешь идти на РЧД',
                placeholder='Если не заполнять, значит любой класс',
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            honor: str = str(self.children[0].value)
            class_role: str = str(self.children[1].value)
            if not class_role:
                class_role = 'Любой класс'
            guild = interaction.user.mutual_guilds[0]
            member = guild.get_member(interaction.user.id)
            field_index = 0 if discord.utils.get(member.roles, name=VETERAN_ROLE) else 1
            field_value = embed.get('rcd_list_embed').fields[field_index].value
            pattern = re.compile(rf'{member.mention}: (🟡|🔴)\n')
            match = pattern.search(field_value)
            if match:
                new_value = field_value.replace(match.group(0), f'{member.mention}: {class_role} ({honor})\n')
            else:
                new_value = field_value + f'{member.mention}: {class_role} ({honor})\n'
            embed.get('rcd_list_embed').fields[field_index].value = new_value
            await last_message_to_finish.get('start_RCD_button_message').edit(embed=embed.get('rcd_list_embed'))
            member_list.append(interaction.user.id)
            if interaction.channel.type.value == 1:
                await interaction.message.delete()
            await interaction.respond(
                '_Заявка принята ✅_',
                delete_after=1
            )
            logger.info(f'Принята заявка на РЧД от "{interaction.user.display_name}"')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При отправке заявки на РЧД пользователем '
                f'"{interaction.user.display_name}" произошла ошибка "{error}"'
            )


class PrivateMessageView(View):
    """
    Кнопка для отказа или соглашения идти на РЧД.
    """
    def __init__(self):
        super().__init__(timeout=None)

    @button(
            label='Отправить заявку на РЧД', style=discord.ButtonStyle.green,
            emoji='📋', custom_id='ЗаявкаРЧД'
    )
    async def acces_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            if interaction.user.id in member_list:
                return await interaction.respond(
                    '_Ты уже подал заявку! ✅_',
                    delete_after=1
                )
            await interaction.response.send_modal(RaidChampionDominionApplication())
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )

    @button(
        label='Меня не будет ❌',
        style=discord.ButtonStyle.red,
        custom_id='МеняНеБудет'
    )
    async def denied_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            guild = interaction.user.mutual_guilds[0]
            member = guild.get_member(interaction.user.id)
            field_index = 0 if discord.utils.get(member.roles, name=VETERAN_ROLE) else 1
            field_value = embed.get('rcd_list_embed').fields[field_index].value
            if member.mention in field_value:
                new_value = field_value.replace(f'{member.mention}: 🟡\n', f'{member.mention}: 🔴\n')
                embed.get('rcd_list_embed').fields[field_index].value = new_value
                await last_message_to_finish.get('start_RCD_button_message').edit(embed=embed.get('rcd_list_embed'))
            await interaction.message.delete()
            await interaction.respond(
                '_Принято ✅_',
                delete_after=1
            )
            logger.info(f'"{interaction.user.display_name}" отказался быть на РЧД')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При отправке отказа пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )


class RCDButton(View):
    """
    Кнопка для запуска модального окна для заявки РЧД.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
            label='Отправить заявку на РЧД', style=discord.ButtonStyle.green,
            emoji='📋', custom_id='ЗаявкаРЧД'
    )
    async def callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            if interaction.user.id in member_list:
                return await interaction.respond(
                    '_Ты уже подал заявку! ✅_',
                    delete_after=1,
                    ephemeral=True
                )
            await interaction.response.send_modal(RaidChampionDominionApplication())
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При нажатии на кнопку отправки заявки на РЧД '
                f'пользователем "{interaction.user.display_name}" '
                f'возникла ошибка "{error}"'
            )


class SelectMemberToRCD(View):
    """
    Меню для выбора пользователей в РЧД список.
    """

    def __init__(
        self,
        index: int,
        item_list: list[discord.ui.Item]
    ) -> None:
        super().__init__(timeout=None)
        self.index: int = index
        self.item_list = item_list

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=3,
        placeholder='Выбери игроков...'
    )
    async def select_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            f_embed: discord.Embed = embed.get('final_rcd_list_embed')
            s_embed: discord.Embed = embed.get('second_final_rcd_list_embed')
            check_set: set[str] = set()

            for each_embed in [f_embed, s_embed]:
                for field in each_embed.fields:
                    for value in field.value.split(','):
                        check_set.add(value.strip())

            for user in select.values:
                if user.mention in check_set:
                    return await interaction.respond(
                        '_Повторно добавлять одного и того же нельзя, проверь списки! ❌_',
                        delete_after=3
                    )
            await self.update_embed(
                interaction,
                ', '.join(user.mention for user in select.values),
                set(select.values)
            )
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При выборе игроков возникла ошибка "{error}"'
            )

    @button(label='Очистить', style=discord.ButtonStyle.gray, custom_id='Очистить')
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(invisible=False, ephemeral=True)
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                delete_after=2
            )
        await self.update_embed(interaction, '', None)

    async def update_embed(
        self,
        interaction: discord.Interaction,
        value: str,
        members: set[discord.Member] | None
    ) -> None:
        try:
            tumbler_button: discord.ui.Button = self.item_list[1]
            is_red = tumbler_button.style == discord.ButtonStyle.red

            embed_name = 'second_final_rcd_list_embed' if is_red else 'final_rcd_list_embed'
            message_name = 'second_final_rcd_list_message' if is_red else 'final_rcd_list_message'
            embed_object: discord.Embed = embed[embed_name]
            embed_object.fields[self.index].value = value

            members_dict = members_by_roles_deff if is_red else members_by_roles_attack
            role = INDEX_CLASS_ROLE.get(self.index)

            if not members and role in members_dict:
                del members_dict[role]
            else:
                members_dict[role] = members

            message: discord.Message = last_message_to_finish.get(message_name)
            await message.edit(embed=embed_object)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При обработке игроков возникла ошибка "{error}"'
            )


class AddMemberToListButton(discord.ui.Button):
    """Кнопка для добавления игроков к классам"""

    def __init__(
        self,
        index: int,
        label: str,
        create_rcd_view: discord.ui.View,
        style=discord.ButtonStyle.green
    ):
        super().__init__(
            label=label,
            style=style
        )
        self.index = index
        self.create_rcd_view = create_rcd_view

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            create_button: discord.ui.Button = self.create_rcd_view.children[0]
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            if not last_message_to_finish.get('final_rcd_list_message'):
                last_message_to_finish['final_rcd_list_message'] = interaction.channel.last_message
                self.create_rcd_view.children[0].disabled = False
                await last_message_to_finish.get('create_RCD_list_buttons').edit(view=self.create_rcd_view)
            if not last_message_to_finish.get('second_final_rcd_list_message') and create_button.style == discord.ButtonStyle.gray:
                last_message_to_finish['second_final_rcd_list_message'] = interaction.channel.last_message
            await interaction.respond(view=SelectMemberToRCD(
                index=self.index, item_list=self.create_rcd_view.children
            ))
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При нажатии на кнопку добавления игроков возникла ошибка "{error}"'
            )


class CreateRCDList(View):
    """
    Кнопки для создания РЧД списка, и отправки готового списка.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @button(
        label='Создать список', style=discord.ButtonStyle.blurple,
        custom_id='СоздатьСписок'
    )
    async def create_list_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            last_message_to_finish['create_RCD_list_buttons'] = interaction.message
            if not last_message_to_finish.get('final_rcd_list_message'):
                for index, roles in INDEX_CLASS_ROLE.items():
                    self.add_item(AddMemberToListButton(
                        index=index,
                        label=f'Редактировать "{roles[:-2]}ов"',
                        create_rcd_view=self
                    ))
                button.label = 'Создать 2-ой список'
                button.disabled = True
                for index in range(2, 5):
                    self.children[index].disabled = False
                    self.children[index].style = discord.ButtonStyle.blurple
                    if index == 4:
                        self.children[index].style = discord.ButtonStyle.red
                await interaction.channel.send(embed=embed.get('final_rcd_list_embed'))
            else:
                button.label = '⬇️ Списки созданы ниже ⬇️'
                button.style = discord.ButtonStyle.gray
                button.disabled = True
                tumbler_button: discord.ui.Button = self.children[1]
                tumbler_button.label = 'СЕЙЧАС работа с 1️⃣ списком'
                tumbler_button.style = discord.ButtonStyle.blurple
                tumbler_button.disabled = False
                await interaction.channel.send(embed=embed.get('second_final_rcd_list_embed'))
            await interaction.message.edit(view=self)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При создании списка возникла ошибка "{error}"'
            )

    @button(
        label='Переключение между списками',
        style=discord.ButtonStyle.gray,
        custom_id='ПереключениеСписков',
        disabled=True
    )
    async def tumbler_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    ephemeral=True,
                    delete_after=2
                )
            if not last_message_to_finish.get('second_final_rcd_list_message'):
                last_message_to_finish['second_final_rcd_list_message'] = interaction.channel.last_message
            if button.style == discord.ButtonStyle.blurple:
                button.label = 'СЕЙЧАС работа с 2️⃣ списком'
                button.style = discord.ButtonStyle.red
            else:
                button.label = 'СЕЙЧАС работа с 1️⃣ списком'
                button.style = discord.ButtonStyle.blurple
            await interaction.response.edit_message(view=self)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При переключении списков возникла ошибка "{error}"'
            )

    @button(
        label='Опубликовать 📨',
        style=discord.ButtonStyle.gray,
        custom_id='Опубликовать',
        disabled=True
    )
    async def publish_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            channel: discord.TextChannel = rcd_application_channel.get('rcd_aplication_channel')
            f_embed: discord.Embed = embed.get('final_rcd_list_embed')
            s_embed: discord.Embed = embed.get('second_final_rcd_list_embed')
            publish_embed: discord.Embed = publish_rcd_embed(date=rcd_date_list.get('convert_rcd_date'))
            publish_second_embed: discord.Embed = publish_rcd_second_embed(date=rcd_date_list.get('convert_rcd_date'))
            if '(АТАКА)' in channel.last_message.embeds[0].title and not rcd_application_last_message.get('attack'):
                rcd_application_last_message['attack'] = channel.last_message
            if self.children[1].style == discord.ButtonStyle.red:
                for field in [field for field in s_embed.fields if field.value != '']:
                    name, value, inline = field.name, field.value, field.inline
                    publish_second_embed.add_field(name=name, value=value, inline=inline)
                if '(АТАКА)' in channel.last_message.embeds[0].title:
                    await channel.send(embed=publish_second_embed)
                    logger.info(f'Список "ЗАЩИТА" опубликован в {channel.name} пользователем {interaction.user.display_name}')
                elif 'Заявки на РЧД' in channel.last_message.embeds[0].title:
                    return await interaction.respond(
                        '_Сначала нужно отправить список "АТАКА"! ❌_',
                        delete_after=3
                    )
                else:
                    await channel.last_message.edit(embed=publish_second_embed)
                    logger.info(f'Список "ЗАЩИТА" изменён в {channel.name} пользователем {interaction.user.display_name}')
            else:
                for field in [field for field in f_embed.fields if field.value != '']:
                    name, value, inline = field.name, field.value, field.inline
                    publish_embed.add_field(name=name, value=value, inline=inline)
                if not last_message_to_finish.get('final_rcd_list_message'):
                    last_message_to_finish['final_rcd_list_message'] = interaction.channel.last_message
                    self.children[0].disabled = False
                    await interaction.message.edit(view=self)
                if 'Заявки на РЧД' in channel.last_message.embeds[0].title:
                    await channel.last_message.delete()
                    await channel.send(embed=publish_embed)
                    logger.info(f'Список "АТАКА" опубликован в {channel.name} пользователем {interaction.user.display_name}')
                else:
                    await rcd_application_last_message.get('attack').edit(embed=publish_embed)
                    logger.info(f'Список "АТАКА" изменён в {channel.name} пользователем {interaction.user.display_name}')
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            logger.error(
                f'При публикации списка возникла ошибка "{error}"'
            )

    @button(
        label='Оповестить об РЧД из списка 📣', style=discord.ButtonStyle.gray,
        custom_id='ОповеститьОСписке', disabled=True
    )
    async def notification_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            sergaunt_role: discord.Role = discord.utils.get(interaction.guild.roles, name=SERGEANT_ROLE)
            channel: discord.TextChannel = rcd_application_channel.get('rcd_aplication_channel')
            permissions_for_sergaunt: discord.permissions = channel.permissions_for(sergaunt_role).read_messages
            jump_url = channel.jump_url if 'Список РЧД' in channel.last_message.embeds[0].title and permissions_for_sergaunt == True else None

            async def send_notification(member: discord.Member, rcd_role: str):
                try:
                    await member.send(
                        embed=rcd_notification_embed(
                            interaction_user=interaction.user.display_name,
                            date=rcd_date_list.get('convert_rcd_date'),
                            jump_url=jump_url,
                            rcd_role=rcd_role
                        ),
                        delete_after=10800
                    )
                    logger.info(
                        f'Пользователю {member.display_name} было отправлено '
                        'оповещение об РЧД!'
                    )
                except discord.Forbidden:
                    logger.warning(f'Пользователю "{member.display_name}" запрещено отправлять сообщения')

            async def get_members_by_role(members_by_roles, pub_info_key):
                if not members_by_roles:
                    return await interaction.respond(
                        '_Дядь, в списке пусто 🤔_',
                        delete_after=3
                    )
                if pub_info.get(pub_info_key):
                    return await interaction.respond(
                        f'_Опевещения из списка {pub_info_key} уже были отправлены! ❌_',
                        delete_after=3
                    )
                for index, member_set in members_by_roles.items():
                    pub_info[pub_info_key] = True
                    for member in member_set:
                        await send_notification(member, index)
                        logger.info(f'"{member.display_name}" оповещён об РЧД')
            if self.children[1].style == discord.ButtonStyle.red:
                await get_members_by_role(members_by_roles_deff, 'ЗАЩИТА')
            else:
                await get_members_by_role(members_by_roles_attack, 'АТАКА')

            if pub_info.get('ЗАЩИТА') and pub_info.get('АТАКА'):
                button.label = 'Все оповещения были отправлены ✅'
                button.style = discord.ButtonStyle.gray
                button.disabled = True
                await interaction.message.edit(view=self)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                'При отправке уведомлений пользователям из списка '
                f'РЧД возникла ошибка: "{error}"!'
            )

    @button(
        label='Завершить работу со списком РЧД', style=discord.ButtonStyle.gray,
        custom_id='ЗавершитьРЧДСписок', disabled=True
    )
    async def stop_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            await interaction.channel.delete_messages(
                [message for key, message in last_message_to_finish.items() if key != 'start_RCD_button_message']
            )
            rcd_app_message: discord.Message | None = (
                rcd_application_channel.get('rcd_aplication_channel').last_message
                if 'Заявки на РЧД' in rcd_application_channel.get('rcd_aplication_channel').last_message.embeds[0].title else None
            )
            if rcd_app_message:
                await rcd_application_channel.get('rcd_aplication_channel').delete_messages([rcd_app_message])
            await last_message_to_finish.get('start_RCD_button_message').edit(view=None)
            member_list.clear()
            rcd_date_list.clear()
            embed.clear()
            last_message_to_finish.clear()
            rcd_application_channel.clear()
            publish_embed.clear()
            members_by_roles_attack.clear()
            members_by_roles_deff.clear()
            rcd_application_last_message.clear()
            pub_info.clear()
            await interaction.respond('✅', delete_after=1)
            logger.info(f'Пользователь "{interaction.user.display_name}" завершил работу с РЧД списками')
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При завершении работы с РЧД возникла ошибка "{error}"'
            )


class StartRCDButton(View):
    """
    Кнопка для запуска РЧД заявок.
    """
    def __init__(
        self,
        timeout: float | None = None
    ):
        super().__init__(timeout=timeout)

    @select(
        select_type=discord.ComponentType.channel_select,
        min_values=1,
        max_values=1,
        placeholder='Выбери канал, в котором будет кнопка для заявок РЧД',
        channel_types=[discord.ChannelType.text]
    )
    async def select_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        await interaction.response.defer(invisible=False, ephemeral=True)
        if not has_required_role(interaction.user):
            return await interaction.respond(
                ANSWERS_IF_NO_ROLE,
                delete_after=2
            )
        last_message_to_finish['start_RCD_button_message'] = interaction.message
        channel: discord.TextChannel = select.values[0]
        rcd_application_channel['rcd_aplication_channel'] = channel
        try:
            await channel.send(
                embed=start_rcd_embed(rcd_date_list.get('convert_rcd_date')),
                view=RCDButton()
            )
            await interaction.channel.send(view=CreateRCDList())
            self.children[0].disabled = True
            self.children[1].disabled = False
            self.remove_item(self.children[0])
            await interaction.message.edit(view=self)
            logger.info(
                f'Пользователь {interaction.user.display_name} запустил '
                f'заявки на РЧД в канале "{channel.name}"'
            )
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(f'При нажатии на кнопку StartRCDButton возникла ошибка {error}')

    @select(
        select_type=discord.ComponentType.user_select,
        min_values=1,
        max_values=24,
        placeholder='Выбери игроков, которых спросить об РЧД',
        disabled=True
    )
    async def ask_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(invisible=False, ephemeral=True)
            if not has_required_role(interaction.user):
                return await interaction.respond(
                    ANSWERS_IF_NO_ROLE,
                    delete_after=2
                )
            ask_users: list[discord.Member] = [user for user in select.values]
            for user in ask_users:
                if user.id in member_list or user.id in ask_member_list:
                    continue
                field_index = 0 if discord.utils.get(user.roles, name=VETERAN_ROLE) else 1
                embed.get('rcd_list_embed').fields[field_index].value += (f'{user.mention}: 🟡\n')
                try:
                    await user.send(
                        embed=ask_veteran_embed(
                            member=interaction.user, date=rcd_date_list.get('convert_rcd_date')
                        ),
                        view=PrivateMessageView(),
                        delete_after=86400
                    )
                    ask_member_list.append(user.id)
                    logger.info(f'Пользователю "{user.display_name}" был отправлен вопрос об РЧД')
                except discord.Forbidden:
                    logger.warning(f'Пользователю "{user.display_name}" запрещено отправлять сообщения')
            await interaction.message.edit(embed=embed.get('rcd_list_embed'), view=self)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При опросе игроков возникла ошибка "{error}"'
            )


@commands.slash_command()
@commands.has_any_role(LEADER_ROLE, OFICER_ROLE, TREASURER_ROLE)
async def rcd_application(ctx: discord.ApplicationContext) -> None:
    """
    Команда для запуска кнопки старта РЧД заявок.
    """
    try:
        await ctx.response.send_modal(RcdDate())
        logger.info(
            f'Команда "/rcd_application" вызвана пользователем'
            f'"{ctx.user.display_name}"!'
        )
    except Exception as error:
        logger.error(
            f'Ошибка при вызове команды "/rcd_application"! '
            f'"{error}"'
        )


@rcd_application.error
async def rcd_application_error(
    ctx: discord.ApplicationContext,
    error: Exception
) -> None:
    """
    Обрабатывать ошибки, возникающие
    при выполнении команды заявок на РЧД.
    """
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(
            'Команду может вызвать только "Лидер, Казначей или Офицер"!',
            ephemeral=True,
            delete_after=10
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            'Команду нельзя вызывать в личные сообщения бота!',
            ephemeral=True,
            delete_after=10
        )
    else:
        raise error


def setup(bot: discord.Bot):
    bot.add_application_command(rcd_application)
