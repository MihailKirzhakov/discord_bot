"""
Тесты списка заявок на РЧД: состояние в БД, сообщение перерисовывается из БД.
Главный сценарий — гонка рассылки "Спросить всех ветеранов" с ответами.
"""
import asyncio
import os
import random
import sys
import tempfile
from pathlib import Path

# Модули бота импортируют друг друга как top-level пакеты (core, rcd_aplication)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bot'))
# Переменные окружения важнее .env: тесты не трогают боевую БД и токен
_DB_DIR = tempfile.mkdtemp(prefix='rcd-test-')
os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{_DB_DIR}/test.db'
for _name in (
    'TOKEN', 'DEBUG_SERVER_ID', 'APPLICATION_CHANNEL_ID',
    'RCD_APPLICATION_CHANNEL_ID', 'PVE_CHANNEL_ID', 'PVE_APP_CHANNEL_ID',
):
    os.environ[_name] = '0'

import discord  # noqa: E402
from core import StaticNames, async_session_factory  # noqa: E402
from core.models import RcdParticipant  # noqa: E402
from core.orm import async_orm, rcd_app_orm  # noqa: E402
from rcd_aplication.embeds import app_list_embed  # noqa: E402
from rcd_aplication.rcd_list_state import (  # noqa: E402
    FIELD_VALUE_LIMIT,
    SECTION_SERGEANTS,
    SECTION_VETERANS,
    build_rcd_list_embed,
    import_legacy_rcd_list,
    refresh_rcd_list,
)

CHANNEL_ID = 111
MESSAGE_ID = 222


class FakeMessage:
    def __init__(self, embed: discord.Embed):
        self.embeds = [embed]
        self.edits = 0

    async def edit(self, embed=None, **_):
        # сетевая задержка Discord: в это окно и возникала гонка
        await asyncio.sleep(random.uniform(0, 0.01))
        if embed is not None:
            self.embeds = [embed]
        self.edits += 1


class FakeChannel:
    def __init__(self, message):
        self.message = message

    async def fetch_message(self, _):
        return self.message


class FakeClient:
    def __init__(self, message):
        self.channel = FakeChannel(message)

    def get_channel(self, _):
        return self.channel


def _lines(message: FakeMessage) -> dict[int, str]:
    result = {}
    for field in message.embeds[0].fields:
        for line in field.value.splitlines():
            mention, state = line.split(': ', 1)
            result[int(mention.strip('<@!>'))] = state
    return result


async def _setup_rcd() -> FakeClient:
    await async_orm.create_tables()
    async with async_session_factory() as session:
        await rcd_app_orm.clear_rcd_data(session)
        await rcd_app_orm.insert_date_info(session, StaticNames.RCD_DATE, '01.01')
        await rcd_app_orm.insert_message_id(session, StaticNames.START_RCD_MESSAGE, MESSAGE_ID)
        await rcd_app_orm.insert_message_id(session, StaticNames.RCD_LIST_CHANNEL, CHANNEL_ID)
        await session.commit()
    return FakeClient(FakeMessage(app_list_embed('01.01')))


def test_participant_lines_and_sections():
    participants = [
        RcdParticipant(member_id=1, section=SECTION_VETERANS, status='asked', created_at=1),
        RcdParticipant(member_id=2, section=SECTION_VETERANS, status='denied', created_at=2),
        RcdParticipant(
            member_id=3, section=SECTION_SERGEANTS, status='applied',
            class_role='Воин\nМаг', honor='12', created_at=3
        ),
    ]
    embed = build_rcd_list_embed('01.01', participants)
    assert embed.fields[0].value == '<@1>: 🟡\n<@2>: 🔴'
    # перевод строки из многострочного поля не ломает список
    assert embed.fields[1].value == '<@3>: Воин Маг (12)'


def test_long_section_split_into_fields():
    participants = [
        RcdParticipant(
            member_id=10**17 + i, section=SECTION_VETERANS, status='applied',
            class_role='Любой класс', honor='100', created_at=i
        )
        for i in range(60)
    ]
    embed = build_rcd_list_embed('01.01', participants)
    veteran_fields = embed.fields[:-1]
    assert len(veteran_fields) > 1
    assert all(len(field.value) <= FIELD_VALUE_LIMIT for field in embed.fields)
    assert sum(len(f.value.splitlines()) for f in veteran_fields) == 60


