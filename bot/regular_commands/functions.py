from random import randint, choice
import sqlite3


# Создание базы данных
conn = sqlite3.connect('reminds.db')
cursor = conn.cursor()


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
            f'_{'\n'.join([f'{i+1} - {val}' for i, val in enumerate(values)])}\n'
            f'Победитель: **{choice(values)}**_'
        )
        return message


def remind_message(date: str, message: str) -> str:
    """
    Функция выдает сообщение о напоминании.

    Parameters
    ----------
        date: str
            Отформатированная строка даты и времени.

        message: str
            Сообщение, которое будет отправлено.

    Returns
    -------
        'str'
            Результирующая строка никнеймом и числом рандомайзера.
    """
    return (
        f'👋\n_Сообщение будет отправлено в {date}.\n'
        f'__**Тебе в ЛС**__✅.\n'
        f'Содержание сообщения: "{message}"._'
    )


def add_remind_to_db(user_id, message, remind_date):
    """Добавляет напоминание в базу данных"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminds
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, remind_date TEXT)
    ''')
    cursor.execute(
        'INSERT INTO reminds (user_id, message, remind_date) VALUES (?, ?, ?)',
        (user_id, message, remind_date)
    )
    conn.commit()


def delete_remind_from_db(user_id, remind_date):
    """Удаляет напоминание из базы данных"""
    cursor.execute(
        'DELETE FROM reminds WHERE user_id = ? AND remind_date = ?',
        (user_id, remind_date)
    )
    conn.commit()
