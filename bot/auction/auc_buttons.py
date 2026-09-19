import asyncio
from datetime import datetime, timedelta
from typing import cast

import discord
from core import LEADER_NICKNAME, MIN_BID_VALUE, NOT_SOLD, async_session_factory
from core.orm.auction_orm import auc_orm
from discord.ext import commands
from discord.ui import Button, InputText, Modal, View
from loguru import logger

from .embeds import outbid_embed, results_embed, start_auc_embed
from .functions import (
    convert_bid,
    convert_sorted_message,
    seconds_until_date,
)

final_time: dict[str, datetime] = {}
channel_last_message_dict: dict[str, discord.Message] = {}
auc_id_by_name: dict[str, int] = {}


class StartAucModal(Modal):
    """
    Модальное окно для ввода данных для старта аукциона.
    """
    def __init__(
        self,
        channel: discord.TextChannel
    ):
        super().__init__(title='Параметры аукциона', timeout=None)
        self.channel = channel

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи название аукциона',
                placeholder='название лотов для розыгрыша'
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи количество разыгрываемых лотов',
                placeholder='кол-во лотов может быть от 1 до 25',
                min_length=1,
                max_length=2
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи начальную ставку',
                placeholder=f'минимальная ставка {MIN_BID_VALUE}',
            )
        )

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Укажи дату и время в формате ДД.ММ ЧЧ:ММ',
                placeholder='ДД.ММ ЧЧ:ММ',
                max_length=11
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=False, ephemeral=True)

        name_value = self.children[0].value
        lot_amount_value = self.children[1].value
        start_bid_value = self.children[2].value
        target_date_time_value = self.children[3].value

        if (
            name_value is None or lot_amount_value is None
            or start_bid_value is None or target_date_time_value is None
        ):
            await interaction.respond('❌', delete_after=1)
            return

        if not lot_amount_value.isdigit() or not start_bid_value.isdigit():
            await interaction.respond(
                '_Количество лотов и стартовая ставка должны быть числами_',
                delete_after=5
            )
            return

        name_auc: str = str(name_value)
        lot_amount: int = int(lot_amount_value)
        start_bid: int = int(start_bid_value)
        target_date_time: str = str(target_date_time_value)

        if not isinstance(interaction.user, discord.Member):
            await interaction.respond('❌', delete_after=1)
            return

        start_auc_user: discord.Member = interaction.user
        user_mention: str = start_auc_user.mention
        button_manager = View(timeout=None)
        button_mentions: dict[str, str] = {}
        today: datetime = datetime.now()

        if lot_amount < 1 or lot_amount > 25:
            return await interaction.respond(
                '_Количество лотов должно быть от 1 до 24_',
                delete_after=10
            )

        if final_time.get(name_auc) or channel_last_message_dict.get(name_auc):
            name_auc += ' 😊'

        seconds_left = seconds_until_date(target_date_time)
        if isinstance(seconds_left, str):
            await interaction.respond(seconds_left, delete_after=5)
            return

        stop_time: datetime = today + timedelta(seconds=seconds_left)
        final_time[name_auc] = stop_time

        async with async_session_factory() as session:
            await auc_orm.insert_auc_info_data(
                session=session,
                name_auc=name_auc,
                data=target_date_time,
                start_auc_user_id=start_auc_user.id,
                start_bid=start_bid,
                lot_amount=lot_amount,
                stop_time=stop_time,
                channel_id=self.channel.id
            )
            await session.commit()

            auction_obj = await auc_orm.get_auc_info_by_name(session, name_auc)
            if not auction_obj:
                await interaction.respond('❌', delete_after=1)
                return
            auction_id = auction_obj.id
            auc_id_by_name[name_auc] = auction_id

            for index in range(lot_amount):
                await auc_orm.insert_bid_data(
                    session=session,
                    auction_id=auction_id,
                    lot_index=index,
                    user_bid=start_bid,
                    user_id=None
                )
                button_manager.add_item(
                    BidButton(
                        start_bid=start_bid,
                        start_auc_user=start_auc_user,
                        lot_amount=lot_amount,
                        name_auc=name_auc,
                        button_mentions=button_mentions,
                        button_manager=button_manager,
                        index=index,
                        auction_id=auction_id
                    )
                )
            await session.commit()

        message = await self.channel.send(
            embed=start_auc_embed(
                user_mention=user_mention,
                name_auc=name_auc,
                stop_time=stop_time,
                lot_count=lot_amount,
                first_bid=convert_bid(start_bid)
            ),
            view=button_manager
        )
        await interaction.respond('✅', delete_after=1)
        channel_last_message_dict[name_auc] = message

        async with async_session_factory() as session:
            await auc_orm.set_auction_message_id(
                session=session,
                auction_id=auction_id,
                message_id=message.id
            )
            await session.commit()

        try:
            await discord.utils.sleep_until(stop_time - timedelta(seconds=60))
            await check_timer(
                view=button_manager,
                user_mention=user_mention,
                name_auc=name_auc,
                lot_amount=lot_amount,
                final_time=final_time,
                button_mentions=button_mentions
            )
        except Exception:
            logger.error("Аукцион был отменён. Сообщение удалёно")


