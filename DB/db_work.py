import psycopg2
from CONFIG.config import DbCondig

try:
    # Подключение к базе данных
    con = psycopg2.connect(
        dbname=DbCondig.DBNAME,
        user=DbCondig.USER,
        password=DbCondig.PASSWORD,
        host=DbCondig.HOST,
        port=DbCondig.PORT
    )
    cur = con.cursor()
except Exception as e:
    print("Ошибка подключения к базе данных:", e)


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
            your_open_pull TEXT[],
            your_close_pull TEXT[],
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
        query = '''CREATE TABLE info_pull (
            id BIGSERIAL PRIMARY KEY,
            description VARCHAR(255),
            id_user BIGINT NOT NULL,
            vote VARCHAR(255),
            variants JSONB,
            multiple_choice BOOLEAN,
            url VARCHAR(255),
            user_accept TEXT[],
            max_vote BIGINT,
            topic_id BIGINT,
            status BOOLEAN,
            FOREIGN KEY (topic_id) REFERENCES current_topic(id),
            FOREIGN KEY (id_user) REFERENCES user_info(user_id_tg)
        );'''
    elif index == 6:
        query = '''CREATE TABLE admin_vote (
            id BIGSERIAL PRIMARY KEY,
            id_pull BIGINT,
            user_id BIGINT,
            FOREIGN KEY (user_id) REFERENCES user_info(user_id_tg)
        );'''

    elif index == 7:
        # не используется
        query = '''CREATE TABLE requirements_user (
            id BIGSERIAL PRIMARY KEY,
            user_info BIGINT NOT NULL,
            FOREIGN KEY (user_info) REFERENCES user_info(user_id_tg),
        );'''

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
        for e in ['user_info', 'your_money', 'admin', 'current_topic', 'info_pull', 'admin_vote']:
            query = f'DROP TABLE {e}'
            cur.execute(query)
            con.commit()
    except Exception as e:
        print(e)
        
# drop(con, cur)
# Пример вызова функции
for i in range(7):
    create_table(con, cur, i)
# Закрытие соединения
cur.close()
con.close()
