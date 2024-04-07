from random import choice, randint

def rand_choice(nicknames='1-100'):
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