class PassBid(Modal):
    def __init__(
        self,
        btn_label: str,
        start_bid: int,
        start_auc_user: discord.Member,
        lot_amount: int,
        name_auc: str,
        button_mentions: dict[str, str],
        button_manager: View,
        index: int,
        button_message: discord.Message,
        auction_id: int
    ):
        super().__init__(title='Укажи свою ставку', timeout=None)
        self.btn_label = btn_label
        self.start_bid = start_bid
        self.start_auc_user = start_auc_user
        self.lot_amount = lot_amount
        self.name_auc = name_auc
        self.button_mentions = button_mentions
        self.button_manager = button_manager
        self.index = index
        self.button_message = button_message
        self.auction_id = auction_id

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Ставка кратная 100.000 и не более 99.9M',
                placeholder='Внимательно считаем количество ноликов!',
                min_length=6,
                max_length=8
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(invisible=False, ephemeral=True)

        try:
            if interaction.user is None:
                await interaction.respond('❌', delete_after=1)
                return
            user = cast(discord.Member, interaction.user)

            bid_value = self.children[0].value
            if bid_value is None or not bid_value.isdigit():
                return await interaction.respond(
                    '_Указанное значение не является положительным числом! ❌_',
                    delete_after=2
                )

            if int(bid_value) % 100_000 != 0:
                return await interaction.respond(
                    '_Ставка должна быть кратна 100.000! ❌_',
                    delete_after=2
                )

            if interaction.guild is None:
                await interaction.respond('❌', delete_after=1)
                return

            select_bid: int = int(bid_value)
            reserve_button_manager = self.button_manager
            user_name: str = user.display_name
            user_mention: str = user.mention
            nowtime: datetime = datetime.now()
            sixty_seconds: timedelta = timedelta(seconds=60)
            plus_minute: datetime = nowtime + sixty_seconds

            if len(self.button_manager.children) == 0:
                await self.button_message.edit(view=reserve_button_manager)
                await interaction.respond(
                    f'В момент обработки, сделанной ставки возникла ошибка!'
                    f'Бот не сломался, попробуй сделать ставку снова. Если '
                    f'данное сообщение появляется снова, обратись к '
                    f'{LEADER_NICKNAME}, для скорейшего решения проблемы!',
                    delete_after=10
                )
                await self.start_auc_user.send(
                    f'_Сигнал об ошибке во время аукциона! '
                    f'При попытке пользователя "{user.display_name}" '
                    f'сделать ставку, произошла неизвестная ошибка! '
                    f'Отработала резервная view._'
                )
                logger.error(
                    f'При попытке сделать ставку пользователем '
                    f'"{user.mention}" возникла неизвестная ошибка, '
                    f'которая сносит кнопки. Во "view" сложили резервную копию.'
                )

            async with async_session_factory() as session:
                bid_obj = await auc_orm.get_lot_bid(
                    session=session,
                    auction_id=self.auction_id,
                    lot_index=self.index
                )
                if not bid_obj:
                    await interaction.respond(
                        '_Не удалось получить данные ставки из БД! ❌_',
                        delete_after=3
                    )
                    return
                full_label_number = bid_obj.user_bid
                current_user_id = bid_obj.user_id

            if full_label_number >= select_bid:
                return await interaction.respond(
                    '_Ставка должна быть большей текущей! ❌_',
                    delete_after=5
                )

            if (select_bid - full_label_number) > 5_000_000:
                return await interaction.respond(
                    '_Сработала защита, твоя ставка больше текущей на 5 000 000.⚠️\n'
                    'Ты точно не указал не ошибся с лишним ноликом?\n'
                    'Сделай ставку меньше, разница с текущей ставкой должна быть '
                    'не более 5 миллионов!👌_',
                    delete_after=4
                )

            async with async_session_factory() as session:
                await auc_orm.upsert_lot_bid(
                    session=session,
                    auction_id=self.auction_id,
                    lot_index=self.index,
                    user_id=user.id,
                    user_bid=select_bid
                )
                await session.commit()

            bid_button = cast(Button, self.button_manager.children[self.index])
            bid_button.label = f'{convert_bid(select_bid)} {user.display_name}'
            bid_button.style = discord.ButtonStyle.blurple
            self.button_mentions[user_name] = user_mention

            current_end = final_time.get(self.name_auc)
            if current_end and (current_end - nowtime) < sixty_seconds:
                await self.button_message.edit(
                    view=self.button_manager,
                    embed=start_auc_embed(
                        user_mention=self.start_auc_user.mention,
                        name_auc=self.name_auc,
                        stop_time=plus_minute,
                        lot_count=self.lot_amount,
                        first_bid=convert_bid(self.start_bid)
                    )
                )
                final_time[self.name_auc] = plus_minute

            logger.info(f'Пользователь "{user.display_name}" сделал ставку')

            if current_user_id and current_user_id != user.id:
                during_member = interaction.guild.get_member(current_user_id)
                if during_member:
                    current_auc_time = final_time.get(self.name_auc)
                    if current_auc_time is None:
                        current_auc_time = plus_minute
                    if (datetime.now() + timedelta(seconds=60)) > current_auc_time > datetime.now():
                        time_of_bid = plus_minute
                        delete_after = 60
                    else:
                        time_of_bid = current_auc_time
                        delete_after = 1800
                    try:
                        await during_member.send(
                            embed=outbid_embed(
                                url=self.button_message.jump_url,
                                stop_time=time_of_bid,
                                delete_after=delete_after
                            ),
                            delete_after=delete_after
                        )
                    except discord.Forbidden:
                        logger.warning(
                            f'Пользователю "{during_member.display_name}" запрещено отправлять сообщения'
                        )
                    logger.info(
                        f'Ставку "{during_member.display_name}" перебил '
                        f'"{user.display_name}"!'
                    )

            await self.button_message.edit(view=self.button_manager)
            await interaction.respond('✅', delete_after=1)
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )


