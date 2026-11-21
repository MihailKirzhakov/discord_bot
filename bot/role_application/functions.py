import functools
from json import JSONDecodeError

import discord
import requests
from core import (
    ANSWERS_IF_NO_ROLE,
    LEADER_ROLE,
    OFICER_ROLE,
    RCD_CONTROL,
    TREASURER_ROLE,
)
from loguru import logger
from requests import exceptions as requests_exceptions

ARMORY_API = 'https://api.allodswiki.ru/api/v2/public'
ASSETS_URL = 'https://assets.allodswiki.ru'
# Без Origin/X-Site API отвечает так же, но держимся заголовков сайта
ARMORY_HEADERS = {
    'Accept': 'application/json',
    'Origin': 'https://allodswiki.ru',
    'Referer': 'https://allodswiki.ru/',
    'X-Site': 'allodswiki.ru',
    'User-Agent': 'discord-guild-bot',
}
ARMORY_TIMEOUT = 10


def _asset_url(path: str | None) -> str | None:
    """API отдаёт путь картинки без хоста и расширения."""
    if not path:
        return None
    if path.startswith('http'):
        return path
    return f'{ASSETS_URL}/{path.lstrip("/")}.webp'


def _armory_request(method: str, url: str, **kwargs) -> dict:
    response = requests.request(
        method, url, headers=ARMORY_HEADERS, timeout=ARMORY_TIMEOUT, **kwargs
    )
    response.raise_for_status()
    return response.json()


def character_lookup(server: int, name: str) -> dict | str | None:
    """
    Функция для получения информации об игроке через оружейку.

    Возвращает словарь параметров персонажа, None если персонаж не найден
    на сервере, или 'Bad site work', если API недоступен / сменил формат.
    """
    lookup_name = name
    # Поиск идёт по всем серверам и без учёта регистра, поэтому
    # фильтруем по id сервера и точному совпадению ника
    try:
        search = _armory_request(
            'POST', f'{ARMORY_API}/search',
            json={'q': lookup_name, 'limit': 50}
        )
        avatars = [
            result['data'] for result in search['results']
            if result.get('kind') == 'avatar'
        ]
    except (JSONDecodeError, KeyError, TypeError, requests_exceptions.RequestException) as e:
        logger.info(f'Упал сайт оружейки аллодов! (поиск) {e!r}')
        return 'Bad site work'

    found = next(
        (
            avatar for avatar in avatars
            if avatar.get('name') == lookup_name
            and (avatar.get('server') or {}).get('id') == server
        ),
        None
    )
    if not found:
        return None

    try:
        char_data = _armory_request(
            'GET', f'{ARMORY_API}/armory/avatars/{found["id"]}'
        )
    except (JSONDecodeError, requests_exceptions.RequestException) as e:
        logger.info(f'Упал сайт оружейки аллодов! (персонаж) {e!r}')
        return 'Bad site work'

    if not char_data or char_data.get('name') != lookup_name:
        return None

    class_capitalized = str(char_data.get('class')).capitalize()
    player_parms = {
        'nickname': lookup_name,
        'greatness': char_data.get('greatness'),
        'class': char_data.get('class'),
        'class_icon': (
            f'{ASSETS_URL}/Interface/Common/Elements/ClassIcons/'
            f'{class_capitalized}.50x50.webp'
        ),
        'faction': char_data.get('faction'),
        'guild': char_data.get('guild'),
        'level': char_data.get('level'),
        'gear_score': char_data.get('gear_score'),
        'updated_at': char_data.get('updated_at'),
    }

    # equipment: список {place, position, item}; слоты как в старом API
    # ('primary-19' — эмблема, 'secondary-19' — драконий артефакт)
    items = {
        f'{slot.get("place")}-{slot.get("position")}': slot.get('item') or {}
        for slot in char_data.get('equipment') or []
    }

    emblem = items.get('primary-19')
    if emblem:
        player_parms['emblem'] = {
            'name': emblem.get('name'),
            'image_url': _asset_url(emblem.get('image')),
        }
    dragon_emblem = items.get('secondary-19')
    if dragon_emblem:
        player_parms['dragon_emblem'] = {
            'name': dragon_emblem.get('name'),
            'image_url': _asset_url(dragon_emblem.get('image')),
        }
    # Наследие богов
    artifact = next(
        (item for item in items.values() if item.get('id') == 14078), None
    )
    if artifact:
        player_parms['artifact'] = {
            'name': artifact.get('name'),
            'image_url': _asset_url(artifact.get('image')),
            'level': artifact.get('level'),
        }
    return player_parms


def rcd_control_required_role(user: discord.Member | discord.User | None):
    """Проверка на наличие требуемых ролей у пользователя."""
    return (
        discord.utils.get(user.roles, name=LEADER_ROLE) or
        discord.utils.get(user.roles, name=RCD_CONTROL)
    )


def has_required_role(user: discord.Member | discord.User | None):
    """Проверка на наличие требуемых ролей у пользователя."""
    return (
        discord.utils.get(user.roles, name=LEADER_ROLE) or
        discord.utils.get(user.roles, name=TREASURER_ROLE) or
        discord.utils.get(user.roles, name=OFICER_ROLE)
    )

def require_role(func):
    """Декоратор для проверки наличия роли с доступом к команде бота"""
    @functools.wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        await interaction.response.defer(invisible=False, ephemeral=True)
        if not has_required_role(interaction.user):
            return await interaction.followup.send(ANSWERS_IF_NO_ROLE, delete_after=2)
        return await func(self, interaction, *args, **kwargs)
    return wrapper