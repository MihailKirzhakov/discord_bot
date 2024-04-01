from decimal import Decimal


def convert_bid(bid) -> str:
    """
    Функция для конвертирования стартовой стоимости лота
    в вид к примеру "800K" или "1,2M" в десятичную систему.
    """
    result = (
        f'{Decimal(bid) / Decimal('1000')}K' if 100000 <= bid
        <= 900000 else f'{Decimal(bid) / Decimal('1000000')}M'
    )
    return result


def thousand_summ(original_label, bid):
    result = (
        original_label + (Decimal(bid) / Decimal('1000'))
    )
    return result


def million_summ(original_label, bid):
    result = (
        original_label + (Decimal(bid) / Decimal('1000000'))
    )
    return result


def label_count(button, original_label, name, bid):
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
    result = []
    for value in label_values:
        split_value = value.split()
        if len(split_value) > 1:
            split_value[-1] = button_mentions[split_value[-1]]
            result.append(' '.join(split_value))
        else:
            result.append('Лот не был выкуплен')
    return result


def convert_sorted_message(sorted_values):
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