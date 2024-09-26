from random import randint, choice


def rand_choice(nicknames: str) -> str | None:
    """
    Функция выдает список победителей в рандомайзере.

    Parameters
    ----------
        nicknames: str
            Строка с никнэймами через пробел.

    Returns
    -------
        message: str | None
            Результирующая строка никнеймом и числом рандомайзера
    """
    values = nicknames.replace('_', '-').split('-')

    if len(values) == 1:
        return None
    if values[0].isdigit():
        return randint(int(values[0]), int(values[1]))
    else:
        message = (
            f'_{'\n'.join([f'{i+1} - {val}' for i, val in enumerate(values)])}\n\n'
            f'**Победитель: {choice(values)}**_'
        )
        return message
