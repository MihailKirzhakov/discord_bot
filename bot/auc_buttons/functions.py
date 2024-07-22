import datetime
from decimal import Decimal

import discord

from variables import NOT_SOLD


def convert_bid(bid: int) -> str:
    """
    Функция для конвертирования стартовой стоимости лота
    в вид к примеру "800K" или "1.2M" в десятичную систему.

    Parameters
    ----------
        bid: int
            Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
        'str'
            Сконвертированная строка с объемом ставки и
            отображением единицы измерения.
    """
    result = (
        f'{Decimal(bid) / Decimal('1000')}K' if 100000 <= bid
        <= 900000 else f'{Decimal(bid) / Decimal('1000000')}M'
    )
    return result


def thousand_summ(
    original_label: Decimal,
    bid: int
) -> Decimal:
    """
    Функция считает суммы ставки с текущим значением на кнопке.

    Parameters
    ----------
    original_label: 'Decimal(float | int
        Число, взятое с кнопки.

    bid: int
        Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
        'Decimal(float | int)'
            Число, полученное в результате прибавления ставки
            для отображения в тысячах.
    """
    result = (
        original_label + (Decimal(bid) / Decimal('1000'))
    )
    return result


def million_summ(original_label, bid) -> Decimal:
    """
    Функция считает суммы ставки с текущим значением на кнопке.

    Parameters
    ----------
        original_label: Decimal(int | float)
            Число, взятое с кнопки.

        bid: str
            Ставка, параметр берется из slash-функции /go_auc.

    Returns
    -------
        'Decimal(float | int)'
            Число, полученное в результате прибавления ставки
            для отображения в миллионах.
    """
    result = (
        original_label + (Decimal(bid) / Decimal('1000000'))
    )
    return result


def label_count(
    button: discord.ui.Button,
    original_label: Decimal,
    name: discord.abc.User.display_name,
    bid: int
) -> str:
    """
    Функция считает результат вычисления числа после сделанной ставки.

    Parameters
    ----------
        button: discord.ui.Button
            Отображающаяся кнопка.

        original_label: Decimal(int | float)
            Число, взятое с кнопки.

        name: interaction.user.display_name
            Имя пользователя, который взаимодействовал с кнопкой.

        bid: int
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
            if original_label < 900 and (
                thousand_summ(original_label, bid) < 1000
            ):
                button.label = f'{thousand_summ(original_label, bid)}K {name}'
            else:
                button.label = (
                    f'{thousand_summ(
                        original_label, bid
                    ) / Decimal('1000')}M {name}'
                )
        else:
            button.label = f'{million_summ(original_label, bid)}M {name}'
    return button.label


def convert_to_mention(
    label_values: list,
    button_mentions: dict
) -> list:
    """
    Функция преобразует никнейм игрока на кнопке в тэг,
    для вывода списка победителей.

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
            result.append(NOT_SOLD)
    return result


def convert_sorted_message(values: list) -> str:
    """
    Функция преобразует список строк, в нумерованный,
    отсортированный список победителей.

    Parameters
    ----------
        values: list
            Список строк с содержимым кнопок (ставка + тэг ника).

    Returns
    -------
        message: str
            Результирующая, отсортированная, пронумерованная строка
            с переносами на новую строку с тэгами ников.
    """
    if values == NOT_SOLD:
        return values
    cost = values.split(' ')[0]
    cost_mult = (
        1_000_000 if cost[-1] == 'M' else 1_000 if cost[-1] == 'K' else 1
    )
    cost = float(cost[:-1]) * cost_mult
    return cost


def seconds_until_date(target_date_time: str) -> int:
    """
    Функция считает количество секунд до определенной даты и времени.

    Parameters
    ----------
        target_date_time: str
            Дата и время в ДД-ММ ЧЧ:ММ:СС формате.

    Returns
    -------
        minutes_until: int
            Количество секунд до определенной даты и времени.
    """
    if len(target_date_time) == 11:
        target_date_time += ':00'
    parts = target_date_time.split()
    if len(parts) != 2:
        raise ValueError("Неверный формат. Ожидался ДД.ММ ЧЧ:ММ:СС")
    day, month = parts[0].replace('-', '.').replace('/', '.').replace('_', '.').split('.')
    hour, minute, second = parts[1].split(':')
    target_datetime = datetime.datetime(
        datetime.date.today().year,
        int(month), int(day), int(hour), int(minute), int(second)
    )
    now = datetime.datetime.now()
    time_diff = target_datetime - now
    seconds_until = time_diff.total_seconds()
    return int(seconds_until)
