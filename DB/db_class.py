import asyncpg
import datetime
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
        query = '''INSERT INTO your_money (user_id, count_money, your_vote, your_open_pull, your_close_pull) VALUES($1, 0, 0, ARRAY[]::INTEGER[], ARRAY[]::INTEGER[])'''
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


    async def check_admin(self):
        res = await self.con.fetch('''SELECT user_id FROM admin''')
        return any(map(lambda x: self.id_user == x, map(lambda v: v['user_id'], res)))

    async def add_topic(self, text):
        query = '''INSERT INTO current_topic (topic_name, count_vote) VALUES($1, 0);'''
        try:
            await self.con.execute(query, text)
        except Exception as e:
            return e


class ConnectUserToBD(DbConnParent):
    def __init__(self, id_user):
        super().__init__(id_user)

    async def check_user(self):
        query = '''SELECT * FROM user_info INNER JOIN your_money on user_info.user_id_tg = your_money.user_id WHERE user_id_tg = $1 and user_id = $1'''

        res = await self.con.fetch(query, self.id_user)
        if len(res) == 0:
            return False
        return True

    async def get_param_user(self):
        sp = []
        for query in ('''SELECT * FROM user_info WHERE user_id_tg = $1''', '''SELECT * FROM your_money WHERE user_id = $1'''):
            sp.append(await self.con.fetchrow(query, self.id_user))
        return sp

    async def get_theam(self):
        res = await self.con.fetch('SELECT topic_name FROM current_topic')
        print(res)
        return res

    async def get_pull_theam(self, theam):
        res = await self.con.fetch('''SELECT * FROM info_pull INNER JOIN current_topic ON info_pull.topic_name = current_topic.id WHERE current_topic.topic_name''')


    async def create_pull(self, dicters: dict):
        query = '''INSERT INTO info_pull (description, id_user, vote, variants, multiple_choice, url, max_vote, topic_id, status) VALUES ($1, $2, 0, $3, $4, $5, $6, $7, True) RETURNING *'''
        descr = dicters['descr']
        variants = dicters['variants']
        multiple_choise = dicters['multiple_choice']
        url = dicters['url']
        max_vote = dicters['max_vote']
        print(dicters)
        id_theam = await self.con.fetchrow('''SELECT id, topic_name FROM current_topic WHERE topic_name = $1''', dicters['topic_name'])
        result = await self.con.fetchrow(query, descr, self.id_user, variants, multiple_choise, url, max_vote, id_theam['id'])
        await self.con.execute('''INSERT INTO admin_vote (id_pull,  user_id) VALUES ($1, $2)''', result['id'], self.id_user)
        await self.con.execute('''SET count_money UPDATE your_open_pull = array_append(your_open_pull, $1) WHERE user_id = $2''', result['id'], self.id_user)
        return result


    async def get_pull(self, topic_name):
        query = '''SELECT * FROM info_pull INNER JOIN current_topic ON info_pull.topic_id = current_topic.id WHERE $1 <> ALL(current_topic.user_accept) 
                    and current_topic.name= $2 and info_pull.status = True'''
        res = await self.con.fetchrow(query, self.id_user, topic_name)
        return res

    async def update_tables(self, vartiants, reconds):
        await self.con.execute('''UPDATE info_pull SET variants = $1, vote = vote + 1 WHERE id = $2''', variants, reconds['id'])
        await self.con.execute('''UPDATE count_money SET count_money = count_money + 1 WHERE user_id = $1''', self.id_user)
        

# class DbcreatePull(DbConnParent):
#     def __init__(self, **dicter): 
#         self.dicter = dicter
#         super().__init__()
    
#     def create_pull(se)

# a = DbCreateUser(1, 'ru')
# a.a()
