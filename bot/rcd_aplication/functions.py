from reminder.functions import cursor, conn


def add_message_id(message_name, message_id):
    """Добавляет или обновляет ID сообщения в котором хранятся заявки на РЧД"""
    cursor.execute(
        'INSERT OR REPLACE INTO rcd_application (message_name, message_id) VALUES (?, ?)',
        (message_name, message_id)
    )
    conn.commit()


def add_date_info(date_name: str, date: str):
    """Добавляет или обновляет информацию о дате РЧД в таблицу date_info"""
    cursor.execute(
        'INSERT OR REPLACE INTO date_info (date_name, date) VALUES (?, ?)',
        (date_name, date)
    )
    conn.commit()


def get_data_from_table(table_name: str, columns: str = '*', condition: str = None):
    """
    Функция для получения данных из таблицы БД.

    Args:
        table_name (str): Название таблицы из которой получаем данные.
        columns (str, optional): Колонка, для указания параметров поиска. По дефолту '*'.
        condition (str, optional): Условия для фильтрации данных. По дефолту None.

    Returns:
        value: Возвращает данные из таблицы.

    """
    query = f'SELECT {columns} FROM {table_name}'
    if condition:
        query += f' WHERE {condition}'
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def clear_rcd_application_table():
    """Очищает таблицу rcd_application в базе данных"""
    cursor.execute('DELETE FROM rcd_application')
    conn.commit()


def clear_date_info_table():
    """Очищает таблицу rcd_application в базе данных"""
    cursor.execute('DELETE FROM date_info')
    conn.commit()
