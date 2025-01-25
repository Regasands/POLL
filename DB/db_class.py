import asyncpg
import datetime

from typing import Union
from CONFIG.config import DbCondig

class DbConnParent:
    '''Родительский клас'''
    def __init__(self, id_user):
        self.id_user = id_user
        self.con = None

    async def __call__(self):
        try:
            connection_str = f"postgresql://{DbCondig.USER}:{DbCondig.PASSWORD}@{DbCondig.HOST}:{DbCondig.PORT}/{DbCondig.DBNAME}"
            self.con = await asyncpg.connect(connection_str)
        except Exception as e:
            print(e)

    async def close(self):
        await self.con.close()

    async def __aenter__(self):
        await self.__call__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        if exc_type:
            print(f'Произошла ошибка, {exc_type}')
        return False



class DbCreateUser(DbConnParent):
    '''Создаем таблицы при новом пользователе '''
    def __init__(self, id_user, lang):
        self.lang = lang
        super().__init__(id_user)

    async def create_info_user(self):
        query = '''INSERT INTO user_info (user_id_tg, language_s, date_register) VALUES($1, $2, $3)'''
        await self.con.execute(query, self.id_user, self.lang, datetime.datetime.now())

    async def create_money(self):
        query = '''INSERT INTO your_money (user_id, count_money, your_vote, your_open_poll, your_close_poll) VALUES($1, 0, 0, ARRAY[]::BIGINT[], ARRAY[]::BIGINT[])'''
        await self.con.execute(query, self.id_user)

    async def a(self):
        try:
            await self.create_info_user()
            await self.create_money()
        except Exception as e:
            print(e)


class AdminWork(DbConnParent):
    '''Тех класс, для быстрой работой с бд'''
    def __init__(self, id_user):    
        super().__init__(id_user)


    async def check_admin(self) -> bool:
        res = await self.con.fetch('''SELECT user_id FROM admin''')
        return any(map(lambda x: self.id_user == x, map(lambda v: v['user_id'], res)))

    async def add_topic(self, text):
        query = '''INSERT INTO current_topic (topic_name, count_vote) VALUES($1, 0);'''
        try:
            await self.con.execute(query, text)
        except Exception as e:
            return e
        
    async def add_chanel(self, dicters):
        query = '''INSERT INTO CHANEL (url, type, chat_id, money, user_done) VALUES($1, $2, $3, $4, ARRAY[]::BIGINT[])'''
        await self.con.execute(query, dicters['url'], dicters['type'], dicters['chat_id'], dicters['money'])
    
    async def delete_chanel(self, url):
        query = '''DELETE FROM CHANEL WHERE url = $1'''
        await self.con.execute(query, url)


