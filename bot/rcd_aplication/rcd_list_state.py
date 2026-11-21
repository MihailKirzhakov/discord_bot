"""
Список поданных заявок на РЧД: состояние в БД (RcdParticipant),
сообщение в Discord — только отображение, которое целиком перерисовывается.

Все перерисовки идут под одной asyncio.Lock: чтение БД -> сборка embed -> edit.
Обработчики сначала коммитят своё изменение, потом вызывают refresh_rcd_list().
Любая перерисовка, начатая после коммита, его увидит, а последняя из очереди
читает итоговое состояние, поэтому ответы больше не перетираются.
"""
import asyncio
import re
import time

import discord
from core import StaticNames, async_session_factory
from core.models import RcdParticipant
from core.orm import rcd_app_orm
from core.orm.rcd_application_orm import (
    PARTICIPANT_APPLIED,
    PARTICIPANT_ASKED,
    PARTICIPANT_DENIED,
)
from loguru import logger

from .embeds import app_list_embed

SECTION_VETERANS = 0
SECTION_SERGEANTS = 1

FIELD_VALUE_LIMIT = 1024
CONTINUATION_FIELD_NAME = '​'

_rcd_list_lock = asyncio.Lock()

_LINE_RE = re.compile(r'^<@!?(\d+)>: (.*)$')
_APPLIED_RE = re.compile(r'^(.*) \((\d+)\)$')


def participant_line(participant: RcdParticipant) -> str:
    mention = f'<@{participant.member_id}>'
    if participant.status == PARTICIPANT_ASKED:
        return f'{mention}: 🟡'
    if participant.status == PARTICIPANT_DENIED:
        return f'{mention}: 🔴'
    # перевод строки из многострочного поля сломал бы список
    class_role = ' '.join((participant.class_role or 'Любой класс').split())
    return f'{mention}: {class_role} ({participant.honor or "0"})'


def _chunk_lines(lines: list[str]) -> list[str]:
    """Режет строки на значения полей не длиннее лимита Discord (1024)."""
    chunks, current = [], ''
    for line in lines:
        candidate = f'{current}\n{line}' if current else line
        if len(candidate) > FIELD_VALUE_LIMIT and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    chunks.append(current)
    return chunks


def build_rcd_list_embed(date: str, participants: list[RcdParticipant]) -> discord.Embed:
    """Собирает embed списка из БД на основе шаблона app_list_embed."""
    template = app_list_embed(date)
    section_names = [field.name for field in template.fields]
    template.clear_fields()
    for section, name in enumerate(section_names):
        lines = [participant_line(p) for p in participants if p.section == section]
        for number, chunk in enumerate(_chunk_lines(lines)):
            template.add_field(
                name=name if number == 0 else CONTINUATION_FIELD_NAME,
                value=chunk,
                inline=False
            )
    return template


def _parse_embed_participants(embed: discord.Embed) -> list[RcdParticipant]:
    """
    Разовый перенос: РЧД, начатая до перехода на БД, хранит список только
    в тексте сообщения. Без переноса первая перерисовка стёрла бы его.
    """
    participants, section, now = [], -1, time.time()
    for field in embed.fields:
        if field.name != CONTINUATION_FIELD_NAME:
            section += 1
        for line in (field.value or '').splitlines():
            match = _LINE_RE.match(line.strip())
            if not match:
                continue
            member_id, rest = int(match.group(1)), match.group(2).strip()
            participant = RcdParticipant(
                member_id=member_id, section=min(section, SECTION_SERGEANTS),
                created_at=now + len(participants) * 1e-3
            )
            if rest == '🟡':
                participant.status = PARTICIPANT_ASKED
            elif rest == '🔴':
                participant.status = PARTICIPANT_DENIED
            else:
                applied = _APPLIED_RE.match(rest)
                participant.status = PARTICIPANT_APPLIED
                participant.class_role = applied.group(1) if applied else rest
                participant.honor = applied.group(2) if applied else '0'
            participants.append(participant)
    return participants


async def _get_start_message(client: discord.Client, session) -> discord.Message | None:
    message_obj = await rcd_app_orm.get_message_data_obj(session, StaticNames.START_RCD_MESSAGE)
    channel_obj = await rcd_app_orm.get_message_data_obj(session, StaticNames.RCD_LIST_CHANNEL)
    if not message_obj or not channel_obj:
        return None
    channel = client.get_channel(channel_obj.message_id)
    if channel is None:
        channel = await client.fetch_channel(channel_obj.message_id)
    return await channel.fetch_message(message_obj.message_id)


async def import_legacy_rcd_list(client: discord.Client) -> int:
    """
    Если РЧД активна, а таблица участников пуста — переносит строки
    из текущего сообщения в БД. Возвращает число перенесённых участников.
    """
    async with _rcd_list_lock:
        async with async_session_factory() as session:
            if await rcd_app_orm.get_all_participant_ids(session):
                return 0
            message = await _get_start_message(client, session)
            if not message or not message.embeds:
                return 0
            participants = _parse_embed_participants(message.embeds[0])
            seen = set()
            for participant in participants:
                if participant.member_id in seen:
                    continue
                seen.add(participant.member_id)
                session.add(participant)
            await session.commit()
            if seen:
                logger.info(f'Список РЧД перенесён из сообщения в БД: {len(seen)} участников')
            return len(seen)


async def refresh_rcd_list(client: discord.Client) -> bool:
    """Перерисовывает сообщение со списком заявок из БД. False — РЧД не запущена."""
    async with _rcd_list_lock:
        async with async_session_factory() as session:
            message = await _get_start_message(client, session)
            if not message:
                return False
            date_obj = await rcd_app_orm.get_rcd_date_obj(session, StaticNames.RCD_DATE)
            participants = await rcd_app_orm.get_participants(session)
        embed = build_rcd_list_embed(date_obj.date if date_obj else '', participants)
        if len(embed) > 6000 or len(embed.fields) > 25:
            logger.error(
                f'Список РЧД не помещается в одно сообщение Discord '
                f'({len(participants)} участников, {len(embed)} символов)'
            )
        # только embed: view (кнопки/селект) сообщения остаётся как есть
        await message.edit(embed=embed)
        return True
