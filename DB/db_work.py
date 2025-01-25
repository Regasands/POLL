import psycopg2
from CONFIG.config import DbCondig

TABLES = [
    'admin_vote',
    'info_poll',
    'your_money',
    'current_topic',
    'admin',
    'user_info'
]

def get_connection():
    try:
        return psycopg2.connect(
            dbname=DbCondig.DBNAME,
            user=DbCondig.USER,
            password=DbCondig.PASSWORD,
            host=DbCondig.HOST,
            port=DbCondig.PORT
        )
    except Exception as e:
        print("Ошибка подключения к базе данных:", e)
        return None

def create_table(con, cur, index):
    query = None

    if index == 1:
        query = '''CREATE TABLE user_info (
            id BIGSERIAL PRIMARY KEY,
            user_id_tg BIGINT UNIQUE,
            language_s VARCHAR(50),
            date_register DATE
        );'''

    elif index == 2:
        query = '''CREATE TABLE your_money (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT,
            count_money BIGINT,
            your_vote BIGINT,
            your_open_poll BIGINT[],
            your_close_poll BIGINT[],
            FOREIGN KEY (user_id) REFERENCES user_info(user_id_tg)
        );'''

    elif index == 3:
        query = '''CREATE TABLE admin (
            user_id BIGINT PRIMARY KEY
        );'''

    elif index == 4:
        query = '''CREATE TABLE current_topic (
            id BIGSERIAL PRIMARY KEY,
            topic_name VARCHAR(255),
            count_vote BIGINT);'''


    elif index == 5:
        query = '''CREATE TABLE info_poll (
            id_p BIGSERIAL PRIMARY KEY,
            description VARCHAR(255),
            id_user BIGINT NOT NULL,
            vote BIGINT,
            variants JSONB,
            multiple_choice BOOLEAN,
            url VARCHAR(255),
            user_accept BIGINT[],
            max_vote BIGINT,
            topic_id BIGINT,
            status BOOLEAN,
            FOREIGN KEY (topic_id) REFERENCES current_topic(id),
            FOREIGN KEY (id_user) REFERENCES user_info(user_id_tg)
        );'''
    elif index == 6:
        query = '''CREATE TABLE admin_vote (
            id BIGSERIAL PRIMARY KEY,
            id_poll BIGINT,
            user_id BIGINT,
            FOREIGN KEY (user_id) REFERENCES user_info(user_id_tg)
        );'''

    elif index == 7:
        # не используется
        query = '''CREATE TABLE chanel (
        id BIGSERIAL PRIMARY KEY,
        url VARCHAR(255),
        type VARCHAR(255),
        chat_id BIGINT,
        money BIGINT,
        user_done INTEGER[]);'''

    else:
        print(f"Неверный индекс: {index}. Таблица не создана.")
        return

    # Выполнение SQL-запроса
    try:
        cur.execute(query)
        con.commit()
        print(f"Таблица с индексом {index} успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании таблицы с индексом {index}:", e)

def drop(con, cur):
    try:
        # Удаление таблиц в правильном порядке (из-за внешних ключей)
        for table in TABLES:
            query = f'DROP TABLE IF EXISTS {table} CASCADE'
            cur.execute(query)
        con.commit()
    except Exception as e:
        print(f"Ошибка при удалении таблиц: {e}")

def main():
    with get_connection() as con:
        with con.cursor() as cur:
            # drop(con, cur)
            for i in range(1, 7):  # создаем только нужные таблицы
                create_table(con, cur, i)
            cur.execute('''INSERT INTO admin (user_id) VALUES(%s)''', (1384189946,))
            con.commit()

if __name__ == "__main__":
    main()
