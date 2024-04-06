from decimal import Decimal
from random import randint


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
    values = nicknames.split()
    result = dict()

    for i in values:
        rand_value = randint(1, 100)
        result[i] = rand_value

    message = '\n'.join([f'{key} - {val}' for key, val in result.items()])

    print(message)