class ConnectUserToBD(DbConnParent):
    def __init__(self, id_user):
        super().__init__(id_user)

    async def check_user(self) -> bool:
        query = '''SELECT * FROM user_info INNER JOIN your_money on user_info.user_id_tg = your_money.user_id WHERE user_id_tg = $1 and user_id = $1'''

        res = await self.con.fetch(query, self.id_user)
        if len(res) == 0:
            return False
        return True

    async def get_param_user(self) -> list:
        # Получает информацию о пользователе
        sp = []
        for query in ('''SELECT * FROM user_info WHERE user_id_tg = $1''', '''SELECT * FROM your_money WHERE user_id = $1'''):
            sp.append(await self.con.fetchrow(query, self.id_user))
        return sp

    async def get_theam(self) -> list:
        res = await self.con.fetch('SELECT topic_name FROM current_topic')
        return res

    async def get_poll_theam(self, theam) -> None:
        res = await self.con.fetch('''SELECT * FROM info_poll INNER JOIN current_topic ON info_poll.topic_name = current_topic.id WHERE current_topic.topic_name''')


    async def create_poll(self, dicters: dict) -> dict:
        query = '''INSERT INTO info_poll (description, id_user, vote, variants, multiple_choice, url, user_accept, max_vote, topic_id, status) VALUES ($1, $2, 0, $3, $4, $5, $6, $7, $8, True) RETURNING *'''
        descr = dicters['descr']
        variants = dicters['variants']
        multiple_choise = dicters['multiple_choice']
        url = dicters['url']
        max_vote = dicters['max_vote']

        id_theam = await self.con.fetchrow('''SELECT id, topic_name FROM current_topic WHERE topic_name = $1''', dicters['topic_name'])
        result = await self.con.fetchrow(query, descr, self.id_user, variants, multiple_choise, url, [1], max_vote, id_theam['id'])
        await self.con.execute('''INSERT INTO admin_vote (id_poll,  user_id) VALUES ($1, $2)''', result['id_p'], self.id_user)
        await self.con.execute('''UPDATE your_money SET your_open_poll = array_append(your_open_poll, $1) WHERE user_id = $2''', result['id_p'], self.id_user)
        return result


    async def get_poll(self, topic_name, additional_param=None) -> Union[dict, None]:
        if not additional_param:
            query = '''SELECT * FROM info_poll INNER JOIN current_topic ON info_poll.topic_id = current_topic.id WHERE NOT ($1 = ANY(info_poll.user_accept))
                        and current_topic.topic_name = $2 and info_poll.status = True'''
            res = await self.con.fetch(query, self.id_user, topic_name)
        else:
            query = '''SELECT * FROM info_poll INNER JOIN current_topic ON info_poll.topic_id = current_topic.id WHERE NOT ($1 = ANY(info_poll.user_accept))
                        and current_topic.topic_name = $2 and info_poll.status = True and NOT (info_poll.id_p = ANY($3)) '''
            res = await self.con.fetch(query, self.id_user, topic_name, additional_param)
        if res:
            return res[0]


    async def update_tables(self, variants, reconds) -> None:
        if reconds['max_vote'] < reconds['vote'] + 1:
            await self.con.execute('''UPDATE info_poll SET status = False WHERE id_p = $1''', reconds['id_p'])
        else:
            await self.con.execute('''UPDATE info_poll SET variants = $1, vote = vote + 1 WHERE id_p = $2''', variants, reconds['id_p'])
        await self.con.execute('''UPDATE info_poll SET user_accept = array_append(user_accept, $1) WHERE id_p = $2''', self.id_user, reconds['id_p']), 
        await self.con.execute('''UPDATE your_money SET count_money = count_money + 1, your_vote = your_vote + 1 WHERE user_id = $1''', self.id_user)
        await self.con.execute('''UPDATE current_topic SET count_vote = count_vote + 1 WHERE id = $1''', reconds['topic_id'])

    async def get_your_polls(self) -> Union[list, None]:
        query = '''SELECT * FROM info_poll WHERE id_user = $1'''
        res = await self.con.fetch(query, self.id_user)
        return res

    async def get_chanels(self) -> list:
        query = '''SELECT * FROM chanel WHERE NOT ($1 =  ANY(chanel.user_done))'''
        res = await self.con.fetch(query, self.id_user)
        res = res[:9] if len(res) > 9 else res
        return res

    async def check_chanel(self, id_c):
        res = await self.con.fetchrow('''SELECT * FROM chanel WHERE id = $1 and  NOT($2 = ANY(chanel.user_done))''', id_c, self.id_user)
        print(res)
        if res:
            return True
        return False

    async def update_param(self, id_c: int):
        query = '''UPDATE chanel SET user_done = array_append(user_done, $1) WHERE id = $2'''
        await self.con.execute(query, self.id_user, id_c)

    async def add_money(self, count: int):
        query = '''UPDATE your_money SET count_money = count_money + $1 WHERE user_id = $2'''
        await self.con.execute(query, count, self.id_user)


# class DbcreatePull(DbConnParent):
#     def __init__(self, **dicter): 
#         self.dicter = dicter
#         super().__init__()
    
#     def create_pull(se)

# a = DbCreateUser(1, 'ru')
# a.a()
