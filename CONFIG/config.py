from CONFIG.confident import *


class DataCallBack:
    GLOBAL_DCITER = {
        'Профиль': '1',
        'Пройти опрос': '1.1',
        'Заказать опрос': '1.2',
        'Посмотреть твои опросы': 'check_your_poll'
        }
    
    ADMIN_FUNC = {
        'Добавить Тему': 'admin.1'
    }

class DbCondig:
    DBNAME = DBNAME
    USER = USER
    PASSWORD = PASSWORD
    HOST = HOST
    PORT = PORT


class TonWallet:
    ADDRESS = "UQD-GWFvMpW8px3ETDOdejZJKaesWlT3raYck0SGFVap5sTe"