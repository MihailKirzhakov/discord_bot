import requests
import base64
import discord

from PIL import Image
from io import BytesIO

from decimal import Decimal
from random import randint, choice


def convert_bid(bid) -> str:
    """
    Функция для конвертирования стартовой стоимости лота
    в вид к примеру "800K" или "1,2M" в десятичную систему.

    Parameters
    ----------
    bid: 'str'
        Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
    'str'
        Сконвертированная строка с объемом ставки и отображением единицы измерения.
    """
    result = (
        f'{Decimal(bid) / Decimal('1000')}K' if 100000 <= bid
        <= 900000 else f'{Decimal(bid) / Decimal('1000000')}M'
    )
    return result


def thousand_summ(original_label, bid):
    """
    Функция считает суммы ставки с текущим значением на кнопке.

    Parameters
    ----------
    original_label: 'Decimal(float | int)'
        Число, взятое с кнопки.

    bid: 'str'
        Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
    'Decimal(float | int)'
        Число, полученное в результате прибавления ставки для отображения в тысячах.
    """
    result = (
        original_label + (Decimal(bid) / Decimal('1000'))
    )
    return result


def million_summ(original_label, bid):
    """
    Функция считает суммы ставки с текущим значением на кнопке.

    Parameters
    ----------
    original_label: 'Decimal(int | float)'
        Число, взятое с кнопки.

    bid: 'str'
        Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
    'Decimal(float | int)'
        Число, полученное в результате прибавления ставки для отображения в миллионах.
    """
    result = (
        original_label + (Decimal(bid) / Decimal('1000000'))
    )
    return result


def label_count(button, original_label, name, bid):
    """
    Функция считает результат вычисления числа после сделанной ставки.

    Parameters
    ----------
    button: 'discord.ui.Button'
        Отображающаяся кнопка.
    
    original_label: 'Decimal(int | float)'
        Число, взятое с кнопки.

    name: 'interaction.user.display_name'
        Имя пользователя, который взаимодействовал с кнопкой.

    bid: 'str'
        Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
    button.label: str
        Строка, отображающаяся на кнопке.
    """
    if len(button.label.split()) == 1:
        if 'K' in button.label:
            button.label = f'{original_label}K {name}'
        else:
            button.label = f'{original_label}M {name}'
    else:
        if 'K' in button.label:
            if original_label < 900 and thousand_summ(original_label, bid) < 1000:
                button.label = f'{thousand_summ(original_label, bid)}K {name}'
            else:
                button.label = f'{thousand_summ(original_label, bid) / Decimal('1000')}M {name}'
        else:
            button.label = f'{million_summ(original_label, bid)}M {name}'
    return button.label


def convert_to_mention(label_values, button_mentions):
    """
    Функция преобразует никнейм игрока на кнопке в тэг, для вывода списка победителей.

    Parameters
    ----------
    label_values: list
        Список строк, которые содержат ставку и никнейм игрока.

    button_mentions: dict
        Словарь, в котором ключи это 'display_nmame', а значения это 'mention'.

    Returns
    -------
    result: list
        Результирующий список строк с тэгами ников.
    """
    result = list()
    for value in label_values:
        split_value = value.split()
        if len(split_value) > 1:
            split_value[-1] = button_mentions[split_value[-1]]
            result.append(' '.join(split_value))
        else:
            result.append('Лот не был выкуплен')
    return result


def convert_sorted_message(sorted_values):
    """
    Функция преобразует список строк, в нумерованный, отсортированный список победителей.

    Parameters
    ----------
    sorted_values: list
        Список строк с содержимым кнопок (ставка + тэг ника).

    Returns
    -------
    message: str
        Результирующая, отсортированная, пронумерованная строка
        с переносами на новую строку с тэгами ников.
    """
    second_sort = list()
    check = 0
    for i in range(0, len(sorted_values)):
        if 'M' in sorted_values[i]:
            second_sort.insert(0, sorted_values[i])
            check += 1
        elif 'K' in sorted_values[i]:
            second_sort.insert(check, sorted_values[i])
        else:
            second_sort.append(sorted_values[i])
    message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(second_sort)])
    return message


def rand_choice(nicknames):
    """
    Функция выдает список победителей в рандомайзере.

    Parameters
    ----------
    nicknames: str
        Строка с никнэймами через пробел.

    Returns
    -------
    message: str
        Результирующая строка никнеймом и числом рандомайзера
    """
    values = nicknames.split('-')

    if values[0].isdigit():
        return randint(int(values[0]), int(values[1]))
    else:
        message = f'Участники:\n{'\n'.join([f'{i+1} - {val}' for i, val in enumerate(values)])}\nПобедитель: {choice(values)}'
        return message


def character_lookup(server: int, name: str):
    """Функция для получения информации об игроке через оружейку"""
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
    emblem = items['primary-19']
    if emblem:
        # Добавляем в словарь название эмблемы и иконку
        player_parms['emblem'] = {
            "name": emblem['name'],
            "image_url": emblem['image']
        }
    else:
        return player_parms
    # Драконий артефакт (шип или память света)
    dragon_emblem = items['secondary-19']
    if dragon_emblem:
        # Добавляем в словарь драконий артефакт
        player_parms['dragon_emblem'] = {
            "name": dragon_emblem['name'],
            "image_url": dragon_emblem['image']
        }
    else:
        return player_parms
    # Наследие богов
    artifact = {}

    # Берём параметры наследия богов
    arts_lookup = [i for k, i in items.items() if i['id'] == 14078]
    if len(arts_lookup) > 0:
        # Элемент списка для выбора параметров
        artifact = arts_lookup[0]

        # Параметры артефакта наследия богов
        player_parms['artifact'] = {
                "name": artifact['name'],
                "image_url": artifact['image'],
                "level": artifact['level']
            }
    return player_parms

def generate_thumbnail(player_parms):
    class_icon_url = player_parms['class_icon']
    class_icon = requests.get(class_icon_url)
    class_image = Image.open(BytesIO(class_icon.content))

    result = Image.new("RGB", (50, 50))

    result.paste(class_image, (0, 0))

    if 'emblem' in player_parms and player_parms['emblem']:
        emblem_icon = requests.get(player_parms['emblem']['image_url'])
        emblem_image = Image.open(BytesIO(emblem_icon.content))
        emblem_image = emblem_image.resize((20, 20))

        result.paste(emblem_image, (30, 30))

    if 'dragon_emblem' in player_parms and player_parms['dragon_emblem']:
        dragon_emblem_icon = requests.get(player_parms['dragon_emblem']['image_url'])
        dragon_emblem_image = Image.open(BytesIO(dragon_emblem_icon.content))
        dragon_emblem_image = dragon_emblem_image.resize((20, 20))

        result.paste(dragon_emblem_image, (0, 30))
    
    # Вылезание картинки на экране
    result.show()

    buffered = BytesIO()
    result.save(buffered, format="JPEG")
    buffered.seek(0)

    file = discord.File(buffered, filename="thumbnail.jpg")

    return file