class BidButton(Button):
    """Кнопка со ставкой и никнеймом, сделавшего ставку"""
    def __init__(
        self,
        start_bid: int,
        start_auc_user: discord.Member,
        lot_amount: int,
        name_auc: str,
        button_mentions: dict[str, str],
        button_manager: View,
        index: int,
        auction_id: int,
        custom_id: str | None = None,
    ):
        if custom_id is None:
            custom_id = f'auction_bid_{auction_id}_{index}'
        super().__init__(
            style=discord.ButtonStyle.green,
            label=convert_bid(start_bid),
            custom_id=custom_id
        )
        self.start_bid = start_bid
        self.start_auc_user = start_auc_user
        self.lot_amount = lot_amount
        self.name_auc = name_auc
        self.button_mentions = button_mentions
        self.button_manager = button_manager
        self.index = index
        self.auction_id = auction_id

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.label is None or interaction.message is None:
                await interaction.respond('❌', delete_after=1)
                return
            await interaction.response.send_modal(
                PassBid(
                    btn_label=self.label,
                    start_bid=self.start_bid,
                    start_auc_user=self.start_auc_user,
                    lot_amount=self.lot_amount,
                    name_auc=self.name_auc,
                    button_mentions=self.button_mentions,
                    button_manager=self.button_manager,
                    index=self.index,
                    button_message=interaction.message,
                    auction_id=self.auction_id
                )
            )
        except Exception as error:
            await interaction.respond('❌', delete_after=1)
            logger.error(
                f'При обработке нажатия на кнопку ставки '
                f'возникла ошибка "{error}"'
            )


