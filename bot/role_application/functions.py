import discord
import requests

from variables import (
    ANSWERS_IF_NO_ROLE, LEADER_ROLE, OFICER_ROLE,
    TREASURER_ROLE
)


def character_lookup(server: int, name: str) -> dict | None:
    """
    Функция для получения информации об игроке через оружейку.

    Parameters
    ----------
    server: int
        Число, обозначающее сервер на сайте оружейки через
        панель разработки.

    name: str
        Никнейм игрока взятый с оружейки.

    Returns
    -------
    player_parms: dict
        Словарь с параметрами персонажа
    """
    # Никнейм игрока, которого ищем в оружейке
    lookup_name = name
    # Отправляем запрос на поиск
    look_response = requests.post(
        'https://api.allodswiki.ru/api/v1/armory/avatars',
        json={"filter": {"name": lookup_name, "server": server}}
    )
    lookup_response = look_response.json()['data']
    data_id = 0
    if len(lookup_response) > 0:
        data_id = lookup_response[0]['id']
    else:
        return None

    lookup_url = f'https://api.allodswiki.ru/api/v1/armory/avatars/{data_id}'

    # Словарь с параметрами персонажа
    player_parms = {}
    # Никнейм
    player_parms['nickname'] = lookup_name

    char_info = requests.get(lookup_url).json()
    char_data = char_info['data']

    if not char_data:
        return None
    if char_data['name'] != lookup_name:
        return None
    # Величка
    player_parms['greatness'] = char_data['greatness']
    # Класс персонажа
    player_parms['class'] = char_data['class']
    # Переменная для конвертирования в url ниже
    class_capitalized = str(player_parms['class']).capitalize()
    # url для иконки класса
    player_parms['class_icon'] = (
        f'https://assets.allodswiki.ru/Interface/Common/Elements/ClassIcons/{class_capitalized}.50x50.webp'
    )
    # Фракция
    player_parms['faction'] = char_data['faction']
    # Гильдия
    player_parms['guild'] = char_data['guild']
    # Уровень персонажа
    player_parms['level'] = char_data['level']
    # Гирскор
    player_parms['gear_score'] = char_data['gear_score']

    # Экипировка персонажа
    items = char_data['items']
    # Если нет элементов экипировки, то ...
    if not items:
        # Возвращаем параметры персонажа
        return player_parms

    # Эмблема персонажа
    emblem = items.get('primary-19', None)
    if emblem:
        # Добавляем в словарь название эмблемы и иконку
        player_parms['emblem'] = {
            "name": emblem['name'],
            "image_url": emblem['image']
        }  # type: ignore
    # Драконий артефакт (шип или память света)
    dragon_emblem = items.get('secondary-19', None)
    if dragon_emblem:
        # Добавляем в словарь драконий артефакт
        player_parms['dragon_emblem'] = {
            "name": dragon_emblem['name'],
            "image_url": dragon_emblem['image']
        }  # type: ignore
    # Наследие богов
    artifact = {}

    # Берём параметры наследия богов
    arts_lookup = [
        i for k, i in items.items() if 'id' in i and i['id'] == 14078
    ]
    if len(arts_lookup) > 0:
        # Элемент списка для выбора параметров
        artifact = arts_lookup[0]

        # Параметры артефакта наследия богов
        player_parms['artifact'] = {
                "name": artifact['name'],
                "image_url": artifact['image'],
                "level": artifact['level']
            }  # type: ignore
    return player_parms


def has_required_role(user: discord.Member):
    """Проверка на наличие требуемых ролей у пользователя

    Parameters
    ----------
        user: discord.abc.Member
            Пользователь, чьи роли проверяем.

    Returns
    -------
        None
    """
    return (
        discord.utils.get(user.roles, name=LEADER_ROLE) or
        discord.utils.get(user.roles, name=TREASURER_ROLE) or
        discord.utils.get(user.roles, name=OFICER_ROLE)
    )
