import sqlite3

# Создание базы данных
def init_db():
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permanent_storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Сохранение данных в постоянное хранилище
def save_to_permanent_storage(data):
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO permanent_storage (title, url, xpath) VALUES (?, ?, ?)', data)
    conn.commit()
    conn.close()

# Сохранение данных во временное хранилище
def save_to_temp_storage(data):
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM temp_storage')  # Очищаем временное хранилище
    cursor.executemany('INSERT INTO temp_storage (title, url, xpath) VALUES (?, ?, ?)', data)
    conn.commit()
    conn.close()

# Получение данных из временного хранилища
def get_temp_data():
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, url, xpath FROM temp_storage')
    data = cursor.fetchall()
    conn.close()
    return data