@commands.slash_command()
@commands.has_role('Аукцион')
async def go_auc(
    ctx: discord.ApplicationContext,
    channel: discord.Option(
        discord.TextChannel,
        description='Текстовый канал в котором будет аукцион',
        name_localizations={'ru': 'канал'}
    ),  # type: ignore
) -> None:
    """
    Команда для запуска аукциона.
    """
    try:
        await ctx.response.send_modal(StartAucModal(channel=channel))
    except Exception as error:
        await ctx.respond('❌', delete_after=1)
        logger.error(
            f'При попытке запустить аукцион командой /go_auc '
            f'возникло исключение "{error}"'
        )


@go_auc.error
async def go_auc_error(
    ctx: discord.ApplicationContext, error: Exception
) -> None:
    """
    Обработчик ошибок для команды go_auc.
    """
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond(
            '_Команду может вызвать только Аукционер! ❌_',
            ephemeral=True,
            delete_after=10
        )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.respond(
            '_Команду нельзя вызывать в личные сообщения бота!❌ _',
            ephemeral=True,
            delete_after=10
        )
    else:
        raise error


async def check_timer(
    view: View,
    user_mention: str,
    name_auc: str,
    lot_amount: int,
    final_time: dict,
    button_mentions: dict
) -> None:
    """
    Функция для полинга таймера, которая автоматически завершает аукцион.
    """
    while True:
        end_time = final_time.get(name_auc)
        if end_time and end_time > datetime.now():
            await asyncio.sleep(0.5)
        else:
            await auto_stop_auc(
                view=view,
                user_mention=user_mention,
                name_auc=name_auc,
                lot_amount=lot_amount,
                button_mentions=button_mentions
            )
            break


async def auto_stop_auc(
    view: View,
    user_mention: str,
    name_auc: str,
    lot_amount: int,
    button_mentions: dict
) -> None:
    """
    Функция для автозавершения аукциона.
    """
    view.disable_all_items()
    auction_id = auc_id_by_name.get(name_auc)
    sorted_list: list[str] = []
    message_obj = channel_last_message_dict.get(name_auc)

    async with async_session_factory() as session:
        if auction_id:
            bids = await auc_orm.get_bids_by_auction(session, auction_id)
            lot_bid_strings: list[str] = []
            for bid in sorted(bids, key=lambda x: x.lot_index):
                if bid.user_id is None:
                    lot_bid_strings.append(NOT_SOLD)
                    continue

                mention = f'<@{bid.user_id}>'
                if message_obj and message_obj.guild:
                    member = message_obj.guild.get_member(bid.user_id)
                    if member:
                        mention = member.mention

                lot_bid_strings.append(f'{convert_bid(bid.user_bid)} {mention}')

            count_not_bid = lot_bid_strings.count(NOT_SOLD)
            removed_not_bid = [i for i in lot_bid_strings if i != NOT_SOLD]
            sorted_list = sorted(
                removed_not_bid,
                key=convert_sorted_message,
                reverse=True
            )
            for _ in range(count_not_bid):
                sorted_list.append(NOT_SOLD)

            await auc_orm.set_auction_status(session, auction_id, 'finished')
            await auc_orm.delete_bids_by_auction(session, auction_id)
            await auc_orm.delete_auction_data(session, auction_id)
            await session.commit()

    message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(sorted_list)])
    view.clear_items()

    try:
        if message_obj:
            await message_obj.edit(
                view=view,
                embed=results_embed(
                    results_message=message,
                    user_mention=user_mention,
                    name_auc=name_auc,
                    lot_amount=lot_amount
                )
            )
        logger.info('Аукцион успешно завершён!')
    except Exception as error:
        logger.error(
            f'При автоматическом завершении аукциона возникла ошибка '
            f'"{error}"'
        )
    finally:
        channel_last_message_dict.pop(name_auc, None)
        final_time.pop(name_auc, None)
        auc_id_by_name.pop(name_auc, None)


