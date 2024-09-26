import sqlite3


# Создание базы данных
conn = sqlite3.connect('reminds.db')
cursor = conn.cursor()


def add_remind_to_db(user_id, message, remind_date):
    """Добавляет напоминание в базу данных"""
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