def test_ask_all_does_not_overwrite_answers():
    """Ответы, пришедшие во время рассылки, не должны откатываться в 🟡."""
    async def scenario():
        client = await _setup_rcd()
        message = client.channel.message
        veterans = list(range(1000, 1030))
        answered = {1003: 'applied', 1010: 'denied', 1025: 'applied'}

        async def ask_all():
            async with async_session_factory() as session:
                for member_id in veterans:
                    await rcd_app_orm.add_asked_participant(session, member_id, SECTION_VETERANS)
                await session.commit()
            await refresh_rcd_list(client)
            # имитация долгой рассылки ЛС, за время которой приходят ответы
            await asyncio.sleep(0.05)

        async def answer(member_id, kind):
            await asyncio.sleep(random.uniform(0, 0.03))
            async with async_session_factory() as session:
                if kind == 'applied':
                    await rcd_app_orm.set_participant_applied(
                        session, member_id, SECTION_VETERANS, 'Воин', '5'
                    )
                else:
                    await rcd_app_orm.set_participant_denied(session, member_id)
                await session.commit()
            await refresh_rcd_list(client)

        await asyncio.gather(ask_all(), *(answer(m, k) for m, k in answered.items()))
        await refresh_rcd_list(client)
        lines = _lines(message)
        assert set(lines) == set(veterans), 'строки рассылки потерялись'
        assert lines[1003] == 'Воин (5)'
        assert lines[1025] == 'Воин (5)'
        # отказ до записи 🟡 невозможен (строки ещё нет), после — 🔴
        assert lines[1010] in ('🔴', '🟡')
        assert sum(1 for state in lines.values() if state == '🟡') >= len(veterans) - 3

    async def repeat():
        # один event loop, как в боте: блокировка модуля привязана к loop
        for _ in range(20):
            await scenario()

    asyncio.run(repeat())


def test_answer_before_ask_keeps_application():
    """Заявка, поданная до опроса, не превращается в 🟡 и не дублируется."""
    async def scenario():
        client = await _setup_rcd()
        async with async_session_factory() as session:
            await rcd_app_orm.set_participant_applied(session, 7, SECTION_VETERANS, 'Маг', '1')
            await session.commit()
            assert not await rcd_app_orm.add_asked_participant(session, 7, SECTION_VETERANS)
            assert not await rcd_app_orm.set_participant_denied(session, 7)
            await session.commit()
        await refresh_rcd_list(client)
        assert _lines(client.channel.message) == {7: 'Маг (1)'}

    asyncio.run(scenario())


def test_import_legacy_message():
    """Активная РЧД со старым форматом переносится в БД и не стирается."""
    async def scenario():
        client = await _setup_rcd()
        legacy = app_list_embed('01.01')
        legacy.set_field_at(0, name=legacy.fields[0].name, value='\n<@1>: 🟡\n<@2>: Воин, Маг (30)', inline=False)
        legacy.set_field_at(1, name=legacy.fields[1].name, value='\n<@3>: 🔴', inline=False)
        client.channel.message.embeds = [legacy]

        assert await import_legacy_rcd_list(client) == 3
        assert await import_legacy_rcd_list(client) == 0, 'повторный перенос'
        await refresh_rcd_list(client)
        embed = client.channel.message.embeds[0]
        assert embed.fields[0].value == '<@1>: 🟡\n<@2>: Воин, Маг (30)'
        assert embed.fields[1].value == '<@3>: 🔴'

    asyncio.run(scenario())


class _FakeRole:
    def __init__(self, name, members=()):
        self.name = name
        self.members = list(members)


class _FakeMember:
    def __init__(self, member_id):
        self.id = member_id
        self.display_name = f'user{member_id}'
        self.roles = []


class _FakeInteraction:
    """Минимум, который трогает ask_all_veteran_callback."""
    def __init__(self, client, roles):
        self.client = client
        self.user = _FakeMember(1)
        self.guild = type('G', (), {'roles': roles})()
        self.message = client.channel.message
        self.responses = []

        async def defer(**_):
            return None
        self.response = type('R', (), {'defer': staticmethod(defer)})()

    async def respond(self, content=None, **_):
        self.responses.append(content)


def test_ask_all_veterans_handler_sends_messages(monkeypatch):
    """
    Регрессия 22.11: дата РЧД читалась после commit -> DetachedInstanceError,
    строки 🟡 записывались, а личные сообщения не уходили.
    """
    import rcd_aplication.rcd_aplication as rcd
    from core import VETERAN_ROLE

    async def scenario():
        client = await _setup_rcd()
        veterans = [_FakeMember(2000 + i) for i in range(3)]
        interaction = _FakeInteraction(client, [_FakeRole(VETERAN_ROLE, veterans)])
        sent = []

        async def fake_send(users, asker, date):
            sent.append(([u.id for u in users], date))
        monkeypatch.setattr(rcd, 'send_ask_messages', fake_send)

        view = rcd.StartRCDButton()
        button = next(c for c in view.children if c.custom_id == 'СпроситьВсехВетеранов')
        await button.callback(interaction)

        assert interaction.responses == ['✅'], interaction.responses
        assert sent == [([2000, 2001, 2002], '01.01')]
        assert set(_lines(client.channel.message)) == {2000, 2001, 2002}

    asyncio.run(scenario())