async def restore_active_auctions(bot: discord.Bot) -> None:
    """
    Восстановление активных аукционов после реконнекта/рестарта бота:
    - восстановление обработчиков кнопок через bot.add_view(..., message_id=...)
    - восстановление таймеров автозавершения
    """
    async with async_session_factory() as session:
        auctions = await auc_orm.get_active_auctions(session)

    if not auctions:
        logger.info('Активные аукционы для восстановления не найдены')
        return

    for auction in auctions:
        auction_id = auction.id
        name_auc = auction.name_auc
        lot_amount = auction.lot_amount
        start_bid = auction.start_bid
        stop_time = auction.stop_time
        message_id = auction.message_id
        channel_id = auction.channel_id
        start_auc_user_id = auction.start_auc_user_id

        if message_id is None:
            logger.warning(
                f'Аукцион "{name_auc}" (id={auction_id}) пропущен: отсутствует message_id'
            )
            continue

        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as error:
                logger.warning(
                    f'Не удалось получить канал "{channel_id}" '
                    f'для аукциона "{name_auc}": {error}'
                )
                continue

        if not isinstance(channel, discord.TextChannel):
            logger.warning(
                f'Канал "{channel_id}" для аукциона "{name_auc}" '
                f'не является TextChannel'
            )
            continue

        try:
            message = await channel.fetch_message(message_id)
        except Exception as error:
            logger.warning(
                f'Не удалось получить сообщение "{message_id}" '
                f'для аукциона "{name_auc}": {error}'
            )
            continue

        guild = message.guild
        if guild is None:
            logger.warning(
                f'Для аукциона "{name_auc}" не удалось получить guild '
                f'из сообщения "{message_id}"'
            )
            continue

        start_auc_user = guild.get_member(start_auc_user_id)
        if start_auc_user is None:
            try:
                start_auc_user = await guild.fetch_member(start_auc_user_id)
            except Exception:
                logger.warning(
                    f'Не удалось получить автора аукциона '
                    f'user_id={start_auc_user_id} для "{name_auc}"'
                )
                continue

        button_manager = View(timeout=None)
        button_mentions: dict[str, str] = {}

        async with async_session_factory() as session:
            bids = await auc_orm.get_bids_by_auction_sorted(session, auction_id)

        if len(bids) != lot_amount:
            logger.warning(
                f'Несоответствие количества лотов/ставок для "{name_auc}": '
                f'lot_amount={lot_amount}, bids={len(bids)}'
            )

        for lot_index in range(lot_amount):
            bid_obj = next((b for b in bids if b.lot_index == lot_index), None)
            if bid_obj is None:
                current_bid = start_bid
                current_user_id = None
            else:
                current_bid = bid_obj.user_bid
                current_user_id = bid_obj.user_id

            bid_button = BidButton(
                start_bid=start_bid,
                start_auc_user=start_auc_user,
                lot_amount=lot_amount,
                name_auc=name_auc,
                button_mentions=button_mentions,
                button_manager=button_manager,
                index=lot_index,
                auction_id=auction_id
            )

            if current_user_id is not None:
                member = guild.get_member(current_user_id)
                if member:
                    bid_button.label = f'{convert_bid(current_bid)} {member.display_name}'
                    bid_button.style = discord.ButtonStyle.blurple
                    button_mentions[member.display_name] = member.mention
                else:
                    bid_button.label = convert_bid(current_bid)
            else:
                bid_button.label = convert_bid(current_bid)

            button_manager.add_item(bid_button)

        bot.add_view(button_manager, message_id=message_id)
        channel_last_message_dict[name_auc] = message
        final_time[name_auc] = stop_time
        auc_id_by_name[name_auc] = auction_id

        if stop_time <= datetime.now():
            await auto_stop_auc(
                view=button_manager,
                user_mention=f'<@{start_auc_user_id}>',
                name_auc=name_auc,
                lot_amount=lot_amount,
                button_mentions=button_mentions
            )
            logger.info(
                f'Аукцион "{name_auc}" восстановлен и сразу завершён '
                f'(время окончания уже прошло)'
            )
        else:
            asyncio.create_task(
                check_timer(
                    view=button_manager,
                    user_mention=f'<@{start_auc_user_id}>',
                    name_auc=name_auc,
                    lot_amount=lot_amount,
                    final_time=final_time,
                    button_mentions=button_mentions
                )
            )
            logger.info(f'Аукцион "{name_auc}" успешно восстановлен')


def setup(bot: discord.Bot):
    bot.add_application_command(go_auc)  # type: ignore[arg-